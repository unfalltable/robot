"""
交易所基础接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExchangeCredentials:
    """交易所凭证"""
    api_key: str
    secret_key: str
    passphrase: Optional[str] = None
    sandbox: bool = True


@dataclass
class OrderRequest:
    """订单请求"""
    symbol: str
    side: str  # 'buy' or 'sell'
    type: str  # 'market', 'limit', etc.
    amount: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    params: Optional[Dict[str, Any]] = None


@dataclass
class OrderResponse:
    """订单响应"""
    id: str
    symbol: str
    side: str
    type: str
    amount: float
    price: Optional[float]
    status: str
    filled: float
    remaining: float
    timestamp: datetime
    info: Dict[str, Any]


@dataclass
class Balance:
    """余额信息"""
    currency: str
    free: float
    used: float
    total: float


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    side: str
    size: float
    entry_price: float
    mark_price: float
    unrealized_pnl: float
    percentage: float


@dataclass
class Ticker:
    """行情信息"""
    symbol: str
    last: float
    bid: float
    ask: float
    high: float
    low: float
    volume: float
    change: float
    percentage: float
    timestamp: datetime


class BaseExchange(ABC):
    """交易所基础类"""
    
    def __init__(self, credentials: ExchangeCredentials):
        self.credentials = credentials
        self.name = self.__class__.__name__.lower().replace('exchange', '')
    
    @abstractmethod
    async def connect(self) -> bool:
        """连接到交易所"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """断开连接"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        pass
    
    @abstractmethod
    async def get_balances(self) -> List[Balance]:
        """获取余额"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """获取持仓"""
        pass
    
    @abstractmethod
    async def create_order(self, order: OrderRequest) -> OrderResponse:
        """创建订单"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """取消订单"""
        pass
    
    @abstractmethod
    async def get_order(self, order_id: str, symbol: str) -> Optional[OrderResponse]:
        """获取订单信息"""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderResponse]:
        """获取未完成订单"""
        pass
    
    @abstractmethod
    async def get_order_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[OrderResponse]:
        """获取订单历史"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Ticker:
        """获取行情"""
        pass
    
    @abstractmethod
    async def get_tickers(self) -> List[Ticker]:
        """获取所有行情"""
        pass
    
    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """获取订单簿"""
        pass
    
    @abstractmethod
    async def get_klines(self, symbol: str, timeframe: str, limit: int = 100) -> List[List[float]]:
        """获取K线数据"""
        pass
    
    @abstractmethod
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近交易"""
        pass
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            await self.get_account_info()
            return True
        except Exception:
            return False
