"""
模型单元测试
"""
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trading import Account, Order, Position, Strategy, OrderSide, OrderType, OrderStatus
from app.models.market_data import MarketData, TradingPair
from app.models.news_data import NewsItem
from app.models.whale_data import WhaleTransaction
from app.models.system_data import SystemMetrics, Alert


@pytest.mark.unit
class TestTradingModels:
    """交易模型测试"""
    
    async def test_account_creation(self, db_session: AsyncSession, sample_account_data):
        """测试账户创建"""
        account = Account(**sample_account_data)
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)
        
        assert account.id is not None
        assert account.name == sample_account_data["name"]
        assert account.exchange == sample_account_data["exchange"]
        assert account.is_active == sample_account_data["is_active"]
        assert account.created_at is not None
    
    async def test_order_creation(self, db_session: AsyncSession, sample_order_data):
        """测试订单创建"""
        # 先创建账户
        account = Account(
            name="测试账户",
            exchange="okx",
            api_key="test",
            api_secret="test",
            passphrase="test"
        )
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)
        
        # 创建订单
        order_data = sample_order_data.copy()
        order_data["account_id"] = account.id
        order_data["status"] = OrderStatus.PENDING
        
        order = Order(**order_data)
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)
        
        assert order.id is not None
        assert order.symbol == sample_order_data["symbol"]
        assert order.side == OrderSide.BUY
        assert order.type == OrderType.LIMIT
        assert order.amount == sample_order_data["amount"]
        assert order.price == sample_order_data["price"]
        assert order.status == OrderStatus.PENDING
    
    async def test_position_creation(self, db_session: AsyncSession):
        """测试持仓创建"""
        # 先创建账户
        account = Account(
            name="测试账户",
            exchange="okx",
            api_key="test",
            api_secret="test",
            passphrase="test"
        )
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)
        
        # 创建持仓
        position = Position(
            account_id=account.id,
            symbol="BTC/USDT",
            size=0.1,
            entry_price=45000.0,
            unrealized_pnl=100.0
        )
        db_session.add(position)
        await db_session.commit()
        await db_session.refresh(position)
        
        assert position.id is not None
        assert position.symbol == "BTC/USDT"
        assert position.size == 0.1
        assert position.entry_price == 45000.0
        assert position.unrealized_pnl == 100.0
    
    async def test_strategy_creation(self, db_session: AsyncSession, sample_strategy_data):
        """测试策略创建"""
        strategy = Strategy(**sample_strategy_data)
        db_session.add(strategy)
        await db_session.commit()
        await db_session.refresh(strategy)
        
        assert strategy.id is not None
        assert strategy.name == sample_strategy_data["name"]
        assert strategy.type == sample_strategy_data["type"]
        assert strategy.symbol == sample_strategy_data["symbol"]
        assert strategy.parameters == sample_strategy_data["parameters"]
        assert strategy.is_active == sample_strategy_data["is_active"]


@pytest.mark.unit
class TestMarketDataModels:
    """市场数据模型测试"""
    
    async def test_market_data_creation(self, db_session: AsyncSession, sample_market_data):
        """测试市场数据创建"""
        market_data = MarketData(
            timestamp=datetime.utcnow(),
            **sample_market_data
        )
        db_session.add(market_data)
        await db_session.commit()
        await db_session.refresh(market_data)
        
        assert market_data.id is not None
        assert market_data.symbol == sample_market_data["symbol"]
        assert market_data.timeframe == sample_market_data["timeframe"]
        assert market_data.open == sample_market_data["open"]
        assert market_data.high == sample_market_data["high"]
        assert market_data.low == sample_market_data["low"]
        assert market_data.close == sample_market_data["close"]
        assert market_data.volume == sample_market_data["volume"]
    
    async def test_trading_pair_creation(self, db_session: AsyncSession):
        """测试交易对创建"""
        trading_pair = TradingPair(
            symbol="BTC/USDT",
            base_currency="BTC",
            quote_currency="USDT",
            is_active=True,
            min_order_size=0.00001,
            price_precision=2,
            amount_precision=8
        )
        db_session.add(trading_pair)
        await db_session.commit()
        await db_session.refresh(trading_pair)
        
        assert trading_pair.id is not None
        assert trading_pair.symbol == "BTC/USDT"
        assert trading_pair.base_currency == "BTC"
        assert trading_pair.quote_currency == "USDT"
        assert trading_pair.is_active is True


@pytest.mark.unit
class TestNewsDataModels:
    """新闻数据模型测试"""
    
    async def test_news_item_creation(self, db_session: AsyncSession, sample_news_data):
        """测试新闻条目创建"""
        news_item = NewsItem(
            published_at=datetime.utcnow(),
            timestamp=datetime.utcnow(),
            **sample_news_data
        )
        db_session.add(news_item)
        await db_session.commit()
        await db_session.refresh(news_item)
        
        assert news_item.id is not None
        assert news_item.title == sample_news_data["title"]
        assert news_item.content == sample_news_data["content"]
        assert news_item.source == sample_news_data["source"]
        assert news_item.sentiment == sample_news_data["sentiment"]
        assert news_item.relevance == sample_news_data["relevance"]
        assert news_item.keywords == sample_news_data["keywords"]


@pytest.mark.unit
class TestWhaleDataModels:
    """大户数据模型测试"""
    
    async def test_whale_transaction_creation(self, db_session: AsyncSession, sample_whale_transaction):
        """测试大户交易创建"""
        whale_transaction = WhaleTransaction(
            timestamp=datetime.utcnow(),
            **sample_whale_transaction
        )
        db_session.add(whale_transaction)
        await db_session.commit()
        await db_session.refresh(whale_transaction)
        
        assert whale_transaction.id is not None
        assert whale_transaction.transaction_hash == sample_whale_transaction["transaction_hash"]
        assert whale_transaction.from_address == sample_whale_transaction["from_address"]
        assert whale_transaction.to_address == sample_whale_transaction["to_address"]
        assert whale_transaction.amount == sample_whale_transaction["amount"]
        assert whale_transaction.currency == sample_whale_transaction["currency"]


@pytest.mark.unit
class TestSystemDataModels:
    """系统数据模型测试"""
    
    async def test_system_metrics_creation(self, db_session: AsyncSession):
        """测试系统指标创建"""
        system_metrics = SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage=75.5,
            memory_usage=60.2,
            disk_usage=45.8,
            network_in=1024000,
            network_out=512000,
            process_count=150
        )
        db_session.add(system_metrics)
        await db_session.commit()
        await db_session.refresh(system_metrics)
        
        assert system_metrics.id is not None
        assert system_metrics.cpu_usage == 75.5
        assert system_metrics.memory_usage == 60.2
        assert system_metrics.disk_usage == 45.8
        assert system_metrics.network_in == 1024000
        assert system_metrics.network_out == 512000
        assert system_metrics.process_count == 150
    
    async def test_alert_creation(self, db_session: AsyncSession):
        """测试告警创建"""
        alert = Alert(
            rule_id=1,
            title="CPU使用率过高",
            message="CPU使用率达到85%，超过阈值80%",
            severity="warning",
            metric_name="cpu_usage",
            metric_value=85.0,
            threshold=80.0,
            triggered_at=datetime.utcnow()
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)
        
        assert alert.id is not None
        assert alert.title == "CPU使用率过高"
        assert alert.severity == "warning"
        assert alert.metric_value == 85.0
        assert alert.threshold == 80.0
        assert alert.status == "active"  # 默认状态


@pytest.mark.unit
class TestModelRelationships:
    """模型关系测试"""
    
    async def test_account_order_relationship(self, db_session: AsyncSession):
        """测试账户和订单的关系"""
        # 创建账户
        account = Account(
            name="测试账户",
            exchange="okx",
            api_key="test",
            api_secret="test",
            passphrase="test"
        )
        db_session.add(account)
        await db_session.commit()
        await db_session.refresh(account)
        
        # 创建订单
        order = Order(
            account_id=account.id,
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            amount=0.001,
            price=45000.0,
            status=OrderStatus.PENDING
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)
        
        # 验证关系
        assert order.account_id == account.id
        
        # 通过外键查询
        from sqlalchemy import select
        result = await db_session.execute(
            select(Order).where(Order.account_id == account.id)
        )
        orders = result.scalars().all()
        assert len(orders) == 1
        assert orders[0].id == order.id
