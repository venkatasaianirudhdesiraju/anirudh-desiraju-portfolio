"""uvicorn apisaas.app:app --reload   → docs at /docs

Put YOUR product endpoints in the `product` router; everything there is authenticated, rate limited,
quota-checked and metered automatically via the `metered` dependency.
"""
from __future__ import annotations

import hmac
import json

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from . import __version__, config
from .billing import SignatureError, verify_stripe
from .db import DB
from .ratelimit import TokenBucket

app = FastAPI(title="Your API", version=__version__)
db = DB(config.DB_PATH)
bucket = TokenBucket()


# ---------------------------------------------------------------- auth + metering dependency
def metered(request: Request, authorization: str = Header(default="")):
    key = authorization.removeprefix("Bearer ").strip()
    cust = db.lookup_key(key) if key else None
    if not cust:
        raise HTTPException(401, "missing or invalid API key", headers={"WWW-Authenticate": "Bearer"})
    plan = config.PLANS.get(cust["plan"], config.PLANS["free"])
    ok, retry = bucket.allow(str(cust["key_id"]), plan.per_minute)
    if not ok:
        raise HTTPException(429, "rate limit exceeded", headers={"Retry-After": f"{retry:.0f}"})
    used = db.month_usage(cust["id"])
    if used >= plan.monthly_quota:
        raise HTTPException(402, f"monthly quota of {plan.monthly_quota} reached — upgrade your plan")
    db.record(cust["id"], request.url.path)
    request.state.quota_remaining = plan.monthly_quota - used - 1
    return cust


def admin(x_admin_token: str = Header(default="")):
    if config.ADMIN_TOKEN == "change-me":
        raise HTTPException(503, "set APISAAS_ADMIN_TOKEN to enable admin endpoints")
    if not hmac.compare_digest(x_admin_token, config.ADMIN_TOKEN):
        raise HTTPException(403, "admin only")


@app.middleware("http")
async def quota_header(request: Request, call_next):
    resp = await call_next(request)
    rem = getattr(request.state, "quota_remaining", None)
    if rem is not None:
        resp.headers["X-Quota-Remaining"] = str(rem)
    return resp


# ---------------------------------------------------------------- public
@app.get("/health")
def health():
    return {"ok": True, "version": __version__}


@app.get("/plans")
def plans():
    return {n: p.__dict__ for n, p in config.PLANS.items()}


class SignupIn(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)


@app.post("/signup", status_code=201)
def signup(body: SignupIn):
    cid = db.upsert_customer(body.email)
    return {"customer_id": cid, "api_key": db.create_key(cid), "plan": db.customer(cid)["plan"],
            "note": "Store this key now — it is not shown again."}


@app.get("/me")
def me(cust=Depends(metered)):
    plan = config.PLANS[cust["plan"]]
    used = db.month_usage(cust["id"])
    return {"email": cust["email"], "plan": plan.name, "used_this_month": used,
            "quota": plan.monthly_quota, "by_endpoint": db.usage_breakdown(cust["id"])}


# ---------------------------------------------------------------- product (replace with yours)
product = APIRouter(prefix="/v1", dependencies=[Depends(metered)])


class TextIn(BaseModel):
    text: str


@product.post("/word-stats")
def word_stats(body: TextIn):
    """Example paid endpoint. Swap in LogLens, JobFit, DataGuard, a model — anything."""
    words = body.text.split()
    return {"words": len(words), "chars": len(body.text), "unique": len({w.lower() for w in words})}


app.include_router(product)


# ---------------------------------------------------------------- admin + billing
@app.post("/admin/customers/{cid}/plan/{plan}", dependencies=[Depends(admin)])
def set_plan(cid: int, plan: str):
    if plan not in config.PLANS or not db.customer(cid):
        raise HTTPException(404, "unknown customer or plan")
    db.set_plan(cid, plan)
    return {"customer_id": cid, "plan": plan}


@app.post("/admin/keys/{prefix}/revoke", dependencies=[Depends(admin)])
def revoke(prefix: str):
    return {"revoked": db.revoke_key(prefix)}


@app.post("/billing/stripe-webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(default="")):
    payload = await request.body()
    try:
        verify_stripe(payload, stripe_signature, config.STRIPE_WEBHOOK_SECRET)
    except SignatureError as e:
        raise HTTPException(400, str(e))
    event = json.loads(payload)
    obj = event.get("data", {}).get("object", {})
    etype = event.get("type")
    if etype == "checkout.session.completed":
        email = (obj.get("customer_details") or {}).get("email") or obj.get("customer_email")
        price = (obj.get("metadata") or {}).get("price_id", "")
        plan = config.STRIPE_PRICE_TO_PLAN.get(price, (obj.get("metadata") or {}).get("plan", "pro"))
        if email and plan in config.PLANS:
            db.set_plan(db.upsert_customer(email), plan, obj.get("customer"))
    elif etype == "customer.subscription.deleted":
        cust = db.customer_by_stripe(obj.get("customer", ""))
        if cust:
            db.set_plan(cust["id"], "free")
    return {"received": True}
