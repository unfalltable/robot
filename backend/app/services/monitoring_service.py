"""
监控服务
"""
import asyncio
import psutil
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.core.database import get_async_session
from app.models.system_data import SystemMetrics, ApplicationMetrics, AlertRule, Alert
from app.repositories.base_repository import BaseRepository
from app.core.config import MonitoringConfig


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.monitoring_task = None
        self.config = MonitoringConfig()
    
    async def start(self):
        """启动监控"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("系统监控已启动")
    
    async def stop(self):
        """停止监控"""
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("系统监控已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                # 收集系统指标
                await self._collect_system_metrics()
                
                # 等待下一次收集
                await asyncio.sleep(self.config.HEALTH_CHECK_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"监控循环错误: {str(e)}")
                await asyncio.sleep(60)  # 错误时等待1分钟
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            # 获取系统指标
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_load = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 网络统计
            net_io = psutil.net_io_counters()
            
            # 进程统计
            process_count = len(psutil.pids())
            
            # 创建系统指标记录
            metrics = {
                'timestamp': datetime.utcnow(),
                'cpu_usage': cpu_percent,
                'cpu_load_1m': cpu_load[0],
                'cpu_load_5m': cpu_load[1],
                'cpu_load_15m': cpu_load[2],
                'memory_usage': memory.percent,
                'memory_used': memory.used,
                'memory_available': memory.available,
                'memory_total': memory.total,
                'disk_usage': disk.percent,
                'disk_used': disk.used,
                'disk_available': disk.free,
                'disk_total': disk.total,
                'network_in': net_io.bytes_recv,
                'network_out': net_io.bytes_sent,
                'network_connections': len(psutil.net_connections()),
                'process_count': process_count
            }
            
            # 保存到数据库
            async with get_async_session() as session:
                system_metrics = SystemMetrics(**metrics)
                session.add(system_metrics)
                await session.commit()
            
            self.logger.debug(f"系统指标收集完成: CPU {cpu_percent}%, 内存 {memory.percent}%")
            
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {str(e)}")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前系统指标"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取当前指标失败: {str(e)}")
            return {}
    
    async def get_metrics_history(
        self, 
        hours: int = 24,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """获取指标历史"""
        try:
            if session is None:
                async with get_async_session() as session:
                    return await self._get_metrics_history_impl(session, hours)
            else:
                return await self._get_metrics_history_impl(session, hours)
                
        except Exception as e:
            self.logger.error(f"获取指标历史失败: {str(e)}")
            return []
    
    async def _get_metrics_history_impl(
        self, 
        session: AsyncSession, 
        hours: int
    ) -> List[Dict[str, Any]]:
        """获取指标历史实现"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = await session.execute(
            select(SystemMetrics)
            .where(SystemMetrics.timestamp >= start_time)
            .order_by(desc(SystemMetrics.timestamp))
            .limit(1000)
        )
        
        metrics = result.scalars().all()
        
        return [
            {
                'timestamp': metric.timestamp.isoformat(),
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'disk_usage': metric.disk_usage,
                'network_in': metric.network_in,
                'network_out': metric.network_out,
                'process_count': metric.process_count
            }
            for metric in metrics
        ]


