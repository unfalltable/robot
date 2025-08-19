"""
监控任务
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.config import settings, MonitoringConfig
from app.services.monitoring_service import SystemMonitor, ApplicationMonitor, AlertEngine
from app.services.notification_service import NotificationService
from app.services.health_service import HealthChecker
from app.models.system_data import SystemMetrics, ApplicationMetrics, Alert
from app.repositories.base_repository import BaseRepository

# 创建Celery实例
celery_app = Celery(
    "monitoring_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟
    task_soft_time_limit=25 * 60,  # 25分钟
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

logger = logging.getLogger(__name__)
monitoring_config = MonitoringConfig()

# 全局监控实例
system_monitor = SystemMonitor()
app_monitor = ApplicationMonitor()
health_checker = HealthChecker()
notification_service = NotificationService()
alert_engine = AlertEngine(notification_service)


@celery_app.task(name="collect_system_metrics")
def collect_system_metrics():
    """收集系统指标任务"""
    try:
        # 由于Celery任务是同步的，我们需要在新的事件循环中运行异步代码
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(system_monitor._collect_system_metrics())
            logger.info("系统指标收集完成")
            return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"收集系统指标失败: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="collect_application_metrics")
def collect_application_metrics():
    """收集应用指标任务"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(app_monitor.collect_application_metrics())
            logger.info("应用指标收集完成")
            return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"收集应用指标失败: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="check_alert_rules")
