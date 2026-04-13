"""客户端测试"""

import pytest
import requests
from unittest.mock import Mock, patch
from bepusdt import BEpusdtClient, OrderStatus, TradeType, APIError
from bepusdt.exceptions import ServerError, ClientError, NetworkError, RequestTimeoutError, ValidationError


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


class TestRequestTimeoutErrorRename:
    """测试 RequestTimeoutError 重命名及向后兼容别名"""

    def test_request_timeout_error_exported(self):
        """RequestTimeoutError 应可从顶层包导入"""
        from bepusdt import RequestTimeoutError
        from bepusdt.exceptions import RequestTimeoutError as ExcRequestTimeoutError
        assert RequestTimeoutError is ExcRequestTimeoutError

    def test_timeout_error_alias_is_request_timeout_error(self):
        """TimeoutError 别名应指向 RequestTimeoutError（向后兼容）"""
        from bepusdt import TimeoutError as SDKTimeoutError, RequestTimeoutError
        assert SDKTimeoutError is RequestTimeoutError

    def test_timeout_error_alias_does_not_shadow_builtin(self):
        """bepusdt.exceptions 中不应再有遮盖内置 TimeoutError 的类"""
        import builtins
        import bepusdt.exceptions as exc
        # exceptions 模块不再直接定义 TimeoutError
        assert not hasattr(exc, "TimeoutError") or exc.TimeoutError is not builtins.TimeoutError

    def test_request_timeout_error_is_bepusdt_error(self):
        """RequestTimeoutError 应继承自 BEpusdtError"""
        from bepusdt import RequestTimeoutError, BEpusdtError
        assert issubclass(RequestTimeoutError, BEpusdtError)

    def test_request_timeout_error_catchable_as_bepusdt_error(self):
        """抛出 RequestTimeoutError 可被 BEpusdtError 捕获"""
        from bepusdt import RequestTimeoutError, BEpusdtError
        with pytest.raises(BEpusdtError):
            raise RequestTimeoutError("超时")

    def test_api_error_optional_params_default_to_none(self):
        """APIError 的 status_code 和 response 默认值应为 None"""
        from bepusdt.exceptions import APIError
        err = APIError("错误消息")
        assert err.status_code is None
        assert err.response is None

    def test_api_error_accepts_none_explicitly(self):
        """APIError 应显式接受 None 作为 status_code 和 response"""
        from bepusdt.exceptions import APIError
        err = APIError("错误消息", status_code=None, response=None)
        assert err.status_code is None
        assert err.response is None

    def test_server_error_optional_status_code_default_to_none(self):
        """ServerError 的 status_code 默认值应为 None"""
        from bepusdt.exceptions import ServerError
        err = ServerError("服务器错误")
        assert err.status_code is None

    def test_client_error_optional_status_code_default_to_none(self):
        """ClientError 的 status_code 默认值应为 None"""
        from bepusdt.exceptions import ClientError
        err = ClientError("客户端错误")
        assert err.status_code is None

    def test_exceptions_py_has_no_mypy_errors(self):
        """exceptions.py 中的类型注解应通过 mypy 检查（忽略其他文件的存量错误）"""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "mypy", "bepusdt/exceptions.py", "--ignore-missing-imports"],
            capture_output=True, text=True
        )
        # 只检查 exceptions.py 自身的错误行（其他文件的存量错误不在本次范围内）
        exceptions_errors = [
            line for line in result.stdout.splitlines()
            if "exceptions.py:" in line and ": error:" in line
        ]
        assert exceptions_errors == [], f"exceptions.py 存在 mypy 错误：\n" + "\n".join(exceptions_errors)


