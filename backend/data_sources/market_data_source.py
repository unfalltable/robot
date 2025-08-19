"""
市场数据源
"""
import asyncio
import ccxt
import websockets
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .base_data_source import BaseDataSource, DataPoint, DataType, MarketData

logger = logging.getLogger(__name__)


class OKXMarketDataSource(BaseDataSource):
    """OKX市场数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("okx_market", config)
        self.exchange = None
        self.websocket = None
        self.subscribed_symbols = set()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    async def connect(self) -> bool:
        """连接到OKX"""
        try:
            # 初始化CCXT交易所实例
            self.exchange = ccxt.okx({
                'apiKey': self.config.get('api_key'),
                'secret': self.config.get('secret_key'),
                'password': self.config.get('passphrase'),
                'sandbox': self.config.get('sandbox', True),
                'enableRateLimit': True,
            })
            
            # 测试连接
            await self.exchange.load_markets()
            self.logger.info("OKX市场数据源连接成功")
            return True
            
        except Exception as e:
            self.logger.error(f"连接OKX失败: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """断开连接"""
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            if self.exchange:
                await self.exchange.close()
                self.exchange = None
            
            self.is_running = False
            self.logger.info("OKX市场数据源断开连接")
            return True
            
        except Exception as e:
            self.logger.error(f"断开OKX连接失败: {str(e)}")
            return False
    
    async def start_streaming(self) -> None:
        """开始WebSocket数据流"""
        if self.is_running:
            return
        
        self.is_running = True
        asyncio.create_task(self._websocket_handler())
        self.logger.info("开始OKX WebSocket数据流")
    
    async def stop_streaming(self) -> None:
        """停止数据流"""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
        self.logger.info("停止OKX WebSocket数据流")
    
    async def _websocket_handler(self):
        """WebSocket处理器"""
        while self.is_running:
            try:
                await self._connect_websocket()
                await self._listen_websocket()
            except Exception as e:
                self.logger.error(f"WebSocket错误: {str(e)}")
                await self._handle_reconnect()
    
    async def _connect_websocket(self):
        """连接WebSocket"""
        ws_url = "wss://ws.okx.com:8443/ws/v5/public"
        if self.config.get('sandbox', True):
            ws_url = "wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999"
        
        self.websocket = await websockets.connect(ws_url)
        self.logger.info("WebSocket连接建立")
        
        # 订阅默认交易对
        default_symbols = self.config.get('default_symbols', ['BTC-USDT', 'ETH-USDT'])
        for symbol in default_symbols:
            await self._subscribe_symbol(symbol)
    
    async def _subscribe_symbol(self, symbol: str):
        """订阅交易对"""
        if not self.websocket:
            return
        
        # 订阅K线数据
        subscribe_msg = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "candle1m",
                    "instId": symbol
                },
                {
                    "channel": "tickers",
                    "instId": symbol
                }
            ]
        }
        
        await self.websocket.send(json.dumps(subscribe_msg))
        self.subscribed_symbols.add(symbol)
        self.logger.info(f"订阅交易对: {symbol}")
    
    async def _listen_websocket(self):
        """监听WebSocket消息"""
        async for message in self.websocket:
            try:
                data = json.loads(message)
                await self._process_websocket_message(data)
            except Exception as e:
                self.logger.error(f"处理WebSocket消息失败: {str(e)}")
    
    async def _process_websocket_message(self, data: Dict[str, Any]):
        """处理WebSocket消息"""
        if 'data' not in data:
            return
        
        channel = data.get('arg', {}).get('channel')
        
        if channel == 'candle1m':
            await self._process_kline_data(data)
        elif channel == 'tickers':
            await self._process_ticker_data(data)
    
    async def _process_kline_data(self, data: Dict[str, Any]):
        """处理K线数据"""
        try:
            symbol = data['arg']['instId']
            for kline in data['data']:
                timestamp = datetime.fromtimestamp(int(kline[0]) / 1000)
                
                market_data = MarketData(
                    symbol=symbol.replace('-', '/'),
                    timestamp=timestamp,
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5]),
                    timeframe="1m"
                )
                
                data_point = DataPoint(
                    source=self.name,
                    data_type=DataType.MARKET_DATA,
                    symbol=market_data.symbol,
                    timestamp=timestamp,
                    data=market_data.to_dict()
                )
                
                await self.notify_subscribers(data_point)
                
        except Exception as e:
            self.logger.error(f"处理K线数据失败: {str(e)}")
    
    async def _process_ticker_data(self, data: Dict[str, Any]):
        """处理Ticker数据"""
        try:
            symbol = data['arg']['instId']
            for ticker in data['data']:
                timestamp = datetime.fromtimestamp(int(ticker['ts']) / 1000)
                
                ticker_data = {
                    'symbol': symbol.replace('-', '/'),
                    'last_price': float(ticker['last']),
                    'bid_price': float(ticker['bidPx']),
                    'ask_price': float(ticker['askPx']),
                    'volume_24h': float(ticker['vol24h']),
                    'change_24h': float(ticker['chg24h']),
                    'timestamp': timestamp.isoformat()
                }
                
                data_point = DataPoint(
                    source=self.name,
                    data_type=DataType.MARKET_DATA,
                    symbol=ticker_data['symbol'],
                    timestamp=timestamp,
                    data=ticker_data,
                    metadata={'data_subtype': 'ticker'}
                )
                
                await self.notify_subscribers(data_point)
                
        except Exception as e:
            self.logger.error(f"处理Ticker数据失败: {str(e)}")
    
    async def _handle_reconnect(self):
        """处理重连"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error("达到最大重连次数，停止重连")
            self.is_running = False
            return
        
        self.reconnect_attempts += 1
        wait_time = min(2 ** self.reconnect_attempts, 60)  # 指数退避，最大60秒
        
        self.logger.info(f"等待 {wait_time} 秒后重连 (尝试 {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        await asyncio.sleep(wait_time)
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_time: datetime, 
        end_time: datetime,
        timeframe: str = '1m',
        limit: int = 1000
    ) -> List[DataPoint]:
        """获取历史K线数据"""
        try:
            if not self.exchange:
                await self.connect()
            
            # 转换symbol格式
            okx_symbol = symbol.replace('/', '-')
            
            # 获取历史数据
            since = int(start_time.timestamp() * 1000)
            ohlcv_data = await self.exchange.fetch_ohlcv(
                okx_symbol, 
                timeframe, 
                since=since, 
                limit=limit
            )
            
            data_points = []
            for ohlcv in ohlcv_data:
                timestamp = datetime.fromtimestamp(ohlcv[0] / 1000)
                
                # 检查时间范围
                if timestamp < start_time or timestamp > end_time:
                    continue
                
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=timestamp,
                    open=float(ohlcv[1]),
                    high=float(ohlcv[2]),
                    low=float(ohlcv[3]),
                    close=float(ohlcv[4]),
                    volume=float(ohlcv[5]),
                    timeframe=timeframe
                )
                
                data_point = DataPoint(
                    source=self.name,
                    data_type=DataType.MARKET_DATA,
                    symbol=symbol,
                    timestamp=timestamp,
                    data=market_data.to_dict()
                )
                
                data_points.append(data_point)
            
            self.logger.info(f"获取历史数据成功: {symbol}, {len(data_points)} 条记录")
            return data_points
            
        except Exception as e:
            self.logger.error(f"获取历史数据失败: {str(e)}")
            return []
    
    def get_supported_symbols(self) -> List[str]:
        """获取支持的交易对"""
        if not self.exchange or not self.exchange.markets:
            return []
        
        return [symbol for symbol in self.exchange.markets.keys() if '/USDT' in symbol]
    
    def get_data_types(self) -> List[DataType]:
        """获取支持的数据类型"""
        return [DataType.MARKET_DATA]
    
    async def subscribe_symbol(self, symbol: str) -> bool:
        """动态订阅交易对"""
        try:
            okx_symbol = symbol.replace('/', '-')
            await self._subscribe_symbol(okx_symbol)
            return True
        except Exception as e:
            self.logger.error(f"订阅交易对失败 {symbol}: {str(e)}")
            return False
    
    async def unsubscribe_symbol(self, symbol: str) -> bool:
        """取消订阅交易对"""
        try:
            if not self.websocket:
                return False
            
            okx_symbol = symbol.replace('/', '-')
            unsubscribe_msg = {
                "op": "unsubscribe",
                "args": [
                    {
                        "channel": "candle1m",
                        "instId": okx_symbol
                    },
                    {
                        "channel": "tickers",
                        "instId": okx_symbol
                    }
                ]
            }
            
            await self.websocket.send(json.dumps(unsubscribe_msg))
            self.subscribed_symbols.discard(okx_symbol)
            self.logger.info(f"取消订阅交易对: {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"取消订阅交易对失败 {symbol}: {str(e)}")
            return False
