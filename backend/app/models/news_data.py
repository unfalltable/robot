"""
新闻数据模型
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, Text, Boolean, Index, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class NewsItem(Base):
    """新闻条目模型"""
    __tablename__ = "news_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 基本信息
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text)  # 摘要
    source = Column(String(100), nullable=False, index=True)
    author = Column(String(200))
    url = Column(String(1000), unique=True, index=True)
    
    # 时间信息
    published_at = Column(DateTime, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 分析结果
    sentiment = Column(Float)  # 情绪分数 -1到1
    relevance = Column(Float)  # 相关性分数 0到1
    importance = Column(Float)  # 重要性分数 0到1
    
    # 关键词和标签
    keywords = Column(JSON)  # 关键词列表
    tags = Column(JSON)      # 标签列表
    symbols = Column(JSON)   # 相关交易对
    
    # 分类信息
    category = Column(String(50), index=True)  # 新闻分类
    language = Column(String(10), default='en')
    region = Column(String(50))  # 地区
    
    # 统计信息
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    
    # 处理状态
    is_processed = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(Integer)  # 重复新闻的原始ID
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_source_published', 'source', 'published_at'),
        Index('idx_sentiment_relevance', 'sentiment', 'relevance'),
        Index('idx_category_timestamp', 'category', 'timestamp'),
    )


class NewsSource(Base):
    """新闻源配置模型"""
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(200), nullable=False)
    
    # 源配置
    source_type = Column(String(20), nullable=False)  # rss, api, scraper
    url = Column(String(1000), nullable=False)
    base_url = Column(String(500))
    
    # RSS配置
    rss_url = Column(String(1000))
    
    # API配置
    api_key = Column(String(500))
    api_endpoint = Column(String(1000))
    api_params = Column(JSON)
    
    # 爬虫配置
    scraper_config = Column(JSON)
    
    # 处理配置
    keywords = Column(JSON)  # 关键词列表
    weight = Column(Float, default=1.0)  # 权重
    language = Column(String(10), default='en')
    region = Column(String(50))
    
    # 状态信息
    is_active = Column(Boolean, default=True)
    last_fetch = Column(DateTime)
    last_success = Column(DateTime)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    
    # 统计信息
    total_articles = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)
    avg_latency = Column(Float)  # 平均延迟(秒)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class NewsKeyword(Base):
    """新闻关键词模型"""
    __tablename__ = "news_keywords"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(100), nullable=False, unique=True, index=True)
    
    # 分类信息
    category = Column(String(50), index=True)
    subcategory = Column(String(50))
    
    # 权重和重要性
    weight = Column(Float, default=1.0)
    importance = Column(Float, default=0.5)
    
    # 情绪倾向
    sentiment_bias = Column(Float, default=0.0)  # -1到1
    
    # 相关交易对
    related_symbols = Column(JSON)
    
    # 统计信息
    frequency = Column(Integer, default=0)  # 出现频次
    last_seen = Column(DateTime)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class NewsAnalysis(Base):
    """新闻分析结果模型"""
    __tablename__ = "news_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, nullable=False, index=True)
    
    # 情绪分析
    sentiment_score = Column(Float)  # 总体情绪分数
    sentiment_confidence = Column(Float)  # 情绪分析置信度
    sentiment_details = Column(JSON)  # 详细情绪分析
    
    # 实体识别
    entities = Column(JSON)  # 识别的实体
    persons = Column(JSON)   # 人物
    organizations = Column(JSON)  # 组织
    locations = Column(JSON)  # 地点
    cryptocurrencies = Column(JSON)  # 加密货币
    
    # 主题分析
    topics = Column(JSON)    # 主题列表
    topic_scores = Column(JSON)  # 主题分数
    
    # 影响分析
    market_impact = Column(Float)  # 市场影响预测
    price_impact = Column(Float)   # 价格影响预测
    volume_impact = Column(Float)  # 成交量影响预测
    
    # 相关性分析
    symbol_relevance = Column(JSON)  # 各交易对相关性
    
    # 分析模型信息
    model_version = Column(String(50))
    analysis_timestamp = Column(DateTime, default=func.now())
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_news_analysis', 'news_id', 'analysis_timestamp'),
    )


class SocialMediaPost(Base):
    """社交媒体帖子模型"""
    __tablename__ = "social_media_posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 基本信息
    platform = Column(String(50), nullable=False, index=True)  # twitter, reddit, telegram
    post_id = Column(String(200), nullable=False, index=True)
    author = Column(String(200))
    author_id = Column(String(200))
    
    # 内容信息
    content = Column(Text, nullable=False)
    url = Column(String(1000))
    
    # 统计信息
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    followers = Column(Integer, default=0)  # 作者粉丝数
    
    # 分析结果
    sentiment = Column(Float)
    relevance = Column(Float)
    influence_score = Column(Float)  # 影响力分数
    
    # 关键词和标签
    keywords = Column(JSON)
    hashtags = Column(JSON)
    mentions = Column(JSON)
    symbols = Column(JSON)
    
    # 时间信息
    posted_at = Column(DateTime, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 处理状态
    is_processed = Column(Boolean, default=False)
    is_spam = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    
    # 复合索引
    __table_args__ = (
        Index('idx_platform_posted', 'platform', 'posted_at'),
        Index('idx_platform_post_id', 'platform', 'post_id'),
    )


class NewsAlert(Base):
    """新闻告警模型"""
    __tablename__ = "news_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 告警配置
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 触发条件
    keywords = Column(JSON)  # 关键词条件
    sentiment_threshold = Column(Float)  # 情绪阈值
    relevance_threshold = Column(Float)  # 相关性阈值
    importance_threshold = Column(Float)  # 重要性阈值
    
    # 过滤条件
    sources = Column(JSON)  # 指定新闻源
    categories = Column(JSON)  # 指定分类
    symbols = Column(JSON)  # 指定交易对
    
    # 告警设置
    is_active = Column(Boolean, default=True)
    notification_channels = Column(JSON)  # 通知渠道
    cooldown_minutes = Column(Integer, default=60)  # 冷却时间
    
    # 统计信息
    trigger_count = Column(Integer, default=0)
    last_triggered = Column(DateTime)
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class NewsAlertLog(Base):
    """新闻告警日志模型"""
    __tablename__ = "news_alert_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(Integer, nullable=False, index=True)
    news_id = Column(Integer, nullable=False, index=True)
    
    # 触发信息
    trigger_reason = Column(Text)
    matched_keywords = Column(JSON)
    sentiment_score = Column(Float)
    relevance_score = Column(Float)
    importance_score = Column(Float)
    
    # 通知状态
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSON)
    notification_error = Column(Text)
    
    # 时间戳
    triggered_at = Column(DateTime, default=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_alert_triggered', 'alert_id', 'triggered_at'),
    )
