"""
日志配置模块
"""
import sys
import os
from loguru import logger
from app.core.config import settings


def setup_logging():
    """设置日志配置"""
    
    # 移除默认处理器
    logger.remove()
    
    # 确保日志目录存在
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True
    )
    
    # 文件输出
    logger.add(
        settings.LOG_FILE,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        encoding="utf-8"
    )
    
    # 错误日志单独文件
    error_log_file = settings.LOG_FILE.replace('.log', '_error.log')
    logger.add(
        error_log_file,
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        encoding="utf-8"
    )
    
    # 交易日志单独文件
    trading_log_file = settings.LOG_FILE.replace('.log', '_trading.log')
    logger.add(
        trading_log_file,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        filter=lambda record: "TRADING" in record["extra"],
        rotation="1 day",
        retention="90 days",
        compression="zip",
        encoding="utf-8"
    )


def get_logger(name: str):
    """获取指定名称的日志器"""
    return logger.bind(name=name)


# 创建不同类型的日志器
app_logger = get_logger("APP")
trading_logger = get_logger("TRADING")
strategy_logger = get_logger("STRATEGY")
exchange_logger = get_logger("EXCHANGE")
data_logger = get_logger("DATA")
