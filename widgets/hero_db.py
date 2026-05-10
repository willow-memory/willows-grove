"""widgets/hero_db.py — SQLite state store for hero easter eggs.
b17: HERO1  ΔΣ=42

Tracks:
  · which easter eggs have ever fired (achievements)
  · per-egg cooldowns (last_fired timestamp)
  · persistent counters (uptime milestones, tick counts, konami progress)
  · session log (last N egg firings for debug)
"""
import sqlite3
import time
from pathlib import Path

_DB_PATH = Path(__file__).parent / "hero_eggs.db"


def _conn() -> sqlite3.Connection:
    con = sqlite3.connect(_DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    """Create tables if they don't exist. Safe to call on every boot."""
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS eggs (
                id          TEXT PRIMARY KEY,
                label       TEXT NOT NULL,
                first_fired REAL,
                last_fired  REAL,
                fire_count  INTEGER NOT NULL DEFAULT 0,
                cooldown_s  REAL NOT NULL DEFAULT 30.0,
                enabled     INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS counters (
                key   TEXT PRIMARY KEY,
                value INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS egg_log (
                ts    REAL NOT NULL,
                egg_id TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS egg_log_ts ON egg_log(ts);
        """)


def register_egg(egg_id: str, label: str, cooldown_s: float = 30.0) -> None:
    """Upsert an egg definition — safe to call every boot."""
    with _conn() as con:
        con.execute("""
            INSERT INTO eggs (id, label, cooldown_s)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET label=excluded.label
        """, (egg_id, label, cooldown_s))


def can_fire(egg_id: str) -> bool:
    """True if the egg is enabled and past its cooldown."""
    with _conn() as con:
        row = con.execute(
            "SELECT enabled, last_fired, cooldown_s FROM eggs WHERE id=?",
            (egg_id,)
        ).fetchone()
    if not row or not row["enabled"]:
        return False
    if row["last_fired"] is None:
        return True
    return (time.time() - row["last_fired"]) >= row["cooldown_s"]


def fire(egg_id: str) -> None:
    """Record a firing — updates last_fired, fire_count, and the log."""
    now = time.time()
    with _conn() as con:
        con.execute("""
            UPDATE eggs
            SET last_fired  = ?,
                first_fired = COALESCE(first_fired, ?),
                fire_count  = fire_count + 1
            WHERE id = ?
        """, (now, now, egg_id))
        con.execute("INSERT INTO egg_log (ts, egg_id) VALUES (?, ?)", (now, egg_id))
        con.execute("DELETE FROM egg_log WHERE ts < ?", (now - 86400,))  # keep 24h


def increment(key: str, by: int = 1) -> int:
    """Increment a named counter, return new value."""
    with _conn() as con:
        con.execute("""
            INSERT INTO counters (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = value + ?
        """, (key, by, by))
        return con.execute(
            "SELECT value FROM counters WHERE key=?", (key,)
        ).fetchone()["value"]


def get_counter(key: str) -> int:
    with _conn() as con:
        row = con.execute(
            "SELECT value FROM counters WHERE key=?", (key,)
        ).fetchone()
    return row["value"] if row else 0


def achievements() -> list[dict]:
    """Return all eggs that have ever fired, ordered by first_fired."""
    with _conn() as con:
        rows = con.execute("""
            SELECT id, label, first_fired, fire_count
            FROM eggs
            WHERE first_fired IS NOT NULL
            ORDER BY first_fired
        """).fetchall()
    return [dict(r) for r in rows]


def recent_log(n: int = 20) -> list[dict]:
    """Return the N most recent egg firings."""
    with _conn() as con:
        rows = con.execute("""
            SELECT l.ts, l.egg_id, e.label
            FROM egg_log l
            JOIN eggs e ON e.id = l.egg_id
            ORDER BY l.ts DESC
            LIMIT ?
        """, (n,)).fetchall()
    return [dict(r) for r in rows]
