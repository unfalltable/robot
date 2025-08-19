"""
市场数据访问层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from .base_repository import BaseRepository
from app.models.market_data import (
    MarketData, TickerData, OrderBookData, TradingPair,
    MarketIndicator, MarketSentiment, ExchangeStatus
)


class MarketDataRepository(BaseRepository[MarketData]):
    """市场数据访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(MarketData, session)
    
    async def get_latest_by_symbol(self, symbol: str, timeframe: str = "1m") -> Optional[MarketData]:
        """获取最新的市场数据"""
        result = await self.session.execute(
            select(self.model)
            .where(
                and_(
                    self.model.symbol == symbol,
                    self.model.timeframe == timeframe
                )
            )
            .order_by(desc(self.model.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_klines(
        self, 
        symbol: str, 
        timeframe: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[MarketData]:
        """获取K线数据"""
        query = select(self.model).where(
            and_(
                self.model.symbol == symbol,
                self.model.timeframe == timeframe
            )
        )
        
        if start_time:
            query = query.where(self.model.timestamp >= start_time)
        if end_time:
            query = query.where(self.model.timestamp <= end_time)
        
        query = query.order_by(asc(self.model.timestamp)).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_ohlcv_data(
        self, 
        symbol: str, 
        timeframe: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取OHLCV数据"""
        result = await self.session.execute(
            select(
                self.model.timestamp,
                self.model.open,
                self.model.high,
                self.model.low,
                self.model.close,
                self.model.volume
            )
            .where(
                and_(
                    self.model.symbol == symbol,
                    self.model.timeframe == timeframe
                )
            )
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        
        return [
            {
                'timestamp': row.timestamp,
                'open': row.open,
                'high': row.high,
                'low': row.low,
                'close': row.close,
                'volume': row.volume
            }
            for row in result
        ]
    
    async def bulk_insert_klines(self, klines: List[Dict[str, Any]]) -> int:
        """批量插入K线数据"""
        if not klines:
            return 0
        
        # 转换为模型对象
        market_data_objects = []
        for kline in klines:
            market_data = MarketData(**kline)
            market_data_objects.append(market_data)
        
        self.session.add_all(market_data_objects)
        await self.session.commit()
        return len(market_data_objects)
    
    async def get_price_statistics(
        self, 
        symbol: str, 
        timeframe: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取价格统计"""
        query = select(
            func.min(self.model.low).label('min_price'),
            func.max(self.model.high).label('max_price'),
            func.avg(self.model.close).label('avg_price'),
            func.sum(self.model.volume).label('total_volume'),
            func.count(self.model.id).label('data_points')
        ).where(
            and_(
                self.model.symbol == symbol,
                self.model.timeframe == timeframe
            )
        )
        
        if start_time:
            query = query.where(self.model.timestamp >= start_time)
        if end_time:
            query = query.where(self.model.timestamp <= end_time)
        
        result = await self.session.execute(query)
        row = result.first()
        
        return {
            'min_price': float(row.min_price or 0),
            'max_price': float(row.max_price or 0),
            'avg_price': float(row.avg_price or 0),
            'total_volume': float(row.total_volume or 0),
            'data_points': row.data_points or 0
        }


class TickerDataRepository(BaseRepository[TickerData]):
    """实时行情数据访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(TickerData, session)
    
    async def get_latest_ticker(self, symbol: str) -> Optional[TickerData]:
        """获取最新行情"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.symbol == symbol)
            .order_by(desc(self.model.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_all_latest_tickers(self) -> List[TickerData]:
        """获取所有交易对的最新行情"""
        # 使用窗口函数获取每个symbol的最新记录
        subquery = select(
            self.model.symbol,
            func.max(self.model.timestamp).label('max_timestamp')
        ).group_by(self.model.symbol).subquery()
        
        result = await self.session.execute(
            select(self.model)
            .join(
                subquery,
                and_(
                    self.model.symbol == subquery.c.symbol,
                    self.model.timestamp == subquery.c.max_timestamp
                )
            )
        )
        return result.scalars().all()
    
    async def update_ticker(self, ticker_data: Dict[str, Any]) -> TickerData:
        """更新行情数据"""
        ticker = TickerData(**ticker_data)
        self.session.add(ticker)
        await self.session.commit()
        await self.session.refresh(ticker)
        return ticker


class OrderBookDataRepository(BaseRepository[OrderBookData]):
    """订单簿数据访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(OrderBookData, session)
    
    async def get_latest_orderbook(self, symbol: str) -> Optional[OrderBookData]:
        """获取最新订单簿"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.symbol == symbol)
            .order_by(desc(self.model.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def update_orderbook(self, orderbook_data: Dict[str, Any]) -> OrderBookData:
        """更新订单簿数据"""
        orderbook = OrderBookData(**orderbook_data)
        self.session.add(orderbook)
        await self.session.commit()
        await self.session.refresh(orderbook)
        return orderbook


class TradingPairRepository(BaseRepository[TradingPair]):
    """交易对配置访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(TradingPair, session)
    
    async def get_active_pairs(self) -> List[TradingPair]:
        """获取活跃交易对"""
        result = await self.session.execute(
            select(self.model).where(self.model.is_active == True)
        )
        return result.scalars().all()
    
    async def get_by_symbol(self, symbol: str) -> Optional[TradingPair]:
        """根据交易对符号获取配置"""
        result = await self.session.execute(
            select(self.model).where(self.model.symbol == symbol)
        )
        return result.scalar_one_or_none()
    
    async def get_by_base_currency(self, base_currency: str) -> List[TradingPair]:
        """根据基础货币获取交易对"""
        result = await self.session.execute(
            select(self.model).where(self.model.base_currency == base_currency)
        )
        return result.scalars().all()
    
    async def get_by_quote_currency(self, quote_currency: str) -> List[TradingPair]:
        """根据计价货币获取交易对"""
        result = await self.session.execute(
            select(self.model).where(self.model.quote_currency == quote_currency)
        )
        return result.scalars().all()


class MarketIndicatorRepository(BaseRepository[MarketIndicator]):
    """市场指标访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(MarketIndicator, session)
    
    async def get_latest_indicators(
        self, 
        symbol: str, 
        timeframe: str
    ) -> Optional[MarketIndicator]:
        """获取最新指标"""
        result = await self.session.execute(
            select(self.model)
            .where(
                and_(
                    self.model.symbol == symbol,
                    self.model.timeframe == timeframe
                )
            )
            .order_by(desc(self.model.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_indicators_history(
        self, 
        symbol: str, 
        timeframe: str,
        limit: int = 100
    ) -> List[MarketIndicator]:
        """获取指标历史"""
        result = await self.session.execute(
            select(self.model)
            .where(
                and_(
                    self.model.symbol == symbol,
                    self.model.timeframe == timeframe
                )
            )
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def bulk_insert_indicators(self, indicators: List[Dict[str, Any]]) -> int:
        """批量插入指标数据"""
        if not indicators:
            return 0
        
        indicator_objects = [MarketIndicator(**indicator) for indicator in indicators]
        self.session.add_all(indicator_objects)
        await self.session.commit()
        return len(indicator_objects)


class MarketSentimentRepository(BaseRepository[MarketSentiment]):
    """市场情绪访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(MarketSentiment, session)
    
    async def get_latest_sentiment(self, symbol: str) -> Optional[MarketSentiment]:
        """获取最新市场情绪"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.symbol == symbol)
            .order_by(desc(self.model.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_sentiment_history(
        self, 
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[MarketSentiment]:
        """获取情绪历史"""
        query = select(self.model).where(self.model.symbol == symbol)
        
        if start_time:
            query = query.where(self.model.timestamp >= start_time)
        if end_time:
            query = query.where(self.model.timestamp <= end_time)
        
        query = query.order_by(desc(self.model.timestamp)).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()


class ExchangeStatusRepository(BaseRepository[ExchangeStatus]):
    """交易所状态访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(ExchangeStatus, session)
    
    async def get_latest_status(self, exchange: str) -> Optional[ExchangeStatus]:
        """获取最新交易所状态"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.exchange == exchange)
            .order_by(desc(self.model.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_all_latest_status(self) -> List[ExchangeStatus]:
        """获取所有交易所的最新状态"""
        subquery = select(
            self.model.exchange,
            func.max(self.model.timestamp).label('max_timestamp')
        ).group_by(self.model.exchange).subquery()
        
        result = await self.session.execute(
            select(self.model)
            .join(
                subquery,
                and_(
                    self.model.exchange == subquery.c.exchange,
                    self.model.timestamp == subquery.c.max_timestamp
                )
            )
        )
        return result.scalars().all()
    
    async def update_status(self, status_data: Dict[str, Any]) -> ExchangeStatus:
        """更新交易所状态"""
        status = ExchangeStatus(**status_data)
        self.session.add(status)
        await self.session.commit()
        await self.session.refresh(status)
        return status
