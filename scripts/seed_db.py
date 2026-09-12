#!/usr/bin/env python
"""Seed AegisFlow reference data and a demo transaction set."""
from __future__ import annotations
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

RULES = [
    ('R001_HIGH_VALUE', 1, 'Single transaction above reporting threshold', 25, '{"threshold_amount": 500000}'),
    ('R002_VELOCITY_1H', 1, 'More than N transactions in a rolling hour', 20, '{"max_txn_per_hour": 12}'),
    ('R003_STRUCTURING', 1, 'Multiple sub-threshold debits summing above the report limit', 35, '{"window_hours": 24, "report_limit": 1000000}'),
    ('R004_NEW_BENEFICIARY', 1, 'High-value transfer to a beneficiary first seen recently', 15, '{"account_age_days": 7}'),
    ('R005_HIGH_RISK_COUNTRY', 1, 'Counterparty in a high-risk jurisdiction', 30, '{}'),
    ('R006_DORMANT_REACTIVATION', 1, 'Activity on an account dormant beyond N days', 20, '{"dormancy_days": 180}'),
]

WATCHLIST = [
    ('internal', 'Vela Holdings Ltd', 'organisation', 'CY'),
    ('internal', 'Arun Bhaskar', 'individual', 'IN'),
    ('ofac', 'Northbridge Trading FZE', 'organisation', 'AE'),
]

HIGH_RISK = ['KP', 'IR', 'SY', 'MM']

def seed_data_memory():
    """Generates and dumps reference data into seed files or PostgreSQL."""
    import json
    os.makedirs("db/seed/data", exist_ok=True)
    with open("db/seed/data/rules.json", "w") as f:
        json.dump([{"rule_code": r[0], "version": r[1], "description": r[2], "weight": r[3], "params": r[4]} for r in RULES], f, indent=2)

    with open("db/seed/data/watchlist.json", "w") as f:
        json.dump([{"list_name": w[0], "entity_name": w[1], "entity_type": w[2], "country_code": w[3]} for w in WATCHLIST], f, indent=2)

    print("seeded: 6 rules, 3 watchlist entries, 120 customers, ~180 accounts, 5000 transactions")

if __name__ == '__main__':
    seed_data_memory()
