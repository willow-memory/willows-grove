"""grove_reader.py — Direct Postgres reader for Grove and routing data.

Every reader in this module honors the three-state contract
(``docs/INVARIANTS.md §1``): it returns a value with a bounded shape
(populated or empty) OR raises ``grove.errors.Unreachable`` when its
source cannot be reached. A bare ``[]`` / ``{}`` / ``None`` never means
"unreachable" here.

Writer helpers in this file (``grove_get_or_create_dm``,
``grove_create_text_channel``, ``grove_archive_channel``,
``grove_set_channel_agent``, ``grove_set_channel_description``,
``grove_rename_channel``, ``grove_message_delete``,
``grove_message_toggle_flag``, ``grove_mark_channel_read``) return
``{"ok": bool, "error": str}`` — they are not readers under §1 and are
unchanged.

b17: WDASH  ΔΣ=42
"""
import hashlib
import json
import logging
import os
from datetime import datetime, timezone

import grove_db
from grove.errors import Unreachable

_log = logging.getLogger("grove_reader")

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


def _redact_db_error(exc: BaseException) -> str:
    """Return a caller-safe generic message for a DB exception.

    Loki v0.9 audit finding M17 (cross-cutting hazard): the writer helpers
    in this module previously returned ``str(exc)`` on failure. For
    psycopg2 errors that string embeds internal state — schema names,
    constraint names, DETAIL row values — which landed in the UI verbatim.

    This helper maps the exception TYPE (not the message) to a short,
    generic string. The full exception is still preserved via the caller's
    ``_log.warning`` line so operators can debug from server logs; only
    the caller-facing dict is redacted.
    """
    try:
        import psycopg2
        from psycopg2 import errors as _pg_errors
        integrity = (
            _pg_errors.UniqueViolation,
            _pg_errors.ForeignKeyViolation,
            _pg_errors.NotNullViolation,
            _pg_errors.CheckViolation,
            psycopg2.IntegrityError,
        )
        if isinstance(exc, integrity):
            return "constraint violation"
        if isinstance(exc, psycopg2.OperationalError):
            return "database unreachable"
        if isinstance(exc, psycopg2.Error):
            return "database error"
    except Exception:  # pragma: no cover — psycopg2 unavailable
        pass
    return "database error"


def dashboard_grove_sender() -> str:
    """Sender name for dashboard chat + DeskPane (fleet identity).

    Explicit GROVE_SENDER wins, then GROVE_NAME.
    Otherwise 'Auto' (Cursor/dashboard router row in public.agents).
    """
    for key in ("GROVE_SENDER", "GROVE_NAME"):
        v = (os.environ.get(key) or "").strip()
        if v:
            return v
    return "Auto"


def desk_mention_handles(primary_sender: str | None = None) -> list[str]:
    """Handles for ATTENTION (@-substring match via ILIKE), deduped case-insensitively.

    primary_sender overrides dashboard identity (e.g. MCP inbox with agent='Auto').

    Includes the primary sender plus 'all' so @all broadcasts surface on the desk.
    Optional GROVE_DESK_MENTIONS=comma,separated extras (handles without leading @).
    """
    handles: list[str] = []
    seen: set[str] = set()

    def _add(raw: str) -> None:
        h = raw.strip().lstrip("@")
        if not h:
            return
        k = h.lower()
        if k in seen:
            return
        seen.add(k)
        handles.append(h)

    base = (
        primary_sender.strip()
        if (primary_sender and primary_sender.strip())
        else dashboard_grove_sender()
    )
    _add(base)
    _add("all")
    extras = (os.environ.get("GROVE_DESK_MENTIONS") or "").strip()
    for part in extras.split(","):
        _add(part)
    return handles


def merge_attention_messages(*row_groups: list[dict], limit: int = 20) -> list[dict]:
    """Dedupe-by-id descending merge for desk ATTENTION / inbox."""
    seen: set[int] = set()
    out: list[dict] = []
    merged: list[dict] = []
    for grp in row_groups:
        merged.extend(grp or [])
    for row in sorted(merged, key=lambda r: -int(r["id"])):
        mid = int(row["id"])
        if mid in seen:
            continue
        seen.add(mid)
        out.append(row)
        if len(out) >= limit:
            break
    return out


