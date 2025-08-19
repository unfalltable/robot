"""
端到端交易流程测试
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.models.trading import Account, Strategy, Order, Position
from app.repositories.base_repository import BaseRepository


@pytest.mark.e2e
class TestCompleteTrading Workflow:
    """完整交易流程测试"""
    
    async def test_complete_trading_flow(
        self, 
        async_client: AsyncClient, 
        db_session: AsyncSession,
        mock_exchange_api,
        sample_account_data,
        sample_strategy_data
    ):
        """测试完整的交易流程"""
        
        # 1. 创建账户
        response = await async_client.post("/api/v1/accounts", json=sample_account_data)
        assert response.status_code == 200
        account_data = response.json()
        account_id = account_data["id"]
        
        # 2. 验证账户创建
        response = await async_client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        assert response.json()["name"] == sample_account_data["name"]
        
        # 3. 创建策略
        strategy_data = sample_strategy_data.copy()
        strategy_data["account_id"] = account_id
        
        response = await async_client.post("/api/v1/strategies", json=strategy_data)
        assert response.status_code == 200
        strategy_response = response.json()
        strategy_id = strategy_response["id"]
        
        # 4. 启动策略
        response = await async_client.post(f"/api/v1/strategies/{strategy_id}/start")
        assert response.status_code == 200
        
        # 5. 验证策略状态
        response = await async_client.get(f"/api/v1/strategies/{strategy_id}")
        assert response.status_code == 200
        strategy_info = response.json()
        assert strategy_info["is_active"] is True
        
        # 6. 模拟创建订单
        with patch('app.services.trading_service.ExchangeAPI') as mock_api:
            mock_api.return_value = mock_exchange_api
            
            order_data = {
                "account_id": account_id,
                "strategy_id": strategy_id,
                "symbol": "BTC/USDT",
                "side": "buy",
                "type": "limit",
                "amount": 0.001,
                "price": 45000.0
            }
            
            response = await async_client.post("/api/v1/orders", json=order_data)
            assert response.status_code == 200
            order_response = response.json()
            order_id = order_response["id"]
        
        # 7. 验证订单创建
        response = await async_client.get(f"/api/v1/orders/{order_id}")
        assert response.status_code == 200
        order_info = response.json()
        assert order_info["symbol"] == "BTC/USDT"
        assert order_info["side"] == "buy"
        assert order_info["amount"] == 0.001
        
        # 8. 获取账户订单列表
        response = await async_client.get(f"/api/v1/accounts/{account_id}/orders")
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) >= 1
        assert any(order["id"] == order_id for order in orders)
        
        # 9. 模拟订单成交
        with patch('app.services.trading_service.ExchangeAPI') as mock_api:
            mock_api.return_value = mock_exchange_api
            
            # 模拟订单成交
            await mock_exchange_api.fill_order(order_id, 0.001, 45000.0)
            
            # 同步订单状态
            response = await async_client.post(f"/api/v1/orders/{order_id}/sync")
            assert response.status_code == 200
        
        # 10. 验证订单状态更新
        response = await async_client.get(f"/api/v1/orders/{order_id}")
        assert response.status_code == 200
        updated_order = response.json()
        assert updated_order["status"] == "filled"
        assert updated_order["filled_amount"] == 0.001
        
        # 11. 检查持仓
        response = await async_client.get(f"/api/v1/accounts/{account_id}/positions")
        assert response.status_code == 200
        positions = response.json()
        
        # 应该有BTC持仓
        btc_position = next((pos for pos in positions if pos["symbol"] == "BTC/USDT"), None)
        assert btc_position is not None
        assert btc_position["size"] == 0.001
        
        # 12. 停止策略
        response = await async_client.post(f"/api/v1/strategies/{strategy_id}/stop")
        assert response.status_code == 200
        
        # 13. 验证策略已停止
        response = await async_client.get(f"/api/v1/strategies/{strategy_id}")
        assert response.status_code == 200
        final_strategy = response.json()
        assert final_strategy["is_active"] is False


@pytest.mark.e2e
class TestMonitoringWorkflow:
    """监控流程测试"""
    
    async def test_complete_monitoring_flow(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        mock_notification_service,
        sample_alert_rule
    ):
        """测试完整的监控流程"""
        
        # 1. 启动监控系统
        response = await async_client.post("/api/v1/monitoring/monitoring/start")
        assert response.status_code == 200
        
        # 2. 检查监控状态
        response = await async_client.get("/api/v1/monitoring/monitoring/status")
        assert response.status_code == 200
        status = response.json()
        assert status["system_monitor_running"] is True
        assert status["alert_engine_running"] is True
        
        # 3. 创建告警规则
        response = await async_client.post(
            "/api/v1/monitoring/alert-rules",
            json=sample_alert_rule
        )
        assert response.status_code == 200
        rule_data = response.json()
        rule_id = rule_data["id"]
        
        # 4. 验证告警规则创建
        response = await async_client.get("/api/v1/monitoring/alert-rules")
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) >= 1
        assert any(rule["id"] == rule_id for rule in rules)
        
        # 5. 检查系统健康状态
        response = await async_client.get("/api/v1/monitoring/health")
        assert response.status_code == 200
        health = response.json()
        assert "status" in health
        assert "checks" in health
        
        # 6. 获取系统指标
        response = await async_client.get("/api/v1/monitoring/metrics/system")
        assert response.status_code == 200
        metrics = response.json()
        assert "current" in metrics
        assert "history" in metrics
        
        # 7. 模拟触发告警
        with patch('app.services.monitoring_service.AlertEngine._get_metric_value') as mock_metric:
            mock_metric.return_value = 85.0  # 超过阈值80.0
            
            # 手动触发告警检查
            from app.services.monitoring_service import AlertEngine
            alert_engine = AlertEngine(mock_notification_service)
            
            # 模拟告警规则
            from app.models.system_data import AlertRule
            rule = AlertRule(**sample_alert_rule)
            rule.id = rule_id
            
            async with db_session as session:
                await alert_engine._evaluate_rule(session, rule)
        
        # 8. 检查活跃告警
        response = await async_client.get("/api/v1/monitoring/alerts/active")
        assert response.status_code == 200
        active_alerts = response.json()
        
        # 9. 如果有告警，解决它
        if active_alerts:
            alert_id = active_alerts[0]["id"]
            response = await async_client.post(
                f"/api/v1/monitoring/alerts/{alert_id}/resolve",
                params={"resolved_by": "test_user", "notes": "测试解决"}
            )
            assert response.status_code == 200
        
        # 10. 测试通知渠道
        response = await async_client.post(
            "/api/v1/monitoring/notifications/test",
            params={"channel": "email", "message": "测试通知"}
        )
        assert response.status_code == 200
        
        # 11. 停止监控系统
        response = await async_client.post("/api/v1/monitoring/monitoring/stop")
        assert response.status_code == 200


@pytest.mark.e2e
class TestDataPipeline:
    """数据管道测试"""
    
    async def test_market_data_pipeline(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_market_data
    ):
        """测试市场数据管道"""
        
        # 1. 创建交易对配置
        trading_pair_data = {
            "symbol": "BTC/USDT",
            "base_currency": "BTC",
            "quote_currency": "USDT",
            "is_active": True,
            "min_order_size": 0.00001,
            "price_precision": 2,
            "amount_precision": 8
        }
        
        response = await async_client.post("/api/v1/trading-pairs", json=trading_pair_data)
        assert response.status_code == 200
        
        # 2. 模拟接收市场数据
        with patch('app.services.market_data_service.MarketDataCollector') as mock_collector:
            mock_collector.return_value.collect_klines = AsyncMock(return_value=[sample_market_data])
            
            # 触发数据收集
            response = await async_client.post("/api/v1/market-data/collect")
            assert response.status_code == 200
        
        # 3. 验证市场数据存储
        response = await async_client.get("/api/v1/market-data/BTC-USDT/klines")
        assert response.status_code == 200
        klines = response.json()
        assert len(klines) >= 1
        
        # 4. 获取最新行情
        response = await async_client.get("/api/v1/market-data/BTC-USDT/ticker")
        assert response.status_code == 200
        ticker = response.json()
        assert "symbol" in ticker
        assert "last_price" in ticker
        
        # 5. 测试技术指标计算
        response = await async_client.get("/api/v1/market-data/BTC-USDT/indicators")
        assert response.status_code == 200
        indicators = response.json()
        assert "sma_20" in indicators or len(indicators) == 0  # 可能没有足够数据计算指标


@pytest.mark.e2e
class TestNewsAndWhaleMonitoring:
    """新闻和大户监控测试"""
    
    async def test_news_monitoring_pipeline(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_news_data
    ):
        """测试新闻监控管道"""
        
        # 1. 创建新闻源配置
        news_source_data = {
            "name": "test_source",
            "display_name": "测试新闻源",
            "source_type": "rss",
            "url": "https://example.com/rss",
            "rss_url": "https://example.com/rss.xml",
            "keywords": ["bitcoin", "crypto"],
            "is_active": True
        }
        
        response = await async_client.post("/api/v1/news-sources", json=news_source_data)
        assert response.status_code == 200
        
        # 2. 模拟新闻收集
        with patch('app.services.news_service.NewsCollector') as mock_collector:
            mock_collector.return_value.collect_news = AsyncMock(return_value=[sample_news_data])
            
            # 触发新闻收集
            response = await async_client.post("/api/v1/news/collect")
            assert response.status_code == 200
        
        # 3. 验证新闻存储
        response = await async_client.get("/api/v1/news")
        assert response.status_code == 200
        news_items = response.json()
        assert len(news_items) >= 1
        
        # 4. 测试新闻分析
        if news_items:
            news_id = news_items[0]["id"]
            response = await async_client.post(f"/api/v1/news/{news_id}/analyze")
            assert response.status_code == 200
    
    async def test_whale_monitoring_pipeline(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_whale_transaction
    ):
        """测试大户监控管道"""
        
        # 1. 创建大户告警规则
        whale_alert_data = {
            "name": "大额BTC转账告警",
            "description": "BTC转账金额超过100时告警",
            "min_amount": 100.0,
            "currencies": ["BTC"],
            "is_active": True
        }
        
        response = await async_client.post("/api/v1/whale-alerts", json=whale_alert_data)
        assert response.status_code == 200
        
        # 2. 模拟大户交易数据收集
        with patch('app.services.whale_service.WhaleMonitor') as mock_monitor:
            mock_monitor.return_value.collect_transactions = AsyncMock(
                return_value=[sample_whale_transaction]
            )
            
            # 触发大户交易收集
            response = await async_client.post("/api/v1/whale-transactions/collect")
            assert response.status_code == 200
        
        # 3. 验证大户交易存储
        response = await async_client.get("/api/v1/whale-transactions")
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) >= 1
        
        # 4. 检查是否触发告警
        response = await async_client.get("/api/v1/whale-alerts/logs")
        assert response.status_code == 200
        alert_logs = response.json()
        # 根据金额判断是否应该有告警


@pytest.mark.e2e
@pytest.mark.slow
class TestPerformanceAndStress:
    """性能和压力测试"""
    
    async def test_api_performance(self, async_client: AsyncClient):
        """测试API性能"""
        import time
        
        # 测试健康检查端点性能
        start_time = time.time()
        response = await async_client.get("/api/v1/monitoring/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # 应该在5秒内完成
        
        # 测试系统指标端点性能
        start_time = time.time()
        response = await async_client.get("/api/v1/monitoring/metrics/system")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 3.0  # 应该在3秒内完成
    
    async def test_concurrent_requests(self, async_client: AsyncClient):
        """测试并发请求"""
        
        async def make_request():
            response = await async_client.get("/api/v1/monitoring/health/summary")
            return response.status_code
        
        # 并发发送10个请求
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 所有请求都应该成功
        assert all(status == 200 for status in results)
    
    async def test_large_data_handling(
        self, 
        async_client: AsyncClient, 
        db_session: AsyncSession
    ):
        """测试大数据量处理"""
        
        # 创建大量告警规则
        rules_data = []
        for i in range(50):
            rule_data = {
                "name": f"测试规则 {i}",
                "description": f"这是测试规则 {i}",
                "category": "system",
                "metric_name": f"test_metric_{i}",
                "operator": ">",
                "threshold": float(i),
                "severity": "warning",
                "is_active": True
            }
            rules_data.append(rule_data)
        
        # 批量创建
        for rule_data in rules_data:
            response = await async_client.post(
                "/api/v1/monitoring/alert-rules",
                json=rule_data
            )
            assert response.status_code == 200
        
        # 测试获取大量数据的性能
        import time
        start_time = time.time()
        response = await async_client.get("/api/v1/monitoring/alert-rules")
        end_time = time.time()
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 50
        assert (end_time - start_time) < 5.0  # 应该在5秒内完成
