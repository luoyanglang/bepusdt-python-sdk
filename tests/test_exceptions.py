"""异常类完整测试覆盖"""

import pytest

from bepusdt.exceptions import (
    APIError,
    BEpusdtError,
    ClientError,
    NetworkError,
    RequestTimeoutError,
    ServerError,
    SignatureError,
    ValidationError,
)
import bepusdt


class TestInheritanceChain:
    """验证所有异常的继承链"""

    def test_bepusdt_error_inherits_exception(self):
        assert issubclass(BEpusdtError, Exception)

    def test_signature_error_inherits_bepusdt_error(self):
        assert issubclass(SignatureError, BEpusdtError)

    def test_api_error_inherits_bepusdt_error(self):
        assert issubclass(APIError, BEpusdtError)

    def test_network_error_inherits_bepusdt_error(self):
        assert issubclass(NetworkError, BEpusdtError)

    def test_request_timeout_error_inherits_bepusdt_error(self):
        assert issubclass(RequestTimeoutError, BEpusdtError)

    def test_server_error_inherits_bepusdt_error(self):
        assert issubclass(ServerError, BEpusdtError)

    def test_client_error_inherits_bepusdt_error(self):
        assert issubclass(ClientError, BEpusdtError)

    def test_validation_error_inherits_bepusdt_error(self):
        assert issubclass(ValidationError, BEpusdtError)

    def test_all_exceptions_catchable_as_bepusdt_error(self):
        """所有 SDK 异常都可用 BEpusdtError 捕获"""
        exceptions = [
            SignatureError("sig"),
            APIError("api"),
            NetworkError("net"),
            RequestTimeoutError("timeout"),
            ServerError("srv"),
            ClientError("cli"),
            ValidationError("val"),
        ]
        for exc in exceptions:
            with pytest.raises(BEpusdtError):
                raise exc


class TestAPIError:
    """APIError 属性存储测试"""

    def test_message_only(self):
        err = APIError("something went wrong")
        assert str(err) == "something went wrong"
        assert err.status_code is None
        assert err.response is None

    def test_with_status_code(self):
        err = APIError("bad request", status_code=400)
        assert err.status_code == 400
        assert err.response is None

    def test_with_response(self):
        payload = {"error": "not found", "code": 404}
        err = APIError("not found", status_code=404, response=payload)
        assert err.status_code == 404
        assert err.response == payload

    def test_all_kwargs(self):
        payload = {"msg": "err"}
        err = APIError("oops", status_code=500, response=payload)
        assert str(err) == "oops"
        assert err.status_code == 500
        assert err.response is payload


class TestServerError:
    """ServerError 属性存储测试"""

    def test_message_only(self):
        err = ServerError("internal error")
        assert str(err) == "internal error"
        assert err.status_code is None

    def test_with_status_code(self):
        err = ServerError("gateway timeout", status_code=504)
        assert err.status_code == 504

    def test_catchable_as_bepusdt_error(self):
        with pytest.raises(BEpusdtError):
            raise ServerError("srv error", status_code=500)


class TestClientError:
    """ClientError 属性存储测试"""

    def test_message_only(self):
        err = ClientError("unauthorized")
        assert str(err) == "unauthorized"
        assert err.status_code is None

    def test_with_status_code(self):
        err = ClientError("forbidden", status_code=403)
        assert err.status_code == 403

    def test_catchable_as_bepusdt_error(self):
        with pytest.raises(BEpusdtError):
            raise ClientError("client error", status_code=400)


class TestSimpleExceptions:
    """无额外属性的简单异常测试"""

    def test_signature_error_message(self):
        err = SignatureError("invalid signature")
        assert str(err) == "invalid signature"

    def test_network_error_message(self):
        err = NetworkError("connection refused")
        assert str(err) == "connection refused"

    def test_request_timeout_error_message(self):
        err = RequestTimeoutError("request timed out")
        assert str(err) == "request timed out"

    def test_validation_error_message(self):
        err = ValidationError("https required")
        assert str(err) == "https required"


class TestBackwardCompatAlias:
    """TimeoutError 向后兼容别名测试"""

    def test_timeout_error_alias_exists(self):
        assert hasattr(bepusdt, "TimeoutError")

    def test_timeout_error_is_request_timeout_error(self):
        assert bepusdt.TimeoutError is RequestTimeoutError

    def test_timeout_error_catchable_as_request_timeout_error(self):
        with pytest.raises(RequestTimeoutError):
            raise bepusdt.TimeoutError("timed out")

    def test_timeout_error_catchable_as_bepusdt_error(self):
        with pytest.raises(BEpusdtError):
            raise bepusdt.TimeoutError("timed out")
