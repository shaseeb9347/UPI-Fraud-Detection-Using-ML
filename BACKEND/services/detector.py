import os
import pandas as pd
import pickle
import numpy as np
from . import risk_engine
from .risk_engine import is_trusted_upi


def _default_csv_path():
    # data folder is at repo root: ../data/upi_transactions.csv from services/
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "upi_transactions.csv"))


def load_dataset(csv_path: str | None = None):
    path = csv_path or os.environ.get("UPI_CSV_PATH") or _default_csv_path()
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found at {path}")
    return pd.read_csv(path)


def load_model_and_scaler(model_dir: str | None = None):
    base = model_dir or os.environ.get("MODEL_DIR") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "model"))
    model_path = os.path.join(base, "fraud_model.pkl")
    scaler_path = os.path.join(base, "scaler.pkl")

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError("Model or scaler not found in model directory")

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)

    return model, scaler


# Load dataset & model once to avoid repeated disk reads in production
_DATASET = None
_MODEL = None
_SCALER = None


def _ensure_loaded(csv_path=None, model_dir=None):
    global _DATASET, _MODEL, _SCALER
    if _DATASET is None:
        try:
            _DATASET = load_dataset(csv_path)
        except Exception:
            _DATASET = None
    if _MODEL is None or _SCALER is None:
        _MODEL, _SCALER = load_model_and_scaler(model_dir)


def detect_transaction(transaction: dict, csv_path: str | None = None, model_dir: str | None = None):
    """Evaluate a transaction using the ML model plus rule-based checks and CSV lookup.

    Returns a dict: {fraud_risk_score, risk_level, alert, reasons, upi_flag}
    """
    _ensure_loaded(csv_path, model_dir)

    # Prepare features for model
    features = np.array([[
        transaction.get("trans_hour", 0),
        transaction.get("trans_day", 0),
        transaction.get("trans_month", 0),
        transaction.get("trans_year", 0),
        transaction.get("trans_amount", 0.0),
    ]])

    try:
        features_scaled = _SCALER.transform(features)
        fraud_probability = float(_MODEL.predict_proba(features_scaled)[0][1])
    except Exception:
        # If model fails, fall back to 0.0 probability
        fraud_probability = 0.0

    fraud_risk_score = round(fraud_probability * 100, 2)

    # Rule-based reasons
    reasons = []
    try:
        reasons = risk_engine.fraud_reasons(transaction, fraud_risk_score)
    except Exception:
        reasons = []

    # CSV lookup: check if upi_number exists in historical frauds
    upi_flag = False
    upi_value = transaction.get("upi_number")
    if upi_value is not None and _DATASET is not None:
        matches = _DATASET[_DATASET["upi_number"].astype(str) == str(upi_value)]
        if not matches.empty:
            # if any matched entry had fraud_risk == 1, mark flag
            if (matches["fraud_risk"] == 1).any():
                upi_flag = True
                reasons.append("UPI observed in historical fraudulent transactions")

    # adjust for historical fraud flag
    if upi_flag:
        fraud_risk_score = min(100.0, fraud_risk_score + 25.0)

    # check for trusted counterparties; if the UPI is on the whitelist we
    # treat it as a mitigating factor (user explicitly marked the receiver as
    # a friend/merchant/known contact)
    trusted_counterparty = is_trusted_upi(upi_value)
    if trusted_counterparty:
        # log the fact but reduce the model score rather than blindly
        # overriding it – a pro security implementation would still
        # perform monitoring for account takeover or social engineering.
        fraud_risk_score = max(0.0, fraud_risk_score - 20.0)
        reasons.append("Counterparty is in trusted UPI list – reduced risk")

    # attach trust flag for downstream consumers
    transaction["trusted_upi"] = trusted_counterparty

    # Final categorization using risk_engine.generate_alert (keeps consistent language)
    alert_text = risk_engine.generate_alert(fraud_risk_score)

    # Map alert_text back to risk_level used by frontend
    if alert_text == "LOW RISK":
        risk_level = "LOW"
    elif alert_text == "MEDIUM RISK":
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "fraud_risk_score": fraud_risk_score,
        "risk_level": risk_level,
        "alert": alert_text,
        "reasons": reasons,
        "upi_flag": upi_flag,
    }
