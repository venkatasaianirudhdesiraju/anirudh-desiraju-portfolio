import importlib
import json

import pytest
from fastapi.testclient import TestClient

from apisaas.billing import sign
from apisaas.ratelimit import TokenBucket


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("APISAAS_DB", str(tmp_path / "t.db"))
    monkeypatch.setenv("APISAAS_ADMIN_TOKEN", "adm")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    import apisaas.config, apisaas.app
    importlib.reload(apisaas.config)
    mod = importlib.reload(apisaas.app)
    return TestClient(mod.app), mod


def _key(c, email="a@b.co"):
    return c.post("/signup", json={"email": email}).json()["api_key"]


def test_signup_and_auth(client):
    c, _ = client
    assert c.post("/signup", json={"email": "nope"}).status_code == 422
    key = _key(c)
    assert key.startswith("sk_live_")
    assert c.post("/v1/word-stats", json={"text": "a b"}).status_code == 401
    r = c.post("/v1/word-stats", json={"text": "Hello hello world"}, headers={"Authorization": f"Bearer {key}"})
    assert r.status_code == 200 and r.json() == {"words": 3, "chars": 17, "unique": 2}
    assert r.headers["X-Quota-Remaining"] == "99"
    me = c.get("/me", headers={"Authorization": f"Bearer {key}"}).json()
    assert me["used_this_month"] == 2 and me["by_endpoint"]["/v1/word-stats"] == 1


def test_rate_limit_and_quota(client):
    c, mod = client
    h = {"Authorization": f"Bearer {_key(c)}"}
    codes = [c.post("/v1/word-stats", json={"text": "x"}, headers=h).status_code for _ in range(12)]
    assert codes[:10] == [200] * 10 and codes[10] == 429  # free plan: 10/min burst
    mod.bucket.state.clear()
    mod.config.PLANS["free"] = mod.config.Plan("free", 10, 1000, 0)
    assert c.post("/v1/word-stats", json={"text": "x"}, headers=h).status_code == 402


def test_admin_and_revoke(client):
    c, _ = client
    key = _key(c)
    assert c.post("/admin/customers/1/plan/pro").status_code == 403
    assert c.post("/admin/customers/1/plan/pro", headers={"X-Admin-Token": "adm"}).json()["plan"] == "pro"
    assert c.post(f"/admin/keys/{key[:12]}/revoke", headers={"X-Admin-Token": "adm"}).json()["revoked"] == 1
    assert c.get("/me", headers={"Authorization": f"Bearer {key}"}).status_code == 401


def test_stripe_webhook_upgrades_and_downgrades(client):
    c, mod = client
    key = _key(c, "pay@x.io")
    ev = {"type": "checkout.session.completed", "data": {"object": {
        "customer": "cus_1", "customer_details": {"email": "pay@x.io"}, "metadata": {"plan": "business"}}}}
    body = json.dumps(ev).encode()
    assert c.post("/billing/stripe-webhook", content=body, headers={"Stripe-Signature": "t=1,v1=bad"}).status_code == 400
    assert c.post("/billing/stripe-webhook", content=body, headers={"Stripe-Signature": sign(body, "whsec_test")}).status_code == 200
    assert c.get("/me", headers={"Authorization": f"Bearer {key}"}).json()["plan"] == "business"
    body = json.dumps({"type": "customer.subscription.deleted", "data": {"object": {"customer": "cus_1"}}}).encode()
    c.post("/billing/stripe-webhook", content=body, headers={"Stripe-Signature": sign(body, "whsec_test")})
    assert c.get("/me", headers={"Authorization": f"Bearer {key}"}).json()["plan"] == "free"


def test_token_bucket_refills():
    t = [0.0]
    b = TokenBucket(clock=lambda: t[0])
    assert all(b.allow("k", 60)[0] for _ in range(60))
    assert b.allow("k", 60)[0] is False
    t[0] += 1.0
    assert b.allow("k", 60)[0] is True
