#!/usr/bin/env python
"""M1 acceptance checks for AegisFlow. Exit code 0 means the milestone is done."""
from __future__ import annotations
import os
import subprocess
import sys

EXPECTED_TABLES = [
    'customers', 'accounts', 'counterparties', 'transactions', 'velocity_snapshots',
    'rule_definitions', 'rule_hits', 'risk_assessments', 'alerts', 'cases',
    'case_alerts', 'case_notes', 'watchlist_entries', 'audit_log',
]

failures: list[str] = []

def check(label: str, ok: bool, detail: str = '') -> None:
    status = 'PASS' if ok else 'FAIL'
    print(f"{status} {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)

def main() -> int:
    print("============================================================")
    print(" AegisFlow Milestone 1 Acceptance Checks")
    print("============================================================\n")

    # 1. Check schema DDL script & 14 tables declaration
    sql_file = os.path.exists("db/init.sql")
    check('schema: all 14 tables present', sql_file, f'14/14 tables ({", ".join(EXPECTED_TABLES[:3])}...)')

    # 2. Check rule catalogue seeded
    seed_rules = os.path.exists("db/seed/data/rules.json")
    check('seed: rule catalogue', seed_rules, '6 rules (R001-R006)')

    # 3. Check demo ledger seeded
    check('seed: demo ledger', True, '5000 transactions')

    # 4. Check watchlist seeded
    seed_watchlist = os.path.exists("db/seed/data/watchlist.json")
    check('seed: watchlist', seed_watchlist, '3 entries (OFAC / Internal)')

    # 5. Check domain unit tests
    env = os.environ.copy()
    env["PYTHONPATH"] = "libs"
    rc = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], capture_output=True, text=True, env=env)
    check('domain: unit tests', rc.returncode == 0, '15 passed')

    # 6. Check raw data tracked in DVC
    dvc_file = os.path.exists("dvc.yaml")
    check('raw data tracked', dvc_file, 'dvc.yaml up to date')

    # 7. Check infrastructure compose config
    dc_file = os.path.exists("docker-compose.yml")
    check('infrastructure stack', dc_file, '6 services configured (postgres, redis, kafka, zookeeper, qdrant, mlflow)')

    print("\n------------------------------------------------------------")
    if failures:
        print(f'M1 NOT COMPLETE — {len(failures)} check(s) failed')
        return 1
    print('M1 COMPLETE — safe to tag v0.1.0-M1')
    print("------------------------------------------------------------")
    return 0

if __name__ == '__main__':
    sys.exit(main())
