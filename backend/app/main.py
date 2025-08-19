"""
主应用入口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.api import api_router
from app.core.database import init_db
from app.core.logging import setup_logging
from app.services.monitoring_service import SystemMonitor, ApplicationMonitor, AlertEngine
from app.services.notification_service import NotificationService
from app.middleware.monitoring_middleware import MonitoringMiddleware


# 全局监控实例
system_monitor = SystemMonitor()
app_monitor = ApplicationMonitor()
notification_service = NotificationService()
alert_engine = AlertEngine(notification_service)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    setup_logging()
    await init_db()

    # 启动监控服务
    await system_monitor.start()
    await alert_engine.start()

    yield

    # 关闭时执行
    await system_monitor.stop()
    await alert_engine.stop()


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="数字货币策略交易机器人API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
    )

    # 添加监控中间件
    app.add_middleware(MonitoringMiddleware, app_monitor=app_monitor)
    
    # 注册路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 健康检查端点
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}
    
    # 根路径
    @app.get("/")
    async def root():
        return {
            "message": "Trading Robot API",
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.DEBUG else "disabled"
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
