"""
系统监控和日志数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, BigInteger, Text, Boolean, Index, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class SystemMetrics(Base):
    """系统指标模型"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # CPU指标
    cpu_usage = Column(Float)  # CPU使用率 %
    cpu_load_1m = Column(Float)  # 1分钟负载
    cpu_load_5m = Column(Float)  # 5分钟负载
    cpu_load_15m = Column(Float)  # 15分钟负载
    
    # 内存指标
    memory_usage = Column(Float)  # 内存使用率 %
    memory_used = Column(BigInteger)  # 已用内存 bytes
    memory_available = Column(BigInteger)  # 可用内存 bytes
    memory_total = Column(BigInteger)  # 总内存 bytes
    
    # 磁盘指标
    disk_usage = Column(Float)  # 磁盘使用率 %
    disk_used = Column(BigInteger)  # 已用磁盘 bytes
    disk_available = Column(BigInteger)  # 可用磁盘 bytes
    disk_total = Column(BigInteger)  # 总磁盘 bytes
    disk_io_read = Column(BigInteger)  # 磁盘读取 bytes/s
    disk_io_write = Column(BigInteger)  # 磁盘写入 bytes/s
    
    # 网络指标
    network_in = Column(BigInteger)  # 网络入流量 bytes/s
    network_out = Column(BigInteger)  # 网络出流量 bytes/s
    network_connections = Column(Integer)  # 网络连接数
    
    # 进程指标
    process_count = Column(Integer)  # 进程数
    thread_count = Column(Integer)  # 线程数
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())


class ApplicationMetrics(Base):
    """应用指标模型"""
    __tablename__ = "application_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # API指标
    api_requests_total = Column(Integer, default=0)
    api_requests_success = Column(Integer, default=0)
    api_requests_error = Column(Integer, default=0)
    api_response_time_avg = Column(Float)  # 平均响应时间 ms
    api_response_time_p95 = Column(Float)  # 95%响应时间 ms
    api_response_time_p99 = Column(Float)  # 99%响应时间 ms
    
    # WebSocket指标
    websocket_connections = Column(Integer, default=0)
    websocket_messages_sent = Column(Integer, default=0)
    websocket_messages_received = Column(Integer, default=0)
    websocket_errors = Column(Integer, default=0)
    
    # 数据库指标
    db_connections_active = Column(Integer, default=0)
    db_connections_idle = Column(Integer, default=0)
    db_queries_total = Column(Integer, default=0)
    db_queries_slow = Column(Integer, default=0)
    db_query_time_avg = Column(Float)  # 平均查询时间 ms
    
    # Redis指标
    redis_connections = Column(Integer, default=0)
    redis_memory_usage = Column(BigInteger)  # Redis内存使用 bytes
    redis_operations_total = Column(Integer, default=0)
    redis_operations_error = Column(Integer, default=0)
    
    # 任务队列指标
    celery_tasks_pending = Column(Integer, default=0)
    celery_tasks_active = Column(Integer, default=0)
    celery_tasks_completed = Column(Integer, default=0)
    celery_tasks_failed = Column(Integer, default=0)
    celery_workers_active = Column(Integer, default=0)
    
    # 交易指标
    orders_total = Column(Integer, default=0)
    orders_filled = Column(Integer, default=0)
    orders_cancelled = Column(Integer, default=0)
    orders_error = Column(Integer, default=0)
    
    # 策略指标
    strategies_active = Column(Integer, default=0)
    strategies_running = Column(Integer, default=0)
    strategies_error = Column(Integer, default=0)
    
    # 数据源指标
    data_sources_active = Column(Integer, default=0)
    data_sources_error = Column(Integer, default=0)
    data_points_received = Column(Integer, default=0)
    data_latency_avg = Column(Float)  # 平均数据延迟 ms
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())


class ErrorLog(Base):
    """错误日志模型"""
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 错误基本信息
    level = Column(String(20), nullable=False, index=True)  # ERROR, WARNING, CRITICAL
    module = Column(String(100), nullable=False, index=True)
    function = Column(String(100))
    line_number = Column(Integer)
    
    # 错误内容
    message = Column(Text, nullable=False)
    exception_type = Column(String(100))
    exception_message = Column(Text)
    traceback = Column(Text)
    
    # 上下文信息
    request_id = Column(String(100), index=True)
    user_id = Column(String(100))
    session_id = Column(String(100))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # 业务上下文
    strategy_id = Column(String(100))
    order_id = Column(String(100))
    symbol = Column(String(50))
    exchange = Column(String(50))
    
    # 环境信息
    environment = Column(String(20))  # development, staging, production
    version = Column(String(50))
    hostname = Column(String(100))
    
    # 处理状态
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    resolution_notes = Column(Text)
    
    # 统计信息
    occurrence_count = Column(Integer, default=1)
    first_occurrence = Column(DateTime)
    last_occurrence = Column(DateTime)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_level_timestamp', 'level', 'timestamp'),
        Index('idx_module_timestamp', 'module', 'timestamp'),
    )


