"""Frozen aa3bd50 merchant contracts, including failure and legacy compatibility."""

from unittest.mock import Mock, patch

import pytest
import requests

from bepusdt import APIError, BEpusdtClient, OrderStatus, ValidationError


def info():
    # Field names/types from aa3bd50 app/handler/epusdt/epusdt.go:399.
    return {
        "status_code": 200,
        "message": "success",
        "data": {
            "trade_id": "fixture-trade",
            "order_id": "fixture-order",
            "status": 1,
            "money": "10",
            "actual_amount": "1.234567890123456789",
            "token": "fixture-wallet",
            "created_at": 1700000000,
            "expired_at": 1700001200,
            "fiat": "CNY",
            "trade_type": "usdt.trc20",
            "network": {"network": "tron"},
            "name": "fixture",
            "reselect": False,
            "trade_url": "https://explorer.example/tx/fixture-trade",
            "redirect_url": "https://merchant.example/success",
            "support_url": "",
        },
    }


def response(body, status=200):
    result = Mock(status_code=status)
    result.json.return_value = body
    return result


def client(mode="current"):
    return BEpusdtClient("https://gateway.example", "fixture-token", max_retries=2, retry_delay=0, query_mode=mode)


def test_explicit_current_mapping_and_clock():
    sdk = client()
    with patch.object(sdk.session, "post", return_value=response(info())) as post:
        with patch("bepusdt.responses.time.time", return_value=1700000000.8):
            order = sdk.query_order("fixture-trade")
    assert post.call_args.args == ("https://gateway.example/api/v1/pay/info",)
    assert post.call_args.kwargs["json"] == {"trade_id": "fixture-trade"}
    assert order.amount == 10.0
    assert isinstance(order.actual_amount, float)
    assert order.actual_amount_text == "1.234567890123456789"
    assert order.amount_text == "10"
    assert order.expiration_time == 1199
    assert order.expired_at == 1700001200
    assert order.created_at == 1700000000
    assert order.trade_type == "usdt.trc20" and order.network == {"network": "tron"}
    assert order.name == "fixture" and order.reselect is False
    assert order.block_transaction_id is None and order.payment_url == ""
    assert order.trade_url.endswith("fixture-trade")


def test_default_remains_legacy():
    sdk = BEpusdtClient("https://gateway.example", "fixture-token")
    with patch.object(sdk.session, "get", return_value=response({"trade_id": "fixture-trade", "status": 2})) as get:
        assert sdk.query_order("fixture-trade").status == OrderStatus.SUCCESS
    assert get.call_args.args == ("https://gateway.example/pay/check-status/fixture-trade",)


def test_invalid_mode_is_local_validation():
    with pytest.raises(ValidationError):
        client("auto")


@pytest.mark.parametrize("status", range(1, 7))
def test_current_six_states(status):
    body = info()
    body["data"]["status"] = status
    sdk = client()
    with patch.object(sdk.session, "post", return_value=response(body)):
        assert sdk.query_order("fixture-trade").status == OrderStatus(status)


@pytest.mark.parametrize("actual", ["0", ""], ids=["gateway-pending", "empty-compatibility"])
def test_expired_and_unselected_snapshot_are_explicit(actual):
    body = info()
    # G BuildPendingOrder retains Amount "0"; an empty string is separate compatibility tolerance.
    body["data"].update(actual_amount=actual, token="", trade_type="", network=None, trade_url="")
    sdk = client()
    with patch.object(sdk.session, "post", return_value=response(body)):
        with patch("bepusdt.responses.time.time", return_value=1700001201):
            order = sdk.query_order("fixture-trade")
    assert order.expiration_time == 0 and order.expired_at == 1700001200
    assert order.actual_amount == 0.0
    assert order.actual_amount_text == (None if actual == "" else "0")
    assert order.token == "" and order.network is None
    assert order.trade_type == "" and order.status == OrderStatus.WAITING
    assert order.block_transaction_id is None and order.payment_url == "" and order.trade_url == ""


