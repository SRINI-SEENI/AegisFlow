"""Online Redis Feature Store Manager.
Executes atomic LUA updates on Redis sorted sets and hashes for 
sub-10ms online feature retrieval during live payment scoring.
"""
from __future__ import annotations
import json
import time
from typing import Dict, Any, Optional

LUA_SLIDING_WINDOW_UPDATE = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window_start = tonumber(ARGV[2])
local score = now
local member = ARGV[3]

-- Add new transaction timestamp member
redis.call('ZADD', key, score, member)

-- Remove expired elements outside sliding window
redis.call('ZREMRANGEBYSCORE', key, '-inf', '(' .. window_start)

-- Set TTL for auto cleanup (86400s = 24 hours)
redis.call('EXPIRE', key, 86400)

-- Return current valid count within window
return redis.call('ZCARD', key)
"""

class OnlineFeatureStore:
    """Manages real-time feature updates in Redis memory."""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.local_cache = {}  # Local fallback when Redis is unavailable

    def record_transaction(
        self,
        account_id: str,
        amount: float,
        timestamp_epoch: float = None,
        transaction_id: str = None
    ) -> Dict[str, Any]:
        """Atomically record incoming transaction event and update Redis feature counters."""
        if timestamp_epoch is None:
            timestamp_epoch = time.time()
        if transaction_id is None:
            transaction_id = f"tx_{int(timestamp_epoch*1000)}"

        now_ms = timestamp_epoch
        window_1h = now_ms - 3600
        window_24h = now_ms - 86400

        features = {}

        if self.redis:
            try:
                # 1. Update 1h sliding window ZSET
                zset_1h = f"vel:acct:{account_id}:1h"
                count_1h = self.redis.eval(
                    LUA_SLIDING_WINDOW_UPDATE, 1, zset_1h, now_ms, window_1h, transaction_id
                )

                # 2. Update 24h sliding window ZSET
                zset_24h = f"vel:acct:{account_id}:24h"
                count_24h = self.redis.eval(
                    LUA_SLIDING_WINDOW_UPDATE, 1, zset_24h, now_ms, window_24h, transaction_id
                )

                # 3. Update account feature HASH
                hash_key = f"feat:acct:{account_id}"
                self.redis.hincrbyfloat(hash_key, "acct_amt_sum_24h", amount)
                self.redis.hset(hash_key, "last_tx_ts", now_ms)

                # Read latest Redis state
                amt_sum_24h = float(self.redis.hget(hash_key, "acct_amt_sum_24h") or 0.0)

                features = {
                    "acct_tx_count_1h": int(count_1h),
                    "acct_tx_count_24h": int(count_24h),
                    "acct_amt_sum_24h": round(amt_sum_24h, 2)
                }
            except Exception as e:
                print(f"[-] Redis update fallback triggered: {e}")

        if not features:
            # Local fallback in-memory dict
            acct_data = self.local_cache.setdefault(account_id, {"txs": [], "sum_24h": 0.0})
            acct_data["txs"].append((timestamp_epoch, amount))
            acct_data["sum_24h"] += amount

            txs_1h = [t for t in acct_data["txs"] if t[0] >= window_1h]
            txs_24h = [t for t in acct_data["txs"] if t[0] >= window_24h]

            features = {
                "acct_tx_count_1h": len(txs_1h),
                "acct_tx_count_24h": len(txs_24h),
                "acct_amt_sum_24h": round(acct_data["sum_24h"], 2)
            }

        return features

    def get_online_features(self, account_id: str) -> Dict[str, Any]:
        """Fetch current online features for account_id in sub-10ms."""
        if self.redis:
            try:
                hash_key = f"feat:acct:{account_id}"
                zset_1h = f"vel:acct:{account_id}:1h"
                zset_24h = f"vel:acct:{account_id}:24h"

                count_1h = self.redis.zcard(zset_1h) or 0
                count_24h = self.redis.zcard(zset_24h) or 0
                sum_24h = float(self.redis.hget(hash_key, "acct_amt_sum_24h") or 0.0)

                # Fetch graph features if present
                gfeat_key = f"gfeat:acct:{account_id}"
                gfeat_raw = self.redis.get(gfeat_key)
                gfeat = json.loads(gfeat_raw) if gfeat_raw else {}

                return {
                    "account_id": account_id,
                    "acct_tx_count_1h": count_1h,
                    "acct_tx_count_24h": count_24h,
                    "acct_amt_sum_24h": sum_24h,
                    "component_size": gfeat.get("component_size", 1),
                    "dist_to_fraud": gfeat.get("dist_to_fraud", -1),
                    "pagerank_score": gfeat.get("pagerank_score", 0.0)
                }
            except Exception as e:
                print(f"[-] Redis read fallback triggered: {e}")

        # Fallback return default profile
        return {
            "account_id": account_id,
            "acct_tx_count_1h": 1,
            "acct_tx_count_24h": 1,
            "acct_amt_sum_24h": 100.0,
            "component_size": 1,
            "dist_to_fraud": -1,
            "pagerank_score": 0.0
        }
