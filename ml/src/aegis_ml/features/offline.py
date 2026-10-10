"""Offline point-in-time feature computation using PyArrow / Pandas.
Guarantees point-in-time correctness: features for transaction T_i 
are calculated strictly as-of timestamp T_i (zero future data leakage).
"""
from __future__ import annotations
import os
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from typing import List, Dict, Any

from aegis_ml.features.definitions import FEATURE_CATALOG

class OfflineFeatureBuilder:
    """Computes point-in-time feature tables for ML model training."""

    def __init__(self, raw_transactions_df: pd.DataFrame):
        self.df = raw_transactions_df.copy()
        if "timestamp" in self.df.columns:
            self.df["ts"] = pd.to_datetime(self.df["timestamp"])
        elif "TransactionDT" in self.df.columns:
            self.df["ts"] = pd.to_datetime(self.df["TransactionDT"], unit="s", origin="2026-01-01")
        else:
            self.df["ts"] = pd.to_datetime(self.df.get("ts", pd.Timestamp.now()))
            
        self.df = self.df.sort_values("ts").reset_index(drop=True)

    def compute_point_in_time_features(self) -> pd.DataFrame:
        """Compute rolling window velocity features as-of each transaction timestamp."""
        results = []

        for idx, row in self.df.iterrows():
            current_ts = row["ts"]
            acct_id = row.get("account_id", row.get("card1", "unknown"))

            # Filter historical transactions strictly prior to or at current_ts for this account
            hist = self.df[(self.df["ts"] <= current_ts) & 
                           (self.df.get("account_id", self.df.get("card1")) == acct_id)]

            # 1m, 1h, 24h, 7d windows
            t_1m = current_ts - pd.Timedelta(minutes=1)
            t_1h = current_ts - pd.Timedelta(hours=1)
            t_24h = current_ts - pd.Timedelta(hours=24)
            t_7d = current_ts - pd.Timedelta(days=7)

            amt_col = "amount" if "amount" in self.df.columns else "TransactionAmt"

            cnt_1m = len(hist[hist["ts"] >= t_1m])
            cnt_1h = len(hist[hist["ts"] >= t_1h])
            cnt_24h = len(hist[hist["ts"] >= t_24h])
            cnt_7d = len(hist[hist["ts"] >= t_7d])

            sum_1h = float(hist[hist["ts"] >= t_1h][amt_col].sum())
            sum_24h = float(hist[hist["ts"] >= t_24h][amt_col].sum())
            sum_7d = float(hist[hist["ts"] >= t_7d][amt_col].sum())

            # 30d z-score
            t_30d = current_ts - pd.Timedelta(days=30)
            hist_30d = hist[hist["ts"] >= t_30d][amt_col]
            if len(hist_30d) > 1 and hist_30d.std() > 0:
                zscore = float((row[amt_col] - hist_30d.mean()) / hist_30d.std())
            else:
                zscore = 0.0

            feat_row = {
                "transaction_id": row.get("id", row.get("TransactionID", idx)),
                "ts": current_ts,
                "account_id": acct_id,
                "acct_tx_count_1m": cnt_1m,
                "acct_tx_count_1h": cnt_1h,
                "acct_tx_count_24h": cnt_24h,
                "acct_tx_count_7d": cnt_7d,
                "acct_amt_sum_1h": round(sum_1h, 2),
                "acct_amt_sum_24h": round(sum_24h, 2),
                "acct_amt_sum_7d": round(sum_7d, 2),
                "acct_amt_zscore_30d": round(zscore, 4),
            }
            results.append(feat_row)

        return pd.DataFrame(results)

    def export_parquet(self, output_path: str):
        """Export computed feature table to Parquet format using PyArrow."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        feat_df = self.compute_point_in_time_features()
        table = pa.Table.from_pandas(feat_df)
        pq.write_table(table, output_path)
        print(f"[+] Exported offline feature store to: {output_path} ({len(feat_df)} rows)")
