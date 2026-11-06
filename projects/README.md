# Projects

Seven tools that run together behind one local launcher, the **Hub**, which is linked from the portfolio site
(an **Apps** button appears in the portfolio nav whenever the Hub is running on this machine).

| App | What it does | Why it matters |
|---|---|---|
| **Hub** (`hub/`) | One server and one Apple-style home page for everything below | Single place to use all of it |
| **LifeOS** (`lifeos/`) | Today view, habits, reading plan, fitness, tasks, risks, goals, money (cards, payoff plan, spending, investments), income ideas, YouTube and research planners | Runs your day. Data stays on your PC |
| **TradeScout** (`tradescout/`) | Daily top-10 stock ideas: news + filings + Reddit sentiment, a model trained from scratch, calibrated confidence, stops, position sizes, a paper-trading ledger | Research + an honest ML showcase |
| **JobFit** (`jobfit/`) | Scores your resume against job postings, finds missing skills and ATS keywords, tailors bullets with a local LLM | Better applications, better job |
| **LogLens** (`loglens/`) | Collapses CI test failures into root causes, with optional local-LLM triage | Matches your GE/Intel V&V work. Sellable |
| **DataGuard** (`dataguard/`) | YAML data-quality rules → HTML report + CI exit code | Matches your ETL/validation work |
| **apisaas** (`apisaas/`) | API keys, plans, quotas, rate limits, Stripe webhooks | Turns any of these into a paid API |

## Start everything (Windows)
Double-click **`start_hub.bat`**, or:
```bat
cd "%USERPROFILE%\ai code\projects"
pip install -r requirements-all.txt
cd hub && python -m hub              :: opens http://localhost:8000
```
Run the portfolio in another terminal (`npm run dev` in `ai code`) → http://localhost:3000. Its nav shows **Apps**.

Optional: `ollama serve` adds AI triage to LogLens and tailored bullets to JobFit (it uses `llama3.1:8b`,
which you already have).

## Tests
Each project has its own suite: `cd <project> && python -m pytest -q`. All 40 tests pass.

## Before you push to GitHub (do this for your resume)
Push each project as its own public repo (better for recruiters) or this folder as one monorepo. `.gitignore`
already excludes your personal data: `*.db`, `.tradescout/`, `.lifeos/`.

## Turning this into money: the shortest paths
1. **Freelance now**: LogLens + DataGuard + JobFit are portfolio pieces for Python automation and data-pipeline gigs.
2. **Productize**: put LogLens or JobFit behind `apisaas`, deploy (Fly.io/Render/Railway, about $5–10/mo), take payments with Stripe.
3. **Content**: every project is a YouTube video and a blog post (ideas are pre-loaded in LifeOS → YouTube).
4. **Career**: the portfolio "Lab" section and these repos show ML, NLP, APIs, data quality and product sense.

> TradeScout is a research tool, not financial advice. Paper trade first.
