"""
系统设置API端点
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_settings():
    """获取系统设置"""
    return {"message": "系统设置功能待实现"}

@router.put("/")
async def update_settings():
    """更新系统设置"""
    return {"message": "更新系统设置功能待实现"}

@router.get("/exchanges")
async def get_exchange_settings():
    """获取交易所设置"""
    return {"message": "交易所设置功能待实现"}

@router.put("/exchanges")
async def update_exchange_settings():
    """更新交易所设置"""
    return {"message": "更新交易所设置功能待实现"}
