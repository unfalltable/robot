"""
交易管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import trading_logger
from app.models.trading import Order, Position, Trade
from app.schemas.trading import (
    OrderCreate, OrderResponse, OrderUpdate,
    PositionResponse, TradeResponse,
    OrderStatus, OrderType, OrderSide
)
from app.services.trading_service import TradingService

router = APIRouter()


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """创建订单"""
    try:
        trading_service = TradingService(db)
        order = await trading_service.create_order(order_data)
        trading_logger.info(f"订单创建成功: {order.id}", extra={"TRADING": True})
        return order
    except Exception as e:
        trading_logger.error(f"创建订单失败: {str(e)}", extra={"TRADING": True})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    symbol: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取订单列表"""
    trading_service = TradingService(db)
    orders = await trading_service.get_orders(
        symbol=symbol,
        status=status,
        limit=limit,
        offset=offset
    )
    return orders


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """获取单个订单详情"""
    trading_service = TradingService(db)
    order = await trading_service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    return order


@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """更新订单"""
    try:
        trading_service = TradingService(db)
        order = await trading_service.update_order(order_id, order_update)
        trading_logger.info(f"订单更新成功: {order_id}", extra={"TRADING": True})
        return order
    except Exception as e:
        trading_logger.error(f"更新订单失败: {str(e)}", extra={"TRADING": True})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新订单失败: {str(e)}"
        )


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """取消订单"""
    try:
        trading_service = TradingService(db)
        result = await trading_service.cancel_order(order_id)
        trading_logger.info(f"订单取消成功: {order_id}", extra={"TRADING": True})
        return {"message": "订单取消成功", "order_id": order_id}
    except Exception as e:
        trading_logger.error(f"取消订单失败: {str(e)}", extra={"TRADING": True})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"取消订单失败: {str(e)}"
        )


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取持仓列表"""
    trading_service = TradingService(db)
    positions = await trading_service.get_positions(symbol=symbol)
    return positions


@router.get("/positions/{symbol}", response_model=PositionResponse)
async def get_position(
    symbol: str,
    db: Session = Depends(get_db)
):
    """获取特定交易对的持仓"""
    trading_service = TradingService(db)
    position = await trading_service.get_position(symbol)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="持仓不存在"
        )
    return position


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    symbol: Optional[str] = None,
    order_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取交易记录"""
    trading_service = TradingService(db)
    trades = await trading_service.get_trades(
        symbol=symbol,
        order_id=order_id,
        limit=limit,
        offset=offset
    )
    return trades


@router.post("/orders/batch", response_model=List[OrderResponse])
async def create_batch_orders(
    orders_data: List[OrderCreate],
    db: Session = Depends(get_db)
):
    """批量创建订单"""
    try:
        trading_service = TradingService(db)
        orders = await trading_service.create_batch_orders(orders_data)
        trading_logger.info(f"批量订单创建成功: {len(orders)}个", extra={"TRADING": True})
        return orders
    except Exception as e:
        trading_logger.error(f"批量创建订单失败: {str(e)}", extra={"TRADING": True})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"批量创建订单失败: {str(e)}"
        )


@router.delete("/orders/batch")
async def cancel_all_orders(
    symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """批量取消订单"""
    try:
        trading_service = TradingService(db)
        count = await trading_service.cancel_all_orders(symbol=symbol)
        trading_logger.info(f"批量取消订单成功: {count}个", extra={"TRADING": True})
        return {"message": f"成功取消{count}个订单"}
    except Exception as e:
        trading_logger.error(f"批量取消订单失败: {str(e)}", extra={"TRADING": True})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"批量取消订单失败: {str(e)}"
        )