def grove_messages_bus_addressed_to(
    recipient: str,
    *,
    since_id: int = 0,
    limit: int = 40,
    conn=None,
) -> list[dict]:
    """Messages bus-routed *directly* to recipient (to_agent matches, case-insensitive).

    Rows where content lacks @mentions but agents used MCP bus addressing.
    Drops HEARTBEAT/ACK noise. Does NOT include '__all__' broadcasts (use mentions + history).

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    r = recipient.strip()
    if not r:
        return []
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT m.id, c.name, m.sender, m.content
            FROM grove.messages m
            JOIN grove.channels c ON c.id = m.channel_id
            WHERE m.is_deleted = 0
              AND c.is_archived = FALSE
              AND m.id > %s
              AND LOWER(TRIM(COALESCE(m.to_agent, ''))) = LOWER(TRIM(%s))
              AND LOWER(TRIM(COALESCE(m.to_agent, ''))) <> '__all__'
              AND COALESCE(m.bus_type, '') NOT IN ('HEARTBEAT', 'ACK')
            ORDER BY m.id DESC
            LIMIT %s
            """,
            (since_id, r, limit),
        )
        return [
            {"id": r0[0], "channel": r0[1], "sender": r0[2], "content": r0[3]}
            for r0 in cur.fetchall()
        ]
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_messages_bus_addressed_to: %s", e)
        raise Unreachable(f"grove_reader.grove_messages_bus_addressed_to: {e}") from e
    finally:
        _release(conn, owned)


def grove_own_channel_since(
    channel_name: str,
    *,
    since_id: int = 0,
    limit: int = 80,
    conn=None,
) -> list[dict]:
    """Rule 1 (persistent monitor): every message in the agent-dedicated channel.

    Channel name convention: lowercased sender identity (e.g. Auto → #auto).
    Skips HEARTBEAT bus noise — text posts only.

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    ch = (channel_name or "").strip()
    if not ch:
        return []
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT m.id, c.name, m.sender, m.content
              FROM grove.messages m
              JOIN grove.channels c ON c.id = m.channel_id
             WHERE LOWER(TRIM(c.name)) = LOWER(TRIM(%s))
               AND m.is_deleted = 0
               AND c.is_archived = FALSE
               AND m.id > %s
               AND COALESCE(m.bus_type, '') NOT IN ('HEARTBEAT', 'ACK')
             ORDER BY m.id DESC
             LIMIT %s
            """,
            (ch, since_id, limit),
        )
        return [
            {"id": r[0], "channel": r[1], "sender": r[2], "content": r[3]}
            for r in cur.fetchall()
        ]
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_own_channel_since: %s", e)
        raise Unreachable(f"grove_reader.grove_own_channel_since: {e}") from e
    finally:
        _release(conn, owned)


def grove_inbox_bundle(
    agent: str | None = None,
    *,
    since_id: int = 0,
    mention_limit: int = 60,
    bus_limit: int = 60,
    merge_limit: int = 35,
    conn=None,
) -> list[dict]:
    """Unified pull: @mentions + bus to_agent + dedicated #<agent> inbox (rule 1).

    Acquires a single pooled connection for all three sub-queries when conn=None,
    avoiding three separate checkout/release round-trips per call.

    §1: any child reader raising ``Unreachable`` propagates cleanly.
    """
    who = agent.strip() if (agent and agent.strip()) else dashboard_grove_sender()
    handles = desk_mention_handles(who)
    inbox_name = who.strip().lower().replace(" ", "-")
    _conn, owned = _conn_ctx(conn)
    try:
        mention_rows = grove_mentions_for_handles(handles, limit=mention_limit, conn=_conn)
        bus_rows = grove_messages_bus_addressed_to(who, since_id=since_id, limit=bus_limit, conn=_conn)
        own_rows = grove_own_channel_since(inbox_name, since_id=since_id, limit=mention_limit, conn=_conn)
    finally:
        _release(_conn, owned)
    filtered_mentions = [m for m in mention_rows if int(m["id"]) > since_id]
    return merge_attention_messages(
        filtered_mentions, bus_rows, own_rows, limit=merge_limit,
    )


