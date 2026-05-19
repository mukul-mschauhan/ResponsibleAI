"""Audit logging utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.config import AUDIT_LOG_PATH, DATA_DIR


def write_audit_event(
    transaction: Dict,
    prediction,
    reason_summary: str,
    final_action: str,
    reviewer: str = "Demo Fraud Analyst",
    path: Path = AUDIT_LOG_PATH,
) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    record = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "transaction_id": transaction.get("transaction_id", "TXN-DEMO"),
        "model_version": "FraudModel_v2.1_RAIDemo",
        "fraud_score": round(float(prediction.fraud_score), 4),
        "risk_level": prediction.risk_level,
        "recommended_action": prediction.recommended_action,
        "final_action": final_action,
        "human_review_required": prediction.human_review_required,
        "reviewer": reviewer,
        "reason_summary": reason_summary,
    }
    df = pd.DataFrame([record])
    if path.exists():
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)


def read_audit_log(path: Path = AUDIT_LOG_PATH) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(
        columns=[
            "timestamp",
            "transaction_id",
            "model_version",
            "fraud_score",
            "risk_level",
            "recommended_action",
            "final_action",
            "human_review_required",
            "reviewer",
            "reason_summary",
        ]
    )
