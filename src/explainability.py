"""Explainability layer for fraud decisions.

This module produces operational reason codes. It is intentionally simple enough for
business users and fraud analysts to understand in a workshop/demo setting.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd


REASON_WEIGHTS = {
    "Amount unusually high vs customer average": 0.22,
    "New device fingerprint": 0.18,
    "Foreign / cross-border transaction": 0.16,
    "Unusual transaction time": 0.10,
    "High-risk merchant category": 0.13,
    "Online channel": 0.08,
    "High transaction velocity": 0.08,
    "Failed authentication attempts": 0.16,
    "Long customer tenure reduces risk": -0.08,
    "Frequent international travel profile reduces cross-border risk": -0.07,
}


def generate_reason_codes(transaction: Dict) -> pd.DataFrame:
    reasons: List[Dict] = []
    amount = float(transaction.get("amount_bhd", 0))
    avg = max(float(transaction.get("customer_avg_spend_bhd", 1)), 1)
    ratio = amount / avg
    hour = int(transaction.get("transaction_hour", 12))

    def add(reason: str, direction: str, contribution: float, detail: str) -> None:
        reasons.append(
            {
                "reason": reason,
                "direction": direction,
                "contribution": contribution,
                "detail": detail,
            }
        )

    if ratio >= 5:
        add(
            "Amount unusually high vs customer average",
            "Increases risk",
            REASON_WEIGHTS["Amount unusually high vs customer average"],
            f"Transaction is {ratio:.1f}x the customer's typical spend.",
        )
    if transaction.get("device_type") == "New Device":
        add("New device fingerprint", "Increases risk", REASON_WEIGHTS["New device fingerprint"], "Device is not previously associated with the customer.")
    if transaction.get("country") != "Bahrain":
        add("Foreign / cross-border transaction", "Increases risk", REASON_WEIGHTS["Foreign / cross-border transaction"], f"Transaction country is {transaction.get('country')}.")
    if hour <= 5 or hour >= 23:
        add("Unusual transaction time", "Increases risk", REASON_WEIGHTS["Unusual transaction time"], f"Transaction occurred at {hour}:00.")
    if transaction.get("merchant_category") in ["Electronics", "Jewellery", "Digital Goods", "Cash Withdrawal"]:
        add("High-risk merchant category", "Increases risk", REASON_WEIGHTS["High-risk merchant category"], f"Merchant category: {transaction.get('merchant_category')}.")
    if transaction.get("channel") == "Online":
        add("Online channel", "Increases risk", REASON_WEIGHTS["Online channel"], "Card-not-present transaction.")
    if int(transaction.get("velocity_10m", 0)) >= 3:
        add("High transaction velocity", "Increases risk", REASON_WEIGHTS["High transaction velocity"], f"{transaction.get('velocity_10m')} transactions in 10 minutes.")
    if int(transaction.get("failed_auth_count", 0)) >= 1:
        add("Failed authentication attempts", "Increases risk", REASON_WEIGHTS["Failed authentication attempts"], f"{transaction.get('failed_auth_count')} recent failed authentication attempts.")
    if transaction.get("tenure_band") == "5+ years":
        add("Long customer tenure reduces risk", "Reduces risk", REASON_WEIGHTS["Long customer tenure reduces risk"], "Customer has long-standing relationship with the bank.")
    if transaction.get("travel_profile") == "Frequent International" and transaction.get("country") != "Bahrain":
        add("Frequent international travel profile reduces cross-border risk", "Reduces risk", REASON_WEIGHTS["Frequent international travel profile reduces cross-border risk"], "Foreign activity is less unusual for this customer.")

    if not reasons:
        add("No major anomaly detected", "Neutral", 0.0, "Transaction appears consistent with customer behavior.")

    df = pd.DataFrame(reasons).sort_values("contribution", ascending=False)
    return df


def analyst_explanation(transaction: Dict, fraud_score: float, recommended_action: str) -> str:
    reasons = generate_reason_codes(transaction)
    top = reasons.head(4)["reason"].tolist()
    return (
        f"The transaction received a fraud risk score of {fraud_score:.2f}. "
        f"The main drivers are: {', '.join(top)}. "
        f"Recommended action: {recommended_action}. The decision should be recorded with reason codes and escalated when customer harm is possible."
    )


def customer_support_explanation(transaction: Dict, recommended_action: str) -> str:
    return (
        "This transaction looks different from the customer's normal usage pattern. "
        "For safety, the bank should verify the customer through a secure channel rather than permanently blocking the transaction without review. "
        f"Current recommendation: {recommended_action}."
    )
