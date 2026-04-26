"""签名算法测试"""

from bepusdt.signature import generate_signature, verify_signature
from bepusdt.models import TradeType


class TestSignature:
    """签名算法测试类"""

    def test_generate_signature_basic(self):
        """测试基本签名生成"""
        params = {"order_id": "TEST_001", "amount": 10, "trade_type": "usdt.trc20"}
        token = "test_token_123"

        signature = generate_signature(params, token)
        assert isinstance(signature, str)
        assert len(signature) == 32  # MD5 hex 长度

    def test_generate_signature_skip_empty(self):
        """测试签名算法跳过空值"""
        params1 = {"order_id": "TEST_001", "amount": 10, "empty_field": "", "none_field": None}
        params2 = {"order_id": "TEST_001", "amount": 10}
        token = "test_token"

        # 空值应该被跳过，签名应该相同
        sig1 = generate_signature(params1, token)
        sig2 = generate_signature(params2, token)
        assert sig1 == sig2

    def test_generate_signature_order(self):
        """测试签名参数排序"""
        params1 = {"b": 2, "a": 1, "c": 3}
        params2 = {"c": 3, "a": 1, "b": 2}
        token = "test_token"

        # 不同顺序应该生成相同签名
        sig1 = generate_signature(params1, token)
        sig2 = generate_signature(params2, token)
        assert sig1 == sig2

    def test_generate_signature_uses_enum_values(self):
        """TradeType 枚举签名应使用实际请求值，而不是枚举成员名"""
        params_with_enum = {"order_id": "TEST_001", "amount": 10, "trade_type": TradeType.USDT_TRC20}
        params_with_string = {"order_id": "TEST_001", "amount": 10, "trade_type": "usdt.trc20"}
        token = "test_token"

        assert generate_signature(params_with_enum, token) == generate_signature(params_with_string, token)

    def test_verify_signature_valid(self):
        """测试验证有效签名"""
        params = {"order_id": "TEST_001", "amount": 10}
        token = "test_token"

        signature = generate_signature(params, token)

        assert verify_signature(params, token, signature) is True

    def test_verify_signature_invalid(self):
        """测试验证无效签名"""
        params = {"order_id": "TEST_001", "amount": 10}
        token = "test_token"

        assert verify_signature(params, token, "invalid_signature") is False

    def test_verify_signature_missing(self):
        """测试缺少签名"""
        params = {"order_id": "TEST_001", "amount": 10}
        token = "test_token"

        assert verify_signature(params, token, "") is False

    def test_verify_signature_constant_time(self):
        """verify_signature 使用常数时间比较，不因签名长度差异产生时序侧信道"""
        import hmac as _hmac
        import unittest.mock as mock

        params = {"order_id": "TEST_001", "amount": 10}
        token = "test_token"
        valid_sig = generate_signature(params, token)

        # 验证内部调用了 hmac.compare_digest 而非 == 比较
        with mock.patch("bepusdt.signature.hmac.compare_digest", wraps=_hmac.compare_digest) as mock_cd:
            result = verify_signature(params, token, valid_sig)
            assert result is True
            mock_cd.assert_called_once_with(valid_sig, valid_sig)

    def test_verify_signature_wrong_token(self):
        """测试 token 不同时签名验证失败"""
        params = {"order_id": "TEST_001", "amount": 10}
        sig = generate_signature(params, "correct_token")

        assert verify_signature(params, "wrong_token", sig) is False
