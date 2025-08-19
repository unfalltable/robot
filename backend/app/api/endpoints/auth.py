"""
认证API端点
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    """用户登录"""
    return {"message": "登录功能待实现"}

@router.post("/logout")
async def logout():
    """用户登出"""
    return {"message": "登出功能待实现"}

@router.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    return {"message": "获取用户信息功能待实现"}
