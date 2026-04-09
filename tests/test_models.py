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
    """支付类型枚举测试"""

    def test_all_21_usdt_constants(self):
        """验证全部 9 个 USDT 常量值"""
        assert TradeType.USDT_TRC20 == "usdt.trc20"
        assert TradeType.USDT_ERC20 == "usdt.erc20"
        assert TradeType.USDT_POLYGON == "usdt.polygon"
        assert TradeType.USDT_BEP20 == "usdt.bep20"
        assert TradeType.USDT_APTOS == "usdt.aptos"
        assert TradeType.USDT_SOLANA == "usdt.solana"
        assert TradeType.USDT_XLAYER == "usdt.xlayer"
        assert TradeType.USDT_ARBITRUM == "usdt.arbitrum"
        assert TradeType.USDT_PLASMA == "usdt.plasma"

    def test_all_21_usdc_constants(self):
        """验证全部 9 个 USDC 常量值"""
        assert TradeType.USDC_TRC20 == "usdc.trc20"
        assert TradeType.USDC_ERC20 == "usdc.erc20"
        assert TradeType.USDC_POLYGON == "usdc.polygon"
        assert TradeType.USDC_BEP20 == "usdc.bep20"
        assert TradeType.USDC_APTOS == "usdc.aptos"
        assert TradeType.USDC_SOLANA == "usdc.solana"
        assert TradeType.USDC_XLAYER == "usdc.xlayer"
        assert TradeType.USDC_ARBITRUM == "usdc.arbitrum"
        assert TradeType.USDC_BASE == "usdc.base"

    def test_all_21_native_token_constants(self):
        """验证全部 3 个原生代币常量值"""
        assert TradeType.TRON_TRX == "tron.trx"
        assert TradeType.ETH_ERC20 == "ethereum.eth"
        assert TradeType.BNB_BEP20 == "bsc.bnb"

    def test_enum_total_count(self):
        """验证枚举成员总数为 21"""
        assert len(list(TradeType)) == 21

    def test_string_comparison(self):
        """str Enum 可直接与字符串比较（向后兼容）"""
        assert TradeType.USDT_TRC20 == "usdt.trc20"
        assert TradeType.ETH_ERC20 == "ethereum.eth"
        assert TradeType.BNB_BEP20 == "bsc.bnb"

    def test_lookup_by_value(self):
        """可通过字符串值反查枚举成员"""
        assert TradeType("usdt.trc20") is TradeType.USDT_TRC20
        assert TradeType("usdc.base") is TradeType.USDC_BASE
        assert TradeType("bsc.bnb") is TradeType.BNB_BEP20

    def test_invalid_value_raises(self):
        """非法值抛出 ValueError"""
        with pytest.raises(ValueError):
            TradeType("invalid.chain")

    def test_iterable(self):
        """枚举可迭代，所有成员均为 str 实例"""
        members = list(TradeType)
        assert len(members) == 21
        for member in members:
            assert isinstance(member, str)

    def test_is_enum_instance(self):
        """成员是枚举实例，同时也是字符串"""
        from enum import Enum
        assert isinstance(TradeType.USDT_TRC20, TradeType)
        assert isinstance(TradeType.USDT_TRC20, str)
