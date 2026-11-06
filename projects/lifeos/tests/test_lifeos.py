from fastapi.testclient import TestClient

from lifeos.app import create_app
from lifeos.finance import card_summary, categorize, parse_bank_csv


def client(tmp_path):
    return TestClient(create_app(str(tmp_path / "l.db")))


def test_seeded_today(tmp_path):
    c = client(tmp_path)
    assert "LifeOS" in c.get("/").text
    d = c.get("/api/today").json()
    assert d["workout"] and len(d["reading"]) == 4 and d["pages_target"] == 12
    assert len(d["risks"]) == 3 and d["risks"][0]["likelihood"] * d["risks"][0]["impact"] == 16
    assert len(d["habits"]) == 6


def test_crud_and_schema(tmp_path):
    c = client(tmp_path)
    assert "tasks" in c.get("/api/schema").json()
    t = c.post("/api/c/tasks", json={"title": "x", "priority": "P1", "status": "todo", "bogus": 1}).json()
    assert c.patch(f"/api/c/tasks/{t['id']}", json={"status": "done"}).json()["status"] == "done"
    assert c.delete(f"/api/c/tasks/{t['id']}").status_code == 200
    assert c.get("/api/c/nope").status_code == 404


def test_reading_rollover_and_habits(tmp_path):
    c = client(tmp_path)
    book = c.get("/api/today").json()["reading"][0]
    r = c.post(f"/api/reading/{book['id']}", json={"pages": 5000}).json()
    assert r["status"] == "done"
    assert len(c.get("/api/today").json()["reading"]) == 4  # next queued book started
    assert c.post("/api/habits/workout").json()["done"] is True
    h = {x["habit"]: x for x in c.get("/api/today").json()["habits"]}
    assert h["workout"]["done"] and h["workout"]["streak"] == 1


def test_money(tmp_path):
    c = client(tmp_path)
    c.post("/api/c/cards", json={"name": "Chase", "balance": 3000, "limit": 5000, "apr": 27.99, "min_payment": 90, "due_day": 1})
    c.post("/api/c/cards", json={"name": "Discover", "balance": 1000, "limit": 8000, "apr": 19.99, "min_payment": 35, "due_day": 15})
    c.post("/api/c/investments", json={"symbol": "VOO", "quantity": 10, "cost_basis": 400, "price": 500, "kind": "ETF"})
    csv = "Transaction Date,Description,Amount\n11/01/2026,STARBUCKS #123,-6.50\n11/02/2026,KROGER,-80.25\n11/03/2026,PAYMENT THANK YOU,500\n"
    r = c.post("/api/purchases/import", files={"file": ("a.csv", csv)}, data={"card": "Chase"}).json()
    assert r["added"] == 2
    assert c.post("/api/purchases/import", files={"file": ("a.csv", csv)}).json()["added"] == 0
    m = c.get("/api/money").json()
    assert m["cards"]["avalanche_order"] == ["Chase", "Discover"]
    assert m["cards"]["utilization"] == round(100 * 4000 / 13000, 1)
    assert m["investments"]["gain"] == 1000 and m["net_worth"] == 5000 - 4000


def test_finance_helpers():
    assert categorize("UBER EATS 123") == "Dining" and categorize("AMZN Mktp") == "Shopping"
    rows = parse_bank_csv("Date,Description,Debit,Credit\n2026-11-01,Netflix,15.49,\n")
    assert rows[0]["amount"] == 15.49 and rows[0]["category"] == "Subscriptions" and rows[0]["need_or_want"] == "want"
    s = card_summary([{"name": "A", "balance": 1000, "limit": 2000, "apr": 24, "min_payment": 50}], extra_payment=200)
    assert s["payoff_months"] and s["payoff_months"] < 6
