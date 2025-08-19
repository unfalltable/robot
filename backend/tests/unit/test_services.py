"""
服务层单元测试
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.services.monitoring_service import SystemMonitor, ApplicationMonitor, AlertEngine
from app.services.notification_service import NotificationService, EmailChannel, SlackChannel
from app.services.health_service import HealthChecker
from app.models.system_data import AlertRule, Alert


@pytest.mark.unit
class TestSystemMonitor:
    """系统监控器测试"""
    
    def test_system_monitor_initialization(self):
        """测试系统监控器初始化"""
        monitor = SystemMonitor()
        assert monitor.is_running is False
        assert monitor.monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_get_current_metrics(self):
        """测试获取当前指标"""
        monitor = SystemMonitor()
        
        with patch('psutil.cpu_percent', return_value=75.5), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            # 模拟内存和磁盘信息
            mock_memory.return_value = Mock(percent=60.2)
            mock_disk.return_value = Mock(percent=45.8)
            
            metrics = await monitor.get_current_metrics()
            
            assert 'cpu_usage' in metrics
            assert 'memory_usage' in metrics
            assert 'disk_usage' in metrics
            assert 'timestamp' in metrics
            assert metrics['cpu_usage'] == 75.5
            assert metrics['memory_usage'] == 60.2
            assert metrics['disk_usage'] == 45.8
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self):
        """测试启动和停止监控"""
        monitor = SystemMonitor()
        
        # 启动监控
        await monitor.start()
        assert monitor.is_running is True
        assert monitor.monitoring_task is not None
        
        # 停止监控
        await monitor.stop()
        assert monitor.is_running is False


@pytest.mark.unit
class TestApplicationMonitor:
    """应用监控器测试"""
    
    def test_application_monitor_initialization(self):
        """测试应用监控器初始化"""
        monitor = ApplicationMonitor()
        assert monitor.metrics_cache == {}
        assert monitor.start_time > 0
    
    def test_record_api_request(self):
        """测试记录API请求"""
        monitor = ApplicationMonitor()
        
        # 记录成功请求
        monitor.record_api_request(True, 150.5)
        
        assert 'api_requests' in monitor.metrics_cache
        cache = monitor.metrics_cache['api_requests']
        assert cache['total'] == 1
        assert cache['success'] == 1
        assert cache['error'] == 0
        assert 150.5 in cache['response_times']
        
        # 记录失败请求
        monitor.record_api_request(False, 2500.0)
        
        assert cache['total'] == 2
        assert cache['success'] == 1
        assert cache['error'] == 1
        assert 2500.0 in cache['response_times']
    
    def test_record_websocket_event(self):
        """测试记录WebSocket事件"""
        monitor = ApplicationMonitor()
        
        monitor.record_websocket_event('connections')
        monitor.record_websocket_event('messages_sent')
        
        assert 'websocket' in monitor.metrics_cache
        cache = monitor.metrics_cache['websocket']
        assert cache['connections'] == 1
        assert cache['messages_sent'] == 1
    
    def test_record_database_query(self):
        """测试记录数据库查询"""
        monitor = ApplicationMonitor()
        
        # 记录正常查询
        monitor.record_database_query(250.0, False)
        
        assert 'database' in monitor.metrics_cache
        cache = monitor.metrics_cache['database']
        assert cache['queries_total'] == 1
        assert cache['queries_slow'] == 0
        assert 250.0 in cache['query_times']
        
        # 记录慢查询
        monitor.record_database_query(1500.0, True)
        
        assert cache['queries_total'] == 2
        assert cache['queries_slow'] == 1
        assert 1500.0 in cache['query_times']
    
    def test_calculate_percentile(self):
        """测试百分位数计算"""
        monitor = ApplicationMonitor()
        
        values = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        
        p50 = monitor._calculate_percentile(values, 50)
        p95 = monitor._calculate_percentile(values, 95)
        p99 = monitor._calculate_percentile(values, 99)
        
        assert p50 == 500  # 中位数
        assert p95 == 950  # 95%分位数
        assert p99 == 990  # 99%分位数
    
    def test_get_uptime(self):
        """测试获取运行时间"""
        monitor = ApplicationMonitor()
        uptime = monitor.get_uptime()
        
        assert uptime >= 0
        assert isinstance(uptime, float)


@pytest.mark.unit
class TestAlertEngine:
    """告警引擎测试"""
    
    def test_alert_engine_initialization(self):
        """测试告警引擎初始化"""
        notification_service = Mock()
        engine = AlertEngine(notification_service)
        
        assert engine.notification_service == notification_service
        assert engine.is_running is False
        assert engine.alert_task is None
        assert engine.alert_cache == {}
    
    def test_evaluate_condition(self):
        """测试条件评估"""
        engine = AlertEngine()
        
        # 测试各种操作符
        assert engine._evaluate_condition(85.0, '>', 80.0) is True
        assert engine._evaluate_condition(75.0, '>', 80.0) is False
        assert engine._evaluate_condition(75.0, '<', 80.0) is True
        assert engine._evaluate_condition(85.0, '<', 80.0) is False
        assert engine._evaluate_condition(80.0, '>=', 80.0) is True
        assert engine._evaluate_condition(80.0, '<=', 80.0) is True
        assert engine._evaluate_condition(80.0, '==', 80.0) is True
        assert engine._evaluate_condition(80.0, '!=', 85.0) is True
    
    def test_is_in_cooldown(self):
        """测试冷却时间检查"""
        engine = AlertEngine()
        
        # 创建模拟告警规则
        rule = Mock()
        rule.id = 1
        rule.cooldown_minutes = 60
        
        # 没有缓存记录，不在冷却期
        assert engine._is_in_cooldown(rule) is False
        
        # 添加缓存记录（刚触发）
        engine.alert_cache[rule.id] = datetime.utcnow()
        assert engine._is_in_cooldown(rule) is True
        
        # 添加过期的缓存记录
        engine.alert_cache[rule.id] = datetime.utcnow() - timedelta(hours=2)
        assert engine._is_in_cooldown(rule) is False
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self):
        """测试解决告警"""
        engine = AlertEngine()
        
        with patch('app.core.database.get_async_session') as mock_session:
            # 模拟数据库会话
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db
            
            # 模拟查询结果
            mock_alert = Mock()
            mock_alert.status = 'active'
            mock_db.execute.return_value.scalar_one_or_none.return_value = mock_alert
            
            # 解决告警
            result = await engine.resolve_alert(1, "admin", "问题已修复")
            
            assert result is True
            assert mock_alert.status == 'resolved'
            assert mock_alert.resolved_by == "admin"
            assert mock_alert.resolution_notes == "问题已修复"


@pytest.mark.unit
class TestNotificationService:
    """通知服务测试"""
    
    def test_notification_service_initialization(self):
        """测试通知服务初始化"""
        service = NotificationService()
        assert service.channels == {}
        
        # 使用配置初始化
        config = {
            'email': {
                'enabled': True,
                'smtp_server': 'localhost',
                'smtp_port': 587
            }
        }
        service = NotificationService(config)
        assert 'email' in service.channels
    
    @pytest.mark.asyncio
    async def test_send_notification(self):
        """测试发送通知"""
        service = NotificationService()
        
        # 添加模拟通知渠道
        mock_channel = AsyncMock()
        mock_channel.send.return_value = True
        service.channels['test'] = mock_channel
        
        # 发送通知
        results = await service.send_notification(
            message="测试消息",
            title="测试标题",
            channels=['test']
        )
        
        assert results['test'] is True
        mock_channel.send.assert_called_once_with(
            message="测试消息",
            title="测试标题"
        )
    
    def test_add_remove_channel(self):
        """测试添加和移除通知渠道"""
        service = NotificationService()
        mock_channel = Mock()
        
        # 添加渠道
        service.add_channel('test', mock_channel)
        assert 'test' in service.channels
        assert service.channels['test'] == mock_channel
        
        # 移除渠道
        service.remove_channel('test')
        assert 'test' not in service.channels
    
    def test_get_channels(self):
        """测试获取通知渠道"""
        service = NotificationService()
        service.channels = {'email': Mock(), 'slack': Mock()}
        
        channels = service.get_channels()
        assert 'email' in channels
        assert 'slack' in channels
        assert len(channels) == 2


@pytest.mark.unit
class TestEmailChannel:
    """邮件通知渠道测试"""
    
    def test_email_channel_initialization(self):
        """测试邮件渠道初始化"""
        config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'test@gmail.com',
            'password': 'password',
            'from_email': 'robot@example.com'
        }
        
        channel = EmailChannel(config)
        assert channel.smtp_server == 'smtp.gmail.com'
        assert channel.smtp_port == 587
        assert channel.username == 'test@gmail.com'
        assert channel.from_email == 'robot@example.com'
    
    @pytest.mark.asyncio
    async def test_send_email_no_recipients(self):
        """测试发送邮件（无接收者）"""
        config = {'smtp_server': 'localhost'}
        channel = EmailChannel(config)
        
        result = await channel.send("测试消息", "测试标题")
        assert result is False


@pytest.mark.unit
class TestSlackChannel:
    """Slack通知渠道测试"""
    
    def test_slack_channel_initialization(self):
        """测试Slack渠道初始化"""
        config = {
            'webhook_url': 'https://hooks.slack.com/test',
            'channel': '#alerts',
            'username': 'Robot'
        }
        
        channel = SlackChannel(config)
        assert channel.webhook_url == 'https://hooks.slack.com/test'
        assert channel.channel == '#alerts'
        assert channel.username == 'Robot'
    
    def test_get_color_by_severity(self):
        """测试根据严重程度获取颜色"""
        channel = SlackChannel({})
        
        assert channel._get_color_by_severity('low') == 'good'
        assert channel._get_color_by_severity('medium') == 'warning'
        assert channel._get_color_by_severity('high') == 'danger'
        assert channel._get_color_by_severity('critical') == 'danger'
        assert channel._get_color_by_severity('unknown') == 'good'


@pytest.mark.unit
class TestHealthChecker:
    """健康检查器测试"""
    
    def test_health_checker_initialization(self):
        """测试健康检查器初始化"""
        checker = HealthChecker()
        assert checker.logger is not None
        assert checker.settings is not None
    
    @pytest.mark.asyncio
    async def test_check_system_health(self):
        """测试系统健康检查"""
        checker = HealthChecker()
        
        with patch('psutil.cpu_percent', return_value=75.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value = Mock(percent=60.0)
            mock_disk.return_value = Mock(percent=45.0)
            
            result = await checker.check_system_health()
            
            assert result['status'] == 'healthy'
            assert result['cpu_usage'] == 75.0
            assert result['memory_usage'] == 60.0
            assert result['disk_usage'] == 45.0
            assert result['issues'] == []
    
    @pytest.mark.asyncio
    async def test_check_system_health_warning(self):
        """测试系统健康检查（警告状态）"""
        checker = HealthChecker()
        
        with patch('psutil.cpu_percent', return_value=85.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value = Mock(percent=90.0)
            mock_disk.return_value = Mock(percent=95.0)
            
            result = await checker.check_system_health()
            
            assert result['status'] == 'critical'  # 磁盘使用率95%为严重
            assert len(result['issues']) > 0
            assert any('CPU使用率过高' in issue for issue in result['issues'])
            assert any('内存使用率过高' in issue for issue in result['issues'])
            assert any('磁盘使用率过高' in issue for issue in result['issues'])