class ApplicationMonitor:
    """应用监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_cache = {}
        self.start_time = time.time()
    
    def record_api_request(self, success: bool, response_time: float):
        """记录API请求"""
        if 'api_requests' not in self.metrics_cache:
            self.metrics_cache['api_requests'] = {
                'total': 0,
                'success': 0,
                'error': 0,
                'response_times': []
            }
        
        self.metrics_cache['api_requests']['total'] += 1
        if success:
            self.metrics_cache['api_requests']['success'] += 1
        else:
            self.metrics_cache['api_requests']['error'] += 1
        
        self.metrics_cache['api_requests']['response_times'].append(response_time)
        
        # 保持最近1000个响应时间
        if len(self.metrics_cache['api_requests']['response_times']) > 1000:
            self.metrics_cache['api_requests']['response_times'] = \
                self.metrics_cache['api_requests']['response_times'][-1000:]
    
    def record_websocket_event(self, event_type: str):
        """记录WebSocket事件"""
        if 'websocket' not in self.metrics_cache:
            self.metrics_cache['websocket'] = {
                'connections': 0,
                'messages_sent': 0,
                'messages_received': 0,
                'errors': 0
            }
        
        if event_type in self.metrics_cache['websocket']:
            self.metrics_cache['websocket'][event_type] += 1
    
    def record_database_query(self, query_time: float, is_slow: bool = False):
        """记录数据库查询"""
        if 'database' not in self.metrics_cache:
            self.metrics_cache['database'] = {
                'queries_total': 0,
                'queries_slow': 0,
                'query_times': []
            }
        
        self.metrics_cache['database']['queries_total'] += 1
        if is_slow:
            self.metrics_cache['database']['queries_slow'] += 1
        
        self.metrics_cache['database']['query_times'].append(query_time)
        
        # 保持最近1000个查询时间
        if len(self.metrics_cache['database']['query_times']) > 1000:
            self.metrics_cache['database']['query_times'] = \
                self.metrics_cache['database']['query_times'][-1000:]
    
    async def collect_application_metrics(self):
        """收集应用指标"""
        try:
            # 计算API指标
            api_metrics = self.metrics_cache.get('api_requests', {})
            response_times = api_metrics.get('response_times', [])
            
            api_response_time_avg = sum(response_times) / len(response_times) if response_times else 0
            api_response_time_p95 = self._calculate_percentile(response_times, 95) if response_times else 0
            api_response_time_p99 = self._calculate_percentile(response_times, 99) if response_times else 0
            
            # 计算数据库指标
            db_metrics = self.metrics_cache.get('database', {})
            query_times = db_metrics.get('query_times', [])
            db_query_time_avg = sum(query_times) / len(query_times) if query_times else 0
            
            # WebSocket指标
            ws_metrics = self.metrics_cache.get('websocket', {})
            
            # 创建应用指标记录
            metrics = {
                'timestamp': datetime.utcnow(),
                'api_requests_total': api_metrics.get('total', 0),
                'api_requests_success': api_metrics.get('success', 0),
                'api_requests_error': api_metrics.get('error', 0),
                'api_response_time_avg': api_response_time_avg,
                'api_response_time_p95': api_response_time_p95,
                'api_response_time_p99': api_response_time_p99,
                'websocket_connections': ws_metrics.get('connections', 0),
                'websocket_messages_sent': ws_metrics.get('messages_sent', 0),
                'websocket_messages_received': ws_metrics.get('messages_received', 0),
                'websocket_errors': ws_metrics.get('errors', 0),
                'db_queries_total': db_metrics.get('queries_total', 0),
                'db_queries_slow': db_metrics.get('queries_slow', 0),
                'db_query_time_avg': db_query_time_avg
            }
            
            # 保存到数据库
            async with get_async_session() as session:
                app_metrics = ApplicationMetrics(**metrics)
                session.add(app_metrics)
                await session.commit()
            
            # 重置缓存
            self.metrics_cache = {}
            
            self.logger.debug("应用指标收集完成")
            
        except Exception as e:
            self.logger.error(f"收集应用指标失败: {str(e)}")
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_uptime(self) -> float:
        """获取运行时间（秒）"""
        return time.time() - self.start_time


class AlertEngine:
    """告警引擎"""

    def __init__(self, notification_service=None):
        self.logger = logging.getLogger(__name__)
        self.notification_service = notification_service
        self.is_running = False
        self.alert_task = None
        self.alert_cache = {}  # 告警冷却缓存

    async def start(self):
        """启动告警引擎"""
        if self.is_running:
            return

        self.is_running = True
        self.alert_task = asyncio.create_task(self._alert_loop())
        self.logger.info("告警引擎已启动")

    async def stop(self):
        """停止告警引擎"""
        self.is_running = False
        if self.alert_task:
            self.alert_task.cancel()
            try:
                await self.alert_task
            except asyncio.CancelledError:
                pass
        self.logger.info("告警引擎已停止")

    async def _alert_loop(self):
        """告警检查循环"""
        while self.is_running:
            try:
                await self._check_alert_rules()
                await asyncio.sleep(60)  # 每分钟检查一次

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"告警检查错误: {str(e)}")
                await asyncio.sleep(60)

    async def _check_alert_rules(self):
        """检查告警规则"""
        try:
            async with get_async_session() as session:
                # 获取活跃的告警规则
                result = await session.execute(
                    select(AlertRule).where(AlertRule.is_active == True)
                )
                rules = result.scalars().all()

                for rule in rules:
                    await self._evaluate_rule(session, rule)

        except Exception as e:
            self.logger.error(f"检查告警规则失败: {str(e)}")

    async def _evaluate_rule(self, session: AsyncSession, rule: AlertRule):
        """评估告警规则"""
        try:
            # 检查冷却时间
            if self._is_in_cooldown(rule):
                return

            # 获取最新指标值
            metric_value = await self._get_metric_value(session, rule.metric_name)
            if metric_value is None:
                return

            # 评估条件
            triggered = self._evaluate_condition(
                metric_value,
                rule.operator,
                rule.threshold
            )

            if triggered:
                await self._trigger_alert(session, rule, metric_value)

        except Exception as e:
            self.logger.error(f"评估告警规则失败 {rule.name}: {str(e)}")

    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """检查是否在冷却时间内"""
        if rule.id not in self.alert_cache:
            return False

        last_triggered = self.alert_cache[rule.id]
        cooldown_seconds = rule.cooldown_minutes * 60

        return (datetime.utcnow() - last_triggered).total_seconds() < cooldown_seconds

    async def _get_metric_value(self, session: AsyncSession, metric_name: str) -> Optional[float]:
        """获取指标值"""
        try:
            if metric_name.startswith('system.'):
                # 系统指标
                field_name = metric_name.replace('system.', '')
                if hasattr(SystemMetrics, field_name):
                    result = await session.execute(
                        select(getattr(SystemMetrics, field_name))
                        .order_by(desc(SystemMetrics.timestamp))
                        .limit(1)
                    )
                    return result.scalar()

            elif metric_name.startswith('app.'):
                # 应用指标
                field_name = metric_name.replace('app.', '')
                if hasattr(ApplicationMetrics, field_name):
                    result = await session.execute(
                        select(getattr(ApplicationMetrics, field_name))
                        .order_by(desc(ApplicationMetrics.timestamp))
                        .limit(1)
                    )
                    return result.scalar()

            return None

        except Exception as e:
            self.logger.error(f"获取指标值失败 {metric_name}: {str(e)}")
            return None

    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """评估条件"""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold
        elif operator == '!=':
            return value != threshold
        else:
            return False

    async def _trigger_alert(self, session: AsyncSession, rule: AlertRule, metric_value: float):
        """触发告警"""
        try:
            # 创建告警记录
            alert = Alert(
                rule_id=rule.id,
                title=f"告警: {rule.name}",
                message=f"{rule.description or rule.name} - 当前值: {metric_value}, 阈值: {rule.threshold}",
                severity=rule.severity,
                metric_name=rule.metric_name,
                metric_value=metric_value,
                threshold=rule.threshold,
                triggered_at=datetime.utcnow()
            )

            session.add(alert)

            # 更新规则统计
            rule.trigger_count += 1
            rule.last_triggered = datetime.utcnow()

            await session.commit()

            # 发送通知
            if self.notification_service and rule.notification_channels:
                await self._send_notification(alert, rule.notification_channels)

            # 更新冷却缓存
            self.alert_cache[rule.id] = datetime.utcnow()

            self.logger.warning(f"告警触发: {rule.name} - {metric_value} {rule.operator} {rule.threshold}")

        except Exception as e:
            self.logger.error(f"触发告警失败: {str(e)}")

    async def _send_notification(self, alert: Alert, channels: List[str]):
        """发送通知"""
        try:
            if self.notification_service:
                await self.notification_service.send_alert_notification(alert, channels)
            else:
                self.logger.warning(f"通知服务未配置，无法发送告警通知: {alert.title}")

        except Exception as e:
            self.logger.error(f"发送告警通知失败: {str(e)}")

    async def resolve_alert(self, alert_id: int, resolved_by: str, notes: str = None):
        """解决告警"""
        try:
            async with get_async_session() as session:
                result = await session.execute(
                    select(Alert).where(Alert.id == alert_id)
                )
                alert = result.scalar_one_or_none()

                if alert and alert.status == 'active':
                    alert.status = 'resolved'
                    alert.resolved_at = datetime.utcnow()
                    alert.resolved_by = resolved_by
                    alert.resolution_notes = notes

                    await session.commit()

                    self.logger.info(f"告警已解决: {alert.title} by {resolved_by}")
                    return True

                return False

        except Exception as e:
            self.logger.error(f"解决告警失败: {str(e)}")
            return False

    async def get_active_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取活跃告警"""
        try:
            async with get_async_session() as session:
                result = await session.execute(
                    select(Alert)
                    .where(Alert.status == 'active')
                    .order_by(desc(Alert.triggered_at))
                    .limit(limit)
                )
                alerts = result.scalars().all()

                return [
                    {
                        'id': alert.id,
                        'title': alert.title,
                        'message': alert.message,
                        'severity': alert.severity,
                        'metric_name': alert.metric_name,
                        'metric_value': alert.metric_value,
                        'threshold': alert.threshold,
                        'triggered_at': alert.triggered_at.isoformat(),
                        'status': alert.status
                    }
                    for alert in alerts
                ]

        except Exception as e:
            self.logger.error(f"获取活跃告警失败: {str(e)}")
            return []
