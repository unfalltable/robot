"""
监控API端点
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.database import get_async_session
from app.services.monitoring_service import SystemMonitor, ApplicationMonitor, AlertEngine
from app.services.health_service import HealthChecker
from app.services.notification_service import NotificationService
from app.models.system_data import Alert, AlertRule, SystemMetrics, ApplicationMetrics
from app.repositories.base_repository import BaseRepository

router = APIRouter()

# 全局监控实例
system_monitor = SystemMonitor()
app_monitor = ApplicationMonitor()
health_checker = HealthChecker()
notification_service = NotificationService()
alert_engine = AlertEngine(notification_service)


@router.get("/health", summary="健康检查")
async def get_health_status():
    """获取系统健康状态"""
    try:
        health_status = await health_checker.check_overall_health()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.get("/health/summary", summary="健康状态摘要")
async def get_health_summary():
    """获取健康状态摘要"""
    try:
        summary = await health_checker.get_health_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取健康摘要失败: {str(e)}")


@router.get("/metrics/system", summary="系统指标")
async def get_system_metrics(
    hours: int = Query(24, description="历史小时数", ge=1, le=168),
    session: AsyncSession = Depends(get_async_session)
):
    """获取系统指标"""
    try:
        # 获取当前指标
        current_metrics = await system_monitor.get_current_metrics()
        
        # 获取历史指标
        history = await system_monitor.get_metrics_history(hours, session)
        
        return {
            "current": current_metrics,
            "history": history,
            "period_hours": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统指标失败: {str(e)}")


@router.get("/metrics/application", summary="应用指标")
async def get_application_metrics(
    hours: int = Query(24, description="历史小时数", ge=1, le=168),
    session: AsyncSession = Depends(get_async_session)
):
    """获取应用指标"""
    try:
        # 获取最近的应用指标
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        repo = BaseRepository(ApplicationMetrics, session)
        metrics = await repo.get_multi(
            filters={"timestamp": start_time},
            order_by="-timestamp",
            limit=1000
        )
        
        # 转换为字典格式
        history = [
            {
                'timestamp': metric.timestamp.isoformat(),
                'api_requests_total': metric.api_requests_total,
                'api_requests_success': metric.api_requests_success,
                'api_requests_error': metric.api_requests_error,
                'api_response_time_avg': metric.api_response_time_avg,
                'websocket_connections': metric.websocket_connections,
                'db_queries_total': metric.db_queries_total,
                'db_query_time_avg': metric.db_query_time_avg
            }
            for metric in metrics
        ]
        
        # 计算当前统计
        current_stats = {
            'uptime_seconds': app_monitor.get_uptime(),
            'cache_stats': app_monitor.metrics_cache
        }
        
        return {
            "current": current_stats,
            "history": history,
            "period_hours": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取应用指标失败: {str(e)}")


@router.get("/alerts", summary="获取告警")
async def get_alerts(
    status: Optional[str] = Query(None, description="告警状态"),
    severity: Optional[str] = Query(None, description="严重程度"),
    limit: int = Query(100, description="返回数量", ge=1, le=1000),
    session: AsyncSession = Depends(get_async_session)
):
    """获取告警列表"""
    try:
        repo = BaseRepository(Alert, session)
        
        filters = {}
        if status:
            filters['status'] = status
        if severity:
            filters['severity'] = severity
        
        alerts = await repo.get_multi(
            filters=filters,
            order_by="-triggered_at",
            limit=limit
        )
        
        return [
            {
                'id': alert.id,
                'rule_id': alert.rule_id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'status': alert.status,
                'metric_name': alert.metric_name,
                'metric_value': alert.metric_value,
                'threshold': alert.threshold,
                'triggered_at': alert.triggered_at.isoformat(),
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                'resolved_by': alert.resolved_by
            }
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取告警失败: {str(e)}")


@router.get("/alerts/active", summary="获取活跃告警")
async def get_active_alerts():
    """获取活跃告警"""
    try:
        alerts = await alert_engine.get_active_alerts()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活跃告警失败: {str(e)}")


@router.post("/alerts/{alert_id}/resolve", summary="解决告警")
async def resolve_alert(
    alert_id: int,
    resolved_by: str,
    notes: Optional[str] = None
):
    """解决告警"""
    try:
        success = await alert_engine.resolve_alert(alert_id, resolved_by, notes)
        if success:
            return {"message": "告警已解决"}
        else:
            raise HTTPException(status_code=404, detail="告警不存在或已解决")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解决告警失败: {str(e)}")


@router.get("/alert-rules", summary="获取告警规则")
async def get_alert_rules(
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    session: AsyncSession = Depends(get_async_session)
):
    """获取告警规则"""
    try:
        repo = BaseRepository(AlertRule, session)
        
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active
        
        rules = await repo.get_multi(filters=filters, order_by="name")
        
        return [
            {
                'id': rule.id,
                'name': rule.name,
                'description': rule.description,
                'category': rule.category,
                'metric_name': rule.metric_name,
                'operator': rule.operator,
                'threshold': rule.threshold,
                'severity': rule.severity,
                'is_active': rule.is_active,
                'trigger_count': rule.trigger_count,
                'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None,
                'created_at': rule.created_at.isoformat()
            }
            for rule in rules
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取告警规则失败: {str(e)}")


@router.post("/alert-rules", summary="创建告警规则")
async def create_alert_rule(
    rule_data: Dict[str, Any],
    session: AsyncSession = Depends(get_async_session)
):
    """创建告警规则"""
    try:
        repo = BaseRepository(AlertRule, session)
        rule = await repo.create(rule_data)
        
        return {
            'id': rule.id,
            'name': rule.name,
            'message': '告警规则创建成功'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建告警规则失败: {str(e)}")


@router.put("/alert-rules/{rule_id}", summary="更新告警规则")
async def update_alert_rule(
    rule_id: int,
    rule_data: Dict[str, Any],
    session: AsyncSession = Depends(get_async_session)
):
    """更新告警规则"""
    try:
        repo = BaseRepository(AlertRule, session)
        rule = await repo.update(rule_id, rule_data)
        
        if rule:
            return {
                'id': rule.id,
                'name': rule.name,
                'message': '告警规则更新成功'
            }
        else:
            raise HTTPException(status_code=404, detail="告警规则不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新告警规则失败: {str(e)}")


@router.delete("/alert-rules/{rule_id}", summary="删除告警规则")
async def delete_alert_rule(
    rule_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """删除告警规则"""
    try:
        repo = BaseRepository(AlertRule, session)
        success = await repo.delete(rule_id)
        
        if success:
            return {"message": "告警规则删除成功"}
        else:
            raise HTTPException(status_code=404, detail="告警规则不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除告警规则失败: {str(e)}")


@router.post("/notifications/test", summary="测试通知")
async def test_notification(
    channel: str,
    message: str = "这是一条测试消息"
):
    """测试通知渠道"""
    try:
        success = await notification_service.test_channel(channel)
        if success:
            return {"message": f"通知渠道 {channel} 测试成功"}
        else:
            return {"message": f"通知渠道 {channel} 测试失败"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试通知失败: {str(e)}")


@router.get("/notifications/channels", summary="获取通知渠道")
async def get_notification_channels():
    """获取可用的通知渠道"""
    try:
        channels = notification_service.get_channels()
        return {"channels": channels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取通知渠道失败: {str(e)}")


@router.post("/monitoring/start", summary="启动监控")
async def start_monitoring():
    """启动监控服务"""
    try:
        await system_monitor.start()
        await alert_engine.start()
        return {"message": "监控服务已启动"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动监控失败: {str(e)}")


@router.post("/monitoring/stop", summary="停止监控")
async def stop_monitoring():
    """停止监控服务"""
    try:
        await system_monitor.stop()
        await alert_engine.stop()
        return {"message": "监控服务已停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止监控失败: {str(e)}")


@router.get("/monitoring/status", summary="监控状态")
async def get_monitoring_status():
    """获取监控服务状态"""
    try:
        return {
            "system_monitor_running": system_monitor.is_running,
            "alert_engine_running": alert_engine.is_running,
            "uptime_seconds": app_monitor.get_uptime(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取监控状态失败: {str(e)}")