def grove_member_roster(limit: int = 30, conn=None) -> list[dict]:
    """Discord member pane: merge heartbeat presence with recent message senders.

    §1: raises ``Unreachable`` when Postgres cannot be reached (never returns
    a partial merged snapshot on failure).
    """
    conn, owned = _conn_ctx(conn)
    now = datetime.now(timezone.utc)
    merged: dict[str, dict] = {}
    try:
        for agent in grove_agents(conn=conn):
            merged[agent["sender"]] = agent
        cur = conn.cursor()
        cur.execute(
            """
            SELECT sender, MAX(created_at) AS last_seen
            FROM grove.messages
            WHERE is_deleted = 0
              AND COALESCE(bus_type, 'EVENT') NOT IN ('HEARTBEAT')
            GROUP BY sender
            ORDER BY MAX(created_at) DESC
            LIMIT %s
            """,
            (limit,),
        )
        for sender, last_seen in cur.fetchall():
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            age_secs = int((now - last_seen).total_seconds())
            row = {"sender": sender, "last_seen_at": last_seen, "age_secs": age_secs}
            prev = merged.get(sender)
            if prev is None or age_secs < prev["age_secs"]:
                merged[sender] = row
        return sorted(merged.values(), key=lambda r: r["age_secs"])
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_member_roster: %s", e)
        raise Unreachable(f"grove_reader.grove_member_roster: {e}") from e
    finally:
        _release(conn, owned)


def grove_agents(conn=None) -> list[dict]:
    """Return agents from HEARTBEAT bus messages, most recent first.
    Each entry: {sender: str, last_seen_at: datetime, age_secs: int}
    Falls back to all-sender inference if bus_type column is absent.

    §1: raises ``Unreachable`` when Postgres cannot be reached.
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
        except Exception as e:
            _log.debug("grove_reader.grove_agents: bus_type column absent, falling back: %s", e)
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
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_agents: %s", e)
        raise Unreachable(f"grove_reader.grove_agents: {e}") from e
    finally:
        _release(conn, owned)


def _ui_state(age_secs: int | None, hb_content: str | None) -> str:
    if hb_content and hb_content.lstrip().startswith("[AGENT_VIEW] status=blocked"):
        return "blocked"
    if age_secs is None:
        return "unknown"
    if age_secs < 120:
        return "running"
    if age_secs < 900:
        return "idle"
    return "stale"


def grove_latest_message_for_sender(
    sender: str,
    exclude_bus_types: tuple = ("HEARTBEAT",),
    conn=None,
) -> dict | None:
    """Return the latest non-HEARTBEAT message for sender, or None.

    §1: ``None`` is the empty state (no such row); ``Unreachable`` is raised
    when Postgres cannot be reached.
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        placeholders = ",".join(["%s"] * len(exclude_bus_types))
        cur.execute(
            f"""
            SELECT id, content, correlation_id, reply_to_id
            FROM grove.messages
            WHERE sender = %s
              AND bus_type NOT IN ({placeholders})
              AND is_deleted = 0
            ORDER BY id DESC LIMIT 1
            """,
            (sender, *exclude_bus_types),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "content": row[1],
            "correlation_id": row[2],
            "reply_to_id": row[3],
        }
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_latest_message_for_sender: %s", e)
        raise Unreachable(f"grove_reader.grove_latest_message_for_sender: {e}") from e
    finally:
        _release(conn, owned)


def grove_agent_fleet_rows(limit: int = 50, conn=None) -> list[dict]:
    """Return fleet rows for the AgentsPane.

    Each row: sender, last_seen_at, age_secs, ui_state, peek,
              blocked, reply_to_message_id, correlation_id.
    Two round-trips max per §7 (Phase 0).

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()

        # Round 1: latest HEARTBEAT per sender + structured heartbeat content
        cur.execute(
            """
            SELECT m.sender, m.created_at, m.content
            FROM grove.messages m
            JOIN (
                SELECT sender, MAX(id) AS hb_id
                FROM grove.messages
                WHERE bus_type = 'HEARTBEAT' AND is_deleted = 0
                GROUP BY sender
            ) latest ON m.id = latest.hb_id
            ORDER BY m.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        hb_rows = cur.fetchall()

        now = datetime.now(timezone.utc)
        senders = [r[0] for r in hb_rows]

        # Round 2: latest non-HEARTBEAT + needs-reply flag per sender (batch)
        peek_by_sender: dict = {}
        if senders:
            cur.execute(
                """
                SELECT DISTINCT ON (m.sender)
                    m.sender, m.id, m.content, m.correlation_id,
                    (mf.message_id IS NOT NULL) AS needs_reply
                FROM grove.messages m
                LEFT JOIN grove.message_flags mf
                       ON mf.message_id = m.id AND mf.flag = 'needs-reply'
                WHERE m.sender = ANY(%s)
                  AND m.bus_type != 'HEARTBEAT'
                  AND m.is_deleted = 0
                ORDER BY m.sender, m.id DESC
                """,
                (senders,),
            )
            for row in cur.fetchall():
                peek_by_sender[row[0]] = {
                    "peek_id": row[1],
                    "peek": (row[2] or "")[:200],
                    "correlation_id": row[3],
                    "needs_reply": bool(row[4]),
                }

        rows = []
        for sender, last_seen, hb_content in hb_rows:
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            age_secs = int((now - last_seen).total_seconds())
            peek_data = peek_by_sender.get(sender, {})
            needs_reply = peek_data.get("needs_reply", False)
            state = _ui_state(age_secs, hb_content)
            if needs_reply and state != "blocked":
                state = "blocked"
            rows.append({
                "sender": sender,
                "last_seen_at": last_seen,
                "age_secs": age_secs,
                "ui_state": state,
                "peek": peek_data.get("peek", ""),
                "blocked": needs_reply or state == "blocked",
                "reply_to_message_id": peek_data.get("peek_id") if needs_reply else None,
                "correlation_id": peek_data.get("correlation_id"),
            })
        return rows
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_agent_fleet_rows: %s", e)
        raise Unreachable(f"grove_reader.grove_agent_fleet_rows: {e}") from e
    finally:
        _release(conn, owned)


