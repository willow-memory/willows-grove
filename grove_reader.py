"""grove_reader.py — Direct Postgres reader for Grove and routing data.
b17: WDASH  ΔΣ=42
"""
import hashlib
from datetime import datetime, timezone

import grove_db

# ── Color hash palette (ANSI 16, maps to curses color pair numbers 11-17) ────
_HASH_PAIRS = [11, 12, 13, 14, 15, 16, 17]


def color_for_sender(name: str) -> int:
    """Return a stable curses color_pair number for this sender name."""
    return _HASH_PAIRS[int(hashlib.md5(name.encode()).hexdigest(), 16) % len(_HASH_PAIRS)]


def _conn_ctx(conn):
    """(conn, owned) — owned=True means caller must release to pool."""
    if conn is not None:
        return conn, False
    return grove_db.get_connection(), True


def _release(conn, owned: bool) -> None:
    if owned:
        grove_db.release_connection(conn)


def grove_agents(conn=None) -> list[dict]:
    """Return agents from HEARTBEAT bus messages, most recent first.
    Each entry: {sender: str, last_seen_at: datetime, age_secs: int}
    Falls back to all-sender inference if bus_type column is absent.
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT sender, MAX(created_at) AS last_seen
                FROM grove.messages
                WHERE bus_type = 'HEARTBEAT' AND is_deleted = 0
                GROUP BY sender
                ORDER BY last_seen DESC
                LIMIT 20
            """)
        except Exception:
            conn.rollback()
            cur.execute("""
                SELECT sender, MAX(created_at) AS last_seen
                FROM grove.messages
                WHERE is_deleted = 0
                GROUP BY sender
                ORDER BY last_seen DESC
                LIMIT 20
            """)
        now = datetime.now(timezone.utc)
        rows = []
        for sender, last_seen in cur.fetchall():
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            age_secs = int((now - last_seen).total_seconds())
            rows.append({"sender": sender, "last_seen_at": last_seen, "age_secs": age_secs})
        return rows
    except Exception:
        return []
    finally:
        _release(conn, owned)


def grove_channels(conn=None, last_seen_ids: dict | None = None) -> list[dict]:
    """Return channels with unread counts.
    last_seen_ids: {channel_name: last_seen_message_id}
    Each entry: {id: int, name: str, unread: int, agent_name: str|None}
    """
    conn, owned = _conn_ctx(conn)
    last_seen_ids = last_seen_ids or {}
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, name, agent_name FROM grove.channels "
                "WHERE is_archived = FALSE ORDER BY id"
            )
            channels = [(r[0], r[1], r[2]) for r in cur.fetchall()]
        except Exception:
            conn.rollback()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name FROM grove.channels "
                "WHERE is_archived = FALSE ORDER BY id"
            )
            channels = [(r[0], r[1], None) for r in cur.fetchall()]
        result = []
        for ch_id, name, agent_name in channels:
            last_id = last_seen_ids.get(name, 0)
            cur.execute(
                "SELECT COUNT(*) FILTER (WHERE id > %s), COALESCE(MAX(id), 0) "
                "FROM grove.messages WHERE channel_id = %s AND is_deleted = 0",
                (last_id, ch_id),
            )
            row = cur.fetchone()
            unread = row[0] if row else 0
            max_id = row[1] if row else 0
            result.append({"id": ch_id, "name": name, "unread": unread,
                           "max_id": max_id, "agent_name": agent_name})
        return result
    except Exception:
        return []
    finally:
        _release(conn, owned)


def grove_messages(channel_name: str, conn=None, limit: int = 50,
                   since_id: int = 0) -> list[dict]:
    """Return messages for a channel, oldest first.
    Each entry: {id: int, sender: str, content: str, created_at: datetime}
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM grove.channels WHERE name = %s LIMIT 1",
            (channel_name,),
        )
        row = cur.fetchone()
        if not row:
            return []
        ch_id = row[0]
        cur.execute(
            """
            SELECT id, sender, content, created_at
            FROM grove.messages
            WHERE channel_id = %s AND id > %s AND is_deleted = 0
            ORDER BY id DESC LIMIT %s
            """,
            (ch_id, since_id, limit),
        )
        msgs = []
        for mid, sender, content, created_at in cur.fetchall():
            msgs.append({"id": mid, "sender": sender,
                         "content": content, "created_at": created_at})
        return list(reversed(msgs))
    except Exception:
        return []
    finally:
        _release(conn, owned)


def grove_messages_all_agents(
    known_agents: "frozenset[str]",
    last_id: int = 0,
    limit: int = 20,
) -> "list[dict]":
    """Return recent grove.messages from known agent senders, id > last_id."""
    conn, owned = _conn_ctx(None)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, sender, content, created_at"
            " FROM grove.messages"
            " WHERE sender = ANY(%s::text[]) AND id > %s AND is_deleted = 0"
            " ORDER BY id DESC LIMIT %s",
            (list(known_agents), last_id, limit),
        )
        rows = cur.fetchall()
        return [
            {"id": r[0], "sender": r[1], "content": r[2], "created_at": r[3]}
            for r in reversed(rows)
        ]
    except Exception:
        return []
    finally:
        _release(conn, owned)


def grove_mentions(name: str, limit: int = 20, conn=None) -> list[dict]:
    """Return recent messages that @mention name across all channels (DB query, not scan).

    Each entry: {id, channel, sender, content}
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT m.id, c.name, m.sender, m.content
            FROM grove.messages m
            JOIN grove.channels c ON c.id = m.channel_id
            WHERE m.content ILIKE %s
              AND m.is_deleted = 0
              AND c.is_archived = FALSE
            ORDER BY m.id DESC
            LIMIT %s
            """,
            (f"%@{name}%", limit),
        )
        return [
            {"id": r[0], "channel": r[1], "sender": r[2], "content": r[3]}
            for r in cur.fetchall()
        ]
    except Exception:
        return []
    finally:
        _release(conn, owned)


_ROUTING_DDL = """
CREATE SCHEMA IF NOT EXISTS willow;
CREATE TABLE IF NOT EXISTS willow.routing_decisions (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT now(),
    session_id  TEXT,
    prompt_snippet TEXT,
    routed_to   TEXT,
    rule_matched TEXT,
    confidence  FLOAT,
    latency_ms  INTEGER
);
CREATE INDEX IF NOT EXISTS idx_routing_decisions_ts
    ON willow.routing_decisions (ts DESC);
"""


def routing_decisions(conn=None, limit: int = 8) -> list[dict]:
    """Return recent routing decisions. Auto-creates table on first call.
    Each entry: {ts, prompt_snippet, routed_to, rule_matched, confidence, latency_ms}
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT ts, prompt_snippet, routed_to, rule_matched, confidence, latency_ms
                FROM willow.routing_decisions
                ORDER BY ts DESC LIMIT %s
                """,
                (limit,),
            )
        except Exception:
            conn.rollback()
            cur.execute(_ROUTING_DDL)
            conn.commit()
            return []
        rows = []
        for ts, snippet, routed_to, rule_matched, confidence, latency_ms in cur.fetchall():
            rows.append({
                "ts": ts,
                "prompt_snippet": snippet,
                "routed_to": routed_to,
                "rule_matched": rule_matched,
                "confidence": float(confidence) if confidence is not None else 1.0,
                "latency_ms": latency_ms,
            })
        return rows
    except Exception:
        return []
    finally:
        _release(conn, owned)
