"""
交易相关数据模式
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.models.trading import OrderStatus, OrderType, OrderSide, PositionSide


class OrderBase(BaseModel):
    """订单基础模式"""
    symbol: str = Field(..., description="交易对")
    side: OrderSide = Field(..., description="订单方向")
    type: OrderType = Field(..., description="订单类型")
    amount: float = Field(..., gt=0, description="订单数量")
    price: Optional[float] = Field(None, gt=0, description="订单价格")
    stop_price: Optional[float] = Field(None, gt=0, description="止损价格")
    notes: Optional[str] = Field(None, description="备注")


class OrderCreate(OrderBase):
    """创建订单模式"""
    account_id: str = Field(..., description="账户ID")
    strategy_id: Optional[str] = Field(None, description="策略ID")
    
    @validator('price')
    def validate_price(cls, v, values):
        if values.get('type') in [OrderType.LIMIT, OrderType.STOP_LIMIT, OrderType.TAKE_PROFIT_LIMIT]:
            if v is None:
                raise ValueError('限价单必须指定价格')
        return v


class OrderUpdate(BaseModel):
    """更新订单模式"""
    amount: Optional[float] = Field(None, gt=0, description="订单数量")
    price: Optional[float] = Field(None, gt=0, description="订单价格")
    stop_price: Optional[float] = Field(None, gt=0, description="止损价格")
    notes: Optional[str] = Field(None, description="备注")


class OrderResponse(OrderBase):
    """订单响应模式"""
    id: str
    account_id: str
    strategy_id: Optional[str]
    exchange_order_id: Optional[str]
    status: OrderStatus
    filled_amount: float
    remaining_amount: Optional[float]
    average_price: Optional[float]
    fee: float
    fee_currency: Optional[str]
    created_at: datetime
    updated_at: datetime
    filled_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    """持仓基础模式"""
    symbol: str = Field(..., description="交易对")
    side: PositionSide = Field(..., description="持仓方向")
    size: float = Field(..., description="持仓数量")


class PositionResponse(PositionBase):
    """持仓响应模式"""
    id: str
    account_id: str
    strategy_id: Optional[str]
    entry_price: Optional[float]
    mark_price: Optional[float]
    unrealized_pnl: float
    realized_pnl: float
    percentage: float
    initial_margin: float
    maintenance_margin: float
    margin_ratio: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    """交易记录响应模式"""
    id: str
    order_id: str
    exchange_trade_id: Optional[str]
    symbol: str
    side: OrderSide
    amount: float
    price: float
    fee: float
    fee_currency: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AccountBase(BaseModel):
    """账户基础模式"""
    name: str = Field(..., description="账户名称")
    exchange: str = Field(..., description="交易所")


class AccountCreate(AccountBase):
    """创建账户模式"""
    api_key: str = Field(..., description="API密钥")
    secret_key: str = Field(..., description="密钥")
    passphrase: Optional[str] = Field(None, description="密码短语")
    sandbox: bool = Field(True, description="是否为测试环境")


class AccountResponse(AccountBase):
    """账户响应模式"""
    id: str
    is_active: bool
    sandbox: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    """余额响应模式"""
    id: str
    account_id: str
    currency: str
    available: float
    frozen: float
    total: float
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StrategyBase(BaseModel):
    """策略基础模式"""
    name: str = Field(..., description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")


class StrategyCreate(StrategyBase):
    """创建策略模式"""
    strategy_type: str = Field(..., description="策略类型")
    parameters: Dict[str, Any] = Field(..., description="策略参数")
    symbols: List[str] = Field(..., description="交易对列表")
    timeframes: List[str] = Field(..., description="时间周期列表")
    account_id: str = Field(..., description="关联账户ID")


class StrategyUpdate(BaseModel):
    """更新策略模式"""
    name: Optional[str] = Field(None, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    parameters: Optional[Dict[str, Any]] = Field(None, description="策略参数")
    symbols: Optional[List[str]] = Field(None, description="交易对列表")
    timeframes: Optional[List[str]] = Field(None, description="时间周期列表")


class StrategyResponse(StrategyBase):
    """策略响应模式"""
    id: str
    strategy_type: str
    parameters: Dict[str, Any]
    symbols: List[str]
    timeframes: List[str]
    account_id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TradingStats(BaseModel):
    """交易统计模式"""
    total_orders: int
    active_orders: int
    filled_orders: int
    cancelled_orders: int
    total_trades: int
    total_volume: float
    total_pnl: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: Optional[float]


class MarketData(BaseModel):
    """市场数据模式"""
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    change_percent_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime


class OrderBook(BaseModel):
    """订单簿模式"""
    symbol: str
    bids: List[List[float]]  # [[price, amount], ...]
    asks: List[List[float]]  # [[price, amount], ...]
    timestamp: datetime


class Kline(BaseModel):
    """K线数据模式"""
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
