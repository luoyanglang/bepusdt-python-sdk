"""签名算法测试"""

import pytest
from bepusdt.signature import generate_signature, verify_signature


class TestSignature:
    """签名算法测试类"""

    def test_generate_signature_basic(self):
        """测试基本签名生成"""
        params = {
            "order_id": "TEST_001",
            "amount": 10,
            "trade_type": "usdt.trc20"
        }
        token = "test_token_123"
        
        signature = generate_signature(params, token)
        assert isinstance(signature, str)
        assert len(signature) == 32  # MD5 hex 长度

    def test_generate_signature_skip_empty(self):
        """测试签名算法跳过空值"""
        params1 = {
            "order_id": "TEST_001",
            "amount": 10,
            "empty_field": "",
            "none_field": None
        }
        params2 = {
            "order_id": "TEST_001",
            "amount": 10
        }
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
