"""Stripe webhook verification (no SDK needed) + plan changes.

Stripe signs payloads: header `Stripe-Signature: t=<ts>,v1=<hex hmac_sha256(secret, f"{t}.{body}")>`.
"""
from __future__ import annotations

import hashlib
import hmac
import time


class SignatureError(Exception):
    pass


def verify_stripe(payload: bytes, header: str, secret: str, tolerance: int = 300) -> None:
    if not secret:
        raise SignatureError("STRIPE_WEBHOOK_SECRET not configured")
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    ts, sig = parts.get("t"), [v for k, v in (p.split("=", 1) for p in header.split(",") if "=" in p) if k == "v1"]
    if not ts or not sig:
        raise SignatureError("malformed signature header")
    if abs(time.time() - int(ts)) > tolerance:
        raise SignatureError("timestamp outside tolerance")
    expected = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, s) for s in sig):
        raise SignatureError("signature mismatch")


def sign(payload: bytes, secret: str, ts: int | None = None) -> str:
    """Helper for tests / local replay."""
    ts = ts or int(time.time())
    return f"t={ts},v1=" + hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
