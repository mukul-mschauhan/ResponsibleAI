"""Configuration constants for the Responsible AI Banking Control Tower demo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
AUDIT_LOG_PATH = DATA_DIR / "audit_log.csv"


@dataclass(frozen=True)
class RiskThresholds:
    low: float = 0.30
    medium: float = 0.60
    high: float = 0.75


@dataclass(frozen=True)
class FairnessThresholds:
    false_positive_warning: float = 0.10
    false_positive_critical: float = 0.15
    disparate_impact_warning: float = 1.35
    disparate_impact_critical: float = 1.75


RISK_THRESHOLDS = RiskThresholds()
FAIRNESS_THRESHOLDS = FairnessThresholds()

MERCHANT_CATEGORIES = [
    "Groceries",
    "Fuel",
    "Electronics",
    "Travel",
    "Jewellery",
    "Digital Goods",
    "Healthcare",
    "Restaurant",
    "Cash Withdrawal",
]

COUNTRIES = ["Bahrain", "UAE", "Saudi Arabia", "India", "UK", "USA", "Singapore", "Unknown"]
CHANNELS = ["POS", "Online", "ATM", "Mobile Wallet"]
DEVICE_TYPES = ["Known Device", "New Device"]
CUSTOMER_SEGMENTS = ["Mass", "Affluent", "Premium", "SME Owner"]
TENURE_BANDS = ["0-6 months", "6-24 months", "2-5 years", "5+ years"]
INCOME_BANDS = ["Low", "Middle", "Upper Middle", "High"]
TRAVEL_PROFILES = ["Domestic Mostly", "Occasional International", "Frequent International"]

PROTECTED_ATTRIBUTES = ["nationality", "religion", "gender", "ethnicity"]
