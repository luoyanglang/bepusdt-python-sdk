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
        """测试原有三种订单状态值"""
        assert OrderStatus.WAITING == 1
        assert OrderStatus.SUCCESS == 2
        assert OrderStatus.TIMEOUT == 3

    def test_order_status_new_values(self):
        """测试新增三种订单状态值（与 Go 网关 v1.23+ 对齐）"""
        assert OrderStatus.CANCELED == 4
        assert OrderStatus.CONFIRMING == 5
        assert OrderStatus.FAILED == 6

    def test_order_status_from_int(self):
        """测试从整数构造枚举（回调 status 字段解析场景）"""
        assert OrderStatus(1) == OrderStatus.WAITING
        assert OrderStatus(2) == OrderStatus.SUCCESS
        assert OrderStatus(3) == OrderStatus.TIMEOUT
        assert OrderStatus(4) == OrderStatus.CANCELED
        assert OrderStatus(5) == OrderStatus.CONFIRMING
        assert OrderStatus(6) == OrderStatus.FAILED

    def test_order_status_invalid_raises(self):
        """测试非法状态值抛出 ValueError"""
        with pytest.raises(ValueError):
            OrderStatus(99)


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
