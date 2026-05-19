"""Fraud model wrapper.

The model is deliberately simple and transparent enough for a banking Responsible AI demo.
It trains on synthetic data at runtime and falls back to a calibrated rule score if needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

try:
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
except Exception:  # pragma: no cover - fallback for minimal environments
    ColumnTransformer = None
    OneHotEncoder = None
    Pipeline = None
    RandomForestClassifier = None
    StandardScaler = None

from src.config import RISK_THRESHOLDS

NUMERIC_FEATURES = [
    "amount_bhd",
    "customer_avg_spend_bhd",
    "amount_to_avg_ratio",
    "transaction_hour",
    "is_foreign",
    "is_new_device",
    "is_online",
    "velocity_10m",
    "failed_auth_count",
]

CATEGORICAL_FEATURES = [
    "merchant_category",
    "country",
    "device_type",
    "channel",
    "customer_segment",
    "tenure_band",
    "income_band",
    "travel_profile",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


@dataclass
class PredictionResult:
    fraud_score: float
    risk_level: str
    recommended_action: str
    human_review_required: bool


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    output = df.copy()
    if "amount_to_avg_ratio" not in output:
        avg = output["customer_avg_spend_bhd"].replace(0, 1)
        output["amount_to_avg_ratio"] = output["amount_bhd"] / avg
    output["is_foreign"] = (output["country"] != "Bahrain").astype(int)
    output["is_new_device"] = (output["device_type"] == "New Device").astype(int)
    output["is_online"] = (output["channel"] == "Online").astype(int)
    return output


class FraudModel:
    def __init__(self) -> None:
        self.pipeline = None
        self.is_trained = False
        self.model_name = "FraudModel_v2.1_RAIDemo"

    def train(self, df: pd.DataFrame) -> None:
        df = add_engineered_features(df)
        if Pipeline is None:
            self.pipeline = None
            self.is_trained = False
            return

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUMERIC_FEATURES),
                ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ]
        )
        clf = RandomForestClassifier(
            n_estimators=160,
            max_depth=9,
            min_samples_leaf=8,
            random_state=42,
            class_weight="balanced_subsample",
        )
        self.pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("model", clf)])
        self.pipeline.fit(df[FEATURES], df["is_fraud"])
        self.is_trained = True

    def predict_score(self, transaction: Dict) -> float:
        tx = add_engineered_features(pd.DataFrame([transaction]))
        rule_score = self._rule_score(tx.iloc[0].to_dict())
        if self.is_trained and self.pipeline is not None:
            proba = self.pipeline.predict_proba(tx[FEATURES])[:, 1][0]
            # Blend the learned model with a transparent policy score for demo readability.
            # In production, this calibration would require formal model validation.
            blended = 0.60 * float(proba) + 0.40 * float(rule_score)
            return float(np.clip(blended, 0.01, 0.99))
        return rule_score

    @staticmethod
    def _rule_score(tx: Dict) -> float:
        raw = -4.75
        raw += 0.45 * np.log1p(float(tx.get("amount_bhd", 0)))
        raw += 0.95 * (float(tx.get("amount_to_avg_ratio", 1)) > 5)
        raw += 0.90 * int(tx.get("is_new_device", 0))
        raw += 0.75 * int(tx.get("is_foreign", 0))
        raw += 0.50 * int(tx.get("transaction_hour", 12) <= 5 or tx.get("transaction_hour", 12) >= 23)
        raw += 0.45 * int(tx.get("is_online", 0))
        raw += 0.35 * float(tx.get("velocity_10m", 0))
        raw += 0.80 * float(tx.get("failed_auth_count", 0))
        if tx.get("tenure_band") == "5+ years":
            raw -= 0.25
        if tx.get("travel_profile") == "Frequent International" and int(tx.get("is_foreign", 0)) == 1:
            raw -= 0.30
        score = 1 / (1 + np.exp(-raw))
        return float(np.clip(score, 0.01, 0.99))

    @staticmethod
    def classify(score: float) -> Tuple[str, str, bool]:
        if score >= RISK_THRESHOLDS.high:
            return "Critical", "Temporary hold + customer verification + fraud analyst review", True
        if score >= RISK_THRESHOLDS.medium:
            return "High", "Step-up authentication / app confirmation", True
        if score >= RISK_THRESHOLDS.low:
            return "Medium", "Approve with monitoring", False
        return "Low", "Approve", False

    def predict(self, transaction: Dict) -> PredictionResult:
        score = self.predict_score(transaction)
        risk_level, action, human_review = self.classify(score)
        return PredictionResult(
            fraud_score=score,
            risk_level=risk_level,
            recommended_action=action,
            human_review_required=human_review,
        )


def score_dataset(model: FraudModel, df: pd.DataFrame) -> pd.DataFrame:
    scored = add_engineered_features(df)
    scores = []
    for row in scored[FEATURES].to_dict(orient="records"):
        scores.append(model.predict_score(row))
    scored["fraud_score"] = scores
    scored["predicted_flag"] = (scored["fraud_score"] >= RISK_THRESHOLDS.medium).astype(int)
    return scored
