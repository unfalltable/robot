"""
新闻数据源
"""
import asyncio
import aiohttp
import feedparser
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import re
from urllib.parse import urljoin

from .base_data_source import BaseDataSource, DataPoint, DataType, NewsItem

logger = logging.getLogger(__name__)


class CryptoNewsSource(BaseDataSource):
    """加密货币新闻数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("crypto_news", config)
        self.session = None
        self.polling_interval = config.get('polling_interval', 300)  # 5分钟
        self.last_update = {}  # 记录每个源的最后更新时间
        
        # 新闻源配置
        self.news_sources = config.get('news_sources', {
            'coindesk': {
                'rss_url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                'base_url': 'https://www.coindesk.com',
                'keywords': ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'defi']
            },
            'cointelegraph': {
                'rss_url': 'https://cointelegraph.com/rss',
                'base_url': 'https://cointelegraph.com',
                'keywords': ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'altcoin']
            },
            'decrypt': {
                'rss_url': 'https://decrypt.co/feed',
                'base_url': 'https://decrypt.co',
                'keywords': ['bitcoin', 'ethereum', 'crypto', 'nft', 'web3']
            }
        })
        
        # 关键词权重
        self.keyword_weights = {
            'bitcoin': 1.0, 'btc': 1.0,
            'ethereum': 0.9, 'eth': 0.9,
            'crypto': 0.8, 'cryptocurrency': 0.8,
            'blockchain': 0.7,
            'defi': 0.6, 'nft': 0.5,
            'regulation': 0.8, 'sec': 0.8,
            'adoption': 0.7, 'institutional': 0.7
        }
    
    async def connect(self) -> bool:
        """连接到新闻源"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'CryptoTradingBot/1.0'}
            )
            self.logger.info("新闻数据源连接成功")
            return True
        except Exception as e:
            self.logger.error(f"连接新闻源失败: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """断开连接"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.is_running = False
            self.logger.info("新闻数据源断开连接")
            return True
        except Exception as e:
            self.logger.error(f"断开新闻源连接失败: {str(e)}")
            return False
    
    async def start_streaming(self) -> None:
        """开始新闻数据流"""
        if self.is_running:
            return
        
        self.is_running = True
        asyncio.create_task(self._polling_handler())
        self.logger.info("开始新闻数据流")
    
    async def stop_streaming(self) -> None:
        """停止数据流"""
        self.is_running = False
        self.logger.info("停止新闻数据流")
    
    async def _polling_handler(self):
        """轮询处理器"""
        while self.is_running:
            try:
                await self._fetch_all_news()
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                self.logger.error(f"新闻轮询错误: {str(e)}")
                await asyncio.sleep(60)  # 错误时等待1分钟
    
    async def _fetch_all_news(self):
        """获取所有新闻源的新闻"""
        tasks = []
        for source_name, source_config in self.news_sources.items():
            task = asyncio.create_task(
                self._fetch_news_from_source(source_name, source_config)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _fetch_news_from_source(self, source_name: str, source_config: Dict[str, Any]):
        """从单个新闻源获取新闻"""
        try:
            rss_url = source_config['rss_url']
            
            async with self.session.get(rss_url) as response:
                if response.status != 200:
                    self.logger.warning(f"获取RSS失败 {source_name}: HTTP {response.status}")
                    return
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                last_update = self.last_update.get(source_name, datetime.min)
                new_articles = []
                
                for entry in feed.entries:
                    try:
                        # 解析发布时间
                        pub_date = self._parse_date(entry.get('published'))
                        if not pub_date or pub_date <= last_update:
                            continue
                        
                        # 创建新闻条目
                        news_item = NewsItem(
                            title=entry.get('title', ''),
                            content=entry.get('summary', ''),
                            source=source_name,
                            url=entry.get('link'),
                            timestamp=pub_date
                        )
                        
                        # 计算相关性和情绪
                        news_item.relevance = self._calculate_relevance(
                            news_item.title + ' ' + news_item.content,
                            source_config.get('keywords', [])
                        )
                        
                        # 只处理相关性较高的新闻
                        if news_item.relevance >= 0.3:
                            news_item.sentiment = self._analyze_sentiment(
                                news_item.title + ' ' + news_item.content
                            )
                            news_item.keywords = self._extract_keywords(
                                news_item.title + ' ' + news_item.content
                            )
                            
                            new_articles.append(news_item)
                    
                    except Exception as e:
                        self.logger.error(f"处理新闻条目失败 {source_name}: {str(e)}")
                        continue
                
                # 通知订阅者
                for news_item in new_articles:
                    data_point = DataPoint(
                        source=self.name,
                        data_type=DataType.NEWS,
                        symbol=None,
                        timestamp=news_item.timestamp,
                        data=news_item.to_dict(),
                        metadata={'source_name': source_name}
                    )
                    await self.notify_subscribers(data_point)
                
                # 更新最后更新时间
                if new_articles:
                    self.last_update[source_name] = max(
                        article.timestamp for article in new_articles
                    )
                    self.logger.info(f"获取新闻成功 {source_name}: {len(new_articles)} 条")
        
        except Exception as e:
            self.logger.error(f"获取新闻失败 {source_name}: {str(e)}")
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试多种日期格式
            from dateutil import parser as date_parser
            return date_parser.parse(date_str)
        except Exception:
            return None
    
    def _calculate_relevance(self, text: str, keywords: List[str]) -> float:
        """计算新闻相关性"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        relevance_score = 0.0
        
        # 检查配置的关键词
        for keyword in keywords:
            if keyword.lower() in text_lower:
                relevance_score += 0.2
        
        # 检查权重关键词
        for keyword, weight in self.keyword_weights.items():
            count = text_lower.count(keyword.lower())
            relevance_score += count * weight * 0.1
        
        return min(relevance_score, 1.0)
    
    def _analyze_sentiment(self, text: str) -> float:
        """简单的情绪分析"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # 正面词汇
        positive_words = [
            'bullish', 'bull', 'rise', 'rising', 'up', 'gain', 'gains', 'growth',
            'positive', 'optimistic', 'surge', 'rally', 'breakthrough', 'adoption',
            'institutional', 'investment', 'buy', 'buying', 'support'
        ]
        
        # 负面词汇
        negative_words = [
            'bearish', 'bear', 'fall', 'falling', 'down', 'loss', 'losses', 'decline',
            'negative', 'pessimistic', 'crash', 'dump', 'regulation', 'ban', 'banned',
            'sell', 'selling', 'resistance', 'concern', 'worry', 'fear'
        ]
        
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        # 归一化到-1到1之间
        sentiment = (positive_score - negative_score) / max(total_words * 0.1, 1)
        return max(-1.0, min(1.0, sentiment))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.keyword_weights.keys():
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_time: datetime, 
        end_time: datetime,
        **kwargs
    ) -> List[DataPoint]:
        """获取历史新闻数据（新闻源通常不支持历史查询）"""
        self.logger.warning("新闻源不支持历史数据查询")
        return []
    
    def get_supported_symbols(self) -> List[str]:
        """获取支持的交易对（新闻不特定于交易对）"""
        return []
    
    def get_data_types(self) -> List[DataType]:
        """获取支持的数据类型"""
        return [DataType.NEWS]
    
    async def search_news(self, query: str, limit: int = 10) -> List[NewsItem]:
        """搜索新闻（简单实现）"""
        # 这里可以实现更复杂的新闻搜索功能
        # 目前返回空列表
        return []
    
    def add_news_source(self, name: str, config: Dict[str, Any]) -> None:
        """添加新闻源"""
        self.news_sources[name] = config
        self.logger.info(f"添加新闻源: {name}")
    
    def remove_news_source(self, name: str) -> None:
        """移除新闻源"""
        if name in self.news_sources:
            del self.news_sources[name]
            if name in self.last_update:
                del self.last_update[name]
            self.logger.info(f"移除新闻源: {name}")
    
    def get_news_sources(self) -> List[str]:
        """获取所有新闻源名称"""
        return list(self.news_sources.keys())
