"""SQLite storage (swap for Postgres by replacing this module). Keys are stored only as SHA-256 hashes."""
from __future__ import annotations

import hashlib
import secrets
import sqlite3
import threading
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, plan TEXT NOT NULL DEFAULT 'free',
  stripe_customer TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS api_keys (
  id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id), key_hash TEXT UNIQUE NOT NULL,
  prefix TEXT NOT NULL, revoked INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS usage (
  customer_id INTEGER NOT NULL, period TEXT NOT NULL, endpoint TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (customer_id, period, endpoint));
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def period() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


class DB:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self.lock = threading.Lock()

    def q(self, sql: str, args: tuple = ()) -> list[sqlite3.Row]:
        with self.lock:
            return self.conn.execute(sql, args).fetchall()

    # customers -------------------------------------------------------------------------------
    def upsert_customer(self, email: str, plan: str = "free") -> int:
        self.q("INSERT OR IGNORE INTO customers(email, plan, created_at) VALUES (?,?,?)", (email.lower(), plan, now()))
        return self.q("SELECT id FROM customers WHERE email=?", (email.lower(),))[0]["id"]

    def set_plan(self, customer_id: int, plan: str, stripe_customer: str | None = None) -> None:
        self.q("UPDATE customers SET plan=?, stripe_customer=COALESCE(?, stripe_customer) WHERE id=?",
               (plan, stripe_customer, customer_id))

    def customer(self, customer_id: int) -> sqlite3.Row | None:
        rows = self.q("SELECT * FROM customers WHERE id=?", (customer_id,))
        return rows[0] if rows else None

    def customer_by_stripe(self, stripe_customer: str) -> sqlite3.Row | None:
        rows = self.q("SELECT * FROM customers WHERE stripe_customer=?", (stripe_customer,))
        return rows[0] if rows else None

    # keys ------------------------------------------------------------------------------------
    def create_key(self, customer_id: int) -> str:
        key = "sk_live_" + secrets.token_urlsafe(32)
        self.q("INSERT INTO api_keys(customer_id, key_hash, prefix, created_at) VALUES (?,?,?,?)",
               (customer_id, hash_key(key), key[:12], now()))
        return key  # shown once; only the hash is stored

    def lookup_key(self, key: str) -> sqlite3.Row | None:
        rows = self.q("""SELECT k.id AS key_id, c.* FROM api_keys k JOIN customers c ON c.id=k.customer_id
                         WHERE k.key_hash=? AND k.revoked=0""", (hash_key(key),))
        return rows[0] if rows else None

    def revoke_key(self, prefix: str) -> int:
        with self.lock:
            return self.conn.execute("UPDATE api_keys SET revoked=1 WHERE prefix=?", (prefix,)).rowcount

    # usage -----------------------------------------------------------------------------------
    def record(self, customer_id: int, endpoint: str) -> None:
        self.q("""INSERT INTO usage(customer_id, period, endpoint, count) VALUES (?,?,?,1)
                  ON CONFLICT(customer_id, period, endpoint) DO UPDATE SET count=count+1""",
               (customer_id, period(), endpoint))

    def month_usage(self, customer_id: int) -> int:
        return self.q("SELECT COALESCE(SUM(count),0) n FROM usage WHERE customer_id=? AND period=?",
                      (customer_id, period()))[0]["n"]

    def usage_breakdown(self, customer_id: int) -> dict[str, int]:
        return {r["endpoint"]: r["count"] for r in
                self.q("SELECT endpoint, count FROM usage WHERE customer_id=? AND period=?", (customer_id, period()))}
