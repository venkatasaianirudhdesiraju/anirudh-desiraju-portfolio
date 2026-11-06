"""News + chatter collectors. Each returns a list of Item(ticker, source, title, summary, url, published).

Sources (all free, no keys): Yahoo Finance RSS per ticker, Google News RSS search, Reddit (r/stocks,
r/investing, r/wallstreetbets, r/StockMarket), SEC EDGAR recent filings (8-K etc.; needs SEC_USER_AGENT),
and any extra RSS/blog feeds you list in feeds.txt (one URL per line).
"""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote_plus

import httpx

from ..config import HTTP_UA, SEC_USER_AGENT

TAG = re.compile(r"<[^>]+>")
CASHTAG = re.compile(r"\$([A-Z]{1,5})\b")


@dataclass
class Item:
    ticker: str
    source: str
    title: str
    summary: str
    url: str
    published: datetime | None

    @property
    def text(self) -> str:
        return f"{self.title}. {self.summary}"


def _clean(s: str | None) -> str:
    return html.unescape(TAG.sub(" ", s or "")).strip()


def _date(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _get(url: str, headers: dict | None = None) -> str | None:
    try:
        r = httpx.get(url, headers={"User-Agent": HTTP_UA, **(headers or {})}, timeout=15, follow_redirects=True)
        return r.text if r.status_code == 200 else None
    except httpx.HTTPError:
        return None


def parse_feed(xml: str, ticker: str, source: str) -> list[Item]:
    """RSS 2.0 and Atom."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = []
    for it in root.iter("item"):
        items.append(Item(ticker, source, _clean(it.findtext("title")), _clean(it.findtext("description"))[:500],
                          it.findtext("link") or "", _date(it.findtext("pubDate"))))
    for e in root.iter("{http://www.w3.org/2005/Atom}entry"):
        link = e.find("a:link", ns)
        items.append(Item(ticker, source, _clean(e.findtext("a:title", namespaces=ns)),
                          _clean(e.findtext("a:summary", namespaces=ns))[:500],
                          link.get("href", "") if link is not None else "",
                          _date(e.findtext("a:updated", namespaces=ns))))
    return items


def yahoo(ticker: str) -> list[Item]:
    x = _get(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US")
    return parse_feed(x, ticker, "yahoo") if x else []


def google_news(ticker: str) -> list[Item]:
    x = _get(f"https://news.google.com/rss/search?q={quote_plus(ticker + ' stock')}+when:2d&hl=en-US&gl=US&ceid=US:en")
    return parse_feed(x, ticker, "google_news") if x else []


def sec_filings(ticker: str) -> list[Item]:
    if not SEC_USER_AGENT:
        return []
    x = _get(f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=&owner=include&count=10&output=atom",
             {"User-Agent": SEC_USER_AGENT})
    return parse_feed(x, ticker, "sec") if x else []


def reddit(universe: set[str]) -> list[Item]:
    """Recent posts from investing subs; tickers found by $CASHTAG or bare uppercase symbol in the universe."""
    out = []
    for sub in ("stocks", "investing", "wallstreetbets", "StockMarket"):
        try:
            r = httpx.get(f"https://www.reddit.com/r/{sub}/new.json?limit=100", headers={"User-Agent": HTTP_UA}, timeout=15)
            posts = r.json()["data"]["children"] if r.status_code == 200 else []
        except (httpx.HTTPError, ValueError, KeyError):
            continue
        for p in posts:
            d = p["data"]
            text = f"{d.get('title', '')} {d.get('selftext', '')[:1000]}"
            syms = set(CASHTAG.findall(text)) | {w for w in re.findall(r"\b[A-Z]{2,5}\b", d.get("title", "")) if w in universe}
            for s in syms & universe:
                out.append(Item(s, f"reddit/{sub}", d.get("title", ""), d.get("selftext", "")[:500],
                                "https://reddit.com" + d.get("permalink", ""),
                                datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc)))
    return out


def custom_feeds(path: str | Path, universe: set[str]) -> list[Item]:
    """Blogs / newsletters / any RSS. Items are attributed to tickers mentioned in their text."""
    p = Path(path)
    if not p.exists():
        return []
    out = []
    for url in [u.strip() for u in p.read_text().splitlines() if u.strip() and not u.startswith("#")]:
        x = _get(url)
        for it in parse_feed(x, "", url) if x else []:
            syms = set(CASHTAG.findall(it.text)) | {w for w in re.findall(r"\b[A-Z]{2,5}\b", it.text) if w in universe}
            for s in syms & universe:
                out.append(Item(s, it.source, it.title, it.summary, it.url, it.published))
    return out


def collect(tickers: list[str], hours: int = 36, feeds_file: str | None = "feeds.txt", workers: int = 16) -> list[Item]:
    universe = set(tickers)
    jobs = [(f, t) for t in tickers for f in (yahoo, google_news, sec_filings)]
    items: list[Item] = []
    with ThreadPoolExecutor(workers) as ex:
        for res in ex.map(lambda ft: ft[0](ft[1]), jobs):
            items.extend(res)
    items += reddit(universe)
    if feeds_file:
        items += custom_feeds(feeds_file, universe)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    seen, out = set(), []
    for it in items:
        key = (it.ticker, it.title.lower()[:120])
        if key in seen or (it.published and it.published < cutoff):
            continue
        seen.add(key)
        out.append(it)
    return out
