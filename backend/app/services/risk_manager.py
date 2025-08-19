"""
风险管理模块
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from sqlalchemy.orm import Session
from decimal import Decimal
import asyncio

from app.models.trading import Account, Position, Order, OrderStatus
from app.schemas.trading import OrderCreate
from app.core.config import settings
from app.core.logging import trading_logger


@dataclass
class RiskCheckResult:
    """风险检查结果"""
    is_valid: bool
    reason: Optional[str] = None
    warnings: List[str] = None


class RiskManager:
    """风险管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.max_position_size = settings.MAX_POSITION_SIZE
        self.max_daily_loss = settings.MAX_DAILY_LOSS
        self.max_drawdown = settings.MAX_DRAWDOWN
        self.stop_loss_ratio = settings.STOP_LOSS_RATIO
        self.take_profit_ratio = settings.TAKE_PROFIT_RATIO
    
    async def check_order_risk(self, order_data: OrderCreate) -> RiskCheckResult:
        """检查订单风险"""
        warnings = []
        
        try:
            # 1. 检查账户状态
            account_check = await self._check_account_status(order_data.account_id)
            if not account_check.is_valid:
                return account_check
            
            # 2. 检查仓位大小
            position_check = await self._check_position_size(order_data)
            if not position_check.is_valid:
                return position_check
            warnings.extend(position_check.warnings or [])
            
            # 3. 检查余额充足性
            balance_check = await self._check_balance_sufficiency(order_data)
            if not balance_check.is_valid:
                return balance_check
            warnings.extend(balance_check.warnings or [])
            
            # 4. 检查日损失限制
            daily_loss_check = await self._check_daily_loss_limit(order_data.account_id)
            if not daily_loss_check.is_valid:
                return daily_loss_check
            warnings.extend(daily_loss_check.warnings or [])
            
            # 5. 检查最大回撤
            drawdown_check = await self._check_max_drawdown(order_data.account_id)
            if not drawdown_check.is_valid:
                return drawdown_check
            warnings.extend(drawdown_check.warnings or [])
            
            # 6. 检查价格合理性
            price_check = await self._check_price_reasonableness(order_data)
            if not price_check.is_valid:
                return price_check
            warnings.extend(price_check.warnings or [])
            
            return RiskCheckResult(is_valid=True, warnings=warnings)
            
        except Exception as e:
            trading_logger.error(f"风险检查异常: {str(e)}", extra={"TRADING": True})
            return RiskCheckResult(is_valid=False, reason=f"风险检查异常: {str(e)}")
    
    async def _check_account_status(self, account_id: str) -> RiskCheckResult:
        """检查账户状态"""
        account = self.db.query(Account).filter(Account.id == account_id).first()
        
        if not account:
            return RiskCheckResult(is_valid=False, reason="账户不存在")
        
        if not account.is_active:
            return RiskCheckResult(is_valid=False, reason="账户已禁用")
        
        return RiskCheckResult(is_valid=True)
    
    async def _check_position_size(self, order_data: OrderCreate) -> RiskCheckResult:
        """检查仓位大小"""
        warnings = []
        
        # 获取当前持仓
        current_position = self.db.query(Position).filter(
            Position.account_id == order_data.account_id,
            Position.symbol == order_data.symbol
        ).first()
        
        current_size = current_position.size if current_position else 0
        
        # 计算新的仓位大小
        if order_data.side.value == "buy":
            new_size = current_size + order_data.amount
        else:
            new_size = current_size - order_data.amount
        
        # 获取账户总资产
        total_balance = await self._get_total_balance(order_data.account_id)
        
        # 计算仓位价值
        position_value = abs(new_size) * (order_data.price or 0)
        position_ratio = position_value / total_balance if total_balance > 0 else 0
        
        # 检查是否超过最大仓位比例
        if position_ratio > self.max_position_size:
            return RiskCheckResult(
                is_valid=False,
                reason=f"仓位比例 {position_ratio:.2%} 超过最大限制 {self.max_position_size:.2%}"
            )
        
        # 警告：仓位比例较高
        if position_ratio > self.max_position_size * 0.8:
            warnings.append(f"仓位比例 {position_ratio:.2%} 接近最大限制")
        
        return RiskCheckResult(is_valid=True, warnings=warnings)
    
    async def _check_balance_sufficiency(self, order_data: OrderCreate) -> RiskCheckResult:
        """检查余额充足性"""
        warnings = []
        
        # 获取账户余额
        available_balance = await self._get_available_balance(
            order_data.account_id,
            order_data.symbol
        )
        
        # 计算所需资金
        if order_data.side.value == "buy":
            required_amount = order_data.amount * (order_data.price or 0)
            if required_amount > available_balance:
                return RiskCheckResult(
                    is_valid=False,
                    reason=f"余额不足，需要 {required_amount}，可用 {available_balance}"
                )
        else:
            # 卖出检查持仓数量
            position = self.db.query(Position).filter(
                Position.account_id == order_data.account_id,
                Position.symbol == order_data.symbol
            ).first()
            
            available_size = position.size if position else 0
            if order_data.amount > available_size:
                return RiskCheckResult(
                    is_valid=False,
                    reason=f"持仓不足，需要 {order_data.amount}，可用 {available_size}"
                )
        
        return RiskCheckResult(is_valid=True, warnings=warnings)
    
    async def _check_daily_loss_limit(self, account_id: str) -> RiskCheckResult:
        """检查日损失限制"""
        warnings = []
        
        # 获取今日已实现损失
        daily_pnl = await self._get_daily_pnl(account_id)
        total_balance = await self._get_total_balance(account_id)
        
        if daily_pnl < 0:
            loss_ratio = abs(daily_pnl) / total_balance if total_balance > 0 else 0
            
            if loss_ratio > self.max_daily_loss:
                return RiskCheckResult(
                    is_valid=False,
                    reason=f"日损失 {loss_ratio:.2%} 超过最大限制 {self.max_daily_loss:.2%}"
                )
            
            # 警告：接近日损失限制
            if loss_ratio > self.max_daily_loss * 0.8:
                warnings.append(f"日损失 {loss_ratio:.2%} 接近最大限制")
        
        return RiskCheckResult(is_valid=True, warnings=warnings)
    
    async def _check_max_drawdown(self, account_id: str) -> RiskCheckResult:
        """检查最大回撤"""
        warnings = []
        
        # 获取账户最大回撤
        current_drawdown = await self._get_current_drawdown(account_id)
        
        if current_drawdown > self.max_drawdown:
            return RiskCheckResult(
                is_valid=False,
                reason=f"当前回撤 {current_drawdown:.2%} 超过最大限制 {self.max_drawdown:.2%}"
            )
        
        # 警告：接近最大回撤
        if current_drawdown > self.max_drawdown * 0.8:
            warnings.append(f"当前回撤 {current_drawdown:.2%} 接近最大限制")
        
        return RiskCheckResult(is_valid=True, warnings=warnings)
    
    async def _check_price_reasonableness(self, order_data: OrderCreate) -> RiskCheckResult:
        """检查价格合理性"""
        warnings = []
        
        if not order_data.price:
            return RiskCheckResult(is_valid=True)
        
        # 获取当前市场价格
        market_price = await self._get_market_price(order_data.symbol)
        
        if market_price:
            price_diff = abs(order_data.price - market_price) / market_price
            
            # 价格偏差超过10%给出警告
            if price_diff > 0.1:
                warnings.append(f"订单价格与市场价格偏差 {price_diff:.2%}")
            
            # 价格偏差超过20%拒绝订单
            if price_diff > 0.2:
                return RiskCheckResult(
                    is_valid=False,
                    reason=f"订单价格与市场价格偏差过大 {price_diff:.2%}"
                )
        
        return RiskCheckResult(is_valid=True, warnings=warnings)
    
    async def _get_total_balance(self, account_id: str) -> float:
        """获取账户总余额"""
        # 这里应该调用交易所API获取实时余额
        # 暂时返回模拟数据
        return 10000.0
    
    async def _get_available_balance(self, account_id: str, symbol: str) -> float:
        """获取可用余额"""
        # 这里应该调用交易所API获取实时余额
        # 暂时返回模拟数据
        return 5000.0
    
    async def _get_daily_pnl(self, account_id: str) -> float:
        """获取日盈亏"""
        # 计算今日已实现盈亏
        # 暂时返回模拟数据
        return -100.0
    
    async def _get_current_drawdown(self, account_id: str) -> float:
        """获取当前回撤"""
        # 计算当前回撤比例
        # 暂时返回模拟数据
        return 0.05
    
    async def _get_market_price(self, symbol: str) -> Optional[float]:
        """获取市场价格"""
        # 这里应该调用市场数据API获取实时价格
        # 暂时返回模拟数据
        return 50000.0
