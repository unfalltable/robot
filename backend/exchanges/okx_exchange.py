"""
OKX交易所接口实现
"""
import ccxt
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from .base_exchange import (
    BaseExchange, ExchangeCredentials, OrderRequest, OrderResponse,
    Balance, Position, Ticker
)
from app.core.logging import exchange_logger


class OKXExchange(BaseExchange):
    """OKX交易所实现"""
    
    def __init__(self, credentials: ExchangeCredentials):
        super().__init__(credentials)
        self.exchange = None
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """初始化交易所连接"""
        try:
            self.exchange = ccxt.okx({
                'apiKey': self.credentials.api_key,
                'secret': self.credentials.secret_key,
                'password': self.credentials.passphrase,
                'sandbox': self.credentials.sandbox,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # spot, margin, swap, future
                }
            })
            exchange_logger.info("OKX交易所初始化成功")
        except Exception as e:
            exchange_logger.error(f"OKX交易所初始化失败: {str(e)}")
            raise
    
    async def connect(self) -> bool:
        """连接到交易所"""
        try:
            # 测试连接
            await self.get_account_info()
            exchange_logger.info("OKX交易所连接成功")
            return True
        except Exception as e:
            exchange_logger.error(f"OKX交易所连接失败: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """断开连接"""
        try:
            if self.exchange:
                await self.exchange.close()
            exchange_logger.info("OKX交易所连接已断开")
            return True
        except Exception as e:
            exchange_logger.error(f"OKX交易所断开连接失败: {str(e)}")
            return False
    
    async def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        try:
            account_info = await self.exchange.fetch_account()
            exchange_logger.info("获取OKX账户信息成功")
            return account_info
        except Exception as e:
            exchange_logger.error(f"获取OKX账户信息失败: {str(e)}")
            raise
    
    async def get_balances(self) -> List[Balance]:
        """获取余额"""
        try:
            balances_data = await self.exchange.fetch_balance()
            balances = []
            
            for currency, balance_info in balances_data.items():
                if currency not in ['info', 'free', 'used', 'total']:
                    balances.append(Balance(
                        currency=currency,
                        free=balance_info.get('free', 0.0),
                        used=balance_info.get('used', 0.0),
                        total=balance_info.get('total', 0.0)
                    ))
            
            exchange_logger.info(f"获取OKX余额成功，共{len(balances)}个币种")
            return balances
        except Exception as e:
            exchange_logger.error(f"获取OKX余额失败: {str(e)}")
            raise
    
    async def get_positions(self) -> List[Position]:
        """获取持仓"""
        try:
            positions_data = await self.exchange.fetch_positions()
            positions = []
            
            for pos_data in positions_data:
                if pos_data['contracts'] > 0:  # 只返回有持仓的
                    positions.append(Position(
                        symbol=pos_data['symbol'],
                        side=pos_data['side'],
                        size=pos_data['contracts'],
                        entry_price=pos_data['entryPrice'] or 0.0,
                        mark_price=pos_data['markPrice'] or 0.0,
                        unrealized_pnl=pos_data['unrealizedPnl'] or 0.0,
                        percentage=pos_data['percentage'] or 0.0
                    ))
            
            exchange_logger.info(f"获取OKX持仓成功，共{len(positions)}个持仓")
            return positions
        except Exception as e:
            exchange_logger.error(f"获取OKX持仓失败: {str(e)}")
            raise
    
    async def create_order(self, order: OrderRequest) -> OrderResponse:
        """创建订单"""
        try:
            # 构建订单参数
            order_params = {
                'symbol': order.symbol,
                'type': order.type,
                'side': order.side,
                'amount': order.amount,
            }
            
            if order.price:
                order_params['price'] = order.price
            
            if order.params:
                order_params.update(order.params)
            
            # 创建订单
            result = await self.exchange.create_order(**order_params)
            
            # 转换为标准格式
            order_response = OrderResponse(
                id=result['id'],
                symbol=result['symbol'],
                side=result['side'],
                type=result['type'],
                amount=result['amount'],
                price=result.get('price'),
                status=result['status'],
                filled=result.get('filled', 0.0),
                remaining=result.get('remaining', result['amount']),
                timestamp=datetime.fromtimestamp(result['timestamp'] / 1000),
                info=result['info']
            )
            
            exchange_logger.info(f"OKX订单创建成功: {result['id']}")
            return order_response
            
        except Exception as e:
            exchange_logger.error(f"OKX订单创建失败: {str(e)}")
            raise
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """取消订单"""
        try:
            await self.exchange.cancel_order(order_id, symbol)
            exchange_logger.info(f"OKX订单取消成功: {order_id}")
            return True
        except Exception as e:
            exchange_logger.error(f"OKX订单取消失败: {order_id}, {str(e)}")
            raise
    
    async def get_order(self, order_id: str, symbol: str) -> Optional[OrderResponse]:
        """获取订单信息"""
        try:
            result = await self.exchange.fetch_order(order_id, symbol)
            
            order_response = OrderResponse(
                id=result['id'],
                symbol=result['symbol'],
                side=result['side'],
                type=result['type'],
                amount=result['amount'],
                price=result.get('price'),
                status=result['status'],
                filled=result.get('filled', 0.0),
                remaining=result.get('remaining', result['amount']),
                timestamp=datetime.fromtimestamp(result['timestamp'] / 1000),
                info=result['info']
            )
            
            return order_response
            
        except Exception as e:
            exchange_logger.error(f"获取OKX订单失败: {order_id}, {str(e)}")
            return None
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderResponse]:
        """获取未完成订单"""
        try:
            orders_data = await self.exchange.fetch_open_orders(symbol)
            orders = []
            
            for order_data in orders_data:
                orders.append(OrderResponse(
                    id=order_data['id'],
                    symbol=order_data['symbol'],
                    side=order_data['side'],
                    type=order_data['type'],
                    amount=order_data['amount'],
                    price=order_data.get('price'),
                    status=order_data['status'],
                    filled=order_data.get('filled', 0.0),
                    remaining=order_data.get('remaining', order_data['amount']),
                    timestamp=datetime.fromtimestamp(order_data['timestamp'] / 1000),
                    info=order_data['info']
                ))
            
            exchange_logger.info(f"获取OKX未完成订单成功，共{len(orders)}个")
            return orders
            
        except Exception as e:
            exchange_logger.error(f"获取OKX未完成订单失败: {str(e)}")
            raise
    
    async def get_order_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[OrderResponse]:
        """获取订单历史"""
        try:
            orders_data = await self.exchange.fetch_orders(symbol, limit=limit)
            orders = []
            
            for order_data in orders_data:
                orders.append(OrderResponse(
                    id=order_data['id'],
                    symbol=order_data['symbol'],
                    side=order_data['side'],
                    type=order_data['type'],
                    amount=order_data['amount'],
                    price=order_data.get('price'),
                    status=order_data['status'],
                    filled=order_data.get('filled', 0.0),
                    remaining=order_data.get('remaining', order_data['amount']),
                    timestamp=datetime.fromtimestamp(order_data['timestamp'] / 1000),
                    info=order_data['info']
                ))
            
            exchange_logger.info(f"获取OKX订单历史成功，共{len(orders)}个")
            return orders
            
        except Exception as e:
            exchange_logger.error(f"获取OKX订单历史失败: {str(e)}")
            raise
    
    async def get_ticker(self, symbol: str) -> Ticker:
        """获取行情"""
        try:
            ticker_data = await self.exchange.fetch_ticker(symbol)
            
            ticker = Ticker(
                symbol=ticker_data['symbol'],
                last=ticker_data['last'],
                bid=ticker_data['bid'],
                ask=ticker_data['ask'],
                high=ticker_data['high'],
                low=ticker_data['low'],
                volume=ticker_data['baseVolume'],
                change=ticker_data['change'],
                percentage=ticker_data['percentage'],
                timestamp=datetime.fromtimestamp(ticker_data['timestamp'] / 1000)
            )
            
            return ticker
            
        except Exception as e:
            exchange_logger.error(f"获取OKX行情失败: {symbol}, {str(e)}")
            raise
    
    async def get_tickers(self) -> List[Ticker]:
        """获取所有行情"""
        try:
            tickers_data = await self.exchange.fetch_tickers()
            tickers = []
            
            for symbol, ticker_data in tickers_data.items():
                tickers.append(Ticker(
                    symbol=ticker_data['symbol'],
                    last=ticker_data['last'],
                    bid=ticker_data['bid'],
                    ask=ticker_data['ask'],
                    high=ticker_data['high'],
                    low=ticker_data['low'],
                    volume=ticker_data['baseVolume'],
                    change=ticker_data['change'],
                    percentage=ticker_data['percentage'],
                    timestamp=datetime.fromtimestamp(ticker_data['timestamp'] / 1000)
                ))
            
            exchange_logger.info(f"获取OKX所有行情成功，共{len(tickers)}个")
            return tickers
            
        except Exception as e:
            exchange_logger.error(f"获取OKX所有行情失败: {str(e)}")
            raise
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """获取订单簿"""
        try:
            orderbook = await self.exchange.fetch_order_book(symbol, limit)
            return orderbook
        except Exception as e:
            exchange_logger.error(f"获取OKX订单簿失败: {symbol}, {str(e)}")
            raise
    
    async def get_klines(self, symbol: str, timeframe: str, limit: int = 100) -> List[List[float]]:
        """获取K线数据"""
        try:
            klines = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return klines
        except Exception as e:
            exchange_logger.error(f"获取OKX K线数据失败: {symbol}, {str(e)}")
            raise
    
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近交易"""
        try:
            trades = await self.exchange.fetch_trades(symbol, limit=limit)
            return trades
        except Exception as e:
            exchange_logger.error(f"获取OKX最近交易失败: {symbol}, {str(e)}")
            raise
