from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    name: str
    monthly_quota: int     # requests per calendar month
    per_minute: int        # burst rate limit
    price_usd: float


PLANS: dict[str, Plan] = {
    "free": Plan("free", 100, 10, 0),
    "pro": Plan("pro", 10_000, 120, 19),
    "business": Plan("business", 250_000, 1_200, 199),
}

DB_PATH = os.getenv("APISAAS_DB", "apisaas.db")
ADMIN_TOKEN = os.getenv("APISAAS_ADMIN_TOKEN", "change-me")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
# Stripe price id → plan name. Fill from your Stripe dashboard.
STRIPE_PRICE_TO_PLAN = {k: v for k, v in (p.split("=") for p in os.getenv("STRIPE_PRICES", "").split(",") if "=" in p)}
