"""
数据API端点
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.services.data_service import DataService
from data_sources.base_data_source import DataType

router = APIRouter()

# 全局数据服务实例（在实际应用中应该通过依赖注入）
_data_service: Optional[DataService] = None


def get_data_service() -> DataService:
    """获取数据服务实例"""
    global _data_service
    if _data_service is None:
        # 这里应该从配置中读取
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
        _data_service = DataService(config)
    return _data_service


class MarketDataResponse(BaseModel):
    """市场数据响应"""
    symbol: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str


class NewsResponse(BaseModel):
    """新闻响应"""
    title: str
    content: str
    source: str
    url: Optional[str]
    timestamp: str
    sentiment: Optional[float]
    relevance: Optional[float]
    keywords: List[str]


class WhaleAlertResponse(BaseModel):
    """大户交易响应"""
    transaction_hash: str
    from_address: str
    to_address: str
    amount: float
    currency: str
    timestamp: str
    exchange_from: Optional[str]
    exchange_to: Optional[str]


@router.get("/health")
async def get_data_health(
    data_service: DataService = Depends(get_data_service)
):
    """获取数据服务健康状态"""
    return await data_service.health_check()


@router.post("/start")
async def start_data_service(
    data_service: DataService = Depends(get_data_service)
):
    """启动数据服务"""
    success = await data_service.start()
    if not success:
        raise HTTPException(status_code=500, detail="启动数据服务失败")
    return {"message": "数据服务启动成功"}


@router.post("/stop")
async def stop_data_service(
    data_service: DataService = Depends(get_data_service)
):
    """停止数据服务"""
    success = await data_service.stop()
    if not success:
        raise HTTPException(status_code=500, detail="停止数据服务失败")
    return {"message": "数据服务停止成功"}


@router.get("/symbols")
async def get_supported_symbols(
    data_service: DataService = Depends(get_data_service)
) -> List[str]:
    """获取支持的交易对"""
    return data_service.get_supported_symbols()


@router.post("/symbols/{symbol}/subscribe")
async def subscribe_symbol(
    symbol: str,
    data_service: DataService = Depends(get_data_service)
):
    """订阅交易对"""
    success = await data_service.subscribe_symbol(symbol)
    if not success:
        raise HTTPException(status_code=400, detail=f"订阅交易对失败: {symbol}")
    return {"message": f"订阅交易对成功: {symbol}"}


@router.get("/market/{symbol}")
async def get_market_data(
    symbol: str,
    count: int = Query(100, ge=1, le=1000, description="数据条数"),
    data_service: DataService = Depends(get_data_service)
) -> List[Dict[str, Any]]:
    """获取市场数据"""
    data = await data_service.get_market_data(symbol, count)
    return data


@router.get("/market/{symbol}/historical")
async def get_historical_market_data(
    symbol: str,
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    timeframe: str = Query("1m", description="时间周期"),
    limit: int = Query(1000, ge=1, le=5000, description="最大条数"),
    data_service: DataService = Depends(get_data_service)
) -> List[Dict[str, Any]]:
    """获取历史市场数据"""
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(days=1)
    
    data = await data_service.get_historical_data(
        DataType.MARKET_DATA,
        symbol=symbol,
        start_time=start_time,
        end_time=end_time,
        timeframe=timeframe,
        limit=limit
    )
    return data


@router.get("/news")
async def get_news_data(
    count: int = Query(50, ge=1, le=200, description="新闻条数"),
    data_service: DataService = Depends(get_data_service)
) -> List[Dict[str, Any]]:
    """获取新闻数据"""
    data = await data_service.get_news_data(count)
    return data


@router.get("/news/historical")
async def get_historical_news_data(
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    data_service: DataService = Depends(get_data_service)
) -> List[Dict[str, Any]]:
    """获取历史新闻数据"""
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(days=1)
    
    data = await data_service.get_historical_data(
        DataType.NEWS,
        start_time=start_time,
        end_time=end_time
    )
    return data


@router.get("/whale-alerts")
async def get_whale_alerts(
    count: int = Query(20, ge=1, le=100, description="大户交易条数"),
    data_service: DataService = Depends(get_data_service)
) -> List[Dict[str, Any]]:
    """获取大户交易数据"""
    data = await data_service.get_whale_alerts(count)
    return data


@router.get("/whale-alerts/historical")
async def get_historical_whale_alerts(
    symbol: Optional[str] = Query(None, description="币种"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    data_service: DataService = Depends(get_data_service)
) -> List[Dict[str, Any]]:
    """获取历史大户交易数据"""
    if not end_time:
        end_time = datetime.now()
    if not start_time:
        start_time = end_time - timedelta(days=1)
    
    data = await data_service.get_historical_data(
        DataType.WHALE_ALERT,
        symbol=symbol,
        start_time=start_time,
        end_time=end_time
    )
    return data


@router.get("/whale-alerts/stats/{currency}")
async def get_whale_stats(
    currency: str,
    hours: int = Query(24, ge=1, le=168, description="统计时间范围（小时）"),
    data_service: DataService = Depends(get_data_service)
) -> Dict[str, Any]:
    """获取大户交易统计"""
    # 获取whale alert数据源
    whale_source = data_service.data_manager.get_data_source("whale_alert")
    if not whale_source:
        raise HTTPException(status_code=404, detail="大户监控数据源未启用")
    
    if not hasattr(whale_source, 'get_whale_stats'):
        raise HTTPException(status_code=500, detail="数据源不支持统计功能")
    
    stats = await whale_source.get_whale_stats(currency, hours)
    if not stats:
        raise HTTPException(status_code=404, detail="获取统计数据失败")
    
    return stats


@router.get("/summary")
async def get_data_summary(
    data_service: DataService = Depends(get_data_service)
) -> Dict[str, Any]:
    """获取数据摘要"""
    try:
        # 获取最新的市场数据
        btc_data = await data_service.get_market_data("BTC/USDT", 1)
        eth_data = await data_service.get_market_data("ETH/USDT", 1)
        
        # 获取最新新闻
        latest_news = await data_service.get_news_data(5)
        
        # 获取最新大户交易
        latest_whale_alerts = await data_service.get_whale_alerts(5)
        
        # 获取健康状态
        health = await data_service.health_check()
        
        return {
            "market_data": {
                "btc_latest": btc_data[0] if btc_data else None,
                "eth_latest": eth_data[0] if eth_data else None
            },
            "latest_news": latest_news,
            "latest_whale_alerts": latest_whale_alerts,
            "service_health": health,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据摘要失败: {str(e)}")


@router.get("/cache/stats")
async def get_cache_stats(
    data_service: DataService = Depends(get_data_service)
) -> Dict[str, Any]:
    """获取缓存统计"""
    return data_service.data_cache.get_cache_stats()


# WebSocket端点用于实时数据推送
@router.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket实时数据推送"""
    await websocket.accept()
    
    data_service = get_data_service()
    
    async def data_handler(data_point):
        """数据处理器"""
        try:
            message = {
                "type": data_point.data_type.value,
                "symbol": data_point.symbol,
                "timestamp": data_point.timestamp.isoformat(),
                "data": data_point.data
            }
            await websocket.send_json(message)
        except Exception as e:
            print(f"WebSocket发送失败: {str(e)}")
    
    # 订阅数据更新
    data_service.subscribe(data_handler)
    
    try:
        while True:
            # 保持连接
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket连接断开: {str(e)}")
    finally:
        # 取消订阅
        data_service.unsubscribe(data_handler)
