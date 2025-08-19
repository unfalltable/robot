"""
大户交易和监控数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean, Index, JSON, BigInteger
from sqlalchemy.sql import func
from app.core.database import Base


class WhaleTransaction(Base):
    """大户交易模型"""
    __tablename__ = "whale_transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 交易基本信息
    transaction_hash = Column(String(100), unique=True, index=True)
    block_number = Column(BigInteger, index=True)
    block_hash = Column(String(100))
    
    # 地址信息
    from_address = Column(String(100), nullable=False, index=True)
    to_address = Column(String(100), nullable=False, index=True)
    
    # 交易金额
    amount = Column(Float, nullable=False)
    currency = Column(String(20), nullable=False, index=True)
    usd_value = Column(Float)  # 美元价值
    
    # 交易所信息
    exchange_from = Column(String(50), index=True)
    exchange_to = Column(String(50), index=True)
    
    # 交易类型
    transaction_type = Column(String(20), index=True)  # transfer, deposit, withdrawal
    direction = Column(String(20))  # inflow, outflow, internal
    
    # 费用信息
    gas_used = Column(BigInteger)
    gas_price = Column(BigInteger)
    transaction_fee = Column(Float)
    
    # 时间信息
    timestamp = Column(DateTime, nullable=False, index=True)
    confirmed_at = Column(DateTime)
    
    # 分析结果
    whale_score = Column(Float)  # 大户评分 0-1
    market_impact = Column(Float)  # 市场影响预测
    significance = Column(String(20))  # low, medium, high, critical
    
    # 标签和分类
    tags = Column(JSON)  # 标签列表
    category = Column(String(50))  # 分类
    
    # 处理状态
    is_processed = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_currency_timestamp', 'currency', 'timestamp'),
        Index('idx_amount_timestamp', 'amount', 'timestamp'),
        Index('idx_exchange_timestamp', 'exchange_from', 'exchange_to', 'timestamp'),
    )


class WhaleAddress(Base):
    """大户地址模型"""
    __tablename__ = "whale_addresses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(100), nullable=False, unique=True, index=True)
    
    # 地址信息
    label = Column(String(200))  # 地址标签
    entity = Column(String(200))  # 实体名称
    entity_type = Column(String(50))  # exchange, whale, institution, fund
    
    # 余额信息
    balances = Column(JSON)  # 各币种余额
    total_usd_value = Column(Float)  # 总美元价值
    
    # 统计信息
    transaction_count = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    
    # 活跃度指标
    daily_volume = Column(Float, default=0.0)
    weekly_volume = Column(Float, default=0.0)
    monthly_volume = Column(Float, default=0.0)
    
    # 行为分析
    behavior_pattern = Column(String(50))  # accumulator, distributor, trader
    risk_level = Column(String(20))  # low, medium, high
    influence_score = Column(Float)  # 影响力分数
    
    # 监控设置
    is_monitored = Column(Boolean, default=False)
    alert_threshold = Column(Float)  # 告警阈值
    
    # 标签和分类
    tags = Column(JSON)
    categories = Column(JSON)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class WhaleAlert(Base):
    """大户告警模型"""
    __tablename__ = "whale_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 告警配置
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 触发条件
    min_amount = Column(Float, nullable=False)  # 最小金额
    currencies = Column(JSON)  # 监控币种
    exchanges = Column(JSON)  # 监控交易所
    addresses = Column(JSON)  # 监控地址
    
    # 过滤条件
    transaction_types = Column(JSON)  # 交易类型
    directions = Column(JSON)  # 交易方向
    exclude_addresses = Column(JSON)  # 排除地址
    
    # 告警设置
    is_active = Column(Boolean, default=True)
    notification_channels = Column(JSON)  # 通知渠道
    cooldown_minutes = Column(Integer, default=5)  # 冷却时间
    
    # 统计信息
    trigger_count = Column(Integer, default=0)
    last_triggered = Column(DateTime)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class WhaleAlertLog(Base):
    """大户告警日志模型"""
    __tablename__ = "whale_alert_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(Integer, nullable=False, index=True)
    transaction_id = Column(Integer, nullable=False, index=True)
    
    # 触发信息
    trigger_reason = Column(Text)
    amount = Column(Float)
    currency = Column(String(20))
    usd_value = Column(Float)
    
    # 通知状态
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSON)
    notification_error = Column(Text)
    
    # 时间戳
    triggered_at = Column(DateTime, default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_alert_triggered', 'alert_id', 'triggered_at'),
    )


class ExchangeFlow(Base):
    """交易所资金流向模型"""
    __tablename__ = "exchange_flows"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange = Column(String(50), nullable=False, index=True)
    currency = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 流向数据
    inflow_1h = Column(Float, default=0.0)    # 1小时流入
    outflow_1h = Column(Float, default=0.0)   # 1小时流出
    netflow_1h = Column(Float, default=0.0)   # 1小时净流入
    
    inflow_24h = Column(Float, default=0.0)   # 24小时流入
    outflow_24h = Column(Float, default=0.0)  # 24小时流出
    netflow_24h = Column(Float, default=0.0)  # 24小时净流入
    
    inflow_7d = Column(Float, default=0.0)    # 7天流入
    outflow_7d = Column(Float, default=0.0)   # 7天流出
    netflow_7d = Column(Float, default=0.0)   # 7天净流入
    
    # 交易统计
    transaction_count_1h = Column(Integer, default=0)
    transaction_count_24h = Column(Integer, default=0)
    transaction_count_7d = Column(Integer, default=0)
    
    # 大户统计
    whale_inflow_1h = Column(Float, default=0.0)
    whale_outflow_1h = Column(Float, default=0.0)
    whale_netflow_1h = Column(Float, default=0.0)
    
    whale_inflow_24h = Column(Float, default=0.0)
    whale_outflow_24h = Column(Float, default=0.0)
    whale_netflow_24h = Column(Float, default=0.0)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_exchange_currency_timestamp', 'exchange', 'currency', 'timestamp'),
    )


class AddressLabel(Base):
    """地址标签模型"""
    __tablename__ = "address_labels"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(100), nullable=False, index=True)
    
    # 标签信息
    label = Column(String(200), nullable=False)
    label_type = Column(String(50), nullable=False)  # exchange, whale, contract, etc.
    confidence = Column(Float, default=1.0)  # 置信度 0-1
    
    # 来源信息
    source = Column(String(100))  # 标签来源
    source_url = Column(String(500))
    verified = Column(Boolean, default=False)
    
    # 详细信息
    description = Column(Text)
    entity_name = Column(String(200))
    entity_type = Column(String(50))
    
    # 统计信息
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_address_label_type', 'address', 'label_type'),
    )


class MonitoringRule(Base):
    """监控规则模型"""
    __tablename__ = "monitoring_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 规则基本信息
    name = Column(String(200), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)  # whale, news, price, volume
    
    # 规则条件
    conditions = Column(JSON, nullable=False)  # 规则条件配置
    
    # 执行设置
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 优先级 1-10
    
    # 通知设置
    notification_channels = Column(JSON)
    notification_template = Column(Text)
    cooldown_seconds = Column(Integer, default=300)
    
    # 统计信息
    trigger_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_triggered = Column(DateTime)
    last_success = Column(DateTime)
    last_error = Column(DateTime)
    last_error_message = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MonitoringLog(Base):
    """监控日志模型"""
    __tablename__ = "monitoring_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(Integer, nullable=False, index=True)
    
    # 执行信息
    execution_id = Column(String(100), index=True)
    status = Column(String(20), nullable=False)  # triggered, success, error, skipped
    
    # 触发数据
    trigger_data = Column(JSON)
    matched_conditions = Column(JSON)
    
    # 执行结果
    action_taken = Column(String(100))
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSON)
    
    # 错误信息
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # 性能信息
    execution_time_ms = Column(Integer)
    
    # 时间戳
    triggered_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    
    # 索引
    __table_args__ = (
        Index('idx_rule_triggered', 'rule_id', 'triggered_at'),
        Index('idx_status_triggered', 'status', 'triggered_at'),
    )