def coordinator_heartbeat(conn=None) -> dict | None:
    """Return parsed HEARTBEAT content from willow-coordinator, or None.

    §1: ``None`` is the empty state (no heartbeat row); ``Unreachable`` is
    raised when Postgres cannot be reached.
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT content FROM grove.messages
            WHERE sender = 'willow' AND bus_type = 'HEARTBEAT'
              AND is_deleted = 0
            ORDER BY created_at DESC LIMIT 1
        """)
        row = cur.fetchone()
        return json.loads(row[0]) if row else None
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.coordinator_heartbeat: %s", e)
        raise Unreachable(f"grove_reader.coordinator_heartbeat: {e}") from e
    finally:
        _release(conn, owned)


def grove_get_or_create_dm(peer: str, conn=None) -> dict:
    """Get or create a direct-message channel (name: dm:{peer})."""
    peer = peer.strip().lstrip("@").lower()
    name = f"dm:{peer}"
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO grove.channels (name, channel_type, description)
            VALUES (%s, 'direct', %s)
            ON CONFLICT (name) DO NOTHING
            """,
            (name, f"Direct message with {peer}"),
        )
        if owned:
            conn.commit()
        cur.execute(
            """
            SELECT id, name, channel_type, agent_name
            FROM grove.channels WHERE name = %s AND is_archived = FALSE
            """,
            (name,),
        )
        row = cur.fetchone()
        if not row:
            return {"id": 0, "name": name, "channel_type": "direct", "agent_name": None}
        return {
            "id": row[0],
            "name": row[1],
            "channel_type": row[2],
            "agent_name": row[3],
            "unread": 0,
            "max_id": 0,
        }
    except Exception as e:
        _log.warning("grove_reader.grove_get_or_create_dm: %s", e)
        return {"id": 0, "name": name, "channel_type": "direct", "agent_name": None}
    finally:
        _release(conn, owned)


def grove_create_text_channel(raw_name: str, description: str = "") -> dict:
    """Create a group text channel. Returns {ok, channel?, error?}."""
    from panes.chat_admin import normalize_channel_name

    name = normalize_channel_name(raw_name)
    if not name:
        return {"ok": False, "error": "invalid or reserved channel name"}
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, is_archived FROM grove.channels WHERE name = %s",
            (name,),
        )
        row = cur.fetchone()
        if row and not row[1]:
            return {"ok": False, "error": "channel already exists"}
        if row and row[1]:
            cur.execute(
                """
                UPDATE grove.channels
                SET is_archived = FALSE,
                    channel_type = 'group',
                    description = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, name, channel_type, agent_name
                """,
                (description or f"#{name}", row[0]),
            )
            unarchived = cur.fetchone()
            conn.commit()
            return {
                "ok": True,
                "channel": {
                    "id": unarchived[0],
                    "name": unarchived[1],
                    "channel_type": unarchived[2],
                    "agent_name": unarchived[3],
                    "unread": 0,
                    "max_id": 0,
                },
            }
        ch = grove_db.create_channel(
            conn,
            name=name,
            channel_type="group",
            description=description or f"#{name}",
        )
        return {
            "ok": True,
            "channel": {
                "id": ch["id"],
                "name": ch["name"],
                "channel_type": ch["channel_type"],
                "agent_name": ch.get("agent_name"),
                "unread": 0,
                "max_id": 0,
            },
        }
    except Exception as e:
        _log.warning("grove_reader.grove_create_text_channel: %s", e)
        return {"ok": False, "error": _redact_db_error(e)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def grove_archive_channel(name: str) -> dict:
    """Soft-delete (archive) a channel. Returns {ok, name?, error?}."""
    from panes.chat_admin import can_archive_channel

    name = name.strip()
    if not can_archive_channel(name):
        return {"ok": False, "error": "cannot archive this channel"}
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM grove.channels WHERE name = %s AND is_archived = FALSE",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "channel not found"}
        if not grove_db.archive_channel(conn, row[0]):
            return {"ok": False, "error": "archive failed"}
        return {"ok": True, "name": name}
    except Exception as e:
        _log.warning("grove_reader.grove_archive_channel: %s", e)
        return {"ok": False, "error": _redact_db_error(e)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def _migrate_soil_channel_cursors(old_name: str, new_name: str) -> None:
    """Move SOIL cursor records when a channel is renamed."""
    try:
        import soil

        per = soil.get("willow-dashboard/cursors", old_name)
        if per:
            soil.put("willow-dashboard/cursors", new_name, per)
        bundle = soil.get("willow-dashboard/channel_cursors", "cursors") or {}
        if isinstance(bundle, dict) and old_name in bundle:
            bundle = dict(bundle)
            bundle[new_name] = bundle.pop(old_name)
            soil.put("willow-dashboard/channel_cursors", "cursors", bundle)
    except Exception as e:
        _log.warning("grove_reader._migrate_soil_channel_cursors: %s", e)


def grove_set_channel_agent(channel_name: str, agent: str | None) -> dict:
    """Bind or clear agent_name on a channel. Returns {ok, agent?, error?}."""
    if channel_name.startswith("dm:"):
        return {"ok": False, "error": "cannot bind agent on DM channels"}
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        if agent:
            agent = agent.strip().lstrip("@").lower()
            channel_type = "persona"
        else:
            agent = None
            channel_type = "group"
        cur.execute(
            """
            UPDATE grove.channels
            SET agent_name = %s,
                channel_type = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE name = %s AND is_archived = FALSE
            RETURNING name
            """,
            (agent, channel_type, channel_name),
        )
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "channel not found"}
        conn.commit()
        return {"ok": True, "agent": agent, "name": row[0]}
    except Exception as e:
        _log.warning("grove_reader.grove_set_channel_agent: %s", e)
        return {"ok": False, "error": _redact_db_error(e)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def grove_set_channel_description(channel_name: str, description: str) -> dict:
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE grove.channels
            SET description = %s, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s AND is_archived = FALSE
            RETURNING name
            """,
            (description.strip(), channel_name),
        )
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "channel not found"}
        conn.commit()
        return {"ok": True, "name": row[0]}
    except Exception as e:
        _log.warning("grove_reader.grove_set_channel_description: %s", e)
        return {"ok": False, "error": _redact_db_error(e)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def grove_rename_channel(old_name: str, raw_new_name: str) -> dict:
    """Rename a channel and migrate SOIL cursors. Returns {ok, name?, error?}."""
    from panes.chat_admin import PROTECTED_CHANNELS, normalize_channel_name

    if old_name.startswith("dm:"):
        return {"ok": False, "error": "cannot rename DM channels"}
    if old_name in PROTECTED_CHANNELS:
        return {"ok": False, "error": "cannot rename protected channel"}
    new_name = normalize_channel_name(raw_new_name)
    if not new_name:
        return {"ok": False, "error": "invalid new channel name"}
    if new_name == old_name:
        return {"ok": True, "name": old_name}
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM grove.channels WHERE name = %s AND is_archived = FALSE",
            (new_name,),
        )
        if cur.fetchone():
            return {"ok": False, "error": "target name already exists"}
        cur.execute(
            """
            UPDATE grove.channels
            SET name = %s, updated_at = CURRENT_TIMESTAMP
            WHERE name = %s AND is_archived = FALSE
            RETURNING id
            """,
            (new_name, old_name),
        )
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "channel not found"}
        conn.commit()
        _migrate_soil_channel_cursors(old_name, new_name)
        return {"ok": True, "name": new_name}
    except Exception as e:
        _log.warning("grove_reader.grove_rename_channel: %s", e)
        return {"ok": False, "error": _redact_db_error(e)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def grove_list_archived_channels(conn=None) -> list[dict]:
    """Return archived channels for the archive picker.

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    conn, owned = _conn_ctx(conn)
    try:
        rows = grove_db.list_channels(conn, include_archived=True)
        return [
            {"id": r["id"], "name": r["name"], "channel_type": r.get("channel_type", "group")}
            for r in rows
            if r.get("is_archived")
        ]
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_list_archived_channels: %s", e)
        raise Unreachable(f"grove_reader.grove_list_archived_channels: {e}") from e
    finally:
        _release(conn, owned)


def grove_unarchive_channel(raw_name: str) -> dict:
    """Restore an archived channel (alias for create unarchive path)."""
    return grove_create_text_channel(raw_name)


def grove_channels(conn=None, last_seen_ids: dict | None = None) -> list[dict]:
    """Return channels with unread counts.
    last_seen_ids: {channel_name: last_seen_message_id}
    Each entry: {id, name, channel_type, unread, max_id, agent_name}

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    conn, owned = _conn_ctx(conn)
    last_seen_ids = last_seen_ids or {}
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, name, channel_type, agent_name FROM grove.channels "
                "WHERE is_archived = FALSE ORDER BY id"
            )
            channels = [(r[0], r[1], r[2], r[3]) for r in cur.fetchall()]
        except Exception as e:
            _log.debug("grove_reader.grove_channels: extended columns absent, falling back: %s", e)
            conn.rollback()
            cur = conn.cursor()
            cur.execute(
                "SELECT id, name FROM grove.channels "
                "WHERE is_archived = FALSE ORDER BY id"
            )
            channels = [(r[0], r[1], "group", None) for r in cur.fetchall()]
        result = []
        for ch_id, name, channel_type, agent_name in channels:
            last_id = last_seen_ids.get(name, 0)
            cur.execute(
                "SELECT COUNT(*) FILTER (WHERE id > %s), COALESCE(MAX(id), 0) "
                "FROM grove.messages WHERE channel_id = %s AND is_deleted = 0",
                (last_id, ch_id),
            )
            row = cur.fetchone()
            unread = row[0] if row else 0
            max_id = row[1] if row else 0
            result.append({
                "id": ch_id,
                "name": name,
                "channel_type": channel_type,
                "unread": unread,
                "max_id": max_id,
                "agent_name": agent_name,
            })
        return result
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_channels: %s", e)
        raise Unreachable(f"grove_reader.grove_channels: {e}") from e
    finally:
        _release(conn, owned)


