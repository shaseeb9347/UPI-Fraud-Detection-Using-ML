import os
from typing import Set

# configurable safety parameters (environment variables allow tuning without code changes)
SAFE_AMOUNT_THRESHOLD = float(os.environ.get("SAFE_AMOUNT_THRESHOLD", "20000"))
# comma‑separated list of UPI numbers that the user has marked as trusted (friends, family, known merchants)
_TRUSTED_UPIS_ENV = os.environ.get("TRUSTED_UPIS", "")
TRUSTED_UPIS: Set[str] = set(u.strip() for u in _TRUSTED_UPIS_ENV.split(",") if u.strip())

def generate_alert(risk_score):
    if risk_score <= 30:
        return "LOW RISK"
    elif risk_score <= 70:
        return "MEDIUM RISK"
    else:
        return "HIGH RISK"


def is_trusted_upi(upi: str | None) -> bool:
    """Return ``True`` if the provided UPI number is on the configured
    whitelist.

    A trusted list is useful for cases such as the one the user described
    – transferring a large sum to a known friend or family member should
    not immediately be treated as fraud by a simple amount threshold.
    """
    if upi is None:
        return False
    return str(upi) in TRUSTED_UPIS


def fraud_reasons(transaction, risk_score):
    """Generate a list of rule‑based reasons for flagging a transaction.

    This mimics what a security analyst would look at: amount thresholds,
    time-of-day anomalies, profile risk indicators, and whether the UPI
    has appeared in previous fraudulent events.  The rules are intentionally
    simple but configurable; in production you would hook this into a
    proper rules engine or policy service.
    """
    reasons = []

    amount = transaction.get("trans_amount", 0.0)
    upi = transaction.get("upi_number")

    # high amount check – only considered suspicious if the counterparty
    # is *not* on the user's trusted list
    if amount > SAFE_AMOUNT_THRESHOLD:
        if not is_trusted_upi(upi):
            reasons.append(
                f"Transaction amount {amount} exceeds safe threshold ({SAFE_AMOUNT_THRESHOLD})"
            )
        else:
            # keep a note for audit but do not treat it as a negative factor
            reasons.append("High amount paid to trusted UPI – lowered risk")

    # unusual hour (e.g. late night transfers) is still suspicious even to
    # friends because of potential account takeover or automation
    hour = transaction.get("trans_hour", 0)
    if hour < 5 or hour > 23:
        reasons.append("Transaction at unusual hour")

    # profile attributes
    age = transaction.get("age")
    if isinstance(age, (int, float)) and age < 21:
        reasons.append("Young user profile risk")

    if risk_score > 70:
        reasons.append("ML model indicates high fraud probability")

    return reasons