class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 操作信息
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(100), index=True)
    
    # 用户信息
    user_id = Column(String(100), index=True)
    username = Column(String(100))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # 操作详情
    old_values = Column(JSON)  # 操作前的值
    new_values = Column(JSON)  # 操作后的值
    changes = Column(JSON)     # 变更内容
    
    # 请求信息
    request_id = Column(String(100))
    session_id = Column(String(100))
    method = Column(String(10))  # GET, POST, PUT, DELETE
    endpoint = Column(String(200))
    
    # 结果信息
    status = Column(String(20))  # success, failure, partial
    error_message = Column(Text)
    
    # 业务上下文
    strategy_id = Column(String(100))
    account_id = Column(String(100))
    order_id = Column(String(100))
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_action_timestamp', 'action', 'timestamp'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_resource_timestamp', 'resource_type', 'resource_id', 'timestamp'),
    )


class PerformanceLog(Base):
    """性能日志模型"""
    __tablename__ = "performance_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 操作信息
    operation = Column(String(100), nullable=False, index=True)
    module = Column(String(100), nullable=False, index=True)
    function = Column(String(100))
    
    # 性能指标
    duration_ms = Column(Float, nullable=False)  # 执行时间 ms
    memory_usage = Column(BigInteger)  # 内存使用 bytes
    cpu_usage = Column(Float)  # CPU使用率 %
    
    # 请求信息
    request_id = Column(String(100), index=True)
    request_size = Column(Integer)  # 请求大小 bytes
    response_size = Column(Integer)  # 响应大小 bytes
    
    # 数据库性能
    db_queries = Column(Integer, default=0)
    db_query_time = Column(Float, default=0.0)
    
    # 外部API性能
    external_api_calls = Column(Integer, default=0)
    external_api_time = Column(Float, default=0.0)
    
    # 缓存性能
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)
    cache_time = Column(Float, default=0.0)
    
    # 业务上下文
    symbol = Column(String(50))
    strategy_id = Column(String(100))
    data_points = Column(Integer)  # 处理的数据点数量
    
    # 状态信息
    status = Column(String(20))  # success, error, timeout
    error_message = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_operation_timestamp', 'operation', 'timestamp'),
        Index('idx_duration_timestamp', 'duration_ms', 'timestamp'),
    )


class AlertRule(Base):
    """告警规则模型"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 规则基本信息
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False, index=True)  # system, application, business
    
    # 规则条件
    metric_name = Column(String(100), nullable=False)
    operator = Column(String(20), nullable=False)  # >, <, >=, <=, ==, !=
    threshold = Column(Float, nullable=False)
    duration_minutes = Column(Integer, default=5)  # 持续时间
    
    # 告警设置
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    is_active = Column(Boolean, default=True)
    
    # 通知设置
    notification_channels = Column(JSON)  # 通知渠道
    notification_template = Column(Text)
    cooldown_minutes = Column(Integer, default=60)  # 冷却时间
    
    # 统计信息
    trigger_count = Column(Integer, default=0)
    last_triggered = Column(DateTime)
    last_resolved = Column(DateTime)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Alert(Base):
    """告警记录模型"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, nullable=False, index=True)
    
    # 告警信息
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    
    # 触发信息
    metric_name = Column(String(100))
    metric_value = Column(Float)
    threshold = Column(Float)
    
    # 状态信息
    status = Column(String(20), default='active', index=True)  # active, resolved, suppressed
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    resolution_notes = Column(Text)
    
    # 通知状态
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSON)
    notification_error = Column(Text)
    
    # 业务上下文
    strategy_id = Column(String(100))
    symbol = Column(String(50))
    exchange = Column(String(50))
    
    # 时间戳
    triggered_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_severity_status', 'severity', 'status'),
        Index('idx_triggered_status', 'triggered_at', 'status'),
    )
