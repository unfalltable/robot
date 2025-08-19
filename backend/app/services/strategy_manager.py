"""
策略管理器
"""
import asyncio
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.trading import Strategy as StrategyModel, Account
from app.schemas.trading import StrategyCreate, StrategyUpdate, StrategyResponse
from app.core.logging import get_logger
from strategies.base_strategy import BaseStrategy, StrategyConfig, TradingSignal
from strategies.grid_strategy import GridStrategy

strategy_logger = get_logger("strategy")


class StrategyManager:
    """策略管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.running_strategies: Dict[str, BaseStrategy] = {}
        self.strategy_classes: Dict[str, Type[BaseStrategy]] = {
            'grid': GridStrategy,
            # 可以在这里添加更多策略类型
        }
        self.signal_queue: asyncio.Queue = asyncio.Queue()
    
    async def create_strategy(self, strategy_data: StrategyCreate) -> StrategyResponse:
        """创建策略"""
        try:
            # 验证策略类型
            if strategy_data.strategy_type not in self.strategy_classes:
                raise ValueError(f"不支持的策略类型: {strategy_data.strategy_type}")
            
            # 创建数据库记录
            db_strategy = StrategyModel(
                name=strategy_data.name,
                description=strategy_data.description,
                strategy_type=strategy_data.strategy_type,
                parameters=strategy_data.parameters,
                symbols=strategy_data.symbols,
                timeframes=strategy_data.timeframes,
                account_id=strategy_data.account_id,
                status="stopped",
                created_at=datetime.now()
            )
            
            self.db.add(db_strategy)
            self.db.commit()
            self.db.refresh(db_strategy)
            
            strategy_logger.info(f"策略创建成功: {db_strategy.name} (ID: {db_strategy.id})")
            
            return StrategyResponse(
                id=str(db_strategy.id),
                name=db_strategy.name,
                description=db_strategy.description,
                strategy_type=db_strategy.strategy_type,
                parameters=db_strategy.parameters,
                symbols=db_strategy.symbols,
                timeframes=db_strategy.timeframes,
                account_id=db_strategy.account_id,
                status=db_strategy.status,
                created_at=db_strategy.created_at,
                updated_at=db_strategy.updated_at
            )
            
        except Exception as e:
            strategy_logger.error(f"创建策略失败: {str(e)}")
            raise
    
    async def start_strategy(self, strategy_id: str) -> bool:
        """启动策略"""
        try:
            # 获取策略配置
            db_strategy = self.db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
            if not db_strategy:
                raise ValueError(f"策略不存在: {strategy_id}")
            
            if strategy_id in self.running_strategies:
                strategy_logger.warning(f"策略已在运行: {strategy_id}")
                return True
            
            # 创建策略配置
            config = StrategyConfig(
                name=db_strategy.name,
                description=db_strategy.description,
                parameters=db_strategy.parameters,
                risk_limits={},  # 从配置中获取
                symbols=db_strategy.symbols,
                timeframes=db_strategy.timeframes
            )
            
            # 创建策略实例
            strategy_class = self.strategy_classes[db_strategy.strategy_type]
            strategy_instance = strategy_class(config)
            
            # 启动策略
            if await strategy_instance.start():
                self.running_strategies[strategy_id] = strategy_instance
                
                # 更新数据库状态
                db_strategy.status = "running"
                db_strategy.updated_at = datetime.now()
                self.db.commit()
                
                strategy_logger.info(f"策略启动成功: {strategy_id}")
                return True
            else:
                strategy_logger.error(f"策略启动失败: {strategy_id}")
                return False
                
        except Exception as e:
            strategy_logger.error(f"启动策略失败: {str(e)}")
            return False
    
    async def stop_strategy(self, strategy_id: str) -> bool:
        """停止策略"""
        try:
            if strategy_id not in self.running_strategies:
                strategy_logger.warning(f"策略未在运行: {strategy_id}")
                return True
            
            strategy_instance = self.running_strategies[strategy_id]
            
            # 停止策略
            if await strategy_instance.stop():
                del self.running_strategies[strategy_id]
                
                # 更新数据库状态
                db_strategy = self.db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
                if db_strategy:
                    db_strategy.status = "stopped"
                    db_strategy.updated_at = datetime.now()
                    self.db.commit()
                
                strategy_logger.info(f"策略停止成功: {strategy_id}")
                return True
            else:
                strategy_logger.error(f"策略停止失败: {strategy_id}")
                return False
                
        except Exception as e:
            strategy_logger.error(f"停止策略失败: {str(e)}")
            return False
    
    async def pause_strategy(self, strategy_id: str) -> bool:
        """暂停策略"""
        try:
            if strategy_id not in self.running_strategies:
                return False
            
            strategy_instance = self.running_strategies[strategy_id]
            
            if await strategy_instance.pause():
                # 更新数据库状态
                db_strategy = self.db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
                if db_strategy:
                    db_strategy.status = "paused"
                    db_strategy.updated_at = datetime.now()
                    self.db.commit()
                
                return True
            return False
            
        except Exception as e:
            strategy_logger.error(f"暂停策略失败: {str(e)}")
            return False
    
    async def resume_strategy(self, strategy_id: str) -> bool:
        """恢复策略"""
        try:
            if strategy_id not in self.running_strategies:
                return False
            
            strategy_instance = self.running_strategies[strategy_id]
            
            if await strategy_instance.resume():
                # 更新数据库状态
                db_strategy = self.db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
                if db_strategy:
                    db_strategy.status = "running"
                    db_strategy.updated_at = datetime.now()
                    self.db.commit()
                
                return True
            return False
            
        except Exception as e:
            strategy_logger.error(f"恢复策略失败: {str(e)}")
            return False
    
    async def update_strategy(self, strategy_id: str, update_data: StrategyUpdate) -> Optional[StrategyResponse]:
        """更新策略"""
        try:
            db_strategy = self.db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
            if not db_strategy:
                return None
            
            # 如果策略正在运行，需要先停止
            if strategy_id in self.running_strategies:
                await self.stop_strategy(strategy_id)
            
            # 更新策略配置
            if update_data.name is not None:
                db_strategy.name = update_data.name
            if update_data.description is not None:
                db_strategy.description = update_data.description
            if update_data.parameters is not None:
                db_strategy.parameters = update_data.parameters
            if update_data.symbols is not None:
                db_strategy.symbols = update_data.symbols
            if update_data.timeframes is not None:
                db_strategy.timeframes = update_data.timeframes
            
            db_strategy.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(db_strategy)
            
            strategy_logger.info(f"策略更新成功: {strategy_id}")
            
            return StrategyResponse(
                id=str(db_strategy.id),
                name=db_strategy.name,
                description=db_strategy.description,
                strategy_type=db_strategy.strategy_type,
                parameters=db_strategy.parameters,
                symbols=db_strategy.symbols,
                timeframes=db_strategy.timeframes,
                account_id=db_strategy.account_id,
                status=db_strategy.status,
                created_at=db_strategy.created_at,
                updated_at=db_strategy.updated_at
            )
            
        except Exception as e:
            strategy_logger.error(f"更新策略失败: {str(e)}")
            raise
    
    async def delete_strategy(self, strategy_id: str) -> bool:
        """删除策略"""
        try:
            # 如果策略正在运行，先停止
            if strategy_id in self.running_strategies:
                await self.stop_strategy(strategy_id)
            
            # 删除数据库记录
            db_strategy = self.db.query(StrategyModel).filter(StrategyModel.id == strategy_id).first()
            if db_strategy:
                self.db.delete(db_strategy)
                self.db.commit()
                strategy_logger.info(f"策略删除成功: {strategy_id}")
                return True
            
            return False
            
        except Exception as e:
            strategy_logger.error(f"删除策略失败: {str(e)}")
            return False
    
    def get_strategy_status(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """获取策略状态"""
        if strategy_id in self.running_strategies:
            return self.running_strategies[strategy_id].get_status()
        return None
    
    def get_all_strategies(self) -> List[StrategyResponse]:
        """获取所有策略"""
        try:
            strategies = self.db.query(StrategyModel).all()
            return [
                StrategyResponse(
                    id=str(strategy.id),
                    name=strategy.name,
                    description=strategy.description,
                    strategy_type=strategy.strategy_type,
                    parameters=strategy.parameters,
                    symbols=strategy.symbols,
                    timeframes=strategy.timeframes,
                    account_id=strategy.account_id,
                    status=strategy.status,
                    created_at=strategy.created_at,
                    updated_at=strategy.updated_at
                )
                for strategy in strategies
            ]
        except Exception as e:
            strategy_logger.error(f"获取策略列表失败: {str(e)}")
            return []
    
    async def process_market_data(self, symbol: str, price: float, volume: float) -> None:
        """处理市场数据"""
        try:
            for strategy_id, strategy in self.running_strategies.items():
                if symbol in strategy.config.symbols:
                    signal = await strategy.on_tick(symbol, price, volume)
                    if signal:
                        await self.signal_queue.put((strategy_id, signal))
        except Exception as e:
            strategy_logger.error(f"处理市场数据失败: {str(e)}")
    
    async def get_next_signal(self) -> Optional[tuple]:
        """获取下一个交易信号"""
        try:
            return await asyncio.wait_for(self.signal_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return None
