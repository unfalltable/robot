"""
网格交易策略
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import math

from .base_strategy import (
    BaseStrategy, StrategyConfig, TradingSignal, 
    SignalType, StrategyStatus
)
from app.core.logging import get_logger

strategy_logger = get_logger("strategy")


class GridStrategy(BaseStrategy):
    """网格交易策略实现"""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        
        # 网格参数
        self.grid_size = config.parameters.get('grid_size', 0.01)  # 网格间距（百分比）
        self.grid_levels = config.parameters.get('grid_levels', 10)  # 网格层数
        self.base_amount = config.parameters.get('base_amount', 100.0)  # 基础下单金额
        self.center_price = config.parameters.get('center_price', 0.0)  # 中心价格
        
        # 网格状态
        self.buy_orders: Dict[float, str] = {}  # price -> order_id
        self.sell_orders: Dict[float, str] = {}  # price -> order_id
        self.grid_prices: List[float] = []
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """初始化策略"""
        try:
            if not self.validate_config():
                return False
            
            # 如果没有设置中心价格，使用当前市价
            if self.center_price <= 0:
                # 这里应该获取当前市价，暂时使用默认值
                self.center_price = 50000.0  # 示例价格
            
            # 生成网格价格
            self._generate_grid_prices()
            
            strategy_logger.info(
                f"网格策略初始化完成: 中心价格={self.center_price}, "
                f"网格间距={self.grid_size*100}%, 层数={self.grid_levels}"
            )
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            strategy_logger.error(f"网格策略初始化失败: {str(e)}")
            return False
    
    def _generate_grid_prices(self) -> None:
        """生成网格价格"""
        self.grid_prices = []
        
        # 生成买入网格（低于中心价格）
        for i in range(1, self.grid_levels + 1):
            buy_price = self.center_price * (1 - self.grid_size * i)
            self.grid_prices.append(buy_price)
        
        # 生成卖出网格（高于中心价格）
        for i in range(1, self.grid_levels + 1):
            sell_price = self.center_price * (1 + self.grid_size * i)
            self.grid_prices.append(sell_price)
        
        self.grid_prices.sort()
        strategy_logger.info(f"生成网格价格: {len(self.grid_prices)}个价格点")
    
    async def on_tick(self, symbol: str, price: float, volume: float) -> Optional[TradingSignal]:
        """处理价格tick数据"""
        if not self.is_initialized or self.status != StrategyStatus.RUNNING:
            return None
        
        self.last_prices[symbol] = price
        
        # 检查是否触发网格交易
        return await self._check_grid_triggers(symbol, price)
    
    async def on_bar(self, symbol: str, timeframe: str, bar_data: Dict[str, float]) -> Optional[TradingSignal]:
        """处理K线数据"""
        if not self.is_initialized or self.status != StrategyStatus.RUNNING:
            return None
        
        close_price = bar_data.get('close', 0.0)
        if close_price > 0:
            return await self.on_tick(symbol, close_price, bar_data.get('volume', 0.0))
        
        return None
    
    async def _check_grid_triggers(self, symbol: str, current_price: float) -> Optional[TradingSignal]:
        """检查网格触发条件"""
        try:
            # 找到最接近当前价格的网格线
            closest_grid_price = min(self.grid_prices, key=lambda x: abs(x - current_price))
            price_diff = abs(current_price - closest_grid_price) / closest_grid_price
            
            # 如果价格接近网格线（误差在0.1%以内）
            if price_diff < 0.001:
                if current_price < self.center_price:
                    # 低于中心价格，生成买入信号
                    return await self._generate_buy_signal(symbol, current_price)
                else:
                    # 高于中心价格，生成卖出信号
                    return await self._generate_sell_signal(symbol, current_price)
            
            return None
            
        except Exception as e:
            strategy_logger.error(f"检查网格触发失败: {str(e)}")
            return None
    
    async def _generate_buy_signal(self, symbol: str, price: float) -> Optional[TradingSignal]:
        """生成买入信号"""
        try:
            # 检查是否已经在该价格有订单
            if price in self.buy_orders:
                return None
            
            # 计算买入数量
            amount = self._calculate_order_amount(price, True)
            
            signal = TradingSignal(
                signal_type=SignalType.BUY,
                symbol=symbol,
                price=price,
                amount=amount,
                confidence=0.8,
                reason=f"网格买入信号，价格={price:.2f}",
                timestamp=datetime.now(),
                metadata={
                    'strategy': 'grid',
                    'grid_level': self._get_grid_level(price),
                    'center_price': self.center_price
                }
            )
            
            self.add_signal(signal)
            return signal
            
        except Exception as e:
            strategy_logger.error(f"生成买入信号失败: {str(e)}")
            return None
    
    async def _generate_sell_signal(self, symbol: str, price: float) -> Optional[TradingSignal]:
        """生成卖出信号"""
        try:
            # 检查是否已经在该价格有订单
            if price in self.sell_orders:
                return None
            
            # 检查是否有持仓可以卖出
            position = self.get_position(symbol)
            if position <= 0:
                return None
            
            # 计算卖出数量
            amount = self._calculate_order_amount(price, False)
            amount = min(amount, position)  # 不能超过持仓
            
            signal = TradingSignal(
                signal_type=SignalType.SELL,
                symbol=symbol,
                price=price,
                amount=amount,
                confidence=0.8,
                reason=f"网格卖出信号，价格={price:.2f}",
                timestamp=datetime.now(),
                metadata={
                    'strategy': 'grid',
                    'grid_level': self._get_grid_level(price),
                    'center_price': self.center_price
                }
            )
            
            self.add_signal(signal)
            return signal
            
        except Exception as e:
            strategy_logger.error(f"生成卖出信号失败: {str(e)}")
            return None
    
    def _calculate_order_amount(self, price: float, is_buy: bool) -> float:
        """计算订单数量"""
        # 基础数量
        base_quantity = self.base_amount / price
        
        # 根据距离中心价格的远近调整数量
        distance_ratio = abs(price - self.center_price) / self.center_price
        
        if is_buy:
            # 买入时，价格越低，数量越大
            multiplier = 1 + distance_ratio
        else:
            # 卖出时，价格越高，数量越大
            multiplier = 1 + distance_ratio
        
        return base_quantity * multiplier
    
    def _get_grid_level(self, price: float) -> int:
        """获取网格层级"""
        if price < self.center_price:
            # 买入网格
            return int((self.center_price - price) / (self.center_price * self.grid_size))
        else:
            # 卖出网格
            return int((price - self.center_price) / (self.center_price * self.grid_size))
    
    async def on_order_filled(self, order_id: str, fill_data: Dict[str, Any]) -> None:
        """处理订单成交"""
        try:
            symbol = fill_data.get('symbol')
            side = fill_data.get('side')
            price = fill_data.get('price', 0.0)
            amount = fill_data.get('amount', 0.0)
            
            if side == 'buy':
                # 买入成交，更新持仓
                current_position = self.get_position(symbol)
                self.update_position(symbol, current_position + amount)
                
                # 移除买入订单记录
                if price in self.buy_orders and self.buy_orders[price] == order_id:
                    del self.buy_orders[price]
                
                strategy_logger.info(f"网格买入成交: {amount} @ {price}")
                
            elif side == 'sell':
                # 卖出成交，更新持仓
                current_position = self.get_position(symbol)
                self.update_position(symbol, current_position - amount)
                
                # 移除卖出订单记录
                if price in self.sell_orders and self.sell_orders[price] == order_id:
                    del self.sell_orders[price]
                
                # 计算盈亏（简化计算）
                pnl = amount * (price - self.center_price)
                self.update_performance(pnl)
                
                strategy_logger.info(f"网格卖出成交: {amount} @ {price}, PnL: {pnl:.2f}")
            
        except Exception as e:
            strategy_logger.error(f"处理订单成交失败: {str(e)}")
    
    async def on_order_cancelled(self, order_id: str) -> None:
        """处理订单取消"""
        try:
            # 从订单记录中移除
            for price, oid in list(self.buy_orders.items()):
                if oid == order_id:
                    del self.buy_orders[price]
                    break
            
            for price, oid in list(self.sell_orders.items()):
                if oid == order_id:
                    del self.sell_orders[price]
                    break
            
            strategy_logger.info(f"网格订单已取消: {order_id}")
            
        except Exception as e:
            strategy_logger.error(f"处理订单取消失败: {str(e)}")
    
    async def cleanup(self) -> bool:
        """清理策略资源"""
        try:
            # 清理订单记录
            self.buy_orders.clear()
            self.sell_orders.clear()
            self.grid_prices.clear()
            
            strategy_logger.info("网格策略清理完成")
            return True
            
        except Exception as e:
            strategy_logger.error(f"网格策略清理失败: {str(e)}")
            return False
    
    def validate_config(self) -> bool:
        """验证配置"""
        if not super().validate_config():
            return False
        
        required_params = ['grid_size', 'grid_levels', 'base_amount']
        for param in required_params:
            if param not in self.config.parameters:
                strategy_logger.error(f"网格策略配置缺少参数: {param}")
                return False
        
        # 验证参数范围
        if self.config.parameters['grid_size'] <= 0 or self.config.parameters['grid_size'] > 0.1:
            strategy_logger.error("网格间距必须在0-10%之间")
            return False
        
        if self.config.parameters['grid_levels'] <= 0 or self.config.parameters['grid_levels'] > 50:
            strategy_logger.error("网格层数必须在1-50之间")
            return False
        
        return True
