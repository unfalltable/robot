"""
数据源基础类
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class DataType(Enum):
    """数据类型枚举"""
    MARKET_DATA = "market_data"      # 市场行情数据
    NEWS = "news"                    # 新闻资讯
    WHALE_ALERT = "whale_alert"      # 大户交易提醒
    SOCIAL_SENTIMENT = "social_sentiment"  # 社交媒体情绪
    ON_CHAIN_DATA = "on_chain_data"  # 链上数据
    ECONOMIC_DATA = "economic_data"  # 经济数据


@dataclass
class DataPoint:
    """数据点"""
    source: str                      # 数据源名称
    data_type: DataType             # 数据类型
    symbol: Optional[str]           # 交易对（如果适用）
    timestamp: datetime             # 时间戳
    data: Dict[str, Any]           # 数据内容
    metadata: Optional[Dict[str, Any]] = None  # 元数据


@dataclass
class MarketData:
    """市场数据"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str = "1m"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'timeframe': self.timeframe
        }


@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    content: str
    source: str
    url: Optional[str]
    timestamp: datetime
    sentiment: Optional[float] = None  # 情绪分数 -1到1
    relevance: Optional[float] = None  # 相关性分数 0到1
    keywords: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'sentiment': self.sentiment,
            'relevance': self.relevance,
            'keywords': self.keywords or []
        }


@dataclass
class WhaleTransaction:
    """大户交易"""
    transaction_hash: str
    from_address: str
    to_address: str
    amount: float
    currency: str
    timestamp: datetime
    exchange_from: Optional[str] = None
    exchange_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'transaction_hash': self.transaction_hash,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'amount': self.amount,
            'currency': self.currency,
            'timestamp': self.timestamp.isoformat(),
            'exchange_from': self.exchange_from,
            'exchange_to': self.exchange_to
        }


class BaseDataSource(ABC):
    """数据源基础类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_running = False
        self.subscribers: List[callable] = []
        self.logger = logging.getLogger(f"data_source.{name}")
    
    @abstractmethod
    async def connect(self) -> bool:
        """连接到数据源"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """断开数据源连接"""
        pass
    
    @abstractmethod
    async def start_streaming(self) -> None:
        """开始数据流"""
        pass
    
    @abstractmethod
    async def stop_streaming(self) -> None:
        """停止数据流"""
        pass
    
    @abstractmethod
    async def get_historical_data(
        self, 
        symbol: str, 
        start_time: datetime, 
        end_time: datetime,
        **kwargs
    ) -> List[DataPoint]:
        """获取历史数据"""
        pass
    
    @abstractmethod
    def get_supported_symbols(self) -> List[str]:
        """获取支持的交易对"""
        pass
    
    @abstractmethod
    def get_data_types(self) -> List[DataType]:
        """获取支持的数据类型"""
        pass
    
    def subscribe(self, callback: callable) -> None:
        """订阅数据更新"""
        if callback not in self.subscribers:
            self.subscribers.append(callback)
            self.logger.info(f"新增订阅者: {callback.__name__}")
    
    def unsubscribe(self, callback: callable) -> None:
        """取消订阅"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            self.logger.info(f"移除订阅者: {callback.__name__}")
    
    async def notify_subscribers(self, data_point: DataPoint) -> None:
        """通知所有订阅者"""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data_point)
                else:
                    callback(data_point)
            except Exception as e:
                self.logger.error(f"通知订阅者失败 {callback.__name__}: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            'name': self.name,
            'is_running': self.is_running,
            'subscribers_count': len(self.subscribers),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """更新配置"""
        self.config.update(new_config)
        self.logger.info(f"配置已更新: {new_config}")


class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self):
        self.data_sources: Dict[str, BaseDataSource] = {}
        self.logger = logging.getLogger("data_source_manager")
    
    def register_data_source(self, data_source: BaseDataSource) -> None:
        """注册数据源"""
        self.data_sources[data_source.name] = data_source
        self.logger.info(f"注册数据源: {data_source.name}")
    
    def unregister_data_source(self, name: str) -> None:
        """注销数据源"""
        if name in self.data_sources:
            del self.data_sources[name]
            self.logger.info(f"注销数据源: {name}")
    
    async def start_all(self) -> None:
        """启动所有数据源"""
        for name, source in self.data_sources.items():
            try:
                await source.connect()
                await source.start_streaming()
                self.logger.info(f"启动数据源成功: {name}")
            except Exception as e:
                self.logger.error(f"启动数据源失败 {name}: {str(e)}")
    
    async def stop_all(self) -> None:
        """停止所有数据源"""
        for name, source in self.data_sources.items():
            try:
                await source.stop_streaming()
                await source.disconnect()
                self.logger.info(f"停止数据源成功: {name}")
            except Exception as e:
                self.logger.error(f"停止数据源失败 {name}: {str(e)}")
    
    def get_data_source(self, name: str) -> Optional[BaseDataSource]:
        """获取数据源"""
        return self.data_sources.get(name)
    
    def list_data_sources(self) -> List[str]:
        """列出所有数据源"""
        return list(self.data_sources.keys())
    
    async def health_check_all(self) -> Dict[str, Any]:
        """检查所有数据源健康状态"""
        results = {}
        for name, source in self.data_sources.items():
            try:
                results[name] = await source.health_check()
            except Exception as e:
                results[name] = {
                    'name': name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        return results
