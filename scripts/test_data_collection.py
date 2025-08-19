#!/usr/bin/env python3
"""
数据采集模块测试脚本
"""
import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

async def test_market_data_source():
    """测试市场数据源"""
    print("=== 测试市场数据源 ===")
    
    try:
        from data_sources.market_data_source import OKXMarketDataSource
        
        config = {
            'sandbox': True,
            'default_symbols': ['BTC-USDT', 'ETH-USDT'],
            'api_key': 'test_key',
            'secret_key': 'test_secret',
            'passphrase': 'test_passphrase'
        }
        
        source = OKXMarketDataSource(config)
        
        # 测试连接
        connected = await source.connect()
        print(f"连接状态: {'成功' if connected else '失败'}")
        
        if connected:
            # 测试获取支持的交易对
            symbols = source.get_supported_symbols()
            print(f"支持的交易对数量: {len(symbols)}")
            if symbols:
                print(f"示例交易对: {symbols[:5]}")
            
            # 测试历史数据获取
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            historical_data = await source.get_historical_data(
                'BTC/USDT', start_time, end_time, '1m', 10
            )
            print(f"历史数据条数: {len(historical_data)}")
            
            if historical_data:
                latest = historical_data[-1]
                print(f"最新数据: {latest.timestamp} - {latest.data}")
        
        await source.disconnect()
        return True
        
    except Exception as e:
        print(f"市场数据源测试失败: {str(e)}")
        return False

async def test_news_data_source():
    """测试新闻数据源"""
    print("\n=== 测试新闻数据源 ===")
    
    try:
        from data_sources.news_data_source import CryptoNewsSource
        
        config = {
            'polling_interval': 60,
            'news_sources': {
                'coindesk': {
                    'rss_url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                    'base_url': 'https://www.coindesk.com',
                    'keywords': ['bitcoin', 'ethereum', 'crypto']
                }
            }
        }
        
        source = CryptoNewsSource(config)
        
        # 测试连接
        connected = await source.connect()
        print(f"连接状态: {'成功' if connected else '失败'}")
        
        if connected:
            # 测试新闻源
            news_sources = source.get_news_sources()
            print(f"配置的新闻源: {news_sources}")
            
            # 测试获取单个新闻源的新闻
            await source._fetch_news_from_source('coindesk', config['news_sources']['coindesk'])
            print("新闻获取测试完成")
        
        await source.disconnect()
        return True
        
    except Exception as e:
        print(f"新闻数据源测试失败: {str(e)}")
        return False

async def test_whale_monitor():
    """测试大户监控"""
    print("\n=== 测试大户监控 ===")
    
    try:
        from data_sources.whale_monitor import WhaleAlertSource
        
        config = {
            'api_key': None,  # 需要真实API密钥
            'polling_interval': 60,
            'min_amount': 1000000,
            'blockchains': ['bitcoin', 'ethereum']
        }
        
        source = WhaleAlertSource(config)
        
        # 测试基本功能
        supported_symbols = source.get_supported_symbols()
        print(f"支持的币种: {supported_symbols}")
        
        data_types = source.get_data_types()
        print(f"数据类型: {[dt.value for dt in data_types]}")
        
        exchange_addresses = source.get_exchange_addresses()
        print(f"已知交易所地址数量: {len(exchange_addresses)}")
        
        if not config['api_key']:
            print("注意: 需要Whale Alert API密钥才能进行实际测试")
        
        return True
        
    except Exception as e:
        print(f"大户监控测试失败: {str(e)}")
        return False

async def test_data_service():
    """测试数据服务"""
    print("\n=== 测试数据服务 ===")
    
    try:
        from app.services.data_service import DataService
        
        config = {
            'market_data': {
                'enabled': True,
                'default_symbols': ['BTC-USDT', 'ETH-USDT'],
                'sandbox': True
            },
            'news_data': {
                'enabled': True,
                'polling_interval': 300
            },
            'whale_data': {
                'enabled': False,  # 需要API密钥
                'polling_interval': 60,
                'min_amount': 1000000
            }
        }
        
        service = DataService(config)
        
        # 测试基本功能
        supported_symbols = service.get_supported_symbols()
        print(f"支持的交易对数量: {len(supported_symbols)}")
        
        # 测试健康检查
        health = await service.health_check()
        print(f"服务状态: {health.get('service_status', 'unknown')}")
        
        # 测试缓存统计
        cache_stats = service.data_cache.get_cache_stats()
        print(f"缓存统计: {cache_stats}")
        
        return True
        
    except Exception as e:
        print(f"数据服务测试失败: {str(e)}")
        return False

def test_data_models():
    """测试数据模型"""
    print("\n=== 测试数据模型 ===")
    
    try:
        from data_sources.base_data_source import (
            DataPoint, DataType, MarketData, NewsItem, WhaleTransaction
        )
        from datetime import datetime
        
        # 测试市场数据
        market_data = MarketData(
            symbol="BTC/USDT",
            timestamp=datetime.now(),
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=1000.0
        )
        print(f"市场数据模型: {market_data.to_dict()}")
        
        # 测试新闻数据
        news_item = NewsItem(
            title="Bitcoin价格上涨",
            content="Bitcoin今日价格上涨5%",
            source="test_source",
            url="https://example.com",
            timestamp=datetime.now(),
            sentiment=0.5,
            relevance=0.8,
            keywords=["bitcoin", "price"]
        )
        print(f"新闻数据模型: {news_item.to_dict()}")
        
        # 测试大户交易
        whale_tx = WhaleTransaction(
            transaction_hash="0x123456789",
            from_address="0xabc",
            to_address="0xdef",
            amount=1000000.0,
            currency="BTC",
            timestamp=datetime.now(),
            exchange_from="Unknown",
            exchange_to="Binance"
        )
        print(f"大户交易模型: {whale_tx.to_dict()}")
        
        # 测试数据点
        data_point = DataPoint(
            source="test_source",
            data_type=DataType.MARKET_DATA,
            symbol="BTC/USDT",
            timestamp=datetime.now(),
            data=market_data.to_dict()
        )
        print(f"数据点模型: {data_point.source}, {data_point.data_type.value}")
        
        return True
        
    except Exception as e:
        print(f"数据模型测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("=== 数据采集模块测试 ===\n")
    
    tests = [
        ("数据模型", test_data_models),
        ("市场数据源", test_market_data_source),
        ("新闻数据源", test_news_data_source),
        ("大户监控", test_whale_monitor),
        ("数据服务", test_data_service),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"运行测试: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"✗ {test_name} 测试失败")
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {str(e)}")
        
        print()
    
    print("=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！数据采集模块功能正常")
        print("\n下一步:")
        print("1. 配置真实的API密钥（OKX、Whale Alert等）")
        print("2. 启动数据服务进行实时测试")
        print("3. 集成到主交易系统")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关配置")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
