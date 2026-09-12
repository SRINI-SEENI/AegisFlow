import uuid
import random
from typing import List, Dict, Any
from faker import Faker

fake = Faker()

class PopulationGenerator:
    def __init__(self, seed: int = 42):
        fake.seed_instance(seed)
        random.seed(seed)

    def generate_accounts(self, count: int = 100) -> List[Dict[str, Any]]:
        accounts = []
        for _ in range(count):
            accounts.append({
                "id": str(uuid.uuid4()),
                "holder_name": fake.name(),
                "risk_tier": random.choice(["LOW", "LOW", "LOW", "MEDIUM", "HIGH"]),
                "kyc_level": random.choice([1, 2, 3]),
                "status": "active"
            })
        return accounts

    def generate_devices(self, count: int = 30) -> List[Dict[str, Any]]:
        devices = []
        for _ in range(count):
            devices.append({
                "id": str(uuid.uuid4()),
                "fingerprint": f"fp_{fake.md5()[:12]}",
                "reputation": round(random.uniform(0.5, 1.0), 2)
            })
        return devices

    def generate_ips(self, count: int = 30) -> List[Dict[str, Any]]:
        ips = []
        for _ in range(count):
            ips.append({
                "id": str(uuid.uuid4()),
                "ip": fake.ipv4(),
                "reputation": round(random.uniform(0.5, 1.0), 2)
            })
        return ips

    def generate_merchants(self, count: int = 20) -> List[Dict[str, Any]]:
        merchants = []
        mccs = ["5411", "5812", "5732", "5999", "7995"]  # Groceries, Dining, Electronics, Misc, Gambling
        for _ in range(count):
            merchants.append({
                "id": str(uuid.uuid4()),
                "name": fake.company(),
                "mcc": random.choice(mccs),
                "reputation": round(random.uniform(0.7, 1.0), 2)
            })
        return merchants