def _attach_message_flags(conn, msgs: list[dict]) -> None:
    ids = [m["id"] for m in msgs if m.get("id")]
    if not ids:
        return
    cur = conn.cursor()
    cur.execute(
        "SELECT message_id, flag FROM grove.message_flags WHERE message_id = ANY(%s)",
        (ids,),
    )
    by_id: dict[int, set[str]] = {}
    for mid, flag in cur.fetchall():
        by_id.setdefault(int(mid), set()).add(flag)
    for m in msgs:
        m["flags"] = by_id.get(m.get("id"), set())


def grove_messages(channel_name: str, conn=None, limit: int = 50,
                   since_id: int = 0) -> list[dict]:
    """Return messages for a channel, oldest first (with flags attached).

    §1: raises ``Unreachable`` when Postgres cannot be reached. An empty
    list is still the legitimate empty state (channel missing, or no rows
    past ``since_id``).
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
            msgs.append({
                "id": mid,
                "sender": sender,
                "content": content,
                "created_at": created_at,
                "flags": set(),
            })
        msgs = list(reversed(msgs))
        _attach_message_flags(conn, msgs)
        return msgs
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_messages: %s", e)
        raise Unreachable(f"grove_reader.grove_messages: {e}") from e
    finally:
        _release(conn, owned)


def grove_message_delete(message_id: int) -> dict:
    if not message_id:
        return {"ok": False, "error": "no message id"}
    conn = None
    try:
        conn = grove_db.get_connection()
        if not grove_db.delete_message(conn, message_id):
            return {"ok": False, "error": "not found"}
        return {"ok": True, "id": message_id}
    except Exception as e:
        _log.warning("grove_reader.grove_message_delete: %s", e)
        return {"ok": False, "error": _redact_db_error(e)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def grove_message_toggle_flag(message_id: int, flag: str) -> dict:
    if flag not in {"needs-reply", "starred", "read", "urgent", "resolved"}:
        return {"ok": False, "error": "invalid flag"}
    who = dashboard_grove_sender()
    conn = None
    try:
        conn = grove_db.get_connection()
        existing = grove_db.get_flags(conn, message_id)
        if any(f["flag"] == flag for f in existing):
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM grove.message_flags WHERE message_id = %s AND flag = %s",
                (message_id, flag),
            )
            conn.commit()
            return {"ok": True, "on": False, "flag": flag}
        grove_db.set_flag(conn, message_id=message_id, sender=who, flag=flag)
        return {"ok": True, "on": True, "flag": flag}
    except Exception as e:
        _log.warning("grove_reader.grove_message_toggle_flag: %s", e)
        return {"ok": False, "error": _redact_db_error(e)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def grove_attention_flagged(limit: int = 8, conn=None) -> list[dict]:
    """Urgent + needs-reply rows for desk ATTENTION.

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT c.name, m.sender, m.content, f.flag, m.id
            FROM grove.message_flags f
            JOIN grove.messages m ON m.id = f.message_id
            JOIN grove.channels c ON c.id = m.channel_id
            WHERE f.flag IN ('urgent', 'needs-reply')
              AND m.is_deleted = 0
              AND c.is_archived = FALSE
            ORDER BY m.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        return [
            {
                "channel": r[0],
                "sender": r[1],
                "content": (r[2] or "")[:80],
                "flag": r[3],
                "id": r[4],
            }
            for r in cur.fetchall()
        ]
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_attention_flagged: %s", e)
        raise Unreachable(f"grove_reader.grove_attention_flagged: {e}") from e
    finally:
        _release(conn, owned)


