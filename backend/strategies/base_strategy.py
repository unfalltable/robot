"""
策略基础类
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.schemas.trading import OrderCreate
from app.core.logging import get_logger

strategy_logger = get_logger("strategy")


class StrategyStatus(Enum):
    """策略状态"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"


@dataclass
class TradingSignal:
    """交易信号"""
    signal_type: SignalType
    symbol: str
    price: float
    amount: float
    confidence: float  # 信号置信度 0-1
    reason: str  # 信号原因
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class StrategyConfig:
    """策略配置"""
    name: str
    description: str
    parameters: Dict[str, Any]
    risk_limits: Dict[str, float]
    symbols: List[str]
    timeframes: List[str]


@dataclass
class StrategyPerformance:
    """策略性能指标"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    start_time: datetime
    end_time: Optional[datetime] = None


class BaseStrategy(ABC):
    """策略基础类"""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.status = StrategyStatus.STOPPED
        self.signals: List[TradingSignal] = []
        self.performance = StrategyPerformance(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            total_pnl=0.0,
            win_rate=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            start_time=datetime.now()
        )
        self.positions: Dict[str, float] = {}  # symbol -> position_size
        self.last_prices: Dict[str, float] = {}  # symbol -> last_price
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化策略"""
        pass
    
    @abstractmethod
    async def on_tick(self, symbol: str, price: float, volume: float) -> Optional[TradingSignal]:
        """处理价格tick数据"""
        pass
    
    @abstractmethod
    async def on_bar(self, symbol: str, timeframe: str, bar_data: Dict[str, float]) -> Optional[TradingSignal]:
        """处理K线数据"""
        pass
    
    @abstractmethod
    async def on_order_filled(self, order_id: str, fill_data: Dict[str, Any]) -> None:
        """处理订单成交"""
        pass
    
    @abstractmethod
    async def on_order_cancelled(self, order_id: str) -> None:
        """处理订单取消"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> bool:
        """清理策略资源"""
        pass
    
    async def start(self) -> bool:
        """启动策略"""
        try:
            if await self.initialize():
                self.status = StrategyStatus.RUNNING
                self.performance.start_time = datetime.now()
                strategy_logger.info(f"策略 {self.config.name} 启动成功")
                return True
            else:
                self.status = StrategyStatus.ERROR
                strategy_logger.error(f"策略 {self.config.name} 初始化失败")
                return False
        except Exception as e:
            self.status = StrategyStatus.ERROR
            strategy_logger.error(f"策略 {self.config.name} 启动失败: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """停止策略"""
        try:
            if await self.cleanup():
                self.status = StrategyStatus.STOPPED
                self.performance.end_time = datetime.now()
                strategy_logger.info(f"策略 {self.config.name} 停止成功")
                return True
            else:
                strategy_logger.error(f"策略 {self.config.name} 清理失败")
                return False
        except Exception as e:
            self.status = StrategyStatus.ERROR
            strategy_logger.error(f"策略 {self.config.name} 停止失败: {str(e)}")
            return False
    
    async def pause(self) -> bool:
        """暂停策略"""
        if self.status == StrategyStatus.RUNNING:
            self.status = StrategyStatus.PAUSED
            strategy_logger.info(f"策略 {self.config.name} 已暂停")
            return True
        return False
    
    async def resume(self) -> bool:
        """恢复策略"""
        if self.status == StrategyStatus.PAUSED:
            self.status = StrategyStatus.RUNNING
            strategy_logger.info(f"策略 {self.config.name} 已恢复")
            return True
        return False
    
    def add_signal(self, signal: TradingSignal) -> None:
        """添加交易信号"""
        self.signals.append(signal)
        strategy_logger.info(
            f"策略 {self.config.name} 生成信号: {signal.signal_type.value} "
            f"{signal.symbol} @ {signal.price}, 置信度: {signal.confidence:.2f}"
        )
    
    def update_position(self, symbol: str, size: float) -> None:
        """更新持仓"""
        self.positions[symbol] = size
    
    def get_position(self, symbol: str) -> float:
        """获取持仓"""
        return self.positions.get(symbol, 0.0)
    
    def update_performance(self, trade_pnl: float) -> None:
        """更新性能指标"""
        self.performance.total_trades += 1
        self.performance.total_pnl += trade_pnl
        
        if trade_pnl > 0:
            self.performance.winning_trades += 1
        else:
            self.performance.losing_trades += 1
        
        # 计算胜率
        if self.performance.total_trades > 0:
            self.performance.win_rate = self.performance.winning_trades / self.performance.total_trades
    
    def get_status(self) -> Dict[str, Any]:
        """获取策略状态"""
        return {
            'name': self.config.name,
            'status': self.status.value,
            'performance': {
                'total_trades': self.performance.total_trades,
                'win_rate': self.performance.win_rate,
                'total_pnl': self.performance.total_pnl,
                'max_drawdown': self.performance.max_drawdown
            },
            'positions': self.positions,
            'signals_count': len(self.signals)
        }
    
    def validate_config(self) -> bool:
        """验证配置"""
        required_params = ['max_position_size', 'stop_loss', 'take_profit']
        for param in required_params:
            if param not in self.config.parameters:
                strategy_logger.error(f"策略配置缺少必要参数: {param}")
                return False
        return True
