"""签名算法"""

import hashlib
import hmac
from enum import Enum
from typing import Dict, Any


def _signature_value(value: Any) -> Any:
    """返回签名协议实际传输的值"""
    if isinstance(value, Enum):
        return value.value
    return value


def generate_signature(params: Dict[str, Any], api_token: str) -> str:
    """生成签名

    Args:
        params: 参数字典
        api_token: API Token

    Returns:
        str: MD5 签名（小写）

    Example:
        >>> params = {"order_id": "001", "amount": 10}
        >>> signature = generate_signature(params, "your-token")
    """
    # 过滤空值
    filtered = {k: v for k, v in params.items() if v not in (None, "", [])}

    # 按键排序
    sorted_params = sorted(filtered.items())

    # 拼接参数
    param_str = "&".join([f"{k}={_signature_value(v)}" for k, v in sorted_params])

    # 添加 token 并计算 MD5
    sign_str = param_str + api_token
    # BEpusdt gateway protocol requires token-appended MD5 signatures.
    signature = hashlib.md5(sign_str.encode("utf-8")).hexdigest().lower()  # nosemgrep

    return signature


def verify_signature(params: Dict[str, Any], api_token: str, received_signature: str) -> bool:
    """验证签名

    Args:
        params: 参数字典（不包含 signature）
        api_token: API Token
        received_signature: 接收到的签名

    Returns:
        bool: 签名是否有效

    Example:
        >>> params = {"order_id": "001", "amount": 10}
        >>> is_valid = verify_signature(params, "your-token", "xxx")
    """
    expected_signature = generate_signature(params, api_token)
    # 使用常数时间比较，防止时序攻击（timing attack）
    return hmac.compare_digest(expected_signature, received_signature)
