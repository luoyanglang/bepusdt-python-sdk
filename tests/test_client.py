"""客户端测试"""

import pytest
from unittest.mock import Mock, patch
from bepusdt import BEpusdtClient, OrderStatus, TradeType, APIError


class TestBEpusdtClient:
    """客户端测试类"""

    def setup_method(self):
        """测试前准备"""
        self.client = BEpusdtClient(
            api_url="https://test.example.com",
            api_token="test_token"
        )

    def test_client_init(self):
        """测试客户端初始化"""
        assert self.client.api_url == "https://test.example.com"
        assert self.client.api_token == "test_token"
        assert self.client.timeout == 30

    def test_client_init_with_timeout(self):
        """测试带超时的客户端初始化"""
        client = BEpusdtClient(
            api_url="https://test.example.com",
            api_token="test_token",
            timeout=60
        )
        assert client.timeout == 60

    @patch('bepusdt.client.requests.Session.post')
    def test_create_order_success(self, mock_post):
        """测试创建订单成功"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status_code": 200,
            "message": "success",
            "data": {
                "trade_id": "test_trade_123",
                "order_id": "ORDER_001",
                "amount": "10.0",
                "actual_amount": "1.35",
                "token": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                "expiration_time": 600,
                "payment_url": "https://test.example.com/pay/xxx"
            }
        }
        mock_post.return_value = mock_response

        # 创建订单
        order = self.client.create_order(
            order_id="ORDER_001",
            amount=10.0,
            notify_url="https://example.com/notify"
        )

        # 验证结果
        assert order.trade_id == "test_trade_123"
        assert order.order_id == "ORDER_001"
        assert order.actual_amount == 1.35

    @patch('bepusdt.client.requests.Session.post')
    def test_create_order_fail(self, mock_post):
        """测试创建订单失败"""
        # 模拟 API 错误响应（HTTP 200，业务层 status_code=400）
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status_code": 400,
            "message": "参数错误"
        }
        mock_post.return_value = mock_response

        # 应该抛出异常
        with pytest.raises(APIError) as exc_info:
            self.client.create_order(
                order_id="ORDER_001",
                amount=10.0,
                notify_url="https://example.com/notify"
            )
        
        assert "参数错误" in str(exc_info.value)

    @patch('bepusdt.client.requests.Session.post')
    def test_cancel_order_success(self, mock_post):
        """测试取消订单成功"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status_code": 200,
            "message": "success",
            "data": {"trade_id": "test_trade_123"}
        }
        mock_post.return_value = mock_response

        # 取消订单
        result = self.client.cancel_order(trade_id="test_trade_123")

        # 验证结果
        assert result["trade_id"] == "test_trade_123"

    @patch('bepusdt.client.requests.Session.get')
    def test_query_order_success(self, mock_get):
        """测试查询订单成功"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "trade_id": "test_trade_123",
            "trade_hash": "0x123abc",
            "status": 2,
            "return_url": "https://example.com/success"
        }
        mock_get.return_value = mock_response

        # 查询订单
        order = self.client.query_order(trade_id="test_trade_123")

        # 验证结果
        assert order.trade_id == "test_trade_123"
        assert order.status == OrderStatus.SUCCESS
        assert order.block_transaction_id == "0x123abc"

    @patch('bepusdt.client.requests.Session.get')
    def test_query_order_not_found(self, mock_get):
        """测试查询不存在的订单"""
        # 模拟 API 响应（订单不存在）
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        # 应该抛出异常
        with pytest.raises(APIError) as exc_info:
            self.client.query_order(trade_id="not_exist")
        
        assert "订单不存在" in str(exc_info.value)

    @patch('bepusdt.client.requests.Session.post')
    def test_create_order_with_zero_timeout(self, mock_post):
        """测试 timeout=0 不被静默丢弃"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status_code": 200,
            "message": "success",
            "data": {
                "trade_id": "test_trade_123",
                "order_id": "ORDER_001",
                "amount": "10.0",
                "actual_amount": "1.35",
                "token": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                "expiration_time": 600,
                "payment_url": "https://test.example.com/pay/xxx"
            }
        }
        mock_post.return_value = mock_response

        self.client.create_order(
            order_id="ORDER_001",
            amount=10.0,
            notify_url="https://example.com/notify",
            timeout=0
        )

        called_data = mock_post.call_args.kwargs["json"]
        assert "timeout" in called_data
        assert called_data["timeout"] == 0

    @patch('bepusdt.client.requests.Session.post')
    def test_create_order_with_zero_rate(self, mock_post):
        """测试 rate=0 不被静默丢弃"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status_code": 200,
            "message": "success",
            "data": {
                "trade_id": "test_trade_123",
                "order_id": "ORDER_001",
                "amount": "10.0",
                "actual_amount": "1.35",
                "token": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                "expiration_time": 600,
                "payment_url": "https://test.example.com/pay/xxx"
            }
        }
        mock_post.return_value = mock_response

        self.client.create_order(
            order_id="ORDER_001",
            amount=10.0,
            notify_url="https://example.com/notify",
            rate=0
        )

        called_data = mock_post.call_args.kwargs["json"]
        assert "rate" in called_data
        assert called_data["rate"] == 0

    def test_verify_callback_valid(self):
        """测试验证有效回调"""
        callback_data = {
            "trade_id": "test_trade_123",
            "order_id": "ORDER_001",
            "amount": 10.0,
            "actual_amount": "1.35",
            "token": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
            "block_transaction_id": "0x123abc",
            "status": 2
        }
        
        # 生成签名
        from bepusdt.signature import generate_signature
        callback_data["signature"] = generate_signature(callback_data, "test_token")

        # 验证签名
        assert self.client.verify_callback(callback_data) is True

    def test_verify_callback_invalid(self):
        """测试验证无效回调"""
        callback_data = {
            "trade_id": "test_trade_123",
            "order_id": "ORDER_001",
            "amount": 10.0,
            "signature": "invalid_signature"
        }

        # 验证签名
        assert self.client.verify_callback(callback_data) is False

    def test_verify_callback_missing_signature(self):
        """测试验证缺少签名的回调"""
        callback_data = {
            "trade_id": "test_trade_123",
            "order_id": "ORDER_001",
            "amount": 10.0
        }

        # 验证签名
        assert self.client.verify_callback(callback_data) is False

    def test_init_produces_no_stdout_output(self, capsys):
        """测试初始化不产生 stdout 输出"""
        BEpusdtClient(
            api_url="https://test.example.com",
            api_token="test_token"
        )
        captured = capsys.readouterr()
        assert captured.out == "", "初始化不应产生任何 stdout 输出"
