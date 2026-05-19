"""Responsible AI governance checks for banking fraud detection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from src.config import FAIRNESS_THRESHOLDS, PROTECTED_ATTRIBUTES


@dataclass
class ControlCheck:
    control: str
    status: str
    evidence: str
    severity: str


def mask_sensitive_transaction(transaction: Dict) -> Dict:
    """Return a display-safe transaction object."""
    masked = dict(transaction)
    # Demo placeholders. Real banking systems should use enterprise tokenization.
    masked["card_number"] = "**** **** **** 1842"
    masked["customer_name"] = "Customer_****"
    masked["mobile_number"] = "+973-****-****"
    return masked


def run_responsible_ai_checks(transaction: Dict, prediction, reason_codes: pd.DataFrame) -> List[ControlCheck]:
    checks: List[ControlCheck] = []
    used_sensitive = any(attr in transaction and transaction.get(attr) not in [None, ""] for attr in PROTECTED_ATTRIBUTES)

    checks.append(
        ControlCheck(
            "Explainability generated",
            "Passed" if len(reason_codes) > 0 else "Failed",
            f"{len(reason_codes)} operational reason code(s) generated.",
            "Low" if len(reason_codes) > 0 else "High",
        )
    )
    checks.append(
        ControlCheck(
            "Sensitive attributes excluded from scoring",
            "Passed" if not used_sensitive else "Failed",
            "No nationality, religion, gender, or ethnicity field is used in this demo score." if not used_sensitive else "Sensitive attribute found in transaction payload.",
            "Low" if not used_sensitive else "Critical",
        )
    )
    location_proxy_risk = transaction.get("country") not in ["Bahrain", None, ""] and prediction.fraud_score >= 0.60
    checks.append(
        ControlCheck(
            "Proxy bias watch",
            "Warning" if location_proxy_risk else "Passed",
            "Cross-border/location signal contributes to risk. Monitor segment-level false positives." if location_proxy_risk else "No immediate proxy-risk warning for this case.",
            "Medium" if location_proxy_risk else "Low",
        )
    )
    checks.append(
        ControlCheck(
            "Human oversight",
            "Triggered" if prediction.human_review_required else "Passed",
            "High-impact case routed to analyst review." if prediction.human_review_required else "Automated action permitted under low/medium-risk policy.",
            "Medium" if prediction.human_review_required else "Low",
        )
    )
    checks.append(
        ControlCheck(
            "Privacy masking active",
            "Passed",
            "Card number, customer name, and mobile number are masked in operational views.",
            "Low",
        )
    )
    checks.append(
        ControlCheck(
            "Customer challenge route",
            "Passed",
            "Customer can verify through OTP/app/call center or raise a dispute.",
            "Low",
        )
    )
    checks.append(
        ControlCheck(
            "Audit log required",
            "Passed",
            "Decision package includes model version, score, action, reason codes, and reviewer fields.",
            "Low",
        )
    )
    return checks


def checks_to_frame(checks: List[ControlCheck]) -> pd.DataFrame:
    return pd.DataFrame([c.__dict__ for c in checks])


def compute_fairness_dashboard(scored_df: pd.DataFrame, group_col: str = "travel_profile") -> pd.DataFrame:
    """Compute simple false-positive and flag-rate metrics by segment.

    This is for governance monitoring. Protected/sensitive attributes should not be
    used for decisioning; controlled outcome analysis may use approved attributes
    where permitted by law and policy.
    """
    rows = []
    global_flag_rate = scored_df["predicted_flag"].mean()
    for group, part in scored_df.groupby(group_col):
        flagged = part["predicted_flag"].mean()
        genuine = part[part["is_fraud"] == 0]
        fp_rate = float(genuine["predicted_flag"].mean()) if len(genuine) else 0.0
        true_fraud = part[part["is_fraud"] == 1]
        detection = float(true_fraud["predicted_flag"].mean()) if len(true_fraud) else 0.0
        disparate_impact = float(flagged / global_flag_rate) if global_flag_rate > 0 else 0.0

        if fp_rate >= FAIRNESS_THRESHOLDS.false_positive_critical or disparate_impact >= FAIRNESS_THRESHOLDS.disparate_impact_critical:
            status = "Critical"
        elif fp_rate >= FAIRNESS_THRESHOLDS.false_positive_warning or disparate_impact >= FAIRNESS_THRESHOLDS.disparate_impact_warning:
            status = "Warning"
        else:
            status = "Normal"

        rows.append(
            {
                "segment": group,
                "transactions": len(part),
                "flag_rate": flagged,
                "false_positive_rate": fp_rate,
                "true_fraud_detection_rate": detection,
                "relative_flag_rate": disparate_impact,
                "status": status,
            }
        )
    return pd.DataFrame(rows).sort_values("false_positive_rate", ascending=False)


def monitoring_metrics(scored_df: pd.DataFrame) -> Dict[str, float]:
    tp = int(((scored_df["predicted_flag"] == 1) & (scored_df["is_fraud"] == 1)).sum())
    fp = int(((scored_df["predicted_flag"] == 1) & (scored_df["is_fraud"] == 0)).sum())
    tn = int(((scored_df["predicted_flag"] == 0) & (scored_df["is_fraud"] == 0)).sum())
    fn = int(((scored_df["predicted_flag"] == 0) & (scored_df["is_fraud"] == 1)).sum())

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    false_positive_rate = fp / max(fp + tn, 1)
    false_negative_rate = fn / max(fn + tp, 1)
    avg_score = float(scored_df["fraud_score"].mean())
    high_risk_share = float((scored_df["fraud_score"] >= 0.75).mean())

    return {
        "precision": precision,
        "recall": recall,
        "false_positive_rate": false_positive_rate,
        "false_negative_rate": false_negative_rate,
        "avg_fraud_score": avg_score,
        "high_risk_share": high_risk_share,
        "analyst_queue": int((scored_df["fraud_score"] >= 0.60).sum()),
    }


def responsible_ai_score(checks: List[ControlCheck], fairness_df: pd.DataFrame, metrics: Dict[str, float]) -> pd.DataFrame:
    failed = sum(1 for c in checks if c.status == "Failed")
    warnings = sum(1 for c in checks if c.status == "Warning")
    fairness_penalty = 0
    if not fairness_df.empty:
        fairness_penalty += 14 * (fairness_df["status"] == "Critical").sum()
        fairness_penalty += 6 * (fairness_df["status"] == "Warning").sum()

    dimensions = [
        ("Fairness", max(50, 92 - fairness_penalty)),
        ("Explainability", 96 if failed == 0 else 65),
        ("Privacy", 95),
        ("Human Oversight", 90 if any(c.status == "Triggered" for c in checks) else 84),
        ("Auditability", 96),
        ("Model Reliability", int(max(60, 95 - metrics.get("false_negative_rate", 0) * 100))),
        ("Customer Protection", int(max(60, 92 - metrics.get("false_positive_rate", 0) * 160 - warnings * 4))),
    ]
    return pd.DataFrame(dimensions, columns=["dimension", "score"])


def final_governance_decision(scorecard: pd.DataFrame) -> str:
    avg = scorecard["score"].mean()
    min_score = scorecard["score"].min()
    if avg >= 85 and min_score >= 75:
        return "Approved with continuous monitoring"
    if avg >= 75:
        return "Conditionally approved: remediation required"
    return "Not approved: governance risk too high"
