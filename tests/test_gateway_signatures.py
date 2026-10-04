"""Goldens produced by actual frozen gateway utils, not SDK self-signing."""

import json
from pathlib import Path

import pytest

from bepusdt import BEpusdtClient, ValidationError
from bepusdt.signature import generate_signature, verify_signature

GOLDENS = json.loads((Path(__file__).parent / "fixtures" / "gateway_signatures.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", GOLDENS["cases"])
def test_actual_gateway_signature(case):
    params = json.loads(case["json"])
    assert generate_signature(params, GOLDENS["token"]) == case["signature"]
    assert verify_signature(params, GOLDENS["token"], case["signature"])
    assert not verify_signature(dict(params, name="tampered"), GOLDENS["token"], case["signature"])


@pytest.mark.parametrize("signature", ["非ASCII", None, [], 123, "", "0" * 32])
def test_malformed_signature_safe_rejection(signature):
    assert verify_signature({"amount": 10}, "fixture-token", signature) is False


def test_signing_not_affected_by_application_decimal_context():
    from decimal import localcontext

    with localcontext() as context:
        context.prec = 2
        assert generate_signature({"amount": 1000000.5}, "fixture-token") == "017040c5598f873112e2691f62380ff3"


@pytest.mark.parametrize("params", [{"name": "\ud800"}, {"\ud800": "name"}])
def test_malformed_unicode_is_rejected_without_callback_exception(params):
    with pytest.raises(ValidationError):
        generate_signature(params, "fixture-token")
    assert verify_signature(params, "fixture-token", "0" * 32) is False


@pytest.mark.parametrize("value", [float("nan"), float("inf"), [1], {"nested": 1}, 10**400])
def test_non_protocol_scalars_cannot_be_signed(value):
    with pytest.raises(ValidationError):
        generate_signature({"amount": value}, "fixture-token")
    sdk = BEpusdtClient("https://gateway.example", "fixture-token")
    assert sdk.verify_callback({"amount": value, "signature": "0" * 32}) is False
