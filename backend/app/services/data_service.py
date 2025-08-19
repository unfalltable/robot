"""
数据处理服务
"""
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import json

from app.core.logging import get_logger
from data_sources.base_data_source import DataSourceManager, DataPoint, DataType
from data_sources.market_data_source import OKXMarketDataSource
from data_sources.news_data_source import CryptoNewsSource
from data_sources.whale_monitor import WhaleAlertSource

data_logger = get_logger("data_service")


class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self.processors: Dict[DataType, List[Callable]] = defaultdict(list)
        self.logger = logging.getLogger("data_processor")
    
    def register_processor(self, data_type: DataType, processor: Callable):
        """注册数据处理器"""
        self.processors[data_type].append(processor)
        self.logger.info(f"注册数据处理器: {data_type.value}")
    
    async def process_data(self, data_point: DataPoint) -> Optional[DataPoint]:
        """处理数据点"""
        try:
            processors = self.processors.get(data_point.data_type, [])
            
            processed_data = data_point
            for processor in processors:
                if asyncio.iscoroutinefunction(processor):
                    processed_data = await processor(processed_data)
                else:
                    processed_data = processor(processed_data)
                
                if not processed_data:
                    break
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"数据处理失败: {str(e)}")
            return None


class DataCache:
    """数据缓存"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.market_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.news_data: deque = deque(maxlen=500)
        self.whale_data: deque = deque(maxlen=200)
        self.logger = logging.getLogger("data_cache")
    
    def add_market_data(self, symbol: str, data_point: DataPoint):
        """添加市场数据"""
        self.market_data[symbol].append(data_point)
    
    def add_news_data(self, data_point: DataPoint):
        """添加新闻数据"""
        self.news_data.append(data_point)
    
    def add_whale_data(self, data_point: DataPoint):
        """添加大户数据"""
        self.whale_data.append(data_point)
    
    def get_latest_market_data(self, symbol: str, count: int = 100) -> List[DataPoint]:
        """获取最新市场数据"""
        data = self.market_data.get(symbol, deque())
        return list(data)[-count:] if data else []
    
    def get_latest_news(self, count: int = 50) -> List[DataPoint]:
        """获取最新新闻"""
        return list(self.news_data)[-count:]
    
    def get_latest_whale_alerts(self, count: int = 20) -> List[DataPoint]:
        """获取最新大户交易"""
        return list(self.whale_data)[-count:]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            'market_data_symbols': len(self.market_data),
            'total_market_points': sum(len(data) for data in self.market_data.values()),
            'news_points': len(self.news_data),
            'whale_points': len(self.whale_data),
            'timestamp': datetime.now().isoformat()
        }


class DataService:
    """数据服务"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_manager = DataSourceManager()
        self.data_processor = DataProcessor()
        self.data_cache = DataCache()
        self.subscribers: List[Callable] = []
        self.is_running = False
        self.logger = data_logger
        
        # 初始化数据源
        self._initialize_data_sources()
        
        # 注册默认数据处理器
        self._register_default_processors()
    
    def _initialize_data_sources(self):
        """初始化数据源"""
        try:
            # 市场数据源
            if self.config.get('market_data', {}).get('enabled', True):
                market_config = self.config.get('market_data', {})
                market_source = OKXMarketDataSource(market_config)
                market_source.subscribe(self._handle_market_data)
                self.data_manager.register_data_source(market_source)
            
            # 新闻数据源
            if self.config.get('news_data', {}).get('enabled', True):
                news_config = self.config.get('news_data', {})
                news_source = CryptoNewsSource(news_config)
                news_source.subscribe(self._handle_news_data)
                self.data_manager.register_data_source(news_source)
            
            # 大户监控数据源
            if self.config.get('whale_data', {}).get('enabled', False):
                whale_config = self.config.get('whale_data', {})
                if whale_config.get('api_key'):
                    whale_source = WhaleAlertSource(whale_config)
                    whale_source.subscribe(self._handle_whale_data)
                    self.data_manager.register_data_source(whale_source)
                else:
                    self.logger.warning("Whale Alert API密钥未配置，跳过大户监控")
            
            self.logger.info("数据源初始化完成")
            
        except Exception as e:
            self.logger.error(f"数据源初始化失败: {str(e)}")
    
    def _register_default_processors(self):
        """注册默认数据处理器"""
        # 市场数据处理器
        self.data_processor.register_processor(
            DataType.MARKET_DATA, 
            self._process_market_data
        )
        
        # 新闻数据处理器
        self.data_processor.register_processor(
            DataType.NEWS, 
            self._process_news_data
        )
        
        # 大户数据处理器
        self.data_processor.register_processor(
            DataType.WHALE_ALERT, 
            self._process_whale_data
        )
    
    async def _handle_market_data(self, data_point: DataPoint):
        """处理市场数据"""
        try:
            processed_data = await self.data_processor.process_data(data_point)
            if processed_data:
                self.data_cache.add_market_data(processed_data.symbol, processed_data)
                await self._notify_subscribers(processed_data)
        except Exception as e:
            self.logger.error(f"处理市场数据失败: {str(e)}")
    
    async def _handle_news_data(self, data_point: DataPoint):
        """处理新闻数据"""
        try:
            processed_data = await self.data_processor.process_data(data_point)
            if processed_data:
                self.data_cache.add_news_data(processed_data)
                await self._notify_subscribers(processed_data)
        except Exception as e:
            self.logger.error(f"处理新闻数据失败: {str(e)}")
    
    async def _handle_whale_data(self, data_point: DataPoint):
        """处理大户数据"""
        try:
            processed_data = await self.data_processor.process_data(data_point)
            if processed_data:
                self.data_cache.add_whale_data(processed_data)
                await self._notify_subscribers(processed_data)
        except Exception as e:
            self.logger.error(f"处理大户数据失败: {str(e)}")
    
    async def _process_market_data(self, data_point: DataPoint) -> DataPoint:
        """市场数据处理器"""
        # 这里可以添加技术指标计算、异常检测等
        return data_point
    
    async def _process_news_data(self, data_point: DataPoint) -> DataPoint:
        """新闻数据处理器"""
        # 这里可以添加情绪分析、关键词提取等
        return data_point
    
    async def _process_whale_data(self, data_point: DataPoint) -> DataPoint:
        """大户数据处理器"""
        # 这里可以添加交易模式分析、影响评估等
        return data_point
    
    async def start(self) -> bool:
        """启动数据服务"""
        try:
            if self.is_running:
                return True
            
            await self.data_manager.start_all()
            self.is_running = True
            self.logger.info("数据服务启动成功")
            return True
            
        except Exception as e:
            self.logger.error(f"启动数据服务失败: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """停止数据服务"""
        try:
            await self.data_manager.stop_all()
            self.is_running = False
            self.logger.info("数据服务停止成功")
            return True
            
        except Exception as e:
            self.logger.error(f"停止数据服务失败: {str(e)}")
            return False
    
    def subscribe(self, callback: Callable):
        """订阅数据更新"""
        if callback not in self.subscribers:
            self.subscribers.append(callback)
            self.logger.info(f"新增数据订阅者: {callback.__name__}")
    
    def unsubscribe(self, callback: Callable):
        """取消订阅"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            self.logger.info(f"移除数据订阅者: {callback.__name__}")
    
    async def _notify_subscribers(self, data_point: DataPoint):
        """通知订阅者"""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data_point)
                else:
                    callback(data_point)
            except Exception as e:
                self.logger.error(f"通知订阅者失败 {callback.__name__}: {str(e)}")
    
    async def get_market_data(self, symbol: str, count: int = 100) -> List[Dict[str, Any]]:
        """获取市场数据"""
        data_points = self.data_cache.get_latest_market_data(symbol, count)
        return [dp.data for dp in data_points]
    
    async def get_news_data(self, count: int = 50) -> List[Dict[str, Any]]:
        """获取新闻数据"""
        data_points = self.data_cache.get_latest_news(count)
        return [dp.data for dp in data_points]
    
    async def get_whale_alerts(self, count: int = 20) -> List[Dict[str, Any]]:
        """获取大户交易数据"""
        data_points = self.data_cache.get_latest_whale_alerts(count)
        return [dp.data for dp in data_points]
    
    async def get_historical_data(
        self, 
        data_type: DataType,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取历史数据"""
        try:
            # 根据数据类型选择数据源
            source_name = {
                DataType.MARKET_DATA: "okx_market",
                DataType.NEWS: "crypto_news",
                DataType.WHALE_ALERT: "whale_alert"
            }.get(data_type)
            
            if not source_name:
                return []
            
            data_source = self.data_manager.get_data_source(source_name)
            if not data_source:
                return []
            
            # 设置默认时间范围
            if not end_time:
                end_time = datetime.now()
            if not start_time:
                start_time = end_time - timedelta(days=1)
            
            data_points = await data_source.get_historical_data(
                symbol or "", start_time, end_time, **kwargs
            )
            
            return [dp.data for dp in data_points]
            
        except Exception as e:
            self.logger.error(f"获取历史数据失败: {str(e)}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            data_sources_health = await self.data_manager.health_check_all()
            cache_stats = self.data_cache.get_cache_stats()
            
            return {
                'service_status': 'running' if self.is_running else 'stopped',
                'data_sources': data_sources_health,
                'cache_stats': cache_stats,
                'subscribers_count': len(self.subscribers),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {str(e)}")
            return {'error': str(e)}
    
    def get_supported_symbols(self) -> List[str]:
        """获取支持的交易对"""
        symbols = set()
        for source in self.data_manager.data_sources.values():
            symbols.update(source.get_supported_symbols())
        return list(symbols)
    
    async def subscribe_symbol(self, symbol: str) -> bool:
        """订阅新的交易对"""
        try:
            market_source = self.data_manager.get_data_source("okx_market")
            if market_source and hasattr(market_source, 'subscribe_symbol'):
                return await market_source.subscribe_symbol(symbol)
            return False
        except Exception as e:
            self.logger.error(f"订阅交易对失败 {symbol}: {str(e)}")
            return False