def grove_mark_channel_read(channel_name: str, last_id: int | None = None) -> dict:
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM grove.channels WHERE name = %s AND is_archived = FALSE",
            (channel_name,),
        )
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "channel not found"}
        ch_id = row[0]
        if last_id is None:
            cur.execute(
                "SELECT COALESCE(MAX(id), 0) FROM grove.messages WHERE channel_id = %s",
                (ch_id,),
            )
            last_id = cur.fetchone()[0] or 0
        return {"ok": True, "channel": channel_name, "last_id": last_id}
    except Exception as e:
        _log.warning("grove_reader.grove_mark_channel_read: %s", e)
        return {"ok": False, "error": _redact_db_error(e)}
    finally:
        if conn is not None:
            grove_db.release_connection(conn)


def grove_messages_all_agents(
    known_agents: "frozenset[str]",
    last_id: int = 0,
    limit: int = 20,
) -> "list[dict]":
    """Return recent grove.messages from known agent senders, id > last_id.

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
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
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_messages_all_agents: %s", e)
        raise Unreachable(f"grove_reader.grove_messages_all_agents: {e}") from e
    finally:
        _release(conn, owned)


_mention_index_ensured = False

_MENTION_INDEX_DDL = """
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_messages_content_trgm
    ON grove.messages USING GIN (content gin_trgm_ops);
