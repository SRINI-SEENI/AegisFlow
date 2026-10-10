"""SINGLE SOURCE OF TRUTH: Feature specifications used for both online (Redis) 
and offline (PyArrow point-in-time batch) computation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(frozen=True)
class FeatureSpec:
    name: str
    entity_key: str  # account_id, device_id, ip_id
    window: str      # 1m, 1h, 24h, 7d
    aggregation: str # count, sum, avg, std, nunique
    default_value: float = 0.0
    description: str = ""

# --- Feature Catalog ---
FEATURE_CATALOG: List[FeatureSpec] = [
    # Velocity Features (Account level)
    FeatureSpec("acct_tx_count_1m", "account_id", "1m", "count", 0.0, "Transaction count in last 1 minute"),
    FeatureSpec("acct_tx_count_1h", "account_id", "1h", "count", 0.0, "Transaction count in last 1 hour"),
    FeatureSpec("acct_tx_count_24h", "account_id", "24h", "count", 0.0, "Transaction count in last 24 hours"),
    FeatureSpec("acct_tx_count_7d", "account_id", "7d", "count", 0.0, "Transaction count in last 7 days"),
    
    FeatureSpec("acct_amt_sum_1h", "account_id", "1h", "sum", 0.0, "Transaction amount sum in last 1 hour"),
    FeatureSpec("acct_amt_sum_24h", "account_id", "24h", "sum", 0.0, "Transaction amount sum in last 24 hours"),
    FeatureSpec("acct_amt_sum_7d", "account_id", "7d", "sum", 0.0, "Transaction amount sum in last 7 days"),

    # Shared Entity Degrees
    FeatureSpec("device_sharing_degree_24h", "device_id", "24h", "nunique", 1.0, "Unique accounts sharing this device in 24h"),
    FeatureSpec("ip_sharing_degree_24h", "ip_id", "24h", "nunique", 1.0, "Unique accounts sharing this IP in 24h"),

    # Behavioral Profile Stats
    FeatureSpec("acct_amt_zscore_30d", "account_id", "30d", "zscore", 0.0, "Amount z-score relative to account 30-day mean/std"),
]

def get_feature_catalog() -> List[FeatureSpec]:
    """Return immutable feature catalog."""
    return FEATURE_CATALOG

def get_feature_names() -> List[str]:
    """Return list of all feature names."""
    return [f.name for f in FEATURE_CATALOG]
