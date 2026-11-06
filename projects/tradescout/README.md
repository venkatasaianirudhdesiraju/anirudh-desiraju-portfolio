# TradeScout — daily stock research bot (trained from scratch)

Every morning TradeScout:
1. **Pulls data** — 8 years of daily prices for ~120 liquid stocks/ETFs (Yahoo via `yfinance`, Stooq fallback),
   plus fresh **news** (Yahoo Finance RSS, Google News), **SEC filings** (EDGAR), **Reddit** (r/stocks, r/investing,
   r/wallstreetbets, r/StockMarket) and any **blogs/RSS** you list in `feeds.txt`.
2. **Scores sentiment** per ticker — finance lexicon with negation handling, recency- and source-weighted
   (optional FinBERT transformer).
3. **Runs its own model** — a gradient-boosted classifier trained **from scratch** on 27 technical and
   cross-sectional features (momentum, mean reversion, volatility, RSI, MACD, distance from highs/averages,
   volume shocks, relative strength vs SPY).
4. **Outputs the top 10** with **LONG/SHORT**, a **confidence %**, entry, **stop-loss**, **target**, **share count**,
   **$ size** and **% of account**, plus the headlines and the reasons behind each pick.
5. **Paper-trades itself** — every pick goes into a ledger and is scored against what the market actually did.

## The part that matters: honesty
- **Confidence is calibrated, not made up.** The model is tested walk-forward (it only ever trains on the past,
  with an embargo gap), and probabilities are calibrated with isotonic regression on those out-of-sample
  predictions. "60%" means: in testing, signals like this were right about 60% of the time.
- **Every report starts with a model health check:** out-of-sample AUC, accuracy vs a naive baseline,
  and a backtest after trading costs. If there's no real edge, it says **"NO reliable edge detected"**.
  The test suite checks this both ways: it finds a planted edge, and it reports none on pure noise.
- Daily stock direction is close to a coin flip for everyone. A real edge of 52–55% is good. Anything claiming
  80–90% is lying. Expect the real-data model to be modest, and **trust the live paper record over the backtest.**
- News sentiment tilts the probability by at most ±3 points. It's a heuristic, because free sources don't give
  years of history to validate it. The ledger stores sentiment with every pick, so after a few months you can
  retrain with sentiment as a validated feature.

## Position sizing
For each idea: stop = 1.5 × ATR, target = 2 × the stop distance. Shares = the **smallest** of:
- **risk budget**: lose at most `--risk`% of the account (default 1%) if the stop is hit
- **quarter-Kelly**: based on the calibrated win probability and the 2:1 payoff (no trade if Kelly ≤ 0)
- **max position**: at most `--max-pos`% of the account (default 10%) in one name

Shorts need a margin account. Beginners: take the LONG ideas only, or just watch.

## Run (Windows, from this folder)
```bat
pip install -r requirements.txt
python -m tradescout train                         :: ~2–5 min: downloads history, trains, validates
python -m tradescout picks --account 10000 --open  :: today's top 10 → .tradescout\reports\picks_DATE.html
python -m tradescout score                         :: score past paper picks: live win rate by confidence
python -m tradescout news NVDA AAPL                :: inspect collected news + sentiment
python -m tradescout train --demo                  :: offline synthetic market (no internet needed)
pytest -q
```
Set `SEC_USER_AGENT="Your Name you@email.com"` to turn on EDGAR filings (the SEC requires it).
Retrain weekly. Schedule `run_daily.bat` in Task Scheduler for weekday mornings.

## Recommended way to use it
1. Paper trade for **at least 4–8 weeks**. Run `score` daily.
2. Only consider real money if the live win rate in the higher-confidence buckets roughly matches the
   calibration table **and** live P&L is positive after costs.
3. Then start small: 0.25–0.5% risk per trade.

## Ideas to extend
Earnings-calendar filter, options-implied volatility, sector-neutral picks, LightGBM/XGBoost or a small
PyTorch sequence model, Alpaca paper-trading API to place bracket orders automatically, Telegram alerts.

> Research tool, not financial advice. Markets are risky; you can lose money.
