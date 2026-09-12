import json
from typing import Dict, Any, List

class LabelSink:
    """Manages evaluation ground-truth labels for transactions and entities."""

    def __init__(self):
        self.labels: List[Dict[str, Any]] = []

    def record_label(
        self,
        transaction_id: str,
        is_fraud: bool,
        typology: str = None,
        ring_id: str = None
    ):
        """Record evaluation label for a generated transaction."""
        self.labels.append({
            "transaction_id": transaction_id,
            "is_fraud": is_fraud,
            "typology": typology,
            "ring_id": ring_id
        })

    def export_json(self, filepath: str):
        """Export recorded ground truth labels to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.labels, f, indent=2)

    def get_summary(self) -> Dict[str, int]:
        """Return summary breakdown of ground truth labels."""
        total = len(self.labels)
        fraud = sum(1 for l in self.labels if l["is_fraud"])
        smurfing = sum(1 for l in self.labels if l.get("typology") == "smurfing")
        layering = sum(1 for l in self.labels if l.get("typology") == "layering")
        round_tripping = sum(1 for l in self.labels if l.get("typology") == "round_tripping")

        return {
            "total_transactions": total,
            "fraud_count": fraud,
            "clean_count": total - fraud,
            "smurfing_count": smurfing,
            "layering_count": layering,
            "round_tripping_count": round_tripping
        }
