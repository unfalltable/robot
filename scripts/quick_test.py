#!/usr/bin/env python3
"""
快速测试脚本 - 不依赖外部服务
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

def test_basic_imports():
    """测试基础导入"""
    print("测试基础模块导入...")
    
    try:
        # 测试配置
        from app.core.config import Settings
        settings = Settings()
        print("✓ 配置模块正常")
        
        # 测试数据模型
        from app.models.trading import OrderStatus, OrderType, OrderSide
        print("✓ 数据模型正常")
        
        # 测试数据模式
        from app.schemas.trading import OrderCreate, StrategyCreate
        print("✓ 数据模式正常")
        
        # 测试策略框架
        from strategies.base_strategy import BaseStrategy, StrategyConfig, TradingSignal
        from strategies.grid_strategy import GridStrategy
        print("✓ 策略框架正常")
        
        # 测试交易所接口
        from exchanges.base_exchange import BaseExchange, ExchangeCredentials
        from exchanges.okx_exchange import OKXExchange
        print("✓ 交易所接口正常")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {str(e)}")
        return False

def test_strategy_creation():
    """测试策略创建"""
    print("\n测试策略创建...")
    
    try:
        from strategies.base_strategy import StrategyConfig
        from strategies.grid_strategy import GridStrategy
        
        # 创建策略配置
        config = StrategyConfig(
            name="测试网格策略",
            description="用于测试的网格策略",
            parameters={
                'grid_size': 0.01,
                'grid_levels': 5,
                'base_amount': 100.0,
                'center_price': 50000.0,
                'max_position_size': 1000.0,
                'stop_loss': 0.05,
                'take_profit': 0.1
            },
            risk_limits={
                'max_daily_loss': 0.05,
                'max_drawdown': 0.2
            },
            symbols=['BTC/USDT'],
            timeframes=['1m', '5m']
        )
        
        # 创建策略实例
        strategy = GridStrategy(config)
        print("✓ 策略实例创建成功")
        
        # 验证配置
        if strategy.validate_config():
            print("✓ 策略配置验证通过")
        else:
            print("✗ 策略配置验证失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 策略创建失败: {str(e)}")
        return False

def test_exchange_creation():
    """测试交易所创建"""
    print("\n测试交易所创建...")
    
    try:
        from exchanges.base_exchange import ExchangeCredentials
        from exchanges.okx_exchange import OKXExchange
        
        # 创建测试凭证
        credentials = ExchangeCredentials(
            api_key="test_key",
            secret_key="test_secret",
            passphrase="test_passphrase",
            sandbox=True
        )
        
        # 创建交易所实例
        exchange = OKXExchange(credentials)
        print("✓ 交易所实例创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 交易所创建失败: {str(e)}")
        return False

def test_data_models():
    """测试数据模型"""
    print("\n测试数据模型...")
    
    try:
        from app.schemas.trading import OrderCreate, StrategyCreate
        from app.models.trading import OrderSide, OrderType
        
        # 测试订单创建模式
        order_data = OrderCreate(
            account_id="test_account",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            amount=0.01,
            price=50000.0
        )
        print("✓ 订单模型创建成功")
        
        # 测试策略创建模式
        strategy_data = StrategyCreate(
            name="测试策略",
            description="测试用策略",
            strategy_type="grid",
            parameters={
                'grid_size': 0.01,
                'grid_levels': 5,
                'base_amount': 100.0
            },
            symbols=["BTC/USDT"],
            timeframes=["1m"],
            account_id="test_account"
        )
        print("✓ 策略模型创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据模型测试失败: {str(e)}")
        return False

def test_api_structure():
    """测试API结构"""
    print("\n测试API结构...")
    
    try:
        from app.api.endpoints import trading, strategies, accounts
        print("✓ API端点模块导入成功")
        
        # 检查路由器
        if hasattr(trading, 'router'):
            print("✓ 交易API路由器存在")
        if hasattr(strategies, 'router'):
            print("✓ 策略API路由器存在")
        if hasattr(accounts, 'router'):
            print("✓ 账户API路由器存在")
        
        return True
        
    except Exception as e:
        print(f"✗ API结构测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=== 数字货币交易机器人快速测试 ===\n")
    
    tests = [
        ("基础模块导入", test_basic_imports),
        ("策略创建", test_strategy_creation),
        ("交易所创建", test_exchange_creation),
        ("数据模型", test_data_models),
        ("API结构", test_api_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ 测试异常: {str(e)}\n")
    
    print("=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！系统基础功能正常")
        print("\n下一步:")
        print("1. 安装Python依赖: pip install -r backend/requirements.txt")
        print("2. 配置数据库连接")
        print("3. 启动开发服务器")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关配置")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
