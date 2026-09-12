import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

class TypologyGenerator:
    """Generates synthetic money-laundering typologies: Smurfing, Layering, Round-Tripping."""

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate_smurfing(
        self,
        target_account_id: str,
        smurf_account_ids: List[str],
        base_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Smurfing / Structuring: Multiple deposits just under $10,000 threshold
        sent from multiple source accounts to one target within a short window.
        """
        if base_time is None:
            base_time = datetime.now(timezone.utc)

        txns = []
        for i, source_id in enumerate(smurf_account_ids):
            # Amount strictly between $8,500 and $9,950
            amount = round(random.uniform(8500.0, 9950.0), 2)
            ts = base_time + timedelta(minutes=i * 12 + random.randint(1, 5))
            txns.append({
                "id": str(uuid.uuid4()),
                "ts": ts.isoformat(),
                "account_id": source_id,
                "counterparty_id": target_account_id,
                "merchant_id": None,
                "amount": amount,
                "currency": "USD",
                "channel": "transfer",
                "status": "completed",
                "typology": "smurfing",
                "is_fraud": True
            })
        return txns

    def generate_layering(
        self,
        chain_account_ids: List[str],
        initial_amount: float = 45000.0,
        base_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Layering: Rapid chain of transfers through a series of accounts
        with slight decay in amount (simulating fee deductions).
        """
        if base_time is None:
            base_time = datetime.now(timezone.utc)

        txns = []
        current_amt = initial_amount
        for i in range(len(chain_account_ids) - 1):
            src_id = chain_account_ids[i]
            dst_id = chain_account_ids[i + 1]
            ts = base_time + timedelta(minutes=i * 8 + random.randint(1, 3))
            
            txns.append({
                "id": str(uuid.uuid4()),
                "ts": ts.isoformat(),
                "account_id": src_id,
                "counterparty_id": dst_id,
                "merchant_id": None,
                "amount": current_amt,
                "currency": "USD",
                "channel": "transfer",
                "status": "completed",
                "typology": "layering",
                "is_fraud": True
            })
            # Deduct 1-3% fee per hop
            current_amt = round(current_amt * random.uniform(0.97, 0.99), 2)

        return txns

    def generate_round_tripping(
        self,
        origin_account_id: str,
        intermediary_account_ids: List[str],
        amount: float = 25000.0,
        base_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Round-Tripping: Circular flow of funds departing an account and
        returning via intermediary entities within a short window.
        """
        if base_time is None:
            base_time = datetime.now(timezone.utc)

        full_path = [origin_account_id] + intermediary_account_ids + [origin_account_id]
        txns = []
        for i in range(len(full_path) - 1):
            src = full_path[i]
            dst = full_path[i + 1]
            ts = base_time + timedelta(minutes=i * 15 + random.randint(2, 6))

            txns.append({
                "id": str(uuid.uuid4()),
                "ts": ts.isoformat(),
                "account_id": src,
                "counterparty_id": dst,
                "merchant_id": None,
                "amount": amount,
                "currency": "USD",
                "channel": "transfer",
                "status": "completed",
                "typology": "round_tripping",
                "is_fraud": True
            })
        return txns
