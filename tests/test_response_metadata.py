"""Known text response fields are validated before returning an Order."""

from unittest.mock import Mock, patch

import pytest

from bepusdt import APIError, BEpusdtClient

FIELDS = {"fiat": "USD", "trade_type": "usdt.trc20", "name": "fixture", "block_transaction_id": "fixture-hash"}
WRONG_TYPES = [[], [1], {}, {"nested": 1}, False, 0, 0.5]


def created():
    return {
        "status_code": 200,
        "data": {
            "trade_id": "fixture-trade",
            "order_id": "fixture-order",
            "amount": "10",
            "actual_amount": "1.35",
            "token": "fixture-wallet",
            "expiration_time": 1200,
            "payment_url": "https://gateway.example/pay",
        },
    }


def sdk():
    return BEpusdtClient("https://gateway.example", "fixture-token", max_retries=2, retry_delay=0)


@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("value", WRONG_TYPES)
def test_create_metadata_wrong_types_are_nonretryable(field, value):
    body = created()
    body["data"][field] = value
    client = sdk()
    with patch.object(client.session, "post", return_value=Mock(status_code=200, json=lambda: body)) as post:
        with pytest.raises(APIError) as caught:
            client.create_order("fixture-order", 10, "https://merchant.example/notify")
    assert caught.value.response == body
    assert post.call_count == 1


@pytest.mark.parametrize("field", FIELDS)
@pytest.mark.parametrize("case", ["absent", "null", "empty", "text"])
def test_create_optional_metadata_compatibility(field, case):
    body = created()
    expected = {"absent": None, "null": None, "empty": "", "text": FIELDS[field]}[case]
    if case != "absent":
        body["data"][field] = expected
    client = sdk()
    with patch.object(client.session, "post", return_value=Mock(status_code=200, json=lambda: body)):
        order = client.create_order("fixture-order", 10, "https://merchant.example/notify")
    assert getattr(order, field) == expected


def test_unmodeled_creation_extras_remain_forward_compatible():
    body = created()
    body["data"]["future_metadata"] = {"nested": []}
    client = sdk()
    with patch.object(client.session, "post", return_value=Mock(status_code=200, json=lambda: body)):
        assert client.create_order("fixture-order", 10, "https://merchant.example/notify").trade_id == "fixture-trade"


@pytest.mark.parametrize("field", ["trade_hash", "block_transaction_id"])
@pytest.mark.parametrize("value", WRONG_TYPES)
def test_legacy_hash_metadata_cannot_hide_wrong_types(field, value):
    body = {"trade_id": "fixture-trade", "status": 2, field: value}
    client = sdk()
    with patch.object(client.session, "get", return_value=Mock(status_code=200, json=lambda: body)) as get:
        with pytest.raises(APIError) as caught:
            client.query_order("fixture-trade")
    assert caught.value.response == body
    assert get.call_count == 1


@pytest.mark.parametrize(
    "extra,expected",
    [
        ({}, ""),
        ({"trade_hash": "fixture-hash"}, "fixture-hash"),
        ({"block_transaction_id": "fixture-hash"}, "fixture-hash"),
        ({"trade_hash": "", "block_transaction_id": "fixture-hash"}, "fixture-hash"),
        ({"trade_hash": "first-hash", "block_transaction_id": "second-hash"}, "first-hash"),
    ],
)
def test_legacy_hash_defaults_and_alias_precedence_remain(extra, expected):
    body = dict(trade_id="fixture-trade", status=2, **extra)
    client = sdk()
    with patch.object(client.session, "get", return_value=Mock(status_code=200, json=lambda: body)):
        assert client.query_order("fixture-trade").block_transaction_id == expected
