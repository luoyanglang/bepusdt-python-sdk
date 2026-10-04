"""Actual example HTTP responses and durable fixed-amount merchant acceptance."""

import asyncio
import importlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from bepusdt import Order
from bepusdt.signature import generate_signature


def attempt(trade_id="first"):
    return Order.from_dict(
        {
            "trade_id": trade_id,
            "order_id": "business",
            "amount": "10",
            "actual_amount": "1.35",
            "token": "fixture-wallet",
            "fiat": "CNY",
            "expiration_time": 1200,
            "payment_url": "https://gateway.example/pay",
        }
    )


def callback(trade_id="first", status=2, **overrides):
    data = {
        "trade_id": trade_id,
        "order_id": "business",
        "amount": 10,
        "actual_amount": "1.35",
        "token": "fixture-wallet",
        "block_transaction_id": "fixture-hash",
        "status": status,
    }
    data.update(overrides)
    data["signature"] = generate_signature(data, "fixture-token")
    return data


@pytest.fixture
def store(tmp_path):
    from examples.callback_store import CallbackStore

    result = CallbackStore(str(tmp_path / "callbacks.sqlite"))
    result.register(attempt())
    result.register(attempt("second"))
    return result


def outbox_count(store):
    with sqlite3.connect(store.path) as conn:
        return conn.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]


def test_known_old_and_new_attempts_fulfill_once_across_restart(store):
    from examples.callback_store import CallbackStore

    assert store.accept(callback(status=3))
    assert store.accept(callback())
    restarted = CallbackStore(store.path)
    assert restarted.accept(callback("second"))
    assert restarted.accept(callback())
    assert outbox_count(restarted) == 1


def test_concurrent_attempts_have_one_order_outbox(store):
    data = [callback("first" if i % 2 else "second") for i in range(12)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert all(pool.map(store.accept, data))
    assert outbox_count(store) == 1


def test_distinct_signed_payloads_preserved_without_second_fulfillment(store):
    assert store.accept(callback())
    assert store.accept(callback(block_transaction_id="another-fixture-hash"))
    with sqlite3.connect(store.path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM inbox").fetchone()[0] == 2
    assert outbox_count(store) == 1


def test_example_state_cannot_be_relative_or_in_repository():
    from pathlib import Path
    from examples.callback_store import CallbackStore

    for path in ("callbacks.sqlite", str(Path(__file__).resolve().parents[1] / "callbacks.sqlite")):
        with pytest.raises(ValueError):
            CallbackStore(path)


@pytest.mark.parametrize(
    "overrides",
    [
        {"trade_id": "unknown"},
        {"order_id": "another"},
        {"amount": 20},
        {"amount": True},
        {"amount": "NaN"},
        {"actual_amount": "bad"},
        {"token": "different-wallet"},
        {"status": 99},
        {"status": True},
    ],
)
def test_rejects_unknown_or_inconsistent_attempts(store, overrides):
    data = callback()
    data.update(overrides)  # Store consumes already verified fields; route tests verify signatures.
    assert store.accept(data) is False
    assert outbox_count(store) == 0


def test_changed_business_currency_or_amount_not_registered(store):
    other = attempt("third")
    other.amount = 20
    other.amount_text = "20"
    with pytest.raises(ValueError):
        store.register(other)
    other.amount = 10
    other.amount_text = "10"
    other.fiat = "USD"
    with pytest.raises(ValueError):
        store.register(other)


async def asgi_post(app, payload, path="/api/payment/notify"):
    sent = []
    body = json.dumps(payload).encode()

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "scheme": "http",
        "method": "POST",
        "path": path,
        "root_path": "",
        "query_string": b"",
        "headers": [(b"content-type", b"application/json")],
        "server": ("test", 80),
        "client": ("127.0.0.1", 1234),
    }
    await app(scope, receive, send)
    return sent[0]["status"], b"".join(m.get("body", b"") for m in sent[1:])


@pytest.fixture(params=["flask", "fastapi"])
def http_example(request, store, monkeypatch):
    module = importlib.import_module("examples." + request.param + "_example")
    monkeypatch.setattr(module, "store", store)
    monkeypatch.setattr(module.client, "api_token", "fixture-token")
    if request.param == "flask":
        test_client = module.app.test_client()

        def post(payload, path="/api/payment/notify"):
            result = test_client.post(path, json=payload)
            return result.status_code, result.data

    else:

        def post(payload, path="/api/payment/notify"):
            return asyncio.run(asgi_post(module.app, payload, path))

    return module, post


def test_http_signature_rejection_is_not_200(http_example):
    _, post = http_example
    data = callback()
    data["signature"] = "非ASCII"
    assert post(data)[0] == 400


def test_http_malformed_callback_unicode_is_safe_rejection(http_example):
    _, post = http_example
    data = callback()
    data["name"] = "\ud800"
    assert post(data)[0] == 400


def test_http_empty_array_tampering_is_rejected(http_example, store):
    _, post = http_example
    data = callback()
    data["extra"] = []
    assert post(data)[0] == 400
    assert outbox_count(store) == 0


def test_http_known_attempts_and_unknown_trade(http_example, store):
    _, post = http_example
    assert post(callback()) == (200, b"ok")
    assert post(callback("second")) == (200, b"ok")
    assert post(callback("unknown"))[0] == 400
    assert outbox_count(store) == 1


def test_http_storage_failure_is_not_acknowledged(http_example, monkeypatch):
    module, post = http_example

    def failed_accept(data):
        raise sqlite3.OperationalError("fixture storage unavailable")

    monkeypatch.setattr(module.store, "accept", failed_accept)
    assert post(callback())[0] == 503


def test_http_creation_records_returned_trade_before_callback(http_example, monkeypatch, store):
    module, post = http_example
    monkeypatch.setattr(module.client, "create_order", lambda **kwargs: attempt("third"))
    status, _ = post({"order_id": "business", "amount": 10}, "/create_payment")
    assert status == 200
    assert post(callback("third")) == (200, b"ok")
    assert outbox_count(store) == 1