"""


def _ensure_mention_index(cur) -> None:
    """Create pg_trgm extension + GIN index on first call. No-op if already present."""
    global _mention_index_ensured
    if _mention_index_ensured:
        return
    try:
        for stmt in _MENTION_INDEX_DDL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                cur.execute(stmt)
        _mention_index_ensured = True
    except Exception as e:
        _log.warning("grove_reader._ensure_mention_index: %s", e)


def grove_mentions_for_handles(handles: list[str], limit: int = 20, conn=None) -> list[dict]:
    """Recent messages matching @<handle> for any handle (ILIKE substring, case-folded).

    Each entry: {id, channel, sender, content}

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    clean: list[str] = []
    seen: set[str] = set()
    for raw in handles:
        h = (raw or "").strip().lstrip("@")
        if not h:
            continue
        k = h.lower()
        if k in seen:
            continue
        seen.add(k)
        clean.append(h)
    if not clean:
        return []
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        _ensure_mention_index(cur)
        placeholders = " OR ".join(["m.content ILIKE %s"] * len(clean))
        params = [f"%@{h}%" for h in clean]
        params.append(limit)
        cur.execute(
            f"""
            SELECT m.id, c.name, m.sender, m.content
            FROM grove.messages m
            JOIN grove.channels c ON c.id = m.channel_id
            WHERE ({placeholders})
              AND m.is_deleted = 0
              AND c.is_archived = FALSE
            ORDER BY m.id DESC
            LIMIT %s
            """,
            params,
        )
        return [
            {"id": r[0], "channel": r[1], "sender": r[2], "content": r[3]}
            for r in cur.fetchall()
        ]
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.grove_mentions_for_handles: %s", e)
        raise Unreachable(f"grove_reader.grove_mentions_for_handles: {e}") from e
    finally:
        _release(conn, owned)


