"""Input validation and protocol rate normalization."""

import math
from decimal import Decimal
from typing import Union
from .exceptions import ValidationError


def _normalize_amount(amount: Union[int, float]) -> Union[int, float]:
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValidationError(f"amount 必须是数字（int 或 float），当前值: {amount!r}")
    try:
        finite = math.isfinite(float(amount))
    except OverflowError:
        finite = False
    if not finite:
        raise ValidationError(f"amount 必须是有限数字，当前值: {amount!r}")
    return int(amount) if amount == int(amount) else amount


def _normalize_rate(rate: Union[int, float, str]) -> str:
    if isinstance(rate, bool) or not isinstance(rate, (int, float, str)):
        raise ValidationError(f"rate 必须是数字或字符串，当前值: {rate!r}")
    if isinstance(rate, (int, float)):
        try:
            finite = math.isfinite(float(rate))
        except OverflowError:
            finite = False
        if not finite:
            raise ValidationError(f"rate 必须是有限数字，当前值: {rate!r}")
        if rate == 0:
            return "0"
        text = format(Decimal(str(rate)), "f")
        return text.rstrip("0").rstrip(".") if "." in text else text
    return rate


def _validate_timeout(timeout: int) -> int:
    if isinstance(timeout, bool) or not isinstance(timeout, int):
        raise ValidationError(f"timeout 必须是整数秒，当前值: {timeout!r}")
    return timeout


def _validate_request_timeout(timeout: Union[int, float]) -> Union[int, float]:
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(float(timeout))
        or timeout <= 0
    ):
        raise ValidationError(f"timeout 必须是正数，当前值: {timeout!r}")
    return timeout


def _validate_max_retries(max_retries: int) -> int:
    if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
        raise ValidationError(f"max_retries 必须是非负整数，当前值: {max_retries!r}")
    return max_retries


def _validate_retry_delay(retry_delay: Union[int, float]) -> Union[int, float]:
    if (
        isinstance(retry_delay, bool)
        or not isinstance(retry_delay, (int, float))
        or not math.isfinite(float(retry_delay))
        or retry_delay < 0
    ):
        raise ValidationError(f"retry_delay 必须是非负数字，当前值: {retry_delay!r}")
    return retry_delay