@pytest.mark.parametrize("body", [[], None, {}, {"status_code": 200}, {"status_code": True, "data": {}}])
def test_bad_envelope_does_not_retry_or_fallback(body):
    sdk = client()
    with patch.object(sdk.session, "post", return_value=response(body)) as post:
        with patch.object(sdk.session, "get") as get:
            with pytest.raises(APIError):
                sdk.query_order("fixture-trade")
    assert post.call_count == 1 and get.call_count == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("trade_id", "another-trade"),
        ("status", 99),
        ("status", True),
        ("status", "2"),
        ("money", "NaN"),
        ("money", []),
        ("actual_amount", "Infinity"),
        ("token", []),
        ("expired_at", "tomorrow"),
        ("expired_at", True),
        ("created_at", -1),
        ("network", []),
        ("reselect", "false"),
        ("fiat", {}),
    ],
)
def test_invalid_current_fields_become_api_error(field, value):
    body = info()
    body["data"][field] = value
    sdk = client()
    with patch.object(sdk.session, "post", return_value=response(body)) as post:
        with pytest.raises(APIError):
            sdk.query_order("fixture-trade")
    assert post.call_count == 1


@pytest.mark.parametrize("field", ["trade_id", "order_id", "status", "money", "expired_at", "created_at"])
def test_missing_required_current_fields(field):
    body = info()
    del body["data"][field]
    sdk = client()
    with patch.object(sdk.session, "post", return_value=response(body)):
        with pytest.raises(APIError):
            sdk.query_order("fixture-trade")


def test_denial_preserves_business_response_and_never_uses_legacy():
    body = {"status_code": 400, "message": "order not found"}
    sdk = client()
    with patch.object(sdk.session, "post", return_value=response(body)) as post:
        with patch.object(sdk.session, "get") as get:
            with pytest.raises(APIError) as caught:
                sdk.query_order("fixture-trade")
    assert caught.value.status_code == 400 and caught.value.response == body
    assert str(caught.value) == "order not found"
    assert post.call_count == 1 and get.call_count == 0


@pytest.mark.parametrize("method", ["create", "cancel", "legacy"])
@pytest.mark.parametrize(
    "body", [[], {}, {"status_code": 200, "data": []}, {"status_code": 200, "data": {"status": 99}}]
)
def test_all_existing_operations_normalize_bad_data(method, body):
    sdk = client("legacy")
    with patch.object(sdk.session, "post", return_value=response(body)), patch.object(
        sdk.session, "get", return_value=response(body)
    ):
        with pytest.raises(APIError):
            if method == "create":
                sdk.create_order("fixture-order", 10, "https://merchant.example/notify")
            elif method == "cancel":
                sdk.cancel_order("fixture-trade")
            else:
                sdk.query_order("fixture-trade")


def test_lost_cancel_reply_retries_identical_request_but_does_not_claim_failure_to_cancel():
    sdk = client()
    failure = {"status_code": 400, "message": "current status does not allow cancellation"}
    with patch.object(sdk.session, "post", side_effect=[requests.exceptions.Timeout(), response(failure)]) as post:
        with pytest.raises(APIError) as caught:
            sdk.cancel_order("fixture-trade")
    assert caught.value.response == failure
    assert post.call_count == 2 and post.call_args_list[0] == post.call_args_list[1]


def test_create_retry_uses_same_signed_body():
    sdk = client()
    data = {
        "trade_id": "fixture-trade",
        "order_id": "fixture-order",
        "amount": "10",
        "actual_amount": "1.35",
        "token": "fixture-wallet",
        "expiration_time": 1200,
        "payment_url": "https://gateway.example/pay/checkout/fixture-trade",
    }
    with patch.object(
        sdk.session, "post", side_effect=[response({}, 503), response({"status_code": 200, "data": data})]
    ) as post:
        assert sdk.create_order("fixture-order", 10, "https://merchant.example/notify").trade_id == "fixture-trade"
    assert post.call_count == 2 and post.call_args_list[0] == post.call_args_list[1]


@pytest.mark.parametrize(
    "rate,expected", [(1e-7, "0.0000001"), (1e20, "100000000000000000000"), (7.4, "7.4"), ("~1.02", "~1.02")]
)
def test_rate_fixed_decimal_transport(rate, expected):
    from bepusdt.client import _normalize_rate

    assert _normalize_rate(rate) == expected
