#!/usr/bin/env python3
"""
系统测试脚本
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

async def test_imports():
    """测试导入"""
    print("测试模块导入...")
    
    try:
        from app.core.config import settings
        print("✓ 配置模块导入成功")
        
        from app.core.logging import setup_logging
        print("✓ 日志模块导入成功")
        
        from app.models.trading import Order, Position, Account
        print("✓ 数据模型导入成功")
        
        from app.schemas.trading import OrderCreate, OrderResponse
        print("✓ 数据模式导入成功")
        
        from app.services.trading_service import TradingService
        print("✓ 交易服务导入成功")
        
        from app.services.risk_manager import RiskManager
        print("✓ 风险管理器导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        return False

async def test_database():
    """测试数据库连接"""
    print("\n测试数据库连接...")
    
    try:
        from app.core.database import engine, SessionLocal
        
        # 测试连接
        with SessionLocal() as session:
            session.execute("SELECT 1")
        
        print("✓ 数据库连接成功")
        return True
        
    except Exception as e:
        print(f"✗ 数据库连接失败: {str(e)}")
        print("提示: 请确保PostgreSQL已启动并配置正确")
        return False

async def test_exchange_connection():
    """测试交易所连接"""
    print("\n测试交易所连接...")
    
    try:
        from exchanges.okx_exchange import OKXExchange
        from exchanges.base_exchange import ExchangeCredentials
        
        # 使用测试凭证
        credentials = ExchangeCredentials(
            api_key="test_key",
            secret_key="test_secret",
            passphrase="test_passphrase",
            sandbox=True
        )
        
        exchange = OKXExchange(credentials)
        print("✓ OKX交易所实例创建成功")
        
        # 注意：这里不测试实际连接，因为需要真实的API凭证
        print("提示: 实际连接测试需要真实的API凭证")
        return True
        
    except Exception as e:
        print(f"✗ 交易所连接测试失败: {str(e)}")
        return False

async def test_api_endpoints():
    """测试API端点"""
    print("\n测试API端点...")
    
    try:
        from app.main import create_app
        from fastapi.testclient import TestClient
        
        app = create_app()
        client = TestClient(app)
        
        # 测试健康检查
        response = client.get("/health")
        if response.status_code == 200:
            print("✓ 健康检查端点正常")
        else:
            print(f"✗ 健康检查端点异常: {response.status_code}")
            return False
        
        # 测试根路径
        response = client.get("/")
        if response.status_code == 200:
            print("✓ 根路径端点正常")
        else:
            print(f"✗ 根路径端点异常: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ API端点测试失败: {str(e)}")
        return False

async def test_risk_manager():
    """测试风险管理器"""
    print("\n测试风险管理器...")
    
    try:
        from app.services.risk_manager import RiskManager, RiskCheckResult
        from app.schemas.trading import OrderCreate
        from app.models.trading import OrderSide, OrderType
        
        # 创建模拟数据库会话
        from app.core.database import SessionLocal
        
        with SessionLocal() as session:
            risk_manager = RiskManager(session)
            
            # 创建测试订单
            test_order = OrderCreate(
                account_id="test_account",
                symbol="BTC/USDT",
                side=OrderSide.BUY,
                type=OrderType.LIMIT,
                amount=0.01,
                price=50000.0
            )
            
            # 测试风险检查
            result = await risk_manager.check_order_risk(test_order)
            
            if isinstance(result, RiskCheckResult):
                print("✓ 风险管理器测试成功")
                return True
            else:
                print("✗ 风险管理器返回结果格式错误")
                return False
        
    except Exception as e:
        print(f"✗ 风险管理器测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("=== 数字货币交易机器人系统测试 ===\n")
    
    tests = [
        ("模块导入", test_imports),
        ("数据库连接", test_database),
        ("交易所连接", test_exchange_connection),
        ("API端点", test_api_endpoints),
        ("风险管理器", test_risk_manager),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"运行测试: {test_name}")
        try:
            if await test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ 测试异常: {str(e)}\n")
    
    print("=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！系统基础功能正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关配置")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
