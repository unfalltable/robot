"""
测试配置文件
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_async_session
from app.core.config import Settings
from app.models import *  # 导入所有模型


# 测试数据库配置
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/trading_robot_test"

# 创建测试引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

# 创建测试会话工厂
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """设置测试数据库"""
    # 创建所有表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # 清理数据库
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """创建数据库会话"""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """覆盖数据库依赖"""
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_async_session] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db) -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_account_data():
    """示例账户数据"""
    return {
        "name": "测试账户",
        "exchange": "okx",
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "passphrase": "test_passphrase",
        "is_sandbox": True,
        "is_active": True
    }


@pytest.fixture
def sample_strategy_data():
    """示例策略数据"""
    return {
        "name": "测试策略",
        "description": "这是一个测试策略",
        "type": "grid",
        "symbol": "BTC/USDT",
        "parameters": {
            "grid_size": 0.5,
            "grid_count": 10,
            "base_amount": 1000
        },
        "is_active": True
    }


@pytest.fixture
def sample_order_data():
    """示例订单数据"""
    return {
        "symbol": "BTC/USDT",
        "side": "buy",
        "type": "limit",
        "amount": 0.001,
        "price": 45000.0
    }


@pytest.fixture
def sample_market_data():
    """示例市场数据"""
    return {
        "symbol": "BTC/USDT",
        "timeframe": "1m",
        "open": 45000.0,
        "high": 45100.0,
        "low": 44900.0,
        "close": 45050.0,
        "volume": 1.5
    }


@pytest.fixture
def sample_news_data():
    """示例新闻数据"""
    return {
        "title": "Bitcoin价格突破新高",
        "content": "Bitcoin价格今日突破45000美元...",
        "source": "CoinDesk",
        "url": "https://example.com/news/1",
        "sentiment": 0.8,
        "relevance": 0.9,
        "keywords": ["bitcoin", "price", "breakout"]
    }


@pytest.fixture
def sample_whale_transaction():
    """示例大户交易数据"""
    return {
        "transaction_hash": "0x123456789abcdef",
        "from_address": "0xabc123",
        "to_address": "0xdef456",
        "amount": 1000.0,
        "currency": "BTC",
        "exchange_from": "Binance",
        "exchange_to": "Coinbase"
    }


@pytest.fixture
def sample_alert_rule():
    """示例告警规则"""
    return {
        "name": "CPU使用率告警",
        "description": "CPU使用率超过80%时告警",
        "category": "system",
        "metric_name": "system.cpu_usage",
        "operator": ">",
        "threshold": 80.0,
        "severity": "warning",
        "is_active": True
    }


class MockExchangeAPI:
    """模拟交易所API"""
    
    def __init__(self):
        self.orders = {}
        self.positions = {}
        self.balance = {"USDT": 10000.0, "BTC": 0.0}
        self.order_id_counter = 1
    
    async def get_account_info(self):
        """获取账户信息"""
        return {
            "balance": self.balance,
            "positions": list(self.positions.values())
        }
    
    async def create_order(self, symbol: str, side: str, type: str, amount: float, price: float = None):
        """创建订单"""
        order_id = str(self.order_id_counter)
        self.order_id_counter += 1
        
        order = {
            "id": order_id,
            "symbol": symbol,
            "side": side,
            "type": type,
            "amount": amount,
            "price": price,
            "status": "open",
            "filled_amount": 0.0,
            "remaining_amount": amount
        }
        
        self.orders[order_id] = order
        return order
    
    async def cancel_order(self, order_id: str):
        """取消订单"""
        if order_id in self.orders:
            self.orders[order_id]["status"] = "cancelled"
            return True
        return False
    
    async def get_order(self, order_id: str):
        """获取订单"""
        return self.orders.get(order_id)
    
    async def get_ticker(self, symbol: str):
        """获取行情"""
        return {
            "symbol": symbol,
            "last_price": 45000.0,
            "bid_price": 44999.0,
            "ask_price": 45001.0,
            "volume_24h": 1000.0
        }


@pytest.fixture
def mock_exchange_api():
    """模拟交易所API"""
    return MockExchangeAPI()


class MockNotificationService:
    """模拟通知服务"""
    
    def __init__(self):
        self.sent_notifications = []
    
    async def send_notification(self, message: str, title: str = None, channels: list = None, **kwargs):
        """发送通知"""
        notification = {
            "message": message,
            "title": title,
            "channels": channels or [],
            "kwargs": kwargs
        }
        self.sent_notifications.append(notification)
        return {channel: True for channel in (channels or [])}
    
    async def send_alert_notification(self, alert, channels: list):
        """发送告警通知"""
        return await self.send_notification(
            message=alert.message,
            title=alert.title,
            channels=channels,
            severity=alert.severity
        )
    
    def get_sent_notifications(self):
        """获取已发送的通知"""
        return self.sent_notifications.copy()
    
    def clear_notifications(self):
        """清空通知记录"""
        self.sent_notifications.clear()


@pytest.fixture
def mock_notification_service():
    """模拟通知服务"""
    return MockNotificationService()


@pytest.fixture
def mock_redis():
    """模拟Redis"""
    class MockRedis:
        def __init__(self):
            self.data = {}
        
        async def get(self, key):
            return self.data.get(key)
        
        async def set(self, key, value, ex=None):
            self.data[key] = value
            return True
        
        async def delete(self, key):
            return self.data.pop(key, None) is not None
        
        async def exists(self, key):
            return key in self.data
        
        async def keys(self, pattern="*"):
            if pattern == "*":
                return list(self.data.keys())
            # 简单的模式匹配
            import fnmatch
            return [k for k in self.data.keys() if fnmatch.fnmatch(k, pattern)]
    
    return MockRedis()


# 测试标记
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow
