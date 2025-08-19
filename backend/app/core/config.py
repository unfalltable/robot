"""
应用配置模块
"""
from typing import Optional, List
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基本配置
    APP_NAME: str = "Trading Robot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # OKX API配置
    OKX_API_KEY: Optional[str] = None
    OKX_SECRET_KEY: Optional[str] = None
    OKX_PASSPHRASE: Optional[str] = None
    OKX_SANDBOX: bool = True
    OKX_BASE_URL: str = "https://www.okx.com"
    OKX_SANDBOX_URL: str = "https://www.okx.com"
    
    # 交易配置
    DEFAULT_QUOTE_CURRENCY: str = "USDT"
    MAX_POSITION_SIZE: float = 0.1  # 最大仓位比例
    DEFAULT_LEVERAGE: int = 1
    
    # 风险控制
    MAX_DAILY_LOSS: float = 0.05  # 最大日损失比例
    MAX_DRAWDOWN: float = 0.2     # 最大回撤比例
    STOP_LOSS_RATIO: float = 0.02 # 默认止损比例
    TAKE_PROFIT_RATIO: float = 0.04 # 默认止盈比例
    
    # 数据源配置
    DATA_UPDATE_INTERVAL: int = 1  # 数据更新间隔(秒)
    KLINE_LIMIT: int = 1000       # K线数据限制
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/trading_robot.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("DATABASE_URL is required")
        return v
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError("SECRET_KEY is required")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()


class ExchangeConfig:
    """交易所配置"""
    
    OKX_CONFIG = {
        "apiKey": settings.OKX_API_KEY,
        "secret": settings.OKX_SECRET_KEY,
        "password": settings.OKX_PASSPHRASE,
        "sandbox": settings.OKX_SANDBOX,
        "enableRateLimit": True,
        "options": {
            "defaultType": "spot",  # spot, margin, swap, future
        }
    }


class StrategyConfig:
    """策略配置"""
    
    # 默认策略参数
    DEFAULT_PARAMS = {
        "timeframe": "1m",
        "lookback_period": 20,
        "risk_per_trade": 0.01,
        "max_positions": 5,
    }
    
    # 策略类型
    STRATEGY_TYPES = [
        "grid_trading",      # 网格交易
        "dca",              # 定投策略
        "momentum",         # 动量策略
        "mean_reversion",   # 均值回归
        "arbitrage",        # 套利策略
        "custom",           # 自定义策略
    ]


class MonitoringConfig(BaseSettings):
    """监控配置"""

    # 健康检查配置
    HEALTH_CHECK_INTERVAL: int = 60  # 秒
    HEALTH_CHECK_TIMEOUT: int = 30   # 秒

    # 指标收集配置
    METRICS_COLLECTION_INTERVAL: int = 60  # 秒
    METRICS_RETENTION_DAYS: int = 30       # 天

    # 告警配置
    ALERT_CHECK_INTERVAL: int = 60         # 秒
    ALERT_COOLDOWN_MINUTES: int = 60       # 分钟

    # 通知配置
    NOTIFICATION_TIMEOUT: int = 30         # 秒
    NOTIFICATION_RETRY_ATTEMPTS: int = 3   # 次数

    # 系统阈值
    CPU_WARNING_THRESHOLD: float = 80.0    # %
    CPU_CRITICAL_THRESHOLD: float = 90.0   # %
    MEMORY_WARNING_THRESHOLD: float = 85.0 # %
    MEMORY_CRITICAL_THRESHOLD: float = 95.0 # %
    DISK_WARNING_THRESHOLD: float = 90.0   # %
    DISK_CRITICAL_THRESHOLD: float = 95.0  # %

    # API性能阈值
    API_RESPONSE_TIME_WARNING: float = 1000.0  # ms
    API_RESPONSE_TIME_CRITICAL: float = 5000.0 # ms
    API_ERROR_RATE_WARNING: float = 0.1        # 10%
    API_ERROR_RATE_CRITICAL: float = 0.2       # 20%

    # 数据库性能阈值
    DB_QUERY_TIME_WARNING: float = 500.0       # ms
    DB_QUERY_TIME_CRITICAL: float = 2000.0     # ms
    DB_CONNECTION_WARNING: int = 50             # 连接数
    DB_CONNECTION_CRITICAL: int = 80            # 连接数

    # 交易告警
    LARGE_LOSS_THRESHOLD: float = 0.02  # 大额亏损告警阈值
    UNUSUAL_VOLUME_MULTIPLIER: float = 3.0  # 异常交易量倍数

    # 通知渠道配置
    EMAIL_ENABLED: bool = False
    EMAIL_SMTP_SERVER: str = "localhost"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_TO: List[str] = []

    SLACK_ENABLED: bool = False
    SLACK_WEBHOOK_URL: str = ""
    SLACK_CHANNEL: str = "#alerts"

    TELEGRAM_ENABLED: bool = False
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    WEBHOOK_ENABLED: bool = False
    WEBHOOK_URL: str = ""

    class Config:
        env_file = ".env"
        env_prefix = "MONITORING_"
