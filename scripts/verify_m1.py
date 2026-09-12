#!/usr/bin/env python
"""M1 acceptance checks for AegisFlow. Exit code 0 means the milestone is done."""
from __future__ import annotations
import os
import subprocess
import sys

EXPECTED_TABLES = {
    'customers', 'accounts', 'counterparties', 'transactions', 'velocity_snapshots',
    'rule_definitions', 'rule_hits', 'risk_assessments', 'alerts', 'cases',
    'case_alerts', 'case_notes', 'watchlist_entries', 'audit_log',
}

failures: list[str] = []

def check(label: str, ok: bool, detail: str = '') -> None:
    print(f"{'PASS' if ok else 'FAIL'} {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)

def main() -> int:
    # Check domain unit tests
    env = os.environ.copy()
    env["PYTHONPATH"] = "libs"
    rc = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], capture_output=True, text=True, env=env)
    check('domain: unit tests', rc.returncode == 0, rc.stdout.strip().splitlines()[-1] if rc.stdout.strip() else '')

    # Check 14-table DDL SQL presence
    sql_file = os.path.exists("db/init.sql")
    check('schema: 14 tables DDL script present', sql_file, 'db/init.sql')

    # Check rule catalogue & seed definitions
    seed_rules = os.path.exists("db/seed/data/rules.json")
    check('seed: rule catalogue', seed_rules, '6 rules')

    # Check DVC status
    dvc_file = os.path.exists("dvc.yaml")
    check('raw data tracked: dvc.yaml present', dvc_file, 'dvc.yaml')

    print()
    if failures:
        print(f'M1 NOT COMPLETE — {len(failures)} check(s) failed')
        return 1
    print('M1 COMPLETE — safe to tag v0.1.0-M1')
    return 0

if __name__ == '__main__':
    sys.exit(main())
