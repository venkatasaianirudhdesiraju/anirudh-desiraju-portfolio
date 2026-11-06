"""LifeOS API + dashboard.  uvicorn lifeos.app:app  → http://localhost:8000"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from fastapi import Body, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .db import Store
from .finance import card_summary, parse_bank_csv, spending_summary
from .schema import COLLECTIONS
from .seed import seed

PRINCIPLES = [
    "Pay yourself first: savings and investing happen automatically, before spending.",
    "Small daily reps beat rare heroic efforts. Protect the streak.",
    "Ship something small today. Done and public beats perfect and private.",
    "Kill high-interest debt before chasing high returns.",
    "Sleep, walk and lift. Your energy is the base of everything else.",
    "Say less, listen more, and remember names. People remember how you made them feel.",
    "One deep-work block before checking messages.",
    "Risk only what you can lose. Size every bet small enough to survive being wrong.",
    "Write it down. A plan you can see is a plan you'll follow.",
    "Ask for more: rates, raises, discounts. The worst answer is no.",
]
HABITS = ["workout", "reading", "8k_steps", "no_impulse_spend", "deep_work", "sleep_7h"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def create_app(db_path: str | None = None, seed_data: bool = True) -> FastAPI:
    app = FastAPI(title="LifeOS", version=__version__)
    store = Store(db_path)
    if seed_data:
        seed(store)
    static = Path(__file__).parent / "static"
    page = (static / "index.html").read_text(encoding="utf-8")
    app.mount("/static", StaticFiles(directory=static), name="static")

    def _coll(c: str) -> str:
        if c not in COLLECTIONS:
            raise HTTPException(404, f"unknown collection {c}")
        return c

    @app.get("/", response_class=HTMLResponse)
    def home():
        return page

    @app.get("/health")
    def health():
        return {"ok": True, "app": "lifeos", "version": __version__}

    @app.get("/api/schema")
    def schema():
        return {c: {"label": s["label"], "fields": [{"name": f, "type": t, **x} for f, t, x in s["fields"]]}
                for c, s in COLLECTIONS.items()}

    @app.get("/api/c/{coll}")
    def list_(coll: str):
        return store.list(_coll(coll))

    @app.post("/api/c/{coll}", status_code=201)
    def add(coll: str, data: dict = Body(...)):
        return store.add(_coll(coll), data)

    @app.patch("/api/c/{coll}/{id_}")
    def update(coll: str, id_: int, data: dict = Body(...)):
        row = store.update(_coll(coll), id_, data)
        if not row:
            raise HTTPException(404)
        return row

    @app.delete("/api/c/{coll}/{id_}")
    def delete(coll: str, id_: int):
        if not store.delete(_coll(coll), id_):
            raise HTTPException(404)
        return {"deleted": id_}

    # ------------------------------------------------------------------ reading + habits
    @app.post("/api/reading/{book_id}")
    def log_reading(book_id: int, pages: float = Body(..., embed=True)):
        b = store.get("books", book_id)
        if not b:
            raise HTTPException(404)
        store.sql("INSERT INTO reading_log(date, book_id, pages) VALUES (?,?,?)", (date.today().isoformat(), book_id, pages))
        read = min((b["pages_read"] or 0) + pages, b["total_pages"] or 10**9)
        upd = {"pages_read": read}
        if b["total_pages"] and read >= b["total_pages"]:
            upd["status"] = "done"
            nxt = store.sql("SELECT id FROM books WHERE status='queued' ORDER BY id LIMIT 1")
            if nxt:
                store.update("books", nxt[0]["id"], {"status": "reading"})
        return store.update("books", book_id, upd)

    @app.post("/api/habits/{habit}")
    def toggle_habit(habit: str):
        if habit not in HABITS:
            raise HTTPException(404)
        d = date.today().isoformat()
        if store.sql("SELECT 1 FROM habit_log WHERE date=? AND habit=?", (d, habit)):
            store.sql("DELETE FROM habit_log WHERE date=? AND habit=?", (d, habit))
            return {"habit": habit, "done": False}
        store.sql("INSERT INTO habit_log(date, habit) VALUES (?,?)", (d, habit))
        return {"habit": habit, "done": True}

    def _streak(habit: str) -> int:
        days = {r["date"] for r in store.sql("SELECT date FROM habit_log WHERE habit=?", (habit,))}
        n, d = 0, date.today()
        if d.isoformat() not in days:
            d -= timedelta(days=1)
        while d.isoformat() in days:
            n, d = n + 1, d - timedelta(days=1)
        return n

    # ------------------------------------------------------------------ money
    @app.get("/api/money")
    def money():
        cards = store.list("cards", "apr DESC")
        inv = store.list("investments")
        purchases = store.list("purchases", "date DESC")
        invested = sum((i["quantity"] or 0) * (i["price"] or 0) for i in inv)
        cost = sum((i["quantity"] or 0) * (i["cost_basis"] or 0) for i in inv)
        cs = card_summary(cards)
        this_month = date.today().strftime("%Y-%m")
        return {"cards": cs, "spending": spending_summary(purchases, this_month),
                "investments": {"value": round(invested, 2), "cost": round(cost, 2), "gain": round(invested - cost, 2),
                                "gain_pct": round(100 * (invested - cost) / cost, 2) if cost else 0,
                                "holdings": sorted(inv, key=lambda i: -((i["quantity"] or 0) * (i["price"] or 0)))},
                "net_worth": round(invested - cs["total_balance"], 2)}

    @app.post("/api/purchases/import")
    async def import_csv(file: UploadFile = File(...), card: str = Form("")):
        rows = parse_bank_csv((await file.read()).decode("utf-8", errors="replace"), card)
        existing = {(p["date"], p["merchant"], p["amount"]) for p in store.list("purchases")}
        added = 0
        for r in rows:
            if (r["date"], r["merchant"], r["amount"]) not in existing:
                store.add("purchases", r)
                added += 1
        return {"parsed": len(rows), "added": added, "duplicates_skipped": len(rows) - added}

    @app.post("/api/investments/refresh")
    def refresh_prices():
        try:
            import yfinance as yf
        except ImportError:
            raise HTTPException(501, "pip install yfinance to auto-refresh prices")
        updated = 0
        for i in store.list("investments"):
            sym = (i["symbol"] or "").upper()
            if not sym or i["kind"] in {"cash", "401k", "other"}:
                continue
            try:
                px = float(yf.Ticker(sym).fast_info["last_price"])
                store.update("investments", i["id"], {"price": round(px, 4)})
                updated += 1
            except Exception:
                continue
        return {"updated": updated}

    # ------------------------------------------------------------------ today
    @app.get("/api/today")
    def today():
        t = date.today()
        dow = DAYS[t.weekday()]
        read_today = {r["book_id"]: r["p"] for r in store.sql(
            "SELECT book_id, SUM(pages) p FROM reading_log WHERE date=? GROUP BY book_id", (t.isoformat(),))}
        reading = [{**b, "read_today": read_today.get(b["id"], 0)} for b in store.list("books", "id")
                   if b["status"] == "reading"]
        tasks = [x for x in store.list("tasks", "priority, due") if x["status"] != "done"]
        overdue = [x for x in tasks if x["due"] and x["due"] < t.isoformat()]
        risks = sorted((r for r in store.list("risks") if r["status"] != "closed"),
                       key=lambda r: -((r["likelihood"] or 0) * (r["impact"] or 0)))
        due_cards = []
        for c in store.list("cards"):
            if c["due_day"] and (c["balance"] or 0) > 0:
                days_left = (int(c["due_day"]) - t.day) % 31
                if days_left <= 7:
                    due_cards.append({**c, "days_left": days_left})
        done = {r["habit"] for r in store.sql("SELECT habit FROM habit_log WHERE date=?", (t.isoformat(),))}
        return {
            "date": t.isoformat(), "weekday": dow, "principle": PRINCIPLES[t.toordinal() % len(PRINCIPLES)],
            "workout": next((w for w in store.list("workouts") if w["day"] == dow), None),
            "reading": reading, "pages_target": sum(b["daily_pages"] or 0 for b in reading),
            "pages_today": sum(read_today.values()),
            "tasks": tasks[:7], "overdue": len(overdue), "open_tasks": len(tasks),
            "risks": risks[:3], "cards_due": due_cards,
            "habits": [{"habit": h, "done": h in done, "streak": _streak(h)} for h in HABITS],
            "goals": store.list("goals", "id"),
        }

    @app.get("/api/export")
    def export():
        data = {c: store.list(c, "id") for c in COLLECTIONS}
        return JSONResponse(data, headers={"Content-Disposition": f"attachment; filename=lifeos-{date.today()}.json"})

    @app.post("/api/import-json")
    def import_json(data: dict = Body(...)):
        n = 0
        for c, rows in data.items():
            if c in COLLECTIONS:
                for r in rows:
                    store.add(c, {k: v for k, v in r.items() if k != "id"})
                    n += 1
        return {"imported": n}

    app.state.store = store
    return app


app = create_app()
