"""
策略管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.trading import StrategyCreate, StrategyUpdate, StrategyResponse
from app.services.strategy_manager import StrategyManager

router = APIRouter()

def get_strategy_manager(db: Session = Depends(get_db)) -> StrategyManager:
    """获取策略管理器实例"""
    return StrategyManager(db)

@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """获取策略列表"""
    return strategy_manager.get_all_strategies()

@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy_data: StrategyCreate,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """创建策略"""
    return await strategy_manager.create_strategy(strategy_data)

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """获取策略详情"""
    strategies = strategy_manager.get_all_strategies()
    for strategy in strategies:
        if strategy.id == strategy_id:
            return strategy
    raise HTTPException(status_code=404, detail="策略不存在")

@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: str,
    update_data: StrategyUpdate,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """更新策略"""
    result = await strategy_manager.update_strategy(strategy_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="策略不存在")
    return result

@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """删除策略"""
    success = await strategy_manager.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="策略不存在")
    return {"message": "策略删除成功"}

@router.post("/{strategy_id}/start")
async def start_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """启动策略"""
    success = await strategy_manager.start_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=400, detail="策略启动失败")
    return {"message": "策略启动成功"}

@router.post("/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """停止策略"""
    success = await strategy_manager.stop_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=400, detail="策略停止失败")
    return {"message": "策略停止成功"}

@router.post("/{strategy_id}/pause")
async def pause_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """暂停策略"""
    success = await strategy_manager.pause_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=400, detail="策略暂停失败")
    return {"message": "策略暂停成功"}

@router.post("/{strategy_id}/resume")
async def resume_strategy(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """恢复策略"""
    success = await strategy_manager.resume_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=400, detail="策略恢复失败")
    return {"message": "策略恢复成功"}

@router.get("/{strategy_id}/status")
async def get_strategy_status(
    strategy_id: str,
    strategy_manager: StrategyManager = Depends(get_strategy_manager)
):
    """获取策略状态"""
    status = strategy_manager.get_strategy_status(strategy_id)
    if not status:
        raise HTTPException(status_code=404, detail="策略未运行或不存在")
    return status
