# apisaas — starter kit for selling an API

The boring-but-essential layer every paid API needs, done properly, so you can put **any** Python
function behind it and charge for it:

- **Signup → API key** (shown once, stored only as a SHA-256 hash, revocable)
- **Plans** (`free` 100 req/mo, `pro` 10k, `business` 250k — edit `config.py`)
- **Per-key rate limiting** (token bucket, `429` + `Retry-After`)
- **Monthly quotas + usage metering** per endpoint (`402` when exhausted, `X-Quota-Remaining` header)
- **Stripe webhooks** with signature verification (no SDK) → upgrade on checkout, downgrade on cancel
- **Admin endpoints** (change plan, revoke key) behind `X-Admin-Token`
- SQLite by default; the DB module is small enough to swap for Postgres in an hour

## Run
```bash
pip install -r requirements.txt
export APISAAS_ADMIN_TOKEN=$(python -c "import secrets;print(secrets.token_hex(16))")
uvicorn apisaas.app:app --reload        # http://localhost:8000/docs
curl -X POST localhost:8000/signup -H 'content-type: application/json' -d '{"email":"me@x.com"}'
curl -X POST localhost:8000/v1/word-stats -H "Authorization: Bearer sk_live_..." \
     -H 'content-type: application/json' -d '{"text":"hello world"}'
pytest -q
```

## Add your product
Add routes to the `product` router in `apisaas/app.py` — they are automatically authenticated, rate limited,
quota-checked and metered:
```python
@product.post("/analyze-logs")
def analyze_logs(body: LogsIn):
    from loglens.core import analyze_texts
    return analyze_texts(body.logs)
```

## Taking payments
1. Create Products/Prices in Stripe and a Payment Link or Checkout Session with `metadata.plan=pro`.
2. Point a webhook at `/billing/stripe-webhook` for `checkout.session.completed` and `customer.subscription.deleted`.
3. Set `STRIPE_WEBHOOK_SECRET` (and optionally `STRIPE_PRICES=price_123=pro,price_456=business`).

## Production checklist
Run behind HTTPS (Caddy / a PaaS), one worker or a Redis-backed limiter, back up the DB volume,
add email verification on signup, and put the admin token in a secret manager.
