"""
交易服务模块
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from app.models.trading import (
    Order, Position, Trade, Account, Balance,
    OrderStatus, OrderType, OrderSide, PositionSide
)
from app.schemas.trading import (
    OrderCreate, OrderUpdate, OrderResponse,
    PositionResponse, TradeResponse, TradingStats
)
from app.core.logging import trading_logger
from app.services.risk_manager import RiskManager
from app.services.exchange_service import ExchangeService


class TradingService:
    """交易服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.risk_manager = RiskManager(db)
        self.exchange_service = ExchangeService()
    
    async def create_order(self, order_data: OrderCreate) -> OrderResponse:
        """创建订单"""
        try:
            # 生成订单ID
            order_id = str(uuid.uuid4())
            
            # 风险检查
            risk_check = await self.risk_manager.check_order_risk(order_data)
            if not risk_check.is_valid:
                raise ValueError(f"风险检查失败: {risk_check.reason}")
            
            # 获取账户信息
            account = self.db.query(Account).filter(Account.id == order_data.account_id).first()
            if not account:
                raise ValueError("账户不存在")
            
            # 创建订单对象
            order = Order(
                id=order_id,
                account_id=order_data.account_id,
                strategy_id=order_data.strategy_id,
                symbol=order_data.symbol,
                side=order_data.side,
                type=order_data.type,
                amount=order_data.amount,
                price=order_data.price,
                stop_price=order_data.stop_price,
                remaining_amount=order_data.amount,
                notes=order_data.notes,
                status=OrderStatus.PENDING
            )
            
            # 保存到数据库
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            # 提交到交易所
            try:
                exchange_order = await self.exchange_service.create_order(
                    account=account,
                    order=order
                )

                # 更新交易所订单ID
                order.exchange_order_id = exchange_order.get('id')
                order.status = OrderStatus.SUBMITTED
                self.db.commit()

                trading_logger.info(
                    f"订单创建成功: {order_id}, 交易所订单ID: {exchange_order.get('id')}",
                    extra={"TRADING": True}
                )

            except Exception as e:
                # 交易所提交失败，更新订单状态
                order.status = OrderStatus.REJECTED
                self.db.commit()
                trading_logger.error(
                    f"订单提交到交易所失败: {order_id}, 错误: {str(e)}",
                    extra={"TRADING": True}
                )
                raise
            
            return OrderResponse.from_orm(order)
            
        except Exception as e:
            self.db.rollback()
            trading_logger.error(f"创建订单失败: {str(e)}", extra={"TRADING": True})
            raise
    
    async def get_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[OrderResponse]:
        """获取订单列表"""
        query = self.db.query(Order)
        
        if symbol:
            query = query.filter(Order.symbol == symbol)
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
        return [OrderResponse.from_orm(order) for order in orders]
    
    async def get_order(self, order_id: str) -> Optional[OrderResponse]:
        """获取单个订单"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        return OrderResponse.from_orm(order) if order else None
    
    async def update_order(self, order_id: str, order_update: OrderUpdate) -> OrderResponse:
        """更新订单"""
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ValueError("订单不存在")
            
            if order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
                raise ValueError("订单状态不允许修改")
            
            # 更新订单信息
            update_data = order_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(order, field, value)
            
            order.updated_at = datetime.utcnow()
            
            # 如果有交易所订单ID，需要更新交易所订单
            if order.exchange_order_id:
                account = self.db.query(Account).filter(Account.id == order.account_id).first()
                await self.exchange_service.update_order(
                    account=account,
                    order_id=order.exchange_order_id,
                    update_data=update_data
                )
            
            self.db.commit()
            self.db.refresh(order)
            
            trading_logger.info(f"订单更新成功: {order_id}", extra={"TRADING": True})
            return OrderResponse.from_orm(order)
            
        except Exception as e:
            self.db.rollback()
            trading_logger.error(f"更新订单失败: {str(e)}", extra={"TRADING": True})
            raise
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ValueError("订单不存在")
            
            if order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED]:
                raise ValueError("订单状态不允许取消")
            
            # 取消交易所订单
            if order.exchange_order_id:
                account = self.db.query(Account).filter(Account.id == order.account_id).first()
                await self.exchange_service.cancel_order(
                    account=account,
                    order_id=order.exchange_order_id
                )
            
            # 更新订单状态
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.utcnow()
            self.db.commit()
            
            trading_logger.info(f"订单取消成功: {order_id}", extra={"TRADING": True})
            return True
            
        except Exception as e:
            self.db.rollback()
            trading_logger.error(f"取消订单失败: {str(e)}", extra={"TRADING": True})
            raise
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[PositionResponse]:
        """获取持仓列表"""
        query = self.db.query(Position).filter(Position.size != 0)
        
        if symbol:
            query = query.filter(Position.symbol == symbol)
        
        positions = query.all()
        return [PositionResponse.from_orm(position) for position in positions]
    
    async def get_position(self, symbol: str) -> Optional[PositionResponse]:
        """获取特定交易对的持仓"""
        position = self.db.query(Position).filter(
            and_(Position.symbol == symbol, Position.size != 0)
        ).first()
        return PositionResponse.from_orm(position) if position else None
    
    async def get_trades(
        self,
        symbol: Optional[str] = None,
        order_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TradeResponse]:
        """获取交易记录"""
        query = self.db.query(Trade)
        
        if symbol:
            query = query.filter(Trade.symbol == symbol)
        if order_id:
            query = query.filter(Trade.order_id == order_id)
        
        trades = query.order_by(Trade.timestamp.desc()).offset(offset).limit(limit).all()
        return [TradeResponse.from_orm(trade) for trade in trades]
    
    async def create_batch_orders(self, orders_data: List[OrderCreate]) -> List[OrderResponse]:
        """批量创建订单"""
        results = []
        for order_data in orders_data:
            try:
                order = await self.create_order(order_data)
                results.append(order)
            except Exception as e:
                trading_logger.error(f"批量订单创建失败: {str(e)}", extra={"TRADING": True})
                # 继续处理其他订单
                continue
        return results
    
    async def cancel_all_orders(self, symbol: Optional[str] = None) -> int:
        """批量取消订单"""
        query = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED])
        )
        
        if symbol:
            query = query.filter(Order.symbol == symbol)
        
        orders = query.all()
        cancelled_count = 0
        
        for order in orders:
            try:
                await self.cancel_order(order.id)
                cancelled_count += 1
            except Exception as e:
                trading_logger.error(f"批量取消订单失败: {order.id}, {str(e)}", extra={"TRADING": True})
                continue
        
        return cancelled_count
    
    async def get_trading_stats(self, account_id: Optional[str] = None) -> TradingStats:
        """获取交易统计"""
        query = self.db.query(Order)
        if account_id:
            query = query.filter(Order.account_id == account_id)
        
        total_orders = query.count()
        active_orders = query.filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED])
        ).count()
        filled_orders = query.filter(Order.status == OrderStatus.FILLED).count()
        cancelled_orders = query.filter(Order.status == OrderStatus.CANCELLED).count()
        
        # 计算交易统计
        trades_query = self.db.query(Trade)
        if account_id:
            trades_query = trades_query.join(Order).filter(Order.account_id == account_id)
        
        total_trades = trades_query.count()
        total_volume = sum([trade.amount * trade.price for trade in trades_query.all()])
        
        # 计算盈亏
        positions_query = self.db.query(Position)
        if account_id:
            positions_query = positions_query.filter(Position.account_id == account_id)
        
        positions = positions_query.all()
        total_pnl = sum([pos.realized_pnl + pos.unrealized_pnl for pos in positions])
        
        # 计算胜率
        win_trades = len([pos for pos in positions if pos.realized_pnl > 0])
        win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
        
        # 计算最大回撤
        max_drawdown = max([pos.percentage for pos in positions]) if positions else 0
        
        return TradingStats(
            total_orders=total_orders,
            active_orders=active_orders,
            filled_orders=filled_orders,
            cancelled_orders=cancelled_orders,
            total_trades=total_trades,
            total_volume=total_volume,
            total_pnl=total_pnl,
            win_rate=win_rate,
            max_drawdown=max_drawdown
        )
