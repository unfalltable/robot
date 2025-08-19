"""
健康检查服务
"""
import asyncio
import aiohttp
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.core.database import get_async_session, engine
from app.models.system_data import SystemMetrics, ApplicationMetrics
from app.core.config import Settings


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = Settings()
    
    async def check_overall_health(self) -> Dict[str, Any]:
        """检查整体健康状态"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {},
            'summary': {
                'healthy': 0,
                'warning': 0,
                'critical': 0
            }
        }
        
        # 执行各项健康检查
        checks = [
            ('database', self.check_database_health),
            ('system', self.check_system_health),
            ('application', self.check_application_health),
            ('external_apis', self.check_external_apis_health),
            ('data_sources', self.check_data_sources_health)
        ]
        
        for check_name, check_func in checks:
            try:
                result = await check_func()
                health_status['checks'][check_name] = result
                
                # 更新摘要
                status = result.get('status', 'unknown')
                if status == 'healthy':
                    health_status['summary']['healthy'] += 1
                elif status == 'warning':
                    health_status['summary']['warning'] += 1
                elif status == 'critical':
                    health_status['summary']['critical'] += 1
                    
            except Exception as e:
                self.logger.error(f"健康检查失败 {check_name}: {str(e)}")
                health_status['checks'][check_name] = {
                    'status': 'critical',
                    'message': f"检查失败: {str(e)}",
                    'timestamp': datetime.utcnow().isoformat()
                }
                health_status['summary']['critical'] += 1
        
        # 确定整体状态
        if health_status['summary']['critical'] > 0:
            health_status['status'] = 'critical'
        elif health_status['summary']['warning'] > 0:
            health_status['status'] = 'warning'
        else:
            health_status['status'] = 'healthy'
        
        return health_status
    
    async def check_database_health(self) -> Dict[str, Any]:
        """检查数据库健康状态"""
        try:
            start_time = datetime.utcnow()
            
            async with get_async_session() as session:
                # 测试基本连接
                await session.execute(text("SELECT 1"))
                
                # 检查连接池状态
                pool = engine.pool
                pool_status = {
                    'size': pool.size(),
                    'checked_in': pool.checkedin(),
                    'checked_out': pool.checkedout(),
                    'overflow': pool.overflow(),
                    'invalid': pool.invalid()
                }
                
                # 测试查询性能
                query_start = datetime.utcnow()
                await session.execute(
                    select(SystemMetrics)
                    .order_by(SystemMetrics.timestamp.desc())
                    .limit(1)
                )
                query_time = (datetime.utcnow() - query_start).total_seconds() * 1000
                
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # 判断状态
            status = 'healthy'
            issues = []
            
            if response_time > 1000:  # 超过1秒
                status = 'warning'
                issues.append(f"数据库响应时间过长: {response_time:.2f}ms")
            
            if query_time > 500:  # 查询超过500ms
                status = 'warning'
                issues.append(f"查询时间过长: {query_time:.2f}ms")
            
            if pool_status['checked_out'] / pool_status['size'] > 0.8:  # 连接池使用率超过80%
                status = 'warning'
                issues.append("数据库连接池使用率过高")
            
            return {
                'status': status,
                'response_time_ms': response_time,
                'query_time_ms': query_time,
                'pool_status': pool_status,
                'issues': issues,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f"数据库连接失败: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        try:
            # 获取系统指标
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 判断状态
            status = 'healthy'
            issues = []
            
            if cpu_percent > 80:
                status = 'warning' if cpu_percent < 90 else 'critical'
                issues.append(f"CPU使用率过高: {cpu_percent}%")
            
            if memory.percent > 85:
                status = 'warning' if memory.percent < 95 else 'critical'
                issues.append(f"内存使用率过高: {memory.percent}%")
            
            if disk.percent > 90:
                status = 'warning' if disk.percent < 95 else 'critical'
                issues.append(f"磁盘使用率过高: {disk.percent}%")
            
            return {
                'status': status,
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'available_memory_gb': memory.available / (1024**3),
                'available_disk_gb': disk.free / (1024**3),
                'issues': issues,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f"系统检查失败: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_application_health(self) -> Dict[str, Any]:
        """检查应用健康状态"""
        try:
            async with get_async_session() as session:
                # 获取最近的应用指标
                result = await session.execute(
                    select(ApplicationMetrics)
                    .order_by(ApplicationMetrics.timestamp.desc())
                    .limit(1)
                )
                latest_metrics = result.scalar_one_or_none()
                
                if not latest_metrics:
                    return {
                        'status': 'warning',
                        'message': '没有应用指标数据',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                
                # 检查指标是否过期
                metrics_age = datetime.utcnow() - latest_metrics.timestamp
                if metrics_age > timedelta(minutes=10):
                    return {
                        'status': 'warning',
                        'message': f'应用指标数据过期: {metrics_age}',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                
                # 分析指标
                status = 'healthy'
                issues = []
                
                # 检查API错误率
                if latest_metrics.api_requests_total > 0:
                    error_rate = latest_metrics.api_requests_error / latest_metrics.api_requests_total
                    if error_rate > 0.1:  # 错误率超过10%
                        status = 'warning' if error_rate < 0.2 else 'critical'
                        issues.append(f"API错误率过高: {error_rate:.2%}")
                
                # 检查响应时间
                if latest_metrics.api_response_time_avg > 1000:  # 超过1秒
                    status = 'warning'
                    issues.append(f"API响应时间过长: {latest_metrics.api_response_time_avg:.2f}ms")
                
                # 检查数据库查询
                if latest_metrics.db_queries_total > 0:
                    slow_query_rate = latest_metrics.db_queries_slow / latest_metrics.db_queries_total
                    if slow_query_rate > 0.1:  # 慢查询率超过10%
                        status = 'warning'
                        issues.append(f"慢查询率过高: {slow_query_rate:.2%}")
                
                return {
                    'status': status,
                    'api_requests_total': latest_metrics.api_requests_total,
                    'api_error_rate': latest_metrics.api_requests_error / max(latest_metrics.api_requests_total, 1),
                    'api_response_time_avg': latest_metrics.api_response_time_avg,
                    'websocket_connections': latest_metrics.websocket_connections,
                    'db_queries_total': latest_metrics.db_queries_total,
                    'issues': issues,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'critical',
                'message': f"应用检查失败: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_external_apis_health(self) -> Dict[str, Any]:
        """检查外部API健康状态"""
        try:
            # 定义要检查的外部API
            apis_to_check = [
                {
                    'name': 'OKX API',
                    'url': 'https://www.okx.com/api/v5/public/time',
                    'timeout': 10
                },
                {
                    'name': 'Whale Alert API',
                    'url': 'https://api.whale-alert.io/v1/status',
                    'timeout': 10
                }
            ]
            
            results = {}
            overall_status = 'healthy'
            
            async with aiohttp.ClientSession() as session:
                for api in apis_to_check:
                    try:
                        start_time = datetime.utcnow()
                        async with session.get(
                            api['url'],
                            timeout=aiohttp.ClientTimeout(total=api['timeout'])
                        ) as response:
                            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                            
                            if response.status == 200:
                                status = 'healthy'
                                if response_time > 5000:  # 超过5秒
                                    status = 'warning'
                            else:
                                status = 'warning'
                                overall_status = 'warning'
                            
                            results[api['name']] = {
                                'status': status,
                                'response_time_ms': response_time,
                                'http_status': response.status
                            }
                            
                    except asyncio.TimeoutError:
                        results[api['name']] = {
                            'status': 'critical',
                            'message': '请求超时'
                        }
                        overall_status = 'critical'
                        
                    except Exception as e:
                        results[api['name']] = {
                            'status': 'critical',
                            'message': str(e)
                        }
                        overall_status = 'critical'
            
            return {
                'status': overall_status,
                'apis': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f"外部API检查失败: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_data_sources_health(self) -> Dict[str, Any]:
        """检查数据源健康状态"""
        try:
            # 这里应该检查各个数据源的状态
            # 由于数据源服务可能还没有完全实现，我们先返回基本状态
            
            return {
                'status': 'healthy',
                'message': '数据源检查功能待实现',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f"数据源检查失败: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """获取健康状态摘要"""
        try:
            health = await self.check_overall_health()
            
            return {
                'status': health['status'],
                'timestamp': health['timestamp'],
                'summary': health['summary'],
                'critical_issues': [
                    f"{name}: {check.get('message', 'Unknown issue')}"
                    for name, check in health['checks'].items()
                    if check.get('status') == 'critical'
                ]
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f"健康检查失败: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }
