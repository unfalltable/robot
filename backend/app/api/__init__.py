"""
API路由模块
"""
from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    strategies,
    trading,
    market_data,
    accounts,
    settings as settings_api,
    data
)
from app.api.v1 import monitoring

# 创建主路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["策略管理"])
api_router.include_router(trading.router, prefix="/trading", tags=["交易管理"])
api_router.include_router(market_data.router, prefix="/market", tags=["市场数据"])
api_router.include_router(data.router, prefix="/data", tags=["数据采集"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["账户管理"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["监控告警"])
api_router.include_router(settings_api.router, prefix="/settings", tags=["系统设置"])
