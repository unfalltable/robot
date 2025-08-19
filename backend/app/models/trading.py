"""
交易相关数据模型
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional

from app.core.database import Base


class OrderStatus(enum.Enum):
    """订单状态"""
    PENDING = "pending"          # 待处理
    SUBMITTED = "submitted"      # 已提交
    PARTIAL_FILLED = "partial_filled"  # 部分成交
    FILLED = "filled"           # 完全成交
    CANCELLED = "cancelled"     # 已取消
    REJECTED = "rejected"       # 已拒绝
    EXPIRED = "expired"         # 已过期


class OrderType(enum.Enum):
    """订单类型"""
    MARKET = "market"           # 市价单
    LIMIT = "limit"             # 限价单
    STOP = "stop"               # 止损单
    STOP_LIMIT = "stop_limit"   # 止损限价单
    TAKE_PROFIT = "take_profit" # 止盈单
    TAKE_PROFIT_LIMIT = "take_profit_limit"  # 止盈限价单


class OrderSide(enum.Enum):
    """订单方向"""
    BUY = "buy"                 # 买入
    SELL = "sell"               # 卖出


class PositionSide(enum.Enum):
    """持仓方向"""
    LONG = "long"               # 多头
    SHORT = "short"             # 空头
    NET = "net"                 # 净持仓


class Account(Base):
    """账户模型"""
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    exchange = Column(String(50), nullable=False)
    api_key = Column(String(255))
    secret_key = Column(String(255))
    passphrase = Column(String(255))
    sandbox = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    orders = relationship("Order", back_populates="account")
    positions = relationship("Position", back_populates="account")
    balances = relationship("Balance", back_populates="account")


class Balance(Base):
    """账户余额模型"""
    __tablename__ = "balances"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    currency = Column(String(20), nullable=False)
    available = Column(Float, default=0.0)
    frozen = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    account = relationship("Account", back_populates="balances")


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    strategy_id = Column(String, ForeignKey("strategies.id"))
    exchange_order_id = Column(String(100))
    
    # 交易信息
    symbol = Column(String(50), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    type = Column(Enum(OrderType), nullable=False)
    amount = Column(Float, nullable=False)
    price = Column(Float)
    stop_price = Column(Float)
    
    # 状态信息
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    filled_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float)
    average_price = Column(Float)
    
    # 费用信息
    fee = Column(Float, default=0.0)
    fee_currency = Column(String(20))
    
    # 时间信息
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    filled_at = Column(DateTime)
    
    # 备注信息
    notes = Column(Text)
    
    # 关联关系
    account = relationship("Account", back_populates="orders")
    strategy = relationship("Strategy", back_populates="orders")
    trades = relationship("Trade", back_populates="order")


class Position(Base):
    """持仓模型"""
    __tablename__ = "positions"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    strategy_id = Column(String, ForeignKey("strategies.id"))
    
    # 持仓信息
    symbol = Column(String(50), nullable=False)
    side = Column(Enum(PositionSide), nullable=False)
    size = Column(Float, default=0.0)
    entry_price = Column(Float)
    mark_price = Column(Float)
    
    # 盈亏信息
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    
    # 保证金信息
    initial_margin = Column(Float, default=0.0)
    maintenance_margin = Column(Float, default=0.0)
    margin_ratio = Column(Float, default=0.0)
    
    # 时间信息
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    account = relationship("Account", back_populates="positions")
    strategy = relationship("Strategy", back_populates="positions")


class Trade(Base):
    """交易记录模型"""
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    exchange_trade_id = Column(String(100))
    
    # 交易信息
    symbol = Column(String(50), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # 费用信息
    fee = Column(Float, default=0.0)
    fee_currency = Column(String(20))
    
    # 时间信息
    timestamp = Column(DateTime, default=func.now())
    
    # 关联关系
    order = relationship("Order", back_populates="trades")


class Strategy(Base):
    """策略模型"""
    __tablename__ = "strategies"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    
    # 策略配置
    config = Column(Text)  # JSON格式的配置
    is_active = Column(Boolean, default=False)
    
    # 统计信息
    total_trades = Column(Integer, default=0)
    win_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    
    # 时间信息
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关联关系
    orders = relationship("Order", back_populates="strategy")
    positions = relationship("Position", back_populates="strategy")
