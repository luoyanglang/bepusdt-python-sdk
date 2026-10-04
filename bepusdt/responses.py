"""Validate protocol responses outside the retryable transport boundary."""

import math
import time
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

from .exceptions import APIError
from .models import Order, OrderStatus


def _object(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def _text(value: Any, *, nonempty: bool = False) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        raise ValueError("expected text")
    return value


def _integer(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("expected nonnegative integer")
    return value


def _amount(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("expected amount")
    decimal = Decimal(str(value))
    number = float(decimal)
    if not decimal.is_finite() or decimal < 0 or not math.isfinite(number):
        raise ValueError("expected finite nonnegative amount")
    return number


def _envelope(body: dict) -> dict:
    _object(body)
    code = _integer(body["status_code"])
    if code != 200:
        message = body.get("message")
        raise APIError(message if isinstance(message, str) else "网关业务错误", status_code=code, response=body)
    return _object(body["data"])


def _status(value: Any) -> OrderStatus:
    return OrderStatus(_integer(value))


def _created(data: dict) -> Order:
    _text(data["trade_id"], nonempty=True)
    _text(data["order_id"], nonempty=True)
    _amount(data["amount"])
    _amount(data["actual_amount"])
    _text(data["token"])
    _text(data["payment_url"])
    _integer(data["expiration_time"])
    if "status" in data:
        _status(data["status"])
    if data.get("fiat") is not None:
        _text(data["fiat"])
    return Order.from_dict(data)


def _guard(parser, body: dict, *args):
    try:
        return parser(body, *args)
    except (KeyError, TypeError, ValueError, InvalidOperation, OverflowError):
        raise APIError("响应字段无效或订单不存在", response=body if isinstance(body, dict) else None) from None


def parse_created_order(body: dict, order_id: str) -> Order:
    def parse(body, order_id):
        data = _envelope(body)
        order = _created(data)
        if order.order_id != order_id:
            raise ValueError("order id mismatch")
        return order

    return _guard(parse, body, order_id)


def parse_cancel(body: dict, trade_id: str) -> dict:
    def parse(body, trade_id):
        data = _envelope(body)
        if _text(data["trade_id"], nonempty=True) != trade_id:
            raise ValueError("trade id mismatch")
        return data

    return _guard(parse, body, trade_id)


def _legacy(body: dict, trade_id: str) -> Order:
    _object(body)
    if "status_code" in body:
        _envelope(body)
    if _text(body["trade_id"], nonempty=True) != trade_id:
        raise ValueError("trade id mismatch")
    tx_hash = body.get("trade_hash") or body.get("block_transaction_id", "")
    return Order(
        trade_id=trade_id,
        order_id="",
        amount=0.0,
        actual_amount=0.0,
        token="",
        expiration_time=0,
        payment_url="",
        status=_status(body["status"]),
        block_transaction_id=_text(tx_hash),
    )


def _current(body: dict, trade_id: str) -> Order:
    data = _envelope(body)
    if _text(data["trade_id"], nonempty=True) != trade_id:
        raise ValueError("trade id mismatch")
    actual = data["actual_amount"]
    deadline = _integer(data["expired_at"])
    network = data.get("network")
    if network is not None:
        _object(network)
    reselect = data.get("reselect")
    if reselect is not None and not isinstance(reselect, bool):
        raise ValueError("expected reselect boolean")
    return Order(
        trade_id=trade_id,
        order_id=_text(data["order_id"], nonempty=True),
        amount=_amount(data["money"]),
        actual_amount=0.0 if actual == "" else _amount(actual),
        token=_text(data["token"]),
        expiration_time=max(0, int(deadline - time.time())),
        payment_url="",
        fiat=_text(data["fiat"]),
        status=_status(data["status"]),
        block_transaction_id=None,
        expired_at=deadline,
        created_at=_integer(data["created_at"]),
        amount_text=str(data["money"]),
        actual_amount_text=None if actual == "" else str(actual),
        trade_type=_text(data["trade_type"]),
        network=network,
        name=_text(data.get("name", "")),
        reselect=reselect,
        trade_url=_text(data.get("trade_url", "")),
    )


def parse_query(body: dict, trade_id: str, mode: str) -> Order:
    return _guard(_current if mode == "current" else _legacy, body, trade_id)
