"""Generic SQLite store: one table per collection, columns from schema.py."""
from __future__ import annotations

import os
import sqlite3
import threading
from pathlib import Path

from .schema import COLLECTIONS

SQL_TYPE = {"number": "REAL", "bool": "INTEGER"}


class Store:
    def __init__(self, path: str | Path | None = None):
        path = path or os.getenv("LIFEOS_DB", str(Path.home() / ".lifeos" / "lifeos.db"))
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        with self.lock, self.conn:
            for name, spec in COLLECTIONS.items():
                cols = ", ".join(f'"{f}" {SQL_TYPE.get(t, "TEXT")}' for f, t, _ in spec["fields"])
                self.conn.execute(f'CREATE TABLE IF NOT EXISTS "{name}" (id INTEGER PRIMARY KEY, {cols})')
                have = {r[1] for r in self.conn.execute(f'PRAGMA table_info("{name}")')}
                for f, t, _ in spec["fields"]:  # simple forward migration when you add fields
                    if f not in have:
                        self.conn.execute(f'ALTER TABLE "{name}" ADD COLUMN "{f}" {SQL_TYPE.get(t, "TEXT")}')
            self.conn.execute("CREATE TABLE IF NOT EXISTS reading_log (id INTEGER PRIMARY KEY, date TEXT, book_id INTEGER, pages REAL)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS habit_log (date TEXT, habit TEXT, PRIMARY KEY(date, habit))")

    def _fields(self, coll: str) -> list[str]:
        return [f for f, _, _ in COLLECTIONS[coll]["fields"]]

    def list(self, coll: str, order: str = "id DESC") -> list[dict]:
        with self.lock:
            return [dict(r) for r in self.conn.execute(f'SELECT * FROM "{coll}" ORDER BY {order}')]

    def get(self, coll: str, id_: int) -> dict | None:
        with self.lock:
            r = self.conn.execute(f'SELECT * FROM "{coll}" WHERE id=?', (id_,)).fetchone()
        return dict(r) if r else None

    def add(self, coll: str, data: dict) -> dict:
        keys = [k for k in self._fields(coll) if k in data]
        with self.lock, self.conn:
            cur = self.conn.execute(
                f'INSERT INTO "{coll}" ({", ".join(chr(34)+k+chr(34) for k in keys)}) VALUES ({", ".join("?" * len(keys))})',
                [data[k] for k in keys])
        return self.get(coll, cur.lastrowid)

    def update(self, coll: str, id_: int, data: dict) -> dict | None:
        keys = [k for k in self._fields(coll) if k in data]
        if keys:
            with self.lock, self.conn:
                self.conn.execute(f'UPDATE "{coll}" SET {", ".join(chr(34)+k+chr(34)+"=?" for k in keys)} WHERE id=?',
                                  [data[k] for k in keys] + [id_])
        return self.get(coll, id_)

    def delete(self, coll: str, id_: int) -> bool:
        with self.lock, self.conn:
            return self.conn.execute(f'DELETE FROM "{coll}" WHERE id=?', (id_,)).rowcount > 0

    def count(self, coll: str) -> int:
        with self.lock:
            return self.conn.execute(f'SELECT COUNT(*) FROM "{coll}"').fetchone()[0]

    def sql(self, q: str, args: tuple = ()) -> list[dict]:
        with self.lock, self.conn:
            return [dict(r) for r in self.conn.execute(q, args)]
