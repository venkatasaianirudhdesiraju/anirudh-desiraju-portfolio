from __future__ import annotations

import os
from pathlib import Path

HOME = Path(os.getenv("TRADESCOUT_HOME", Path.cwd() / ".tradescout"))
CACHE = HOME / "cache"
MODELS = HOME / "models"
REPORTS = HOME / "reports"
LEDGER_DB = HOME / "ledger.db"
for d in (CACHE, MODELS, REPORTS):
    d.mkdir(parents=True, exist_ok=True)

# SEC requires a descriptive User-Agent with contact info for EDGAR requests.
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "")
HTTP_UA = "Mozilla/5.0 (TradeScout research bot)"

BENCHMARK = "SPY"

# Liquid large caps + sector ETFs. Override with --universe file.txt (one ticker per line).
DEFAULT_UNIVERSE = """
AAPL MSFT NVDA AMZN GOOGL META TSLA AVGO AMD NFLX CRM ORCL ADBE INTC QCOM TXN MU AMAT LRCX KLAC
CSCO IBM NOW UBER SHOP PLTR SNOW PANW CRWD ANET MRVL SMCI ARM COIN MSTR
JPM BAC WFC C GS MS SCHW BLK AXP V MA PYPL SQ
UNH JNJ LLY PFE MRK ABBV TMO ABT DHR BMY AMGN GILD ISRG VRTX REGN MRNA
XOM CVX COP SLB OXY EOG
WMT COST HD LOW TGT NKE SBUX MCD KO PEP PG DIS CMCSA
BA CAT DE GE HON LMT RTX UPS FDX
NEE DUK SO T VZ
SPY QQQ IWM DIA XLF XLK XLE XLV XLI XLY XLP XLU SMH ARKK TLT GLD
""".split()