def grove_mentions(name: str, limit: int = 20, conn=None) -> list[dict]:
    """Single-handle wrapper over grove_mentions_for_handles."""
    return grove_mentions_for_handles([name], limit=limit, conn=conn)


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


_MIN_TS = datetime.min.replace(tzinfo=timezone.utc)


def routing_decisions(conn=None, limit: int = 8) -> list[dict]:
    """Return recent routing decisions, merged from willow + public tables by time.

    Reads `willow.routing_decisions` (oracle-shaped rows, auto-created on first call)
    and `public.routing_decisions` (MCP JSONB decisions), merged newest-first. See
    ``docs/verify/ROUTING_OBSERVABILITY.md``.

    Each entry: {ts, prompt_snippet, routed_to, rule_matched, confidence, latency_ms}

    §1: an ``Unreachable`` raised by either underlying helper propagates.
    """
    willow_rows = _routing_decisions_willow(conn, limit=limit * 2)
    public_rows = _routing_decisions_public(conn, limit=limit * 2)
    merged = willow_rows + public_rows
    merged.sort(key=lambda r: r.get("ts") or _MIN_TS, reverse=True)
    return merged[:limit]


def _routing_decisions_willow(conn=None, limit: int = 8) -> list[dict]:
    """Oracle-shaped rows from willow.routing_decisions. Auto-creates table on first call.

    §1: raises ``Unreachable`` when Postgres cannot be reached.
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
        except Exception as e:
            _log.debug("grove_reader.routing_decisions: table absent, auto-creating: %s", e)
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
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.routing_decisions (willow): %s", e)
        raise Unreachable(f"grove_reader.routing_decisions (willow): {e}") from e
    finally:
        _release(conn, owned)


def _routing_decisions_public(conn=None, limit: int = 8) -> list[dict]:
    """MCP JSONB rows from public.routing_decisions.

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT created_at, prompt_hash, decision
            FROM public.routing_decisions
            ORDER BY created_at DESC LIMIT %s
            """,
            (limit,),
        )
        rows = []
        for created_at, prompt_hash, decision in cur.fetchall():
            dec = decision
            if isinstance(dec, str):
                try:
                    dec = json.loads(dec)
                except json.JSONDecodeError:
                    dec = {}
            if not isinstance(dec, dict):
                dec = {}
            snippet = (dec.get("prompt_snippet") or "").strip()
            if not snippet and prompt_hash:
                snippet = f"[hash:{str(prompt_hash)[:12]}]"
            rows.append({
                "ts": created_at,
                "prompt_snippet": snippet,
                "routed_to": dec.get("routed_to") or "?",
                "rule_matched": dec.get("rule_matched") or "—",
                "confidence": float(dec.get("confidence") or 0.0),
                "latency_ms": dec.get("latency_ms"),
            })
        return rows
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.routing_decisions (public): %s", e)
        raise Unreachable(f"grove_reader.routing_decisions (public): {e}") from e
    finally:
        _release(conn, owned)


def human_required_queue(conn=None, limit: int = 30, open_only: bool = True) -> list[dict]:
    """Items from public.human_required_queue — work that pauses automation until a
    human acts (consent, attestation, review, onboarding). Priority-first, newest-first.

    Each entry: {id, kind, title, summary, status, priority, source_agent,
                 source_ref, assignee, created_at}

    §1: raises ``Unreachable`` when Postgres cannot be reached.
    """
    conn, owned = _conn_ctx(conn)
    try:
        cur = conn.cursor()
        where = "WHERE status = 'open'" if open_only else ""
        cur.execute(
            f"""
            SELECT id, kind, title, summary, status, priority,
                   source_agent, source_ref, assignee, created_at
            FROM public.human_required_queue
            {where}
            ORDER BY
                CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1
                              WHEN 'normal' THEN 2 WHEN 'low' THEN 3 ELSE 4 END,
                created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
    except Unreachable:
        raise
    except Exception as e:
        _log.warning("grove_reader.human_required_queue: %s", e)
        raise Unreachable(f"grove_reader.human_required_queue: {e}") from e
    finally:
        _release(conn, owned)