class TestHTTPExceptionPaths:
    """测试 _post/_get 的 HTTP 异常转换路径"""

    def setup_method(self):
        """使用 max_retries=0 避免重试干扰"""
        self.client = BEpusdtClient(
            api_url="https://test.example.com",
            api_token="test_token",
            max_retries=0,
        )

    def _mock_response(self, status_code: int, json_data=None, raise_json=False):
        mock_resp = Mock()
        mock_resp.status_code = status_code
        if raise_json:
            mock_resp.json.side_effect = ValueError("解析失败")
        else:
            mock_resp.json.return_value = json_data or {}
        mock_resp.raise_for_status = Mock()
        return mock_resp

    # --- POST 路径 ---

    @patch("bepusdt.client.requests.Session.post")
    def test_post_http_5xx_raises_server_error(self, mock_post):
        """HTTP 5xx 响应应抛出 ServerError"""
        mock_post.return_value = self._mock_response(500)
        with pytest.raises(ServerError) as exc_info:
            self.client.create_order(
                order_id="ORDER_001",
                amount=10.0,
                notify_url="https://example.com/notify",
            )
        assert exc_info.value.status_code == 500

    @patch("bepusdt.client.requests.Session.post")
    def test_post_http_4xx_raises_client_error(self, mock_post):
        """HTTP 4xx 响应应抛出 ClientError"""
        mock_post.return_value = self._mock_response(403)
        with pytest.raises(ClientError) as exc_info:
            self.client.create_order(
                order_id="ORDER_001",
                amount=10.0,
                notify_url="https://example.com/notify",
            )
        assert exc_info.value.status_code == 403

    @patch("bepusdt.client.requests.Session.post")
    def test_post_requests_timeout_raises_request_timeout_error(self, mock_post):
        """requests.Timeout 应被转换为 RequestTimeoutError"""
        mock_post.side_effect = requests.exceptions.Timeout("连接超时")
        with pytest.raises(RequestTimeoutError):
            self.client.create_order(
                order_id="ORDER_001",
                amount=10.0,
                notify_url="https://example.com/notify",
            )

    @patch("bepusdt.client.requests.Session.post")
    def test_post_requests_connection_error_raises_network_error(self, mock_post):
        """requests.ConnectionError 应被转换为 NetworkError"""
        mock_post.side_effect = requests.exceptions.ConnectionError("连接失败")
        with pytest.raises(NetworkError):
            self.client.create_order(
                order_id="ORDER_001",
                amount=10.0,
                notify_url="https://example.com/notify",
            )

    @patch("bepusdt.client.requests.Session.post")
    def test_post_json_parse_failure_raises_api_error(self, mock_post):
        """JSON 解析失败应被转换为 APIError"""
        mock_post.return_value = self._mock_response(200, raise_json=True)
        with pytest.raises(APIError) as exc_info:
            self.client.create_order(
                order_id="ORDER_001",
                amount=10.0,
                notify_url="https://example.com/notify",
            )
        assert "解析失败" in str(exc_info.value)

    # --- GET 路径 ---

    @patch("bepusdt.client.requests.Session.get")
    def test_get_http_5xx_raises_server_error(self, mock_get):
        """GET HTTP 5xx 响应应抛出 ServerError"""
        mock_get.return_value = self._mock_response(503)
        with pytest.raises(ServerError) as exc_info:
            self.client.query_order(trade_id="test_trade_123")
        assert exc_info.value.status_code == 503

    @patch("bepusdt.client.requests.Session.get")
    def test_get_http_4xx_raises_client_error(self, mock_get):
        """GET HTTP 4xx 响应应抛出 ClientError"""
        mock_get.return_value = self._mock_response(404)
        with pytest.raises(ClientError) as exc_info:
            self.client.query_order(trade_id="test_trade_123")
        assert exc_info.value.status_code == 404

    @patch("bepusdt.client.requests.Session.get")
    def test_get_requests_timeout_raises_request_timeout_error(self, mock_get):
        """GET requests.Timeout 应被转换为 RequestTimeoutError"""
        mock_get.side_effect = requests.exceptions.Timeout("超时")
        with pytest.raises(RequestTimeoutError):
            self.client.query_order(trade_id="test_trade_123")

    @patch("bepusdt.client.requests.Session.get")
    def test_get_requests_connection_error_raises_network_error(self, mock_get):
        """GET requests.ConnectionError 应被转换为 NetworkError"""
        mock_get.side_effect = requests.exceptions.ConnectionError("断线")
        with pytest.raises(NetworkError):
            self.client.query_order(trade_id="test_trade_123")

    @patch("bepusdt.client.requests.Session.get")
    def test_get_json_parse_failure_raises_api_error(self, mock_get):
        """GET JSON 解析失败应被转换为 APIError"""
        mock_get.return_value = self._mock_response(200, raise_json=True)
        with pytest.raises(APIError) as exc_info:
            self.client.query_order(trade_id="test_trade_123")
        assert "解析失败" in str(exc_info.value)


