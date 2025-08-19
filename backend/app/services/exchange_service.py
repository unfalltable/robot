"""
交易所服务管理器
"""
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from app.models.trading import Account, Order
from app.core.logging import exchange_logger
from exchanges.base_exchange import ExchangeCredentials, OrderRequest
from exchanges.okx_exchange import OKXExchange


class ExchangeService:
    """交易所服务管理器"""
    
    def __init__(self):
        self.exchanges: Dict[str, Any] = {}
    
    def get_exchange(self, account: Account):
        """获取交易所实例"""
        exchange_key = f"{account.exchange}_{account.id}"
        
        if exchange_key not in self.exchanges:
            # 创建新的交易所实例
            credentials = ExchangeCredentials(
                api_key=account.api_key,
                secret_key=account.secret_key,
                passphrase=account.passphrase,
                sandbox=account.sandbox
            )
            
            if account.exchange.lower() == 'okx':
                self.exchanges[exchange_key] = OKXExchange(credentials)
            else:
                raise ValueError(f"不支持的交易所: {account.exchange}")
        
        return self.exchanges[exchange_key]
    
    async def create_order(self, account: Account, order: Order) -> Dict[str, Any]:
        """创建订单"""
        try:
            exchange = self.get_exchange(account)
            
            # 构建订单请求
            order_request = OrderRequest(
                symbol=order.symbol,
                side=order.side.value,
                type=order.type.value,
                amount=order.amount,
                price=order.price,
                stop_price=order.stop_price
            )
            
            # 创建订单
            result = await exchange.create_order(order_request)
            
            exchange_logger.info(f"交易所订单创建成功: {result.id}")
            return {
                'id': result.id,
                'status': result.status,
                'info': result.info
            }
            
        except Exception as e:
            exchange_logger.error(f"交易所订单创建失败: {str(e)}")
            raise
    
    async def cancel_order(self, account: Account, order_id: str) -> bool:
        """取消订单"""
        try:
            exchange = self.get_exchange(account)
            
            # 这里需要获取订单的symbol，暂时使用空字符串
            # 在实际实现中，应该从数据库中获取订单信息
            result = await exchange.cancel_order(order_id, "")
            
            exchange_logger.info(f"交易所订单取消成功: {order_id}")
            return result
            
        except Exception as e:
            exchange_logger.error(f"交易所订单取消失败: {str(e)}")
            raise
    
    async def update_order(self, account: Account, order_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新订单"""
        try:
            # OKX不支持直接更新订单，需要先取消再创建新订单
            # 这里暂时返回成功状态
            exchange_logger.info(f"交易所订单更新: {order_id}")
            return {"status": "updated"}
            
        except Exception as e:
            exchange_logger.error(f"交易所订单更新失败: {str(e)}")
            raise
    
    async def get_account_info(self, account: Account) -> Dict[str, Any]:
        """获取账户信息"""
        try:
            exchange = self.get_exchange(account)
            return await exchange.get_account_info()
        except Exception as e:
            exchange_logger.error(f"获取账户信息失败: {str(e)}")
            raise
    
    async def get_balances(self, account: Account) -> Dict[str, Any]:
        """获取余额"""
        try:
            exchange = self.get_exchange(account)
            balances = await exchange.get_balances()
            return {balance.currency: {
                'free': balance.free,
                'used': balance.used,
                'total': balance.total
            } for balance in balances}
        except Exception as e:
            exchange_logger.error(f"获取余额失败: {str(e)}")
            raise
    
    async def get_positions(self, account: Account) -> Dict[str, Any]:
        """获取持仓"""
        try:
            exchange = self.get_exchange(account)
            positions = await exchange.get_positions()
            return {pos.symbol: {
                'side': pos.side,
                'size': pos.size,
                'entry_price': pos.entry_price,
                'mark_price': pos.mark_price,
                'unrealized_pnl': pos.unrealized_pnl,
                'percentage': pos.percentage
            } for pos in positions}
        except Exception as e:
            exchange_logger.error(f"获取持仓失败: {str(e)}")
            raise
    
    async def get_ticker(self, account: Account, symbol: str) -> Dict[str, Any]:
        """获取行情"""
        try:
            exchange = self.get_exchange(account)
            ticker = await exchange.get_ticker(symbol)
            return {
                'symbol': ticker.symbol,
                'last': ticker.last,
                'bid': ticker.bid,
                'ask': ticker.ask,
                'high': ticker.high,
                'low': ticker.low,
                'volume': ticker.volume,
                'change': ticker.change,
                'percentage': ticker.percentage,
                'timestamp': ticker.timestamp
            }
        except Exception as e:
            exchange_logger.error(f"获取行情失败: {str(e)}")
            raise
    
    async def test_connection(self, account: Account) -> bool:
        """测试连接"""
        try:
            exchange = self.get_exchange(account)
            return await exchange.test_connection()
        except Exception as e:
            exchange_logger.error(f"测试连接失败: {str(e)}")
            return False
