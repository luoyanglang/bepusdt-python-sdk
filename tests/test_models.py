"""数据模型测试"""

import pytest
from bepusdt.models import Order, OrderStatus, TradeType


class TestOrder:
    """订单模型测试"""

    def test_order_creation(self):
        """测试订单创建"""
        order = Order(
            trade_id="TRD_001",
            order_id="ORD_001",
            amount=10.0,
            actual_amount=1.35,
            token="TQhAwH4zSsgP78CdqMNqpEDik988888888",
            expiration_time=600,
            payment_url="https://pay.example.com/xxx"
        )
        
        assert order.trade_id == "TRD_001"
        assert order.order_id == "ORD_001"
        assert order.amount == 10.0
        assert order.actual_amount == 1.35
        assert order.status is None

    def test_order_with_status(self):
        """测试带状态的订单"""
        order = Order(
            trade_id="TRD_001",
            order_id="ORD_001",
            amount=10.0,
            actual_amount=1.35,
            token="TQhAwH4zSsgP78CdqMNqpEDik988888888",
            expiration_time=600,
            payment_url="https://pay.example.com/xxx",
            status=OrderStatus.SUCCESS
        )
        
        assert order.status == OrderStatus.SUCCESS


class TestOrderStatus:
    """订单状态测试"""

    def test_order_status_values(self):
        """测试订单状态值"""
        assert OrderStatus.WAITING == 1
        assert OrderStatus.SUCCESS == 2
        assert OrderStatus.TIMEOUT == 3


class TestTradeType:
    """支付类型测试"""

    def test_trade_type_usdt(self):
        """测试 USDT 支付类型"""
        assert TradeType.USDT_TRC20 == "usdt.trc20"
        assert TradeType.USDT_ERC20 == "usdt.erc20"
        assert TradeType.USDT_POLYGON == "usdt.polygon"

    def test_trade_type_usdc(self):
        """测试 USDC 支付类型"""
        assert TradeType.USDC_TRC20 == "usdc.trc20"
        assert TradeType.USDC_ERC20 == "usdc.erc20"

    def test_trade_type_trx(self):
        """测试 TRX 支付类型"""
        assert TradeType.TRON_TRX == "tron.trx"
