import pytest

from app import app
from services import risk_engine


def test_prediction_with_trusted_upi(monkeypatch):
    # prepare environment for rule engine
    monkeypatch.setenv("TRUSTED_UPIS", "friend123")
    monkeypatch.setenv("SAFE_AMOUNT_THRESHOLD", "20000")
    import importlib
    importlib.reload(risk_engine)

    client = app.test_client()
    payload = {
        "User_ID": "friend123",
        "Transaction_Amount": 50000,
        "Device": "Mobile",
        "Location": "City",
        "Payment_Method": "UPI"
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    # because UPI is trusted, reasons should mention trusted
    assert any("trusted" in r.lower() for r in data.get("reasons", []))
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")


def test_prediction_high_amount_nontrusted(monkeypatch):
    monkeypatch.setenv("TRUSTED_UPIS", "")
    monkeypatch.setenv("SAFE_AMOUNT_THRESHOLD", "20000")
    import importlib
    importlib.reload(risk_engine)

    client = app.test_client()
    payload = {
        "User_ID": "unknown",
        "Transaction_Amount": 50000,
        "Device": "Mobile",
        "Location": "City",
        "Payment_Method": "UPI"
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert any("amount" in r.lower() for r in data.get("reasons", []))
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")
