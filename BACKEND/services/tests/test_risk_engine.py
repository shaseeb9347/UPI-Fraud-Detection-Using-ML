import os
import pytest

from services import risk_engine


def test_trusted_upi_whitelist(tmp_path, monkeypatch):
    # set env to include one trusted UPI
    monkeypatch.setenv("TRUSTED_UPIS", "friend1,friend2")
    # reload module to pick up new env variables
    import importlib
    importlib.reload(risk_engine)

    assert risk_engine.is_trusted_upi("friend1")
    assert risk_engine.is_trusted_upi("friend2")
    assert not risk_engine.is_trusted_upi("unknown")


def test_amount_threshold_flagging(monkeypatch):
    monkeypatch.setenv("SAFE_AMOUNT_THRESHOLD", "50000")
    monkeypatch.setenv("TRUSTED_UPIS", "")
    import importlib
    importlib.reload(risk_engine)

    tx = {"trans_amount": 60000, "trans_hour": 12, "age": 30, "upi_number": "foo"}
    reasons = risk_engine.fraud_reasons(tx, risk_score=0)
    assert any("exceeds safe threshold" in r for r in reasons)

    # a lower amount should not trigger
    tx["trans_amount"] = 40000
    reasons = risk_engine.fraud_reasons(tx, risk_score=0)
    assert not any("exceeds safe threshold" in r for r in reasons)


def test_trusted_counterparty_reduces_risk(monkeypatch):
    monkeypatch.setenv("SAFE_AMOUNT_THRESHOLD", "20000")
    monkeypatch.setenv("TRUSTED_UPIS", "trustedupi123")
    import importlib
    importlib.reload(risk_engine)

    tx = {"trans_amount": 50000, "trans_hour": 12, "age": 30, "upi_number": "trustedupi123"}
    reasons = risk_engine.fraud_reasons(tx, risk_score=0)

    assert "lowered risk" in " ".join(reasons) or "trusted" in " ".join(reasons)
