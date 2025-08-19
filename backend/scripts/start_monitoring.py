#!/usr/bin/env python3
"""
启动监控系统脚本
"""
import asyncio
import logging
import signal
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings, MonitoringConfig
from app.core.logging import setup_logging
from app.services.monitoring_service import SystemMonitor, ApplicationMonitor, AlertEngine
from app.services.notification_service import NotificationService
from app.services.health_service import HealthChecker


class MonitoringSystem:
    """监控系统管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = MonitoringConfig()
        
        # 初始化服务
        self.notification_service = self._init_notification_service()
        self.system_monitor = SystemMonitor()
        self.app_monitor = ApplicationMonitor()
        self.alert_engine = AlertEngine(self.notification_service)
        self.health_checker = HealthChecker()
        
        # 运行状态
        self.is_running = False
        self.tasks = []
    
    def _init_notification_service(self) -> NotificationService:
        """初始化通知服务"""
        notification_config = {}
        
        # 邮件配置
        if self.config.EMAIL_ENABLED:
            notification_config['email'] = {
                'enabled': True,
                'smtp_server': self.config.EMAIL_SMTP_SERVER,
                'smtp_port': self.config.EMAIL_SMTP_PORT,
                'username': self.config.EMAIL_USERNAME,
                'password': self.config.EMAIL_PASSWORD,
                'from_email': self.config.EMAIL_FROM,
                'default_recipients': self.config.EMAIL_TO
            }
        
        # Slack配置
        if self.config.SLACK_ENABLED:
            notification_config['slack'] = {
                'enabled': True,
                'webhook_url': self.config.SLACK_WEBHOOK_URL,
                'channel': self.config.SLACK_CHANNEL
            }
        
        # Telegram配置
        if self.config.TELEGRAM_ENABLED:
            notification_config['telegram'] = {
                'enabled': True,
                'bot_token': self.config.TELEGRAM_BOT_TOKEN,
                'chat_id': self.config.TELEGRAM_CHAT_ID
            }
        
        # Webhook配置
        if self.config.WEBHOOK_ENABLED:
            notification_config['webhook'] = {
                'enabled': True,
                'url': self.config.WEBHOOK_URL
            }
        
        return NotificationService(notification_config)
    
    async def start(self):
        """启动监控系统"""
        if self.is_running:
            self.logger.warning("监控系统已在运行")
            return
        
        self.logger.info("启动监控系统...")
        
        try:
            # 启动各个监控服务
            await self.system_monitor.start()
            await self.alert_engine.start()
            
            # 启动定期任务
            self.tasks = [
                asyncio.create_task(self._periodic_health_check()),
                asyncio.create_task(self._periodic_metrics_collection()),
                asyncio.create_task(self._periodic_cleanup())
            ]
            
            self.is_running = True
            self.logger.info("监控系统启动成功")
            
            # 发送启动通知
            await self.notification_service.send_system_notification(
                event_type="system_start",
                message="监控系统已启动",
                severity="info"
            )
            
        except Exception as e:
            self.logger.error(f"启动监控系统失败: {str(e)}")
            await self.stop()
            raise
    
    async def stop(self):
        """停止监控系统"""
        if not self.is_running:
            return
        
        self.logger.info("停止监控系统...")
        
        try:
            # 停止定期任务
            for task in self.tasks:
                task.cancel()
            
            # 等待任务完成
            if self.tasks:
                await asyncio.gather(*self.tasks, return_exceptions=True)
            
            # 停止监控服务
            await self.system_monitor.stop()
            await self.alert_engine.stop()
            
            self.is_running = False
            self.logger.info("监控系统已停止")
            
            # 发送停止通知
            await self.notification_service.send_system_notification(
                event_type="system_stop",
                message="监控系统已停止",
                severity="warning"
            )
            
        except Exception as e:
            self.logger.error(f"停止监控系统失败: {str(e)}")
    
    async def _periodic_health_check(self):
        """定期健康检查"""
        while self.is_running:
            try:
                health_status = await self.health_checker.check_overall_health()
                
                # 如果健康状态不佳，发送通知
                if health_status['status'] in ['warning', 'critical']:
                    message = f"系统健康检查警告: {health_status['status']}\n"
                    message += f"问题数量: 严重 {health_status['summary']['critical']}, 警告 {health_status['summary']['warning']}"
                    
                    await self.notification_service.send_system_notification(
                        event_type="health_check",
                        message=message,
                        severity=health_status['status']
                    )
                
                await asyncio.sleep(self.config.HEALTH_CHECK_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"健康检查失败: {str(e)}")
                await asyncio.sleep(60)
    
    async def _periodic_metrics_collection(self):
        """定期指标收集"""
        while self.is_running:
            try:
                # 收集应用指标
                await self.app_monitor.collect_application_metrics()
                
                await asyncio.sleep(self.config.METRICS_COLLECTION_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"指标收集失败: {str(e)}")
                await asyncio.sleep(60)
    
    async def _periodic_cleanup(self):
        """定期清理"""
        while self.is_running:
            try:
                # 每天执行一次清理
                await asyncio.sleep(24 * 60 * 60)
                
                # 这里可以添加清理逻辑
                self.logger.info("执行定期清理任务")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"定期清理失败: {str(e)}")
    
    async def get_status(self) -> dict:
        """获取监控系统状态"""
        return {
            'is_running': self.is_running,
            'system_monitor_running': self.system_monitor.is_running,
            'alert_engine_running': self.alert_engine.is_running,
            'notification_channels': self.notification_service.get_channels(),
            'uptime_seconds': self.app_monitor.get_uptime()
        }


async def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 创建监控系统
    monitoring_system = MonitoringSystem()
    
    # 信号处理
    def signal_handler(signum, frame):
        logger.info(f"接收到信号 {signum}，准备停止...")
        asyncio.create_task(monitoring_system.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动监控系统
        await monitoring_system.start()
        
        # 保持运行
        while monitoring_system.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("接收到中断信号")
    except Exception as e:
        logger.error(f"监控系统运行错误: {str(e)}")
    finally:
        await monitoring_system.stop()


if __name__ == "__main__":
    asyncio.run(main())
