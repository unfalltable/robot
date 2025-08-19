"""
API集成测试
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trading import Account, Strategy
from app.models.system_data import AlertRule, Alert
from app.repositories.base_repository import BaseRepository


@pytest.mark.integration
class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_endpoint(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/api/v1/monitoring/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
        assert "summary" in data
        
        # 检查摘要结构
        summary = data["summary"]
        assert "healthy" in summary
        assert "warning" in summary
        assert "critical" in summary
    
    def test_health_summary_endpoint(self, client: TestClient):
        """测试健康状态摘要端点"""
        response = client.get("/api/v1/monitoring/health/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "summary" in data


@pytest.mark.integration
class TestMonitoringAPI:
    """监控API测试"""
    
    def test_system_metrics_endpoint(self, client: TestClient):
        """测试系统指标端点"""
        response = client.get("/api/v1/monitoring/metrics/system")
        assert response.status_code == 200
        
        data = response.json()
        assert "current" in data
        assert "history" in data
        assert "period_hours" in data
        
        # 检查当前指标结构
        current = data["current"]
        assert "cpu_usage" in current
        assert "memory_usage" in current
        assert "disk_usage" in current
        assert "timestamp" in current
    
    def test_system_metrics_with_custom_hours(self, client: TestClient):
        """测试自定义时间范围的系统指标"""
        response = client.get("/api/v1/monitoring/metrics/system?hours=12")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_hours"] == 12
    
    def test_application_metrics_endpoint(self, client: TestClient):
        """测试应用指标端点"""
        response = client.get("/api/v1/monitoring/metrics/application")
        assert response.status_code == 200
        
        data = response.json()
        assert "current" in data
        assert "history" in data
        assert "period_hours" in data


@pytest.mark.integration
class TestAlertsAPI:
    """告警API测试"""
    
    async def test_get_alerts_empty(self, async_client: AsyncClient):
        """测试获取告警（空列表）"""
        response = await async_client.get("/api/v1/monitoring/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_create_alert_rule(self, async_client: AsyncClient, sample_alert_rule):
        """测试创建告警规则"""
        response = await async_client.post(
            "/api/v1/monitoring/alert-rules",
            json=sample_alert_rule
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "message" in data
        assert data["name"] == sample_alert_rule["name"]
    
    async def test_get_alert_rules(self, async_client: AsyncClient, db_session: AsyncSession, sample_alert_rule):
        """测试获取告警规则"""
        # 先创建一个告警规则
        repo = BaseRepository(AlertRule, db_session)
        rule = await repo.create(sample_alert_rule)
        
        response = await async_client.get("/api/v1/monitoring/alert-rules")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # 检查规则结构
        rule_data = data[0]
        assert "id" in rule_data
        assert "name" in rule_data
        assert "description" in rule_data
        assert "metric_name" in rule_data
        assert "operator" in rule_data
        assert "threshold" in rule_data
        assert "severity" in rule_data
        assert "is_active" in rule_data
    
    async def test_update_alert_rule(self, async_client: AsyncClient, db_session: AsyncSession, sample_alert_rule):
        """测试更新告警规则"""
        # 先创建一个告警规则
        repo = BaseRepository(AlertRule, db_session)
        rule = await repo.create(sample_alert_rule)
        
        # 更新规则
        update_data = {"threshold": 90.0, "severity": "critical"}
        response = await async_client.put(
            f"/api/v1/monitoring/alert-rules/{rule.id}",
            json=update_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == rule.id
        assert "message" in data
    
    async def test_delete_alert_rule(self, async_client: AsyncClient, db_session: AsyncSession, sample_alert_rule):
        """测试删除告警规则"""
        # 先创建一个告警规则
        repo = BaseRepository(AlertRule, db_session)
        rule = await repo.create(sample_alert_rule)
        
        # 删除规则
        response = await async_client.delete(f"/api/v1/monitoring/alert-rules/{rule.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        
        # 验证规则已删除
        deleted_rule = await repo.get(rule.id)
        assert deleted_rule is None
    
    async def test_resolve_alert(self, async_client: AsyncClient, db_session: AsyncSession):
        """测试解决告警"""
        # 先创建一个告警
        alert = Alert(
            rule_id=1,
            title="测试告警",
            message="这是一个测试告警",
            severity="warning",
            metric_name="test_metric",
            metric_value=85.0,
            threshold=80.0,
            triggered_at="2024-01-01T10:00:00Z"
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)
        
        # 解决告警
        response = await async_client.post(
            f"/api/v1/monitoring/alerts/{alert.id}/resolve",
            params={"resolved_by": "admin", "notes": "问题已修复"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data


@pytest.mark.integration
class TestNotificationAPI:
    """通知API测试"""
    
    def test_get_notification_channels(self, client: TestClient):
        """测试获取通知渠道"""
        response = client.get("/api/v1/monitoring/notifications/channels")
        assert response.status_code == 200
        
        data = response.json()
        assert "channels" in data
        assert isinstance(data["channels"], list)
    
    def test_test_notification_channel(self, client: TestClient):
        """测试通知渠道测试"""
        response = client.post(
            "/api/v1/monitoring/notifications/test",
            params={"channel": "email", "message": "测试消息"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data


@pytest.mark.integration
class TestMonitoringControlAPI:
    """监控控制API测试"""
    
    def test_monitoring_status(self, client: TestClient):
        """测试监控状态"""
        response = client.get("/api/v1/monitoring/monitoring/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "system_monitor_running" in data
        assert "alert_engine_running" in data
        assert "uptime_seconds" in data
        assert "timestamp" in data
    
    def test_start_monitoring(self, client: TestClient):
        """测试启动监控"""
        response = client.post("/api/v1/monitoring/monitoring/start")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
    
    def test_stop_monitoring(self, client: TestClient):
        """测试停止监控"""
        response = client.post("/api/v1/monitoring/monitoring/stop")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data


@pytest.mark.integration
class TestTradingAPI:
    """交易API测试"""
    
    async def test_get_accounts_empty(self, async_client: AsyncClient):
        """测试获取账户（空列表）"""
        response = await async_client.get("/api/v1/accounts")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_create_account(self, async_client: AsyncClient, sample_account_data):
        """测试创建账户"""
        response = await async_client.post(
            "/api/v1/accounts",
            json=sample_account_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert data["name"] == sample_account_data["name"]
        assert data["exchange"] == sample_account_data["exchange"]
    
    async def test_get_strategies_empty(self, async_client: AsyncClient):
        """测试获取策略（空列表）"""
        response = await async_client.get("/api/v1/strategies")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_create_strategy(self, async_client: AsyncClient, sample_strategy_data):
        """测试创建策略"""
        response = await async_client.post(
            "/api/v1/strategies",
            json=sample_strategy_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert data["name"] == sample_strategy_data["name"]
        assert data["type"] == sample_strategy_data["type"]


@pytest.mark.integration
class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_endpoint(self, client: TestClient):
        """测试404错误"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    async def test_invalid_alert_rule_id(self, async_client: AsyncClient):
        """测试无效的告警规则ID"""
        response = await async_client.get("/api/v1/monitoring/alert-rules/99999")
        assert response.status_code == 404
    
    async def test_invalid_json_data(self, async_client: AsyncClient):
        """测试无效的JSON数据"""
        response = await async_client.post(
            "/api/v1/monitoring/alert-rules",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    async def test_missing_required_fields(self, async_client: AsyncClient):
        """测试缺少必需字段"""
        incomplete_data = {"name": "测试规则"}  # 缺少其他必需字段
        
        response = await async_client.post(
            "/api/v1/monitoring/alert-rules",
            json=incomplete_data
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestPagination:
    """分页测试"""
    
    async def test_alerts_pagination(self, async_client: AsyncClient, db_session: AsyncSession):
        """测试告警分页"""
        # 创建多个告警
        for i in range(15):
            alert = Alert(
                rule_id=1,
                title=f"测试告警 {i}",
                message=f"这是测试告警 {i}",
                severity="warning",
                metric_name="test_metric",
                metric_value=85.0,
                threshold=80.0,
                triggered_at="2024-01-01T10:00:00Z"
            )
            db_session.add(alert)
        
        await db_session.commit()
        
        # 测试默认分页
        response = await async_client.get("/api/v1/monitoring/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 100  # 默认限制
        
        # 测试自定义限制
        response = await async_client.get("/api/v1/monitoring/alerts?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 5


@pytest.mark.integration
class TestFiltering:
    """过滤测试"""
    
    async def test_alerts_filtering_by_status(self, async_client: AsyncClient, db_session: AsyncSession):
        """测试按状态过滤告警"""
        # 创建不同状态的告警
        active_alert = Alert(
            rule_id=1,
            title="活跃告警",
            message="这是活跃告警",
            severity="warning",
            status="active",
            metric_name="test_metric",
            metric_value=85.0,
            threshold=80.0,
            triggered_at="2024-01-01T10:00:00Z"
        )
        
        resolved_alert = Alert(
            rule_id=1,
            title="已解决告警",
            message="这是已解决告警",
            severity="warning",
            status="resolved",
            metric_name="test_metric",
            metric_value=85.0,
            threshold=80.0,
            triggered_at="2024-01-01T10:00:00Z"
        )
        
        db_session.add(active_alert)
        db_session.add(resolved_alert)
        await db_session.commit()
        
        # 测试过滤活跃告警
        response = await async_client.get("/api/v1/monitoring/alerts?status=active")
        assert response.status_code == 200
        
        data = response.json()
        assert all(alert["status"] == "active" for alert in data)
        
        # 测试过滤已解决告警
        response = await async_client.get("/api/v1/monitoring/alerts?status=resolved")
        assert response.status_code == 200
        
        data = response.json()
        assert all(alert["status"] == "resolved" for alert in data)
