"""Online / Offline Feature Parity Integration Test Suite.
Replays transaction streams and asserts 100% parity between 
online feature store reads and offline PyArrow point-in-time batch feature outputs.
"""
from __future__ import annotations
import pandas as pd
from datetime import datetime, timedelta, timezone
import pytest

from aegis_ml.features.definitions import get_feature_catalog
from aegis_ml.features.offline import OfflineFeatureBuilder
from ingestion.online_features import OnlineFeatureStore

NOW = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)

def test_single_source_catalog_definitions():
    """Verify feature catalog defines specs correctly."""
    catalog = get_feature_catalog()
    assert len(catalog) > 0
    names = [f.name for f in catalog]
    assert "acct_tx_count_1h" in names
    assert "acct_amt_sum_24h" in names

def test_online_offline_velocity_parity():
    """Stream transactions and assert online and offline feature calculation parity."""
    # 1. Setup test transaction sequence for Account A100
    txns = [
        {"id": "tx_1", "account_id": "A100", "amount": 150.0, "ts": NOW - timedelta(minutes=45)},
        {"id": "tx_2", "account_id": "A100", "amount": 350.0, "ts": NOW - timedelta(minutes=15)},
        {"id": "tx_3", "account_id": "A100", "amount": 500.0, "ts": NOW},
    ]
    df_raw = pd.DataFrame(txns)

    # 2. Offline batch point-in-time calculation
    offline_builder = OfflineFeatureBuilder(df_raw)
    offline_df = offline_builder.compute_point_in_time_features()

    # 3. Online real-time ingestion calculation
    online_store = OnlineFeatureStore()
    online_results = []
    for tx in txns:
        epoch = tx["ts"].timestamp()
        res = online_store.record_transaction(
            account_id=tx["account_id"],
            amount=tx["amount"],
            timestamp_epoch=epoch,
            transaction_id=tx["id"]
        )
        online_results.append(res)

    # 4. Assert 100% Parity across transaction sequence
    for idx in range(len(txns)):
        off_row = offline_df.iloc[idx]
        on_res = online_results[idx]

        # Parity assertions
        assert off_row["acct_tx_count_1h"] == on_res["acct_tx_count_1h"], f"1h Count parity mismatch at index {idx}"
        assert off_row["acct_tx_count_24h"] == on_res["acct_tx_count_24h"], f"24h Count parity mismatch at index {idx}"
        assert off_row["acct_amt_sum_24h"] == on_res["acct_amt_sum_24h"], f"24h Sum parity mismatch at index {idx}"

def test_offline_parquet_export(tmp_path):
    """Verify PyArrow offline feature export produces valid parquet file."""
    df_raw = pd.DataFrame([
        {"id": "tx_1", "account_id": "A200", "amount": 200.0, "ts": NOW}
    ])
    builder = OfflineFeatureBuilder(df_raw)
    out_file = str(tmp_path / "offline_features.parquet")
    builder.export_parquet(out_file)

    # Read back parquet file using pandas
    read_df = pd.read_parquet(out_file)
    assert len(read_df) == 1
    assert read_df.iloc[0]["account_id"] == "A200"
    assert read_df.iloc[0]["acct_amt_sum_24h"] == 200.0
