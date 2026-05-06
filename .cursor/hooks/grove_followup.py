#!/usr/bin/env python3
"""
stop hook helper — enqueue new Grove inbox as followup_message for Cursor Auto.
b17: GVFLW  ΔΣ=42

Reads LAST_ID from .cursor/grove_followup_last_id; advances after each batch.
Bootstrap: missing file seeds to MAX(id) with no notification (prevents backlog flood).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE_REL = Path(".cursor") / "grove_followup_last_id"

# Which Grove identity owns #<lowercase> inbox + @mentions
AGENT = os.environ.get("GROVE_FOLLOWUP_AGENT", "Auto").strip() or "Auto"
MAX_CHARS = int(os.environ.get("GROVE_FOLLOWUP_MAX_CHARS", "11000"))
MAX_ROWS = int(os.environ.get("GROVE_FOLLOWUP_MAX_ROWS", "12"))
HOOK_LOOP_MAX = int(os.environ.get("GROVE_FOLLOWUP_HOOK_LOOP_GUARD", "22"))


def _emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj))
    sys.stdout.flush()


def _state_path() -> Path:
    return ROOT / STATE_REL


def _read_state() -> int | None:
    try:
        return int(_state_path().read_text().strip())
    except Exception:
        return None


def _write_state(n: int) -> None:
    try:
        p = _state_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(n) + "\n")
    except Exception:
        pass


def _seed_tail() -> int:
    sys.path.insert(0, str(ROOT))
    import grove_db as db  # noqa: WPS433 — hook bootstrap

    conn = db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(MAX(id), 0) FROM grove.messages WHERE is_deleted = 0")
        row = cur.fetchone()
        return int(row[0] or 0)
    finally:
        db.release_connection(conn)


def main() -> None:
    try:
        hook_in = json.load(sys.stdin)
    except Exception:
        hook_in = {}
    if int(hook_in.get("loop_count") or 0) > HOOK_LOOP_MAX:
        _emit({})
        return

    sys.path.insert(0, str(ROOT))
    import grove_reader as gr  # noqa: WPS433

    since_id = _read_state()
    if since_id is None:
        _write_state(_seed_tail())
        _emit({})
        return

    rows = gr.grove_inbox_bundle(AGENT, since_id=since_id, merge_limit=max(MAX_ROWS * 5, 40))
    fresh = [r for r in rows if int(r["id"]) > since_id]
    if not fresh:
        _emit({})
        return

    fresh.sort(key=lambda r: int(r["id"]))
    fresh = fresh[:MAX_ROWS]
    hi = max(int(r["id"]) for r in fresh)

    lines = [
        "[Grove → " + AGENT + "] New message(s) since your last Cursor turn "
        "(# + @mentions + bus to_agent). Use grove_get_thread(id) for full body.",
    ]
    for r in fresh:
        ch = r.get("channel", "?")
        body = str(r.get("content", "")).replace("\n", " ").strip()
        snip = body[:80] + ("…" if len(body) > 80 else "")
        lines.append(f"- #{ch} id={r['id']} | {r.get('sender', '?')}: {snip}")

    msg = "\n".join(lines)
    if len(msg) > MAX_CHARS:
        msg = msg[: MAX_CHARS - 20] + "\n… (truncated)"

    _write_state(hi)
    _emit({"followup_message": msg})


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[grove_followup] FATAL: {e.__class__.__name__}: {e}", file=sys.stderr)
        sys.stderr.flush()
        _emit({})
