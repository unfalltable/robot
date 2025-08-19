"""
通知服务
"""
import asyncio
import aiohttp
import smtplib
import logging
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

from app.models.system_data import Alert
from app.core.config import Settings


class NotificationChannel:
    """通知渠道基类"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    async def send(self, message: str, title: str = None, **kwargs) -> bool:
        """发送通知"""
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    """邮件通知渠道"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("email", config)
        self.smtp_server = config.get('smtp_server', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.from_email = config.get('from_email')
        self.use_tls = config.get('use_tls', True)
    
    async def send(self, message: str, title: str = None, recipients: List[str] = None, **kwargs) -> bool:
        """发送邮件"""
        try:
            if not recipients:
                recipients = self.config.get('default_recipients', [])
            
            if not recipients:
                self.logger.warning("没有指定邮件接收者")
                return False
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = title or "系统通知"
            
            # 添加邮件内容
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg)
            
            self.logger.info(f"邮件发送成功: {title} -> {recipients}")
            return True
            
        except Exception as e:
            self.logger.error(f"邮件发送失败: {str(e)}")
            return False


class WebhookChannel(NotificationChannel):
    """Webhook通知渠道"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("webhook", config)
        self.url = config.get('url')
        self.method = config.get('method', 'POST')
        self.headers = config.get('headers', {})
        self.timeout = config.get('timeout', 30)
    
    async def send(self, message: str, title: str = None, **kwargs) -> bool:
        """发送Webhook"""
        try:
            if not self.url:
                self.logger.warning("Webhook URL未配置")
                return False
            
            # 构建请求数据
            data = {
                'title': title or "系统通知",
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'trading_robot',
                **kwargs
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    self.method,
                    self.url,
                    json=data,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status < 400:
                        self.logger.info(f"Webhook发送成功: {title}")
                        return True
                    else:
                        self.logger.error(f"Webhook发送失败: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Webhook发送失败: {str(e)}")
            return False


class SlackChannel(NotificationChannel):
    """Slack通知渠道"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("slack", config)
        self.webhook_url = config.get('webhook_url')
        self.channel = config.get('channel', '#general')
        self.username = config.get('username', 'Trading Robot')
        self.icon_emoji = config.get('icon_emoji', ':robot_face:')
    
    async def send(self, message: str, title: str = None, **kwargs) -> bool:
        """发送Slack消息"""
        try:
            if not self.webhook_url:
                self.logger.warning("Slack Webhook URL未配置")
                return False
            
            # 构建Slack消息
            slack_data = {
                'channel': self.channel,
                'username': self.username,
                'icon_emoji': self.icon_emoji,
                'text': title or "系统通知",
                'attachments': [
                    {
                        'color': self._get_color_by_severity(kwargs.get('severity', 'info')),
                        'text': message,
                        'ts': int(datetime.utcnow().timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=slack_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Slack消息发送成功: {title}")
                        return True
                    else:
                        self.logger.error(f"Slack消息发送失败: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Slack消息发送失败: {str(e)}")
            return False
    
    def _get_color_by_severity(self, severity: str) -> str:
        """根据严重程度获取颜色"""
        color_map = {
            'low': 'good',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'danger'
        }
        return color_map.get(severity, 'good')


class TelegramChannel(NotificationChannel):
    """Telegram通知渠道"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("telegram", config)
        self.bot_token = config.get('bot_token')
        self.chat_id = config.get('chat_id')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send(self, message: str, title: str = None, **kwargs) -> bool:
        """发送Telegram消息"""
        try:
            if not self.bot_token or not self.chat_id:
                self.logger.warning("Telegram配置不完整")
                return False
            
            # 构建消息
            text = f"*{title or '系统通知'}*\n\n{message}"
            
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/sendMessage",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Telegram消息发送成功: {title}")
                        return True
                    else:
                        self.logger.error(f"Telegram消息发送失败: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Telegram消息发送失败: {str(e)}")
            return False


class NotificationService:
    """通知服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.channels: Dict[str, NotificationChannel] = {}
        
        if config:
            self._initialize_channels(config)
    
    def _initialize_channels(self, config: Dict[str, Any]):
        """初始化通知渠道"""
        try:
            # 邮件渠道
            if 'email' in config and config['email'].get('enabled', False):
                self.channels['email'] = EmailChannel(config['email'])
            
            # Webhook渠道
            if 'webhook' in config and config['webhook'].get('enabled', False):
                self.channels['webhook'] = WebhookChannel(config['webhook'])
            
            # Slack渠道
            if 'slack' in config and config['slack'].get('enabled', False):
                self.channels['slack'] = SlackChannel(config['slack'])
            
            # Telegram渠道
            if 'telegram' in config and config['telegram'].get('enabled', False):
                self.channels['telegram'] = TelegramChannel(config['telegram'])
            
            self.logger.info(f"通知渠道初始化完成: {list(self.channels.keys())}")
            
        except Exception as e:
            self.logger.error(f"初始化通知渠道失败: {str(e)}")
    
    async def send_notification(
        self, 
        message: str, 
        title: str = None,
        channels: List[str] = None,
        **kwargs
    ) -> Dict[str, bool]:
        """发送通知"""
        if not channels:
            channels = list(self.channels.keys())
        
        results = {}
        
        for channel_name in channels:
            if channel_name in self.channels:
                try:
                    success = await self.channels[channel_name].send(
                        message=message,
                        title=title,
                        **kwargs
                    )
                    results[channel_name] = success
                except Exception as e:
                    self.logger.error(f"通知发送失败 {channel_name}: {str(e)}")
                    results[channel_name] = False
            else:
                self.logger.warning(f"未知的通知渠道: {channel_name}")
                results[channel_name] = False
        
        return results
    
    async def send_alert_notification(self, alert: Alert, channels: List[str]) -> Dict[str, bool]:
        """发送告警通知"""
        title = f"🚨 {alert.title}"
        message = f"""
告警详情:
- 告警名称: {alert.title}
- 严重程度: {alert.severity.upper()}
- 指标名称: {alert.metric_name}
- 当前值: {alert.metric_value}
- 阈值: {alert.threshold}
- 触发时间: {alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}
- 描述: {alert.message}
        """.strip()
        
        return await self.send_notification(
            message=message,
            title=title,
            channels=channels,
            severity=alert.severity,
            alert_id=alert.id
        )
    
    async def send_system_notification(
        self, 
        event_type: str, 
        message: str,
        severity: str = 'info'
    ) -> Dict[str, bool]:
        """发送系统通知"""
        title = f"📊 系统通知 - {event_type}"
        
        return await self.send_notification(
            message=message,
            title=title,
            severity=severity,
            event_type=event_type
        )
    
    def add_channel(self, name: str, channel: NotificationChannel):
        """添加通知渠道"""
        self.channels[name] = channel
        self.logger.info(f"添加通知渠道: {name}")
    
    def remove_channel(self, name: str):
        """移除通知渠道"""
        if name in self.channels:
            del self.channels[name]
            self.logger.info(f"移除通知渠道: {name}")
    
    def get_channels(self) -> List[str]:
        """获取可用的通知渠道"""
        return list(self.channels.keys())
    
    async def test_channel(self, channel_name: str) -> bool:
        """测试通知渠道"""
        if channel_name not in self.channels:
            return False
        
        try:
            return await self.channels[channel_name].send(
                message="这是一条测试消息",
                title="通知渠道测试"
            )
        except Exception as e:
            self.logger.error(f"测试通知渠道失败 {channel_name}: {str(e)}")
            return False
