import uuid
import random
from typing import List, Dict, Any

class FraudRingGenerator:
    """Generates coordinated fraud rings sharing devices, IPs, and executing linked activity."""

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate_ring(
        self,
        accounts: List[Dict[str, Any]],
        devices: List[Dict[str, Any]],
        ips: List[Dict[str, Any]],
        ring_size: int = 4
    ) -> Dict[str, Any]:
        """Form a ring of accounts sharing a primary device and IP address."""
        if len(accounts) < ring_size:
            selected_accts = accounts
        else:
            selected_accts = random.sample(accounts, ring_size)

        shared_device = random.choice(devices) if devices else {"id": str(uuid.uuid4())}
        shared_ip = random.choice(ips) if ips else {"id": str(uuid.uuid4())}
        ring_id = f"ring_{uuid.uuid4().hex[:8]}"

        edges = []
        for acct in selected_accts:
            # Account <-> Device edge
            edges.append({
                "src_type": "account",
                "src_id": acct["id"],
                "dst_type": "device",
                "dst_id": shared_device["id"],
                "edge_type": "SHARED_DEVICE",
                "weight": 1.0
            })
            # Account <-> IP edge
            edges.append({
                "src_type": "account",
                "src_id": acct["id"],
                "dst_type": "ip",
                "dst_id": shared_ip["id"],
                "edge_type": "SHARED_IP",
                "weight": 1.0
            })

        return {
            "ring_id": ring_id,
            "account_ids": [a["id"] for a in selected_accts],
            "shared_device_id": shared_device["id"],
            "shared_ip_id": shared_ip["id"],
            "edges": edges
        }
