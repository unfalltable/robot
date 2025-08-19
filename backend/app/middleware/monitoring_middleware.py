"""
监控中间件
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.services.monitoring_service import ApplicationMonitor


class MonitoringMiddleware(BaseHTTPMiddleware):
    """监控中间件 - 自动收集API请求指标"""
    
    def __init__(self, app: ASGIApp, app_monitor: ApplicationMonitor):
        super().__init__(app)
        self.app_monitor = app_monitor
        self.logger = logging.getLogger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并收集指标"""
        start_time = time.time()
        
        # 记录请求开始
        method = request.method
        path = request.url.path
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 判断请求是否成功
            success = 200 <= response.status_code < 400
            
            # 记录API请求指标
            self.app_monitor.record_api_request(success, response_time)
            
            # 记录详细日志（仅在调试模式下）
            if response_time > 1000:  # 响应时间超过1秒时记录警告
                self.logger.warning(
                    f"慢请求: {method} {path} - {response_time:.2f}ms - {response.status_code}"
                )
            elif not success:
                self.logger.warning(
                    f"请求失败: {method} {path} - {response_time:.2f}ms - {response.status_code}"
                )
            else:
                self.logger.debug(
                    f"请求完成: {method} {path} - {response_time:.2f}ms - {response.status_code}"
                )
            
            return response
            
        except Exception as e:
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000
            
            # 记录失败的请求
            self.app_monitor.record_api_request(False, response_time)
            
            # 记录错误日志
            self.logger.error(
                f"请求异常: {method} {path} - {response_time:.2f}ms - {str(e)}"
            )
            
            # 重新抛出异常
            raise


class DatabaseMonitoringMiddleware:
    """数据库监控中间件"""
    
    def __init__(self, app_monitor: ApplicationMonitor):
        self.app_monitor = app_monitor
        self.logger = logging.getLogger(__name__)
        self.slow_query_threshold = 500  # 慢查询阈值(毫秒)
    
    def before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """查询执行前的钩子"""
        context._query_start_time = time.time()
    
    def after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """查询执行后的钩子"""
        if hasattr(context, '_query_start_time'):
            query_time = (time.time() - context._query_start_time) * 1000  # 转换为毫秒
            is_slow = query_time > self.slow_query_threshold
            
            # 记录数据库查询指标
            self.app_monitor.record_database_query(query_time, is_slow)
            
            # 记录慢查询日志
            if is_slow:
                self.logger.warning(
                    f"慢查询: {query_time:.2f}ms - {statement[:100]}..."
                )


class WebSocketMonitoringMixin:
    """WebSocket监控混入类"""
    
    def __init__(self, app_monitor: ApplicationMonitor):
        self.app_monitor = app_monitor
        self.logger = logging.getLogger(__name__)
    
    def on_connect(self, websocket):
        """WebSocket连接时调用"""
        self.app_monitor.record_websocket_event('connections')
        self.logger.debug(f"WebSocket连接: {websocket.client}")
    
    def on_disconnect(self, websocket):
        """WebSocket断开时调用"""
        # 这里应该减少连接数，但由于我们的指标是累加的，暂时不处理
        self.logger.debug(f"WebSocket断开: {websocket.client}")
    
    def on_message_sent(self, websocket, message):
        """发送消息时调用"""
        self.app_monitor.record_websocket_event('messages_sent')
        self.logger.debug(f"WebSocket发送消息: {len(str(message))} bytes")
    
    def on_message_received(self, websocket, message):
        """接收消息时调用"""
        self.app_monitor.record_websocket_event('messages_received')
        self.logger.debug(f"WebSocket接收消息: {len(str(message))} bytes")
    
    def on_error(self, websocket, error):
        """WebSocket错误时调用"""
        self.app_monitor.record_websocket_event('errors')
        self.logger.error(f"WebSocket错误: {websocket.client} - {str(error)}")


class PerformanceLogger:
    """性能日志记录器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.performance")
    
    def log_function_performance(self, func_name: str, duration_ms: float, **kwargs):
        """记录函数性能"""
        if duration_ms > 1000:  # 超过1秒的函数调用
            self.logger.warning(
                f"慢函数: {func_name} - {duration_ms:.2f}ms - {kwargs}"
            )
        else:
            self.logger.debug(
                f"函数执行: {func_name} - {duration_ms:.2f}ms - {kwargs}"
            )
    
    def log_external_api_call(self, api_name: str, duration_ms: float, success: bool, **kwargs):
        """记录外部API调用"""
        status = "成功" if success else "失败"
        if duration_ms > 5000 or not success:  # 超过5秒或失败的API调用
            self.logger.warning(
                f"外部API: {api_name} - {duration_ms:.2f}ms - {status} - {kwargs}"
            )
        else:
            self.logger.debug(
                f"外部API: {api_name} - {duration_ms:.2f}ms - {status} - {kwargs}"
            )


def performance_monitor(func_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # 记录性能日志
                perf_logger = PerformanceLogger()
                perf_logger.log_function_performance(name, duration_ms)
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # 记录错误和性能
                perf_logger = PerformanceLogger()
                perf_logger.log_function_performance(
                    name, duration_ms, error=str(e)
                )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # 记录性能日志
                perf_logger = PerformanceLogger()
                perf_logger.log_function_performance(name, duration_ms)
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # 记录错误和性能
                perf_logger = PerformanceLogger()
                perf_logger.log_function_performance(
                    name, duration_ms, error=str(e)
                )
                
                raise
        
        # 根据函数类型返回相应的包装器
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # 检查是否是协程函数
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ErrorTracker:
    """错误跟踪器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.errors")
        self.error_counts = {}
    
    def track_error(self, error: Exception, context: dict = None):
        """跟踪错误"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # 更新错误计数
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # 记录错误日志
        self.logger.error(
            f"错误跟踪: {error_type} - {error_message} - 计数: {self.error_counts[error_type]} - 上下文: {context}"
        )
    
    def get_error_summary(self) -> dict:
        """获取错误摘要"""
        return {
            'error_counts': self.error_counts.copy(),
            'total_errors': sum(self.error_counts.values()),
            'unique_errors': len(self.error_counts)
        }
    
    def reset_counts(self):
        """重置错误计数"""
        self.error_counts.clear()


# 全局实例
performance_logger = PerformanceLogger()
error_tracker = ErrorTracker()
