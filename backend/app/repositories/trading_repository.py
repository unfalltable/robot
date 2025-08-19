"""
交易数据访问层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from .base_repository import BaseRepository
from app.models.trading import Account, Order, Position, Trade, Strategy, OrderStatus, OrderSide


class AccountRepository(BaseRepository[Account]):
    """账户数据访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Account, session)
    
    async def get_by_exchange(self, exchange: str) -> List[Account]:
        """根据交易所获取账户"""
        result = await self.session.execute(
            select(self.model).where(self.model.exchange == exchange)
        )
        return result.scalars().all()
    
    async def get_active_accounts(self) -> List[Account]:
        """获取活跃账户"""
        result = await self.session.execute(
            select(self.model).where(self.model.is_active == True)
        )
        return result.scalars().all()
    
    async def update_balance(self, account_id: str, currency: str, balance: float) -> bool:
        """更新账户余额"""
        account = await self.get(account_id)
        if not account:
            return False
        
        if not account.balances:
            account.balances = {}
        
        account.balances[currency] = balance
        await self.session.commit()
        return True


class OrderRepository(BaseRepository[Order]):
    """订单数据访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)
    
    async def get_by_account(self, account_id: str, limit: int = 100) -> List[Order]:
        """根据账户获取订单"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.account_id == account_id)
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_strategy(self, strategy_id: str, limit: int = 100) -> List[Order]:
        """根据策略获取订单"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.strategy_id == strategy_id)
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_symbol(self, symbol: str, limit: int = 100) -> List[Order]:
        """根据交易对获取订单"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.symbol == symbol)
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(self, status: OrderStatus, limit: int = 100) -> List[Order]:
        """根据状态获取订单"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.status == status)
            .order_by(desc(self.model.created_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_orders(self, account_id: Optional[str] = None) -> List[Order]:
        """获取活跃订单"""
        query = select(self.model).where(
            self.model.status.in_([OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED])
        )
        
        if account_id:
            query = query.where(self.model.account_id == account_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_orders_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        account_id: Optional[str] = None
    ) -> List[Order]:
        """根据日期范围获取订单"""
        query = select(self.model).where(
            and_(
                self.model.created_at >= start_date,
                self.model.created_at <= end_date
            )
        )
        
        if account_id:
            query = query.where(self.model.account_id == account_id)
        
        query = query.order_by(desc(self.model.created_at))
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_order_statistics(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """获取订单统计"""
        query = select(
            func.count(self.model.id).label('total_orders'),
            func.count(self.model.id).filter(self.model.status == OrderStatus.FILLED).label('filled_orders'),
            func.count(self.model.id).filter(self.model.status == OrderStatus.CANCELLED).label('cancelled_orders'),
            func.count(self.model.id).filter(self.model.status.in_([OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED])).label('active_orders'),
            func.sum(self.model.amount).label('total_amount'),
            func.avg(self.model.price).label('avg_price')
        )
        
        if account_id:
            query = query.where(self.model.account_id == account_id)
        
        result = await self.session.execute(query)
        row = result.first()
        
        return {
            'total_orders': row.total_orders or 0,
            'filled_orders': row.filled_orders or 0,
            'cancelled_orders': row.cancelled_orders or 0,
            'active_orders': row.active_orders or 0,
            'total_amount': float(row.total_amount or 0),
            'avg_price': float(row.avg_price or 0)
        }


class PositionRepository(BaseRepository[Position]):
    """持仓数据访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Position, session)
    
    async def get_by_account(self, account_id: str) -> List[Position]:
        """根据账户获取持仓"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.account_id == account_id)
            .where(self.model.size != 0)  # 只获取有持仓的记录
        )
        return result.scalars().all()
    
    async def get_by_symbol(self, symbol: str) -> List[Position]:
        """根据交易对获取持仓"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.symbol == symbol)
            .where(self.model.size != 0)
        )
        return result.scalars().all()
    
    async def get_position(self, account_id: str, symbol: str) -> Optional[Position]:
        """获取特定持仓"""
        result = await self.session.execute(
            select(self.model)
            .where(
                and_(
                    self.model.account_id == account_id,
                    self.model.symbol == symbol
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_position(
        self, 
        account_id: str, 
        symbol: str, 
        size: float, 
        entry_price: float,
        unrealized_pnl: float = 0.0
    ) -> Position:
        """更新持仓"""
        position = await self.get_position(account_id, symbol)
        
        if position:
            position.size = size
            position.entry_price = entry_price
            position.unrealized_pnl = unrealized_pnl
            position.updated_at = datetime.utcnow()
        else:
            position = Position(
                account_id=account_id,
                symbol=symbol,
                size=size,
                entry_price=entry_price,
                unrealized_pnl=unrealized_pnl
            )
            self.session.add(position)
        
        await self.session.commit()
        await self.session.refresh(position)
        return position


class TradeRepository(BaseRepository[Trade]):
    """交易记录数据访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Trade, session)
    
    async def get_by_order(self, order_id: str) -> List[Trade]:
        """根据订单获取交易记录"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.order_id == order_id)
            .order_by(desc(self.model.timestamp))
        )
        return result.scalars().all()
    
    async def get_by_symbol(self, symbol: str, limit: int = 100) -> List[Trade]:
        """根据交易对获取交易记录"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.symbol == symbol)
            .order_by(desc(self.model.timestamp))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_trades_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        symbol: Optional[str] = None
    ) -> List[Trade]:
        """根据日期范围获取交易记录"""
        query = select(self.model).where(
            and_(
                self.model.timestamp >= start_date,
                self.model.timestamp <= end_date
            )
        )
        
        if symbol:
            query = query.where(self.model.symbol == symbol)
        
        query = query.order_by(desc(self.model.timestamp))
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_trade_statistics(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取交易统计"""
        query = select(
            func.count(self.model.id).label('total_trades'),
            func.sum(self.model.amount).label('total_volume'),
            func.sum(self.model.amount * self.model.price).label('total_value'),
            func.avg(self.model.price).label('avg_price'),
            func.sum(self.model.fee).label('total_fees')
        )
        
        conditions = []
        if start_date:
            conditions.append(self.model.timestamp >= start_date)
        if end_date:
            conditions.append(self.model.timestamp <= end_date)
        if symbol:
            conditions.append(self.model.symbol == symbol)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        row = result.first()
        
        return {
            'total_trades': row.total_trades or 0,
            'total_volume': float(row.total_volume or 0),
            'total_value': float(row.total_value or 0),
            'avg_price': float(row.avg_price or 0),
            'total_fees': float(row.total_fees or 0)
        }


class StrategyRepository(BaseRepository[Strategy]):
    """策略数据访问层"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Strategy, session)
    
    async def get_active_strategies(self) -> List[Strategy]:
        """获取活跃策略"""
        result = await self.session.execute(
            select(self.model).where(self.model.is_active == True)
        )
        return result.scalars().all()
    
    async def get_by_type(self, strategy_type: str) -> List[Strategy]:
        """根据类型获取策略"""
        result = await self.session.execute(
            select(self.model).where(self.model.type == strategy_type)
        )
        return result.scalars().all()
    
    async def get_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """获取策略性能"""
        strategy = await self.get(strategy_id)
        if not strategy:
            return {}
        
        # 获取策略相关的订单和交易
        orders_result = await self.session.execute(
            select(func.count(Order.id)).where(Order.strategy_id == strategy_id)
        )
        total_orders = orders_result.scalar() or 0
        
        trades_result = await self.session.execute(
            select(
                func.count(Trade.id),
                func.sum(Trade.amount * Trade.price),
                func.sum(Trade.fee)
            )
            .select_from(Trade)
            .join(Order, Trade.order_id == Order.id)
            .where(Order.strategy_id == strategy_id)
        )
        trade_row = trades_result.first()
        
        return {
            'strategy_id': strategy_id,
            'total_orders': total_orders,
            'total_trades': trade_row[0] or 0,
            'total_volume': float(trade_row[1] or 0),
            'total_fees': float(trade_row[2] or 0),
            'total_pnl': strategy.total_pnl,
            'win_rate': strategy.win_trades / max(strategy.total_trades, 1) * 100,
            'max_drawdown': strategy.max_drawdown
        }
