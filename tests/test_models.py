"""数据模型测试"""

import base64
import sys
from unittest.mock import MagicMock, patch

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
            payment_url="https://pay.example.com/xxx",
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
            status=OrderStatus.SUCCESS,
        )

        assert order.status == OrderStatus.SUCCESS

    def test_from_dict_accepts_missing_optional_fields(self):
        """缺失可选字段时仍可从创建订单响应生成订单对象"""
        order = Order.from_dict(
            {
                "trade_id": "TRD_001",
                "order_id": "ORD_001",
                "amount": "10.0",
                "actual_amount": "1.35",
                "token": "sample-wallet-address",
                "expiration_time": 600,
                "payment_url": "https://pay.example.com/xxx",
            }
        )

        assert order.trade_id == "TRD_001"
        assert order.fiat is None
        assert order.status is None
        assert order.block_transaction_id is None

    def test_from_dict_ignores_gateway_extra_fields(self):
        """网关新增字段不应影响已知订单字段解析"""
        order = Order.from_dict(
            {
                "fiat": "CNY",
                "trade_type": "usdt.trc20",
                "trade_id": "TRD_001",
                "order_id": "ORD_001",
                "name": "VIP",
                "status": 1,
                "amount": "10.0",
                "actual_amount": "1.35",
                "token": "sample-wallet-address",
                "expiration_time": 600,
                "payment_url": "https://pay.example.com/xxx",
                "return_url": "",
                "network": [],
            }
        )

        assert order.trade_id == "TRD_001"
        assert order.status == OrderStatus.WAITING
        assert order.fiat == "CNY"


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
        assert isinstance(TradeType.USDT_TRC20, TradeType)
        assert isinstance(TradeType.USDT_TRC20, str)


def _make_order(token: str = "TQhAwH4zSsgP78CdqMNqpEDik988888888") -> Order:
    return Order(
        trade_id="TRD_001",
        order_id="ORD_001",
        amount=10.0,
        actual_amount=1.35,
        token=token,
        expiration_time=600,
        payment_url="https://pay.example.com/xxx",
    )


class TestOrderQRCode:
    """订单二维码方法测试"""

    def test_generate_qrcode_uses_token_as_data(self):
        """generate_qrcode 应使用 order.token 作为二维码数据"""
        token = "TQhAwH4zSsgP78CdqMNqpEDik988888888"
        order = _make_order(token=token)

        mock_qr = MagicMock()
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        mock_qrcode = MagicMock()
        mock_qrcode.QRCode.return_value = mock_qr
        mock_qrcode.constants.ERROR_CORRECT_L = 1

        with patch.dict(sys.modules, {"qrcode": mock_qrcode}):
            result = order.generate_qrcode()

        mock_qr.add_data.assert_called_once_with(token)
        assert result is mock_img

    def test_generate_qrcode_raises_import_error_when_qrcode_missing(self):
        """未安装 qrcode 时应抛出含安装提示的 ImportError"""
        order = _make_order()

        with patch.dict(sys.modules, {"qrcode": None}):
            with pytest.raises(ImportError) as exc_info:
                order.generate_qrcode()

        assert "pip install" in str(exc_info.value)
        assert "qrcode" in str(exc_info.value)

    def test_get_qrcode_base64_returns_valid_base64(self):
        """get_qrcode_base64 应返回合法的 base64 字符串"""
        order = _make_order()
        result = order.get_qrcode_base64()

        assert isinstance(result, str)
        # 合法 base64 字符串可无异常解码
        decoded = base64.b64decode(result)
        assert len(decoded) > 0

    def test_get_qrcode_data_uri_has_correct_prefix(self):
        """get_qrcode_data_uri 应返回 data:image/png;base64, 前缀"""
        order = _make_order()
        result = order.get_qrcode_data_uri()

        assert result.startswith("data:image/png;base64,")
        # 前缀之后是合法 base64
        b64_part = result[len("data:image/png;base64,") :]
        decoded = base64.b64decode(b64_part)
        assert len(decoded) > 0
