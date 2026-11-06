# LifeOS — your private life dashboard

One page that runs your day: **today's workout, reading targets, habits, focus tasks, top risks, goals**,
plus **money** (card debt, utilization, avalanche payoff plan, spending by category, investments, net worth)
and planners for **income ideas, YouTube, research and goals**.

Everything is stored in a single SQLite file (`~/.lifeos/lifeos.db` by default) on **your** computer. Nothing is
uploaded anywhere.

It comes pre-filled with a starter plan you can edit:
- **Reading:** 15 books in a deliberate order (money → habits → senior engineering → people → business).
  4 are active at once, with **2–5 pages/day each (12/day total ≈ 15 books/year)**. Finishing a book auto-starts the next.
- **Fitness:** a beginner full-body plan, 3 days/week, plus walking, mobility and a Sunday review.
- **Risks:** 8 common ones, each scored by likelihood × impact with a mitigation plan.
- **Earn:** 7 income ideas tied to the projects in this repo, each with a concrete first step.
- **YouTube:** 5 video ideas with hooks. **Research:** 4 publishable topics with method and venue.
- **Habits:** workout, reading, 8k steps, no impulse spend, deep work, 7h sleep (with streaks).

## Run
```bash
pip install -r requirements.txt
uvicorn lifeos.app:app --port 8001     # http://localhost:8001  (or launch everything via the Hub)
pytest -q
```

## Money setup (10 minutes)
1. **Cards** tab → add each card: balance, limit, APR, minimum payment, due day.
2. **Money** tab → import a CSV export from each bank or card website (Chase, Amex, Discover, Capital One,
   BoA and most others work: date / description / amount or debit+credit columns are detected automatically).
3. **Investments** tab → add holdings; "Refresh prices" pulls live quotes (yfinance).

Backup: `GET /api/export` downloads everything as JSON. To restore, `POST /api/import-json`.
Add a field to any section by editing `lifeos/schema.py`. The database and UI update automatically.
