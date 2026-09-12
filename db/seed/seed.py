import os
import json
import uuid
from datetime import datetime, timezone

DEMO_USERS = [
    {"email": "admin@aegisflow.io", "name": "System Admin", "role": "admin"},
    {"email": "analyst.priya@aegisflow.io", "name": "Priya Sharma", "role": "aml_analyst"},
    {"email": "analyst.marcus@aegisflow.io", "name": "Marcus Vance", "role": "fraud_analyst"},
    {"email": "manager.sarah@aegisflow.io", "name": "Sarah Connor", "role": "manager"},
]

MOCK_SANCTIONS_LIST = [
    {"entity_name": "Apex Holdings Ltd", "entity_type": "ORGANIZATION", "country": "RU", "list_name": "OFAC_SDN"},
    {"entity_name": "Vortex Trading Corp", "entity_type": "ORGANIZATION", "country": "IR", "list_name": "OFAC_SDN"},
    {"entity_name": "Viktor Petrov", "entity_type": "INDIVIDUAL", "country": "RU", "list_name": "EU_SANCTIONS"},
    {"entity_name": "Shadow Global Logistics", "entity_type": "ORGANIZATION", "country": "KP", "list_name": "UN_SANCTIONS"},
]

INITIAL_RULES = [
    {"rule_id": "RULE_001", "name": "Sanctions List Direct Match", "action": "DECLINE", "priority": 100},
    {"rule_id": "RULE_002", "name": "Impossible Travel Velocity", "action": "DECLINE", "priority": 90},
    {"rule_id": "RULE_003", "name": "High Amount New Device", "action": "REVIEW", "priority": 70},
    {"rule_id": "RULE_004", "name": "Rapid Smurfing Threshold", "action": "REVIEW", "priority": 80},
]

ADVERSE_MEDIA_CORPUS = [
    {
        "article_id": "news_001",
        "title": "International Shell Network Uncovered in Banking Probe",
        "entities": ["Apex Holdings Ltd", "Viktor Petrov"],
        "date": "2026-05-14",
        "source": "Global Financial Intelligence",
        "text": "Regulators and law enforcement agencies have identified Apex Holdings Ltd and individual associate Viktor Petrov as core nodes in an elaborate international shell network facilitating illicit fund transfers through high-frequency accounts across multiple international jurisdictions."
    },
    {
        "article_id": "news_002",
        "title": "Fintech Fraud Ring Exploits Shared Mobile Devices",
        "entities": ["Vortex Trading Corp"],
        "date": "2026-07-22",
        "source": "CyberCrime Watch",
        "text": "Cybersecurity researchers highlighted a major fraud syndicate utilizing virtualized device emulators and shared IP proxies to execute automated smurfing deposits into digital wallets linked to Vortex Trading Corp."
    }
]

def generate_seed_artifacts(output_dir: str = "db/seed/data"):
    """Generate JSON seed data files for database initialization."""
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "users.json"), "w") as f:
        json.dump(DEMO_USERS, f, indent=2)

    with open(os.path.join(output_dir, "sanctions.json"), "w") as f:
        json.dump(MOCK_SANCTIONS_LIST, f, indent=2)

    with open(os.path.join(output_dir, "rules.json"), "w") as f:
        json.dump(INITIAL_RULES, f, indent=2)

    with open(os.path.join(output_dir, "adverse_media.json"), "w") as f:
        json.dump(ADVERSE_MEDIA_CORPUS, f, indent=2)

    print(f"[+] Successfully generated seed data artifacts in '{output_dir}':")
    print(f"  - users.json ({len(DEMO_USERS)} users)")
    print(f"  - sanctions.json ({len(MOCK_SANCTIONS_LIST)} entries)")
    print(f"  - rules.json ({len(INITIAL_RULES)} rules)")
    print(f"  - adverse_media.json ({len(ADVERSE_MEDIA_CORPUS)} articles)")

if __name__ == "__main__":
    generate_seed_artifacts()
