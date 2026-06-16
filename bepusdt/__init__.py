"""BEpusdt Python SDK - USDT/USDC/TRX/ETH/BNB/GRAM 支付网关客户端"""

from .client import BEpusdtClient
from .exceptions import (
    BEpusdtError,
    SignatureError,
    APIError,
    NetworkError,
    RequestTimeoutError,
    ServerError,
    ClientError,
    ValidationError,
)
from .models import Order, OrderStatus, TradeType

# 向后兼容别名，下个 major 版本移除
TimeoutError = RequestTimeoutError

try:
    from ._version import version as __version__
except ImportError:
    try:
        from importlib.metadata import PackageNotFoundError, version
    except ImportError:  # pragma: no cover - Python < 3.8
        from importlib_metadata import PackageNotFoundError, version  # type: ignore

    try:
        __version__ = version("bepusdt")
    except PackageNotFoundError:
        __version__ = "0.0.0"

__author__ = "luoyanglang"
__url__ = "https://github.com/luoyanglang/bepusdt-python-sdk"
__all__ = [
    "BEpusdtClient",
    "BEpusdtError",
    "SignatureError",
    "APIError",
    "NetworkError",
    "RequestTimeoutError",
    "TimeoutError",
    "ServerError",
    "ClientError",
    "ValidationError",
    "Order",
    "OrderStatus",
    "TradeType",
]
