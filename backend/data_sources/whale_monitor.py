"""
大户监控数据源
"""
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .base_data_source import BaseDataSource, DataPoint, DataType, WhaleTransaction

logger = logging.getLogger(__name__)


class WhaleAlertSource(BaseDataSource):
    """Whale Alert大户监控数据源"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("whale_alert", config)
        self.api_key = config.get('api_key')
        self.session = None
        self.polling_interval = config.get('polling_interval', 60)  # 1分钟
        self.min_amount = config.get('min_amount', 1000000)  # 最小金额100万美元
        self.last_timestamp = None
        
        # 支持的区块链
        self.supported_blockchains = config.get('blockchains', [
            'bitcoin', 'ethereum', 'tron', 'bsc', 'polygon'
        ])
        
        # 交易所地址映射（简化版）
        self.exchange_addresses = {
            # Bitcoin
            '1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ': 'Bitfinex',
            '3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS': 'Binance',
            '3LYJfcfHPXYJreMsASk2jkn69LWEYKzexb': 'Bittrex',
            
            # Ethereum
            '0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be': 'Binance',
            '0xd551234ae421e3bcba99a0da6d736074f22192ff': 'Binance',
            '0x564286362092d8e7936f0549571a803b203aaced': 'Binance',
            '0x0681d8db095565fe8a346fa0277bffde9c0edbbf': 'Kraken',
            '0xe93381fb4c4f14bda253907b18fad305d799241a': 'Huobi',
        }
    
    async def connect(self) -> bool:
        """连接到Whale Alert API"""
        try:
            if not self.api_key:
                self.logger.error("Whale Alert API密钥未配置")
                return False
            
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'CryptoTradingBot/1.0'}
            )
            
            # 测试API连接
            test_url = f"https://api.whale-alert.io/v1/status?api_key={self.api_key}"
            async with self.session.get(test_url) as response:
                if response.status == 200:
                    self.logger.info("Whale Alert连接成功")
                    return True
                else:
                    self.logger.error(f"Whale Alert API测试失败: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"连接Whale Alert失败: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """断开连接"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.is_running = False
            self.logger.info("Whale Alert断开连接")
            return True
        except Exception as e:
            self.logger.error(f"断开Whale Alert连接失败: {str(e)}")
            return False
    
    async def start_streaming(self) -> None:
        """开始大户监控数据流"""
        if self.is_running:
            return
        
        self.is_running = True
        self.last_timestamp = int(datetime.now().timestamp())
        asyncio.create_task(self._polling_handler())
        self.logger.info("开始大户监控数据流")
    
    async def stop_streaming(self) -> None:
        """停止数据流"""
        self.is_running = False
        self.logger.info("停止大户监控数据流")
    
    async def _polling_handler(self):
        """轮询处理器"""
        while self.is_running:
            try:
                await self._fetch_whale_transactions()
                await asyncio.sleep(self.polling_interval)
            except Exception as e:
                self.logger.error(f"大户监控轮询错误: {str(e)}")
                await asyncio.sleep(60)  # 错误时等待1分钟
    
    async def _fetch_whale_transactions(self):
        """获取大户交易"""
        try:
            # 计算时间范围（最近10分钟）
            end_time = int(datetime.now().timestamp())
            start_time = self.last_timestamp or (end_time - 600)
            
            url = (
                f"https://api.whale-alert.io/v1/transactions"
                f"?api_key={self.api_key}"
                f"&start={start_time}"
                f"&end={end_time}"
                f"&min_value={self.min_amount}"
                f"&limit=100"
            )
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    self.logger.warning(f"获取大户交易失败: HTTP {response.status}")
                    return
                
                data = await response.json()
                transactions = data.get('transactions', [])
                
                for tx_data in transactions:
                    try:
                        whale_tx = self._parse_transaction(tx_data)
                        if whale_tx:
                            data_point = DataPoint(
                                source=self.name,
                                data_type=DataType.WHALE_ALERT,
                                symbol=whale_tx.currency,
                                timestamp=whale_tx.timestamp,
                                data=whale_tx.to_dict()
                            )
                            await self.notify_subscribers(data_point)
                    
                    except Exception as e:
                        self.logger.error(f"解析大户交易失败: {str(e)}")
                        continue
                
                if transactions:
                    self.last_timestamp = end_time
                    self.logger.info(f"获取大户交易成功: {len(transactions)} 条")
        
        except Exception as e:
            self.logger.error(f"获取大户交易失败: {str(e)}")
    
    def _parse_transaction(self, tx_data: Dict[str, Any]) -> Optional[WhaleTransaction]:
        """解析交易数据"""
        try:
            timestamp = datetime.fromtimestamp(tx_data['timestamp'])
            
            # 识别交易所
            from_exchange = self._identify_exchange(tx_data.get('from', {}).get('address'))
            to_exchange = self._identify_exchange(tx_data.get('to', {}).get('address'))
            
            whale_tx = WhaleTransaction(
                transaction_hash=tx_data['hash'],
                from_address=tx_data.get('from', {}).get('address', ''),
                to_address=tx_data.get('to', {}).get('address', ''),
                amount=float(tx_data['amount']),
                currency=tx_data['symbol'],
                timestamp=timestamp,
                exchange_from=from_exchange,
                exchange_to=to_exchange
            )
            
            return whale_tx
            
        except Exception as e:
            self.logger.error(f"解析交易数据失败: {str(e)}")
            return None
    
    def _identify_exchange(self, address: str) -> Optional[str]:
        """识别交易所地址"""
        if not address:
            return None
        
        return self.exchange_addresses.get(address.lower())
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_time: datetime, 
        end_time: datetime,
        **kwargs
    ) -> List[DataPoint]:
        """获取历史大户交易数据"""
        try:
            if not self.session:
                await self.connect()
            
            start_timestamp = int(start_time.timestamp())
            end_timestamp = int(end_time.timestamp())
            
            url = (
                f"https://api.whale-alert.io/v1/transactions"
                f"?api_key={self.api_key}"
                f"&start={start_timestamp}"
                f"&end={end_timestamp}"
                f"&min_value={self.min_amount}"
                f"&currency={symbol.lower()}"
                f"&limit=100"
            )
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    self.logger.warning(f"获取历史大户交易失败: HTTP {response.status}")
                    return []
                
                data = await response.json()
                transactions = data.get('transactions', [])
                
                data_points = []
                for tx_data in transactions:
                    whale_tx = self._parse_transaction(tx_data)
                    if whale_tx:
                        data_point = DataPoint(
                            source=self.name,
                            data_type=DataType.WHALE_ALERT,
                            symbol=whale_tx.currency,
                            timestamp=whale_tx.timestamp,
                            data=whale_tx.to_dict()
                        )
                        data_points.append(data_point)
                
                self.logger.info(f"获取历史大户交易成功: {len(data_points)} 条")
                return data_points
        
        except Exception as e:
            self.logger.error(f"获取历史大户交易失败: {str(e)}")
            return []
    
    def get_supported_symbols(self) -> List[str]:
        """获取支持的币种"""
        return ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'ADA', 'DOT', 'LINK']
    
    def get_data_types(self) -> List[DataType]:
        """获取支持的数据类型"""
        return [DataType.WHALE_ALERT]
    
    async def get_whale_stats(self, currency: str, hours: int = 24) -> Dict[str, Any]:
        """获取大户交易统计"""
        try:
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (hours * 3600)
            
            url = (
                f"https://api.whale-alert.io/v1/transactions"
                f"?api_key={self.api_key}"
                f"&start={start_time}"
                f"&end={end_time}"
                f"&currency={currency.lower()}"
                f"&min_value={self.min_amount}"
                f"&limit=100"
            )
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {}
                
                data = await response.json()
                transactions = data.get('transactions', [])
                
                # 统计分析
                total_amount = sum(float(tx['amount']) for tx in transactions)
                exchange_inflow = 0
                exchange_outflow = 0
                
                for tx in transactions:
                    amount = float(tx['amount'])
                    from_addr = tx.get('from', {}).get('address', '')
                    to_addr = tx.get('to', {}).get('address', '')
                    
                    if self._identify_exchange(to_addr):
                        exchange_inflow += amount
                    elif self._identify_exchange(from_addr):
                        exchange_outflow += amount
                
                return {
                    'currency': currency,
                    'period_hours': hours,
                    'total_transactions': len(transactions),
                    'total_amount': total_amount,
                    'exchange_inflow': exchange_inflow,
                    'exchange_outflow': exchange_outflow,
                    'net_flow': exchange_inflow - exchange_outflow,
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            self.logger.error(f"获取大户统计失败: {str(e)}")
            return {}
    
    def update_min_amount(self, amount: float) -> None:
        """更新最小监控金额"""
        self.min_amount = amount
        self.logger.info(f"更新最小监控金额: ${amount:,.0f}")
    
    def add_exchange_address(self, address: str, exchange_name: str) -> None:
        """添加交易所地址"""
        self.exchange_addresses[address.lower()] = exchange_name
        self.logger.info(f"添加交易所地址: {exchange_name} - {address}")
    
    def get_exchange_addresses(self) -> Dict[str, str]:
        """获取所有交易所地址映射"""
        return self.exchange_addresses.copy()
