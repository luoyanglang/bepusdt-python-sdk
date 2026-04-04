"""BEpusdt Python SDK - USDT/TRX/USDC 支付网关客户端"""

from .client import BEpusdtClient
from .exceptions import (
    BEpusdtError, SignatureError, APIError,
    NetworkError, RequestTimeoutError, ServerError, ClientError, ValidationError
)

# 向后兼容别名，下个 major 版本移除
TimeoutError = RequestTimeoutError
from .models import Order, OrderStatus, TradeType

__version__ = "0.3.3"
__author__ = "luoyanglang"
__url__ = "https://github.com/luoyanglang/bepusdt-python-sdk"
__all__ = [
    "BEpusdtClient",
    "BEpusdtError", "SignatureError", "APIError",
    "NetworkError", "RequestTimeoutError", "TimeoutError", "ServerError", "ClientError", "ValidationError",
    "Order", "OrderStatus", "TradeType"
]
