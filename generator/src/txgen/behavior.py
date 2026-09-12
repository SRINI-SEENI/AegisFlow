import numpy as np
import random
from typing import Dict, Any

class BehaviorModel:
    """Models per-account spending habits, log-normal transaction amounts, and channel selection."""

    CHANNELS = ["card", "transfer", "wallet"]
    CHANNEL_WEIGHTS = [0.6, 0.25, 0.15]

    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)

    def sample_amount(self, risk_tier: str) -> float:
        """Sample log-normal transaction amount based on account risk tier."""
        if risk_tier == "HIGH":
            # Higher mean & variance for high-risk accounts
            mean, sigma = 5.5, 1.2
        elif risk_tier == "MEDIUM":
            mean, sigma = 4.2, 0.9
        else:
            mean, sigma = 3.5, 0.6

        raw_amt = np.random.lognormal(mean=mean, sigma=sigma)
        return round(float(np.clip(raw_amt, 1.0, 50000.0)), 2)

    def sample_channel(self) -> str:
        """Sample transaction channel (card, transfer, wallet)."""
        return random.choices(self.CHANNELS, weights=self.CHANNEL_WEIGHTS)[0]

    def sample_time_offset_minutes(self) -> int:
        """Sample realistic time gap between transactions for an account."""
        # Exponential distribution with average gap of 180 minutes (3 hours)
        gap = np.random.exponential(scale=180)
        return max(1, int(gap))
