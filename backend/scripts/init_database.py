#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import Settings
from app.core.database import Base, get_database_url
from app.models import *  # 导入所有模型


async def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    settings = Settings()
    
    # 解析数据库URL
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        # 获取数据库名称
        db_name = db_url.split("/")[-1]
        # 创建连接到postgres数据库的URL
        postgres_url = db_url.rsplit("/", 1)[0] + "/postgres"
        
        try:
            # 连接到postgres数据库
            engine = create_engine(postgres_url)
            with engine.connect() as conn:
                # 设置自动提交模式
                conn.execute(text("COMMIT"))
                
                # 检查数据库是否存在
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name}
                )
                
                if not result.fetchone():
                    print(f"创建数据库: {db_name}")
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                else:
                    print(f"数据库已存在: {db_name}")
            
            engine.dispose()
            
        except Exception as e:
            print(f"创建数据库失败: {str(e)}")
            return False
    
    return True


async def create_tables():
    """创建数据表"""
    try:
        settings = Settings()
        
        # 创建同步引擎用于创建表
        engine = create_engine(settings.DATABASE_URL)
        
        print("创建数据表...")
        Base.metadata.create_all(bind=engine)
        print("数据表创建完成")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"创建数据表失败: {str(e)}")
        return False


async def create_indexes():
    """创建额外的索引"""
    try:
        settings = Settings()
        engine = create_engine(settings.DATABASE_URL)
        
        print("创建额外索引...")
        
        with engine.connect() as conn:
            # 市场数据索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp 
                ON market_data (symbol, timestamp DESC);
            """))
            
            # 新闻数据索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_news_items_published_relevance 
                ON news_items (published_at DESC, relevance DESC);
            """))
            
            # 大户交易索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_whale_transactions_amount_timestamp 
                ON whale_transactions (amount DESC, timestamp DESC);
            """))
            
            # 系统指标索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp 
                ON system_metrics (timestamp DESC);
            """))
            
            conn.commit()
        
        print("索引创建完成")
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"创建索引失败: {str(e)}")
        return False


async def insert_sample_data():
    """插入示例数据"""
    try:
        settings = Settings()
        engine = create_engine(settings.DATABASE_URL)
        
        print("插入示例数据...")
        
        with engine.connect() as conn:
            # 插入交易对配置
            conn.execute(text("""
                INSERT INTO trading_pairs (symbol, base_currency, quote_currency, is_active, 
                                         min_order_size, price_precision, amount_precision)
                VALUES 
                    ('BTC/USDT', 'BTC', 'USDT', true, 0.00001, 2, 8),
                    ('ETH/USDT', 'ETH', 'USDT', true, 0.0001, 2, 6),
                    ('BNB/USDT', 'BNB', 'USDT', true, 0.001, 2, 6),
                    ('ADA/USDT', 'ADA', 'USDT', true, 1.0, 4, 2),
                    ('SOL/USDT', 'SOL', 'USDT', true, 0.01, 2, 4)
                ON CONFLICT (symbol) DO NOTHING;
            """))
            
            # 插入新闻源配置
            conn.execute(text("""
                INSERT INTO news_sources (name, display_name, source_type, url, rss_url, 
                                        keywords, weight, is_active)
                VALUES 
                    ('coindesk', 'CoinDesk', 'rss', 'https://www.coindesk.com', 
                     'https://www.coindesk.com/arc/outboundfeeds/rss/',
                     '["bitcoin", "ethereum", "crypto", "blockchain", "defi"]', 1.0, true),
                    ('cointelegraph', 'Cointelegraph', 'rss', 'https://cointelegraph.com',
                     'https://cointelegraph.com/rss',
                     '["bitcoin", "ethereum", "altcoin", "trading", "market"]', 0.8, true),
                    ('decrypt', 'Decrypt', 'rss', 'https://decrypt.co',
                     'https://decrypt.co/feed',
                     '["crypto", "web3", "defi", "dao"]', 0.6, true)
                ON CONFLICT (name) DO NOTHING;
            """))
            
            # 插入关键词配置
            conn.execute(text("""
                INSERT INTO news_keywords (keyword, category, weight, importance, sentiment_bias)
                VALUES 
                    ('bitcoin', 'cryptocurrency', 1.0, 0.9, 0.0),
                    ('ethereum', 'cryptocurrency', 1.0, 0.9, 0.0),
                    ('bull market', 'market', 0.8, 0.7, 0.5),
                    ('bear market', 'market', 0.8, 0.7, -0.5),
                    ('crash', 'market', 0.9, 0.8, -0.8),
                    ('pump', 'market', 0.7, 0.6, 0.6),
                    ('dump', 'market', 0.7, 0.6, -0.6),
                    ('regulation', 'policy', 0.8, 0.8, -0.2),
                    ('adoption', 'adoption', 0.7, 0.7, 0.4),
                    ('hack', 'security', 0.9, 0.9, -0.9)
                ON CONFLICT (keyword) DO NOTHING;
            """))
            
            # 插入告警规则
            conn.execute(text("""
                INSERT INTO alert_rules (name, description, category, metric_name, 
                                       operator, threshold, severity, is_active)
                VALUES 
                    ('高CPU使用率', 'CPU使用率超过80%', 'system', 'cpu_usage', '>', 80.0, 'high', true),
                    ('高内存使用率', '内存使用率超过85%', 'system', 'memory_usage', '>', 85.0, 'high', true),
                    ('磁盘空间不足', '磁盘使用率超过90%', 'system', 'disk_usage', '>', 90.0, 'critical', true),
                    ('API响应时间过长', 'API平均响应时间超过1000ms', 'application', 'api_response_time_avg', '>', 1000.0, 'medium', true),
                    ('数据库连接过多', '活跃数据库连接超过50', 'application', 'db_connections_active', '>', 50.0, 'medium', true)
                ON CONFLICT (name) DO NOTHING;
            """))
            
            conn.commit()
        
        print("示例数据插入完成")
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"插入示例数据失败: {str(e)}")
        return False


async def main():
    """主函数"""
    print("开始初始化数据库...")
    
    # 1. 创建数据库
    if not await create_database_if_not_exists():
        print("数据库创建失败，退出")
        return False
    
    # 2. 创建数据表
    if not await create_tables():
        print("数据表创建失败，退出")
        return False
    
    # 3. 创建索引
    if not await create_indexes():
        print("索引创建失败，但继续执行")
    
    # 4. 插入示例数据
    if not await insert_sample_data():
        print("示例数据插入失败，但继续执行")
    
    print("数据库初始化完成！")
    return True


if __name__ == "__main__":
    asyncio.run(main())
