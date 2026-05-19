"""Synthetic banking transaction data for demo purposes only.

No real customer data is used. This generator intentionally creates realistic-looking
patterns for a Responsible AI fraud detection walkthrough.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import (
    CHANNELS,
    COUNTRIES,
    CUSTOMER_SEGMENTS,
    DEVICE_TYPES,
    INCOME_BANDS,
    MERCHANT_CATEGORIES,
    TENURE_BANDS,
    TRAVEL_PROFILES,
)


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1 / (1 + np.exp(-x))


def generate_transactions(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    amount = rng.gamma(shape=2.0, scale=42.0, size=n)
    amount = np.clip(amount, 2, 2500).round(2)

    customer_avg_spend = rng.gamma(shape=2.2, scale=28.0, size=n) + 10
    amount_to_avg_ratio = amount / customer_avg_spend

    hour = rng.integers(0, 24, size=n)
    is_night = ((hour <= 5) | (hour >= 23)).astype(int)

    country = rng.choice(COUNTRIES, size=n, p=[0.60, 0.10, 0.07, 0.08, 0.05, 0.05, 0.03, 0.02])
    is_foreign = (country != "Bahrain").astype(int)

    device_type = rng.choice(DEVICE_TYPES, size=n, p=[0.78, 0.22])
    is_new_device = (device_type == "New Device").astype(int)

    merchant_category = rng.choice(
        MERCHANT_CATEGORIES,
        size=n,
        p=[0.20, 0.13, 0.13, 0.11, 0.07, 0.11, 0.07, 0.12, 0.06],
    )
    high_risk_merchant = np.isin(merchant_category, ["Electronics", "Jewellery", "Digital Goods", "Cash Withdrawal"]).astype(int)

    channel = rng.choice(CHANNELS, size=n, p=[0.43, 0.38, 0.08, 0.11])
    is_online = (channel == "Online").astype(int)

    velocity_10m = rng.poisson(lam=1.2, size=n)
    failed_auth_count = rng.poisson(lam=0.25, size=n)
    customer_segment = rng.choice(CUSTOMER_SEGMENTS, size=n, p=[0.45, 0.28, 0.18, 0.09])
    tenure_band = rng.choice(TENURE_BANDS, size=n, p=[0.15, 0.25, 0.32, 0.28])
    income_band = rng.choice(INCOME_BANDS, size=n, p=[0.22, 0.42, 0.25, 0.11])
    travel_profile = rng.choice(TRAVEL_PROFILES, size=n, p=[0.62, 0.27, 0.11])

    # Latent synthetic fraud process. Avoid protected attributes entirely.
    score_raw = (
        -5.0
        + 0.42 * np.log1p(amount)
        + 0.75 * (amount_to_avg_ratio > 5).astype(int)
        + 0.90 * is_new_device
        + 0.65 * is_foreign
        + 0.55 * is_night
        + 0.65 * high_risk_merchant
        + 0.55 * is_online
        + 0.35 * velocity_10m
        + 0.75 * failed_auth_count
        - 0.35 * (tenure_band == "5+ years").astype(int)
        - 0.25 * (travel_profile == "Frequent International").astype(int) * is_foreign
        + rng.normal(0, 0.75, size=n)
    )
    fraud_probability = _sigmoid(score_raw)
    is_fraud = rng.binomial(1, fraud_probability)

    df = pd.DataFrame(
        {
            "transaction_id": [f"TXN-{100000 + i}" for i in range(n)],
            "amount_bhd": amount,
            "customer_avg_spend_bhd": customer_avg_spend.round(2),
            "amount_to_avg_ratio": amount_to_avg_ratio.round(2),
            "merchant_category": merchant_category,
            "transaction_hour": hour,
            "country": country,
            "is_foreign": is_foreign,
            "device_type": device_type,
            "is_new_device": is_new_device,
            "channel": channel,
            "is_online": is_online,
            "velocity_10m": velocity_10m,
            "failed_auth_count": failed_auth_count,
            "customer_segment": customer_segment,
            "tenure_band": tenure_band,
            "income_band": income_band,
            "travel_profile": travel_profile,
            "is_fraud": is_fraud,
        }
    )
    return df


def default_transaction() -> dict:
    return {
        "amount_bhd": 1200.0,
        "customer_avg_spend_bhd": 35.0,
        "merchant_category": "Electronics",
        "transaction_hour": 2,
        "country": "UK",
        "device_type": "New Device",
        "channel": "Online",
        "velocity_10m": 4,
        "failed_auth_count": 2,
        "customer_segment": "Affluent",
        "tenure_band": "5+ years",
        "income_band": "Upper Middle",
        "travel_profile": "Occasional International",
    }
