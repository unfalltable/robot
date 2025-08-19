"""
市场数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean, Index
from sqlalchemy.sql import func
from app.core.database import Base


class MarketData(Base):
    """市场数据模型"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # OHLCV数据
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # 额外指标
    quote_volume = Column(Float)  # 计价货币成交量
    trades_count = Column(Integer)  # 交易笔数
    
    # 技术指标（可选）
    sma_20 = Column(Float)  # 20日简单移动平均
    ema_20 = Column(Float)  # 20日指数移动平均
    rsi_14 = Column(Float)  # 14日RSI
    macd = Column(Float)    # MACD
    macd_signal = Column(Float)  # MACD信号线
    macd_histogram = Column(Float)  # MACD柱状图
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
        Index('idx_timestamp_symbol', 'timestamp', 'symbol'),
    )


class TickerData(Base):
    """实时行情数据模型"""
    __tablename__ = "ticker_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 价格数据
    last_price = Column(Float, nullable=False)
    bid_price = Column(Float)
    ask_price = Column(Float)
    bid_size = Column(Float)
    ask_size = Column(Float)
    
    # 24小时统计
    high_24h = Column(Float)
    low_24h = Column(Float)
    volume_24h = Column(Float)
    quote_volume_24h = Column(Float)
    change_24h = Column(Float)
    change_percent_24h = Column(Float)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )


class OrderBookData(Base):
    """订单簿数据模型"""
    __tablename__ = "orderbook_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 订单簿数据（JSON格式存储）
    bids = Column(Text, nullable=False)  # JSON: [[price, amount], ...]
    asks = Column(Text, nullable=False)  # JSON: [[price, amount], ...]
    
    # 统计数据
    bid_count = Column(Integer)
    ask_count = Column(Integer)
    spread = Column(Float)  # 买卖价差
    spread_percent = Column(Float)  # 价差百分比
    
    # 深度统计
    bid_depth_1 = Column(Float)  # 1%深度买单量
    ask_depth_1 = Column(Float)  # 1%深度卖单量
    bid_depth_5 = Column(Float)  # 5%深度买单量
    ask_depth_5 = Column(Float)  # 5%深度卖单量
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )


class TradingPair(Base):
    """交易对配置模型"""
    __tablename__ = "trading_pairs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, unique=True, index=True)
    base_currency = Column(String(20), nullable=False)
    quote_currency = Column(String(20), nullable=False)
    
    # 交易配置
    is_active = Column(Boolean, default=True)
    min_order_size = Column(Float)
    max_order_size = Column(Float)
    price_precision = Column(Integer, default=8)
    amount_precision = Column(Integer, default=8)
    
    # 费率配置
    maker_fee = Column(Float, default=0.001)
    taker_fee = Column(Float, default=0.001)
    
    # 风险控制
    max_position_size = Column(Float)
    daily_volume_limit = Column(Float)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MarketIndicator(Base):
    """市场指标模型"""
    __tablename__ = "market_indicators"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 趋势指标
    sma_5 = Column(Float)
    sma_10 = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    
    ema_5 = Column(Float)
    ema_10 = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    ema_200 = Column(Float)
    
    # 动量指标
    rsi_14 = Column(Float)
    rsi_21 = Column(Float)
    stoch_k = Column(Float)
    stoch_d = Column(Float)
    
    # MACD指标
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    
    # 布林带
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    bb_width = Column(Float)
    bb_percent = Column(Float)
    
    # 成交量指标
    volume_sma_20 = Column(Float)
    volume_ratio = Column(Float)
    obv = Column(Float)  # On-Balance Volume
    
    # 波动率指标
    atr_14 = Column(Float)  # Average True Range
    volatility_20 = Column(Float)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )


class MarketSentiment(Base):
    """市场情绪模型"""
    __tablename__ = "market_sentiment"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 情绪指标
    fear_greed_index = Column(Float)  # 恐惧贪婪指数 0-100
    social_sentiment = Column(Float)  # 社交媒体情绪 -1到1
    news_sentiment = Column(Float)    # 新闻情绪 -1到1
    
    # 资金流向
    net_flow_1h = Column(Float)   # 1小时净流入
    net_flow_24h = Column(Float)  # 24小时净流入
    net_flow_7d = Column(Float)   # 7天净流入
    
    # 持仓数据
    long_short_ratio = Column(Float)  # 多空比
    top_trader_long_ratio = Column(Float)  # 大户多头比例
    top_trader_short_ratio = Column(Float)  # 大户空头比例
    
    # 期货数据
    funding_rate = Column(Float)  # 资金费率
    open_interest = Column(Float)  # 未平仓合约
    open_interest_change = Column(Float)  # 未平仓变化
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )


class ExchangeStatus(Base):
    """交易所状态模型"""
    __tablename__ = "exchange_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 状态信息
    is_online = Column(Boolean, default=True)
    api_status = Column(String(20))  # normal, maintenance, error
    websocket_status = Column(String(20))  # connected, disconnected, error
    
    # 性能指标
    api_latency = Column(Float)  # API延迟(ms)
    websocket_latency = Column(Float)  # WebSocket延迟(ms)
    error_rate = Column(Float)  # 错误率
    
    # 限制信息
    rate_limit_remaining = Column(Integer)
    rate_limit_reset = Column(DateTime)
    
    # 维护信息
    maintenance_start = Column(DateTime)
    maintenance_end = Column(DateTime)
    maintenance_reason = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_exchange_timestamp', 'exchange', 'timestamp'),
    )
