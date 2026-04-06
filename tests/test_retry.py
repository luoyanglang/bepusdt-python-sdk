"""retry_on_error 装饰器测试"""

import time
from unittest.mock import MagicMock, call, patch

import pytest

from bepusdt.exceptions import NetworkError, RequestTimeoutError, ServerError, ClientError
from bepusdt.retry import retry_on_error


def test_success_on_first_attempt_no_sleep():
    """首次调用成功，不触发任何 sleep"""
    mock_func = MagicMock(return_value="ok")

    @retry_on_error(max_retries=3, delay=1.0)
    def call_api():
        return mock_func()

    with patch("bepusdt.retry.time.sleep") as mock_sleep:
        result = call_api()

    assert result == "ok"
    mock_func.assert_called_once()
    mock_sleep.assert_not_called()


def test_retry_succeeds_after_network_error():
    """网络错误后重试，第二次成功"""
    mock_func = MagicMock(side_effect=[NetworkError("conn refused"), "ok"])

    @retry_on_error(max_retries=3, delay=0.0)
    def call_api():
        return mock_func()

    with patch("bepusdt.retry.time.sleep"):
        result = call_api()

    assert result == "ok"
    assert mock_func.call_count == 2


def test_raises_after_max_retries_exceeded():
    """超出最大重试次数后，抛出最后一次异常"""
    mock_func = MagicMock(side_effect=NetworkError("persistent error"))

    @retry_on_error(max_retries=2, delay=0.0)
    def call_api():
        return mock_func()

    with patch("bepusdt.retry.time.sleep"):
        with pytest.raises(NetworkError, match="persistent error"):
            call_api()

    assert mock_func.call_count == 3  # 首次 + 2 次重试


def test_exponential_backoff_delays():
    """验证指数退避延迟：delay=1.0, backoff=2.0 → sleep(1.0), sleep(2.0)"""
    mock_func = MagicMock(side_effect=NetworkError("err"))

    @retry_on_error(max_retries=2, delay=1.0, backoff=2.0)
    def call_api():
        return mock_func()

    with patch("bepusdt.retry.time.sleep") as mock_sleep:
        with pytest.raises(NetworkError):
            call_api()

    assert mock_sleep.call_count == 2
    mock_sleep.assert_has_calls([call(1.0), call(2.0)])


def test_non_retryable_exception_propagates_immediately():
    """ClientError 不在重试列表，直接抛出，不触发 sleep"""
    mock_func = MagicMock(side_effect=ClientError("bad request", status_code=400))

    @retry_on_error(max_retries=3, delay=1.0)
    def call_api():
        return mock_func()

    with patch("bepusdt.retry.time.sleep") as mock_sleep:
        with pytest.raises(ClientError):
            call_api()

    mock_func.assert_called_once()
    mock_sleep.assert_not_called()


def test_max_retries_zero_calls_function_exactly_once():
    """`max_retries=0` 时，失败不重试，函数只被调用一次"""
    mock_func = MagicMock(side_effect=RequestTimeoutError("timeout"))

    @retry_on_error(max_retries=0, delay=1.0)
    def call_api():
        return mock_func()

    with patch("bepusdt.retry.time.sleep") as mock_sleep:
        with pytest.raises(RequestTimeoutError):
            call_api()

    mock_func.assert_called_once()
    mock_sleep.assert_not_called()