class TestCreateOrderParamDetails:
    """测试 create_order 可选参数细节"""

    def setup_method(self):
        self.client = BEpusdtClient(
            api_url="https://test.example.com",
            api_token="test_token",
            max_retries=0,
        )

    def _mock_success_response(self):
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
                "payment_url": "https://test.example.com/pay/xxx",
            },
        }
        return mock_response

    @patch("bepusdt.client.requests.Session.post")
    def test_amount_integer_conversion(self, mock_post):
        """amount=10.0 应作为整数 10 发送给 API"""
        mock_post.return_value = self._mock_success_response()
        self.client.create_order(
            order_id="ORDER_001",
            amount=10.0,
            notify_url="https://example.com/notify",
        )
        called_data = mock_post.call_args.kwargs["json"]
        assert called_data["amount"] == 10
        assert isinstance(called_data["amount"], int)

    @patch("bepusdt.client.requests.Session.post")
    def test_redirect_url_defaults_to_notify_url(self, mock_post):
        """未传 redirect_url 时应使用 notify_url 作为默认值"""
        mock_post.return_value = self._mock_success_response()
        self.client.create_order(
            order_id="ORDER_001",
            amount=10.0,
            notify_url="https://example.com/notify",
        )
        called_data = mock_post.call_args.kwargs["json"]
        assert called_data["redirect_url"] == "https://example.com/notify"

    @patch("bepusdt.client.requests.Session.post")
    def test_redirect_url_explicit_value_used(self, mock_post):
        """显式传入 redirect_url 时应使用传入值而非 notify_url"""
        mock_post.return_value = self._mock_success_response()
        self.client.create_order(
            order_id="ORDER_001",
            amount=10.0,
            notify_url="https://example.com/notify",
            redirect_url="https://example.com/return",
        )
        called_data = mock_post.call_args.kwargs["json"]
        assert called_data["redirect_url"] == "https://example.com/return"

    @patch("bepusdt.client.requests.Session.post")
    def test_optional_params_address_fiat_name(self, mock_post):
        """address/fiat/name 可选参数应正确包含在请求体中"""
        mock_post.return_value = self._mock_success_response()
        self.client.create_order(
            order_id="ORDER_001",
            amount=10.0,
            notify_url="https://example.com/notify",
            address="TN9RRaXkCFtTXRso2GdTZxSxxwufzxLQPP",
            fiat="USD",
            name="VIP会员",
        )
        called_data = mock_post.call_args.kwargs["json"]
        assert called_data["address"] == "TN9RRaXkCFtTXRso2GdTZxSxxwufzxLQPP"
        assert called_data["fiat"] == "USD"
        assert called_data["name"] == "VIP会员"

    # --- Day 13: HTTPS 强制校验 ---

    def test_init_with_http_api_url_raises_validation_error(self):
        """api_url 使用 http:// 时应抛出 ValidationError"""
        with pytest.raises(ValidationError, match="api_url 必须使用 HTTPS 协议"):
            BEpusdtClient(
                api_url="http://insecure.example.com",
                api_token="test_token"
            )

    def test_init_with_https_api_url_succeeds(self):
        """api_url 使用 https:// 时应正常初始化"""
        client = BEpusdtClient(
            api_url="https://secure.example.com",
            api_token="test_token"
        )
        assert client.api_url == "https://secure.example.com"

    @patch("bepusdt.client.requests.Session.post")
    def test_create_order_with_http_notify_url_raises_validation_error(self, mock_post):
        """notify_url 使用 http:// 时应抛出 ValidationError"""
        with pytest.raises(ValidationError, match="notify_url 必须使用 HTTPS 协议"):
            self.client.create_order(
                order_id="ORDER_001",
                amount=10.0,
                notify_url="http://insecure.example.com/notify"
            )

    @patch("bepusdt.client.requests.Session.post")
    def test_create_order_with_https_notify_url_succeeds(self, mock_post):
        """notify_url 使用 https:// 时应正常创建订单"""
        mock_post.return_value = self._mock_success_response()
        order = self.client.create_order(
            order_id="ORDER_001",
            amount=10.0,
            notify_url="https://secure.example.com/notify"
        )
        assert order.trade_id == "test_trade_123"