def check_alert_rules():
    """检查告警规则任务"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(alert_engine._check_alert_rules())
            logger.info("告警规则检查完成")
            return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"检查告警规则失败: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="health_check")
def health_check():
    """健康检查任务"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            health_status = loop.run_until_complete(health_checker.check_overall_health())
            
            # 如果健康状态不佳，发送通知
            if health_status['status'] in ['warning', 'critical']:
                notification_message = f"系统健康检查警告: {health_status['status']}\n"
                notification_message += f"问题数量: 严重 {health_status['summary']['critical']}, 警告 {health_status['summary']['warning']}"
                
                loop.run_until_complete(
                    notification_service.send_system_notification(
                        event_type="health_check",
                        message=notification_message,
                        severity=health_status['status']
                    )
                )
            
            logger.info(f"健康检查完成: {health_status['status']}")
            return {
                "status": "success", 
                "health_status": health_status['status'],
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="cleanup_old_metrics")
def cleanup_old_metrics():
    """清理旧指标数据任务"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=monitoring_config.METRICS_RETENTION_DAYS)
            
            async def cleanup():
                async with get_async_session() as session:
                    # 清理系统指标
                    system_repo = BaseRepository(SystemMetrics, session)
                    system_deleted = await system_repo.bulk_delete([
                        metric.id for metric in await system_repo.get_multi(
                            filters={"timestamp": cutoff_date},
                            limit=10000
                        ) if metric.timestamp < cutoff_date
                    ])
                    
                    # 清理应用指标
                    app_repo = BaseRepository(ApplicationMetrics, session)
                    app_deleted = await app_repo.bulk_delete([
                        metric.id for metric in await app_repo.get_multi(
                            filters={"timestamp": cutoff_date},
                            limit=10000
                        ) if metric.timestamp < cutoff_date
                    ])
                    
                    return system_deleted, app_deleted
            
            system_deleted, app_deleted = loop.run_until_complete(cleanup())
            
            logger.info(f"清理完成: 系统指标 {system_deleted} 条, 应用指标 {app_deleted} 条")
            return {
                "status": "success",
                "system_metrics_deleted": system_deleted,
                "app_metrics_deleted": app_deleted,
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"清理旧指标失败: {str(e)}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="generate_monitoring_report")
def generate_monitoring_report():
    """生成监控报告任务"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def generate_report():
                async with get_async_session() as session:
                    # 获取最近24小时的统计
                    start_time = datetime.utcnow() - timedelta(hours=24)
                    
                    # 系统指标统计
                    system_repo = BaseRepository(SystemMetrics, session)
                    system_metrics = await system_repo.get_multi(
                        filters={"timestamp": start_time},
                        order_by="-timestamp",
                        limit=1440  # 24小时 * 60分钟
                    )
                    
                    # 应用指标统计
                    app_repo = BaseRepository(ApplicationMetrics, session)
                    app_metrics = await app_repo.get_multi(
                        filters={"timestamp": start_time},
                        order_by="-timestamp",
                        limit=1440
                    )
                    
                    # 告警统计
                    alert_repo = BaseRepository(Alert, session)
                    alerts = await alert_repo.get_multi(
                        filters={"triggered_at": start_time},
                        order_by="-triggered_at"
                    )
                    
                    # 计算统计数据
                    report = {
                        "period": "24h",
                        "generated_at": datetime.utcnow().isoformat(),
                        "system_metrics": {
                            "data_points": len(system_metrics),
                            "avg_cpu": sum(m.cpu_usage for m in system_metrics if m.cpu_usage) / max(len(system_metrics), 1),
                            "avg_memory": sum(m.memory_usage for m in system_metrics if m.memory_usage) / max(len(system_metrics), 1),
                            "avg_disk": sum(m.disk_usage for m in system_metrics if m.disk_usage) / max(len(system_metrics), 1),
                        },
                        "application_metrics": {
                            "data_points": len(app_metrics),
                            "total_api_requests": sum(m.api_requests_total for m in app_metrics if m.api_requests_total),
                            "total_api_errors": sum(m.api_requests_error for m in app_metrics if m.api_requests_error),
                            "avg_response_time": sum(m.api_response_time_avg for m in app_metrics if m.api_response_time_avg) / max(len(app_metrics), 1),
                        },
                        "alerts": {
                            "total": len(alerts),
                            "by_severity": {
                                "critical": len([a for a in alerts if a.severity == 'critical']),
                                "high": len([a for a in alerts if a.severity == 'high']),
                                "medium": len([a for a in alerts if a.severity == 'medium']),
                                "low": len([a for a in alerts if a.severity == 'low']),
                            }
                        }
                    }
                    
                    return report
            
            report = loop.run_until_complete(generate_report())
            
            # 发送报告通知
            report_message = f"""
监控报告 (最近24小时):

系统指标:
- 平均CPU使用率: {report['system_metrics']['avg_cpu']:.1f}%
- 平均内存使用率: {report['system_metrics']['avg_memory']:.1f}%
- 平均磁盘使用率: {report['system_metrics']['avg_disk']:.1f}%

应用指标:
- API请求总数: {report['application_metrics']['total_api_requests']}
- API错误总数: {report['application_metrics']['total_api_errors']}
- 平均响应时间: {report['application_metrics']['avg_response_time']:.1f}ms

告警统计:
- 告警总数: {report['alerts']['total']}
- 严重告警: {report['alerts']['by_severity']['critical']}
- 高级告警: {report['alerts']['by_severity']['high']}
            """.strip()
            
            loop.run_until_complete(
                notification_service.send_system_notification(
                    event_type="daily_report",
                    message=report_message,
                    severity="info"
                )
            )
            
            logger.info("监控报告生成完成")
            return {"status": "success", "report": report}
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"生成监控报告失败: {str(e)}")
        return {"status": "error", "error": str(e)}


# 定期任务配置
celery_app.conf.beat_schedule = {
    'collect-system-metrics': {
        'task': 'collect_system_metrics',
        'schedule': monitoring_config.METRICS_COLLECTION_INTERVAL,
    },
    'collect-application-metrics': {
        'task': 'collect_application_metrics',
        'schedule': monitoring_config.METRICS_COLLECTION_INTERVAL,
    },
    'check-alert-rules': {
        'task': 'check_alert_rules',
        'schedule': monitoring_config.ALERT_CHECK_INTERVAL,
    },
    'health-check': {
        'task': 'health_check',
        'schedule': monitoring_config.HEALTH_CHECK_INTERVAL,
    },
    'cleanup-old-metrics': {
        'task': 'cleanup_old_metrics',
        'schedule': 24 * 60 * 60,  # 每天执行一次
    },
    'generate-monitoring-report': {
        'task': 'generate_monitoring_report',
        'schedule': 24 * 60 * 60,  # 每天生成一次报告
    },
}

celery_app.conf.timezone = 'UTC'
