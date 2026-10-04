"""签名算法"""

import hashlib
import hmac
import math
from decimal import Decimal
from enum import Enum
from typing import Dict, Any
from .exceptions import ValidationError


def _signature_value(value: Any) -> str:
    """Match Go %v after the gateway decodes JSON numbers into float64."""
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if not isinstance(value, (int, float)):
        raise ValidationError("签名仅支持 JSON 标量参数")
    try:
        number = float(value)
    except OverflowError:
        raise ValidationError("签名数字超出 float64 范围") from None
    if not math.isfinite(number):
        raise ValidationError("签名数字必须有限")
    if number == 0:
        return "-0" if math.copysign(1, number) < 0 else "0"
    decimal = Decimal(repr(number))
    if -4 <= decimal.adjusted() < 6:
        text = format(decimal, "f")
        return text.rstrip("0").rstrip(".") if "." in text else text
    mantissa, exponent = format(decimal, "e").split("e")
    if "." in mantissa:
        mantissa = mantissa.rstrip("0").rstrip(".")
    exponent = int(exponent)
    return "{}e{}{:02d}".format(mantissa, "+" if exponent >= 0 else "-", abs(exponent))


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
    if not isinstance(params, dict) or any(not isinstance(key, str) for key in params):
        raise ValidationError("签名参数必须是字符串键的字典")
    # Only protocol null/empty text is omitted; containers must reach scalar validation.
    filtered = {k: v for k, v in params.items() if k != "signature" and v not in (None, "")}

    # 按键排序
    sorted_params = sorted(filtered.items())

    # 拼接参数
    # Go trims every trailing '&', including suffixes of the final included value.
    param_str = "&".join([f"{k}={_signature_value(v)}" for k, v in sorted_params]).rstrip("&")

    # 添加 token 并计算 MD5
    sign_str = param_str + api_token
    # BEpusdt gateway protocol requires token-appended MD5 signatures.
    try:
        encoded = sign_str.encode("utf-8")
    except UnicodeEncodeError:
        raise ValidationError("签名文本必须是有效 UTF-8") from None
    signature = hashlib.md5(encoded).hexdigest().lower()  # nosemgrep

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
    if not isinstance(received_signature, str) or not received_signature.isascii():
        return False
    try:
        expected_signature = generate_signature(params, api_token)
    except ValidationError:
        return False
    # 使用常数时间比较，防止时序攻击（timing attack）
    return hmac.compare_digest(expected_signature, received_signature)
