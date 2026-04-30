"""widgets/card_grid.py — CardCell, CardGrid, CardActivated for Textual.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os

from textual import work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


_STATE_COLORS: dict[str, str] = {
    "green":  "#3fb950",
    "amber":  "#d29922",
    "red":    "#f85149",
    "blue":   "#58a6ff",
    "yellow": "#d29922",
    "dim":    "#8b949e",
    "":       "#8b949e",
}

_CARD_NAV: dict[str, str] = {
    "kart":      "#pane-tasks",
    "knowledge": "knowledge",
    "yggdrasil": "providers",
    "agents":    "#pane-agents",
    "secrets":   "",
    "fleet":     "providers",
    "mcp":       "providers",
}

# (card_id, label) — order controls grid position
BUILTIN_CARDS: list[tuple[str, str]] = [
    ("kart",      "Kart Queue"),
    ("knowledge", "Knowledge"),
    ("yggdrasil", "Yggdrasil"),
    ("agents",    "Agents"),
    ("secrets",   "Secrets"),
    ("fleet",     "Fleet"),
    ("mcp",       "MCP Servers"),
]

# (card_id, label, nav_target)
LAUNCHER_CARDS: list[tuple[str, str, str]] = [
    ("tasks",   "Tasks",   "#pane-tasks"),
    ("agents",  "Agents",  "#pane-agents"),
    ("routing", "Routing", "#pane-routing"),
    ("skills",  "Skills",  "#pane-skills"),
    ("logs",    "Logs",    "#pane-logs"),
]


def fetch_runtime_card_values() -> dict[str, dict]:
    """Fetch live values for all 7 built-in cards. Never raises.

    Returns {card_id: {"value": str, "sub": str, "state": str}}.
    Defaults to {"value": "—", "sub": "", "state": ""} on any failure.
    """
    import json
    from pathlib import Path

    out: dict[str, dict] = {cid: {"value": "—", "sub": "", "state": ""} for cid, _ in BUILTIN_CARDS}

    # Kart Queue — pending/running counts from Kart task queue
    try:
        from panes.tasks import fetch_tasks
        t = fetch_tasks()
        pending = t.get("pending", 0)
        running = t.get("running", 0)
        state = "amber" if pending > 10 else "green" if pending > 0 else "dim"
        out["kart"] = {"value": str(pending), "sub": f"{running} running", "state": state}
    except Exception:
        pass

    # Knowledge — total atom count + today's additions
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.knowledge")
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM public.knowledge"
            " WHERE created_at > NOW() - INTERVAL '24 hours'"
        )
        today = cur.fetchone()[0]
        conn.close()
        out["knowledge"] = {"value": str(total), "sub": f"{today} today", "state": "blue"}
    except Exception:
        pass

    # Yggdrasil — active model from env
    try:
        model = os.environ.get("WILLOW_MODEL", "—")
        out["yggdrasil"] = {"value": model, "sub": "active model", "state": "dim"}
    except Exception:
        pass

    # Agents — live agent count from Grove
    try:
        import grove_reader
        agents = grove_reader.grove_agents()
        count = len(agents)
        if agents:
            freshest = min(agents, key=lambda a: a.get("age_secs", 9999))
            sub   = freshest["sender"]
            age   = freshest.get("age_secs", 9999)
            state = "green" if age < 120 else "yellow" if age < 900 else "dim"
        else:
            sub, state = "none", "dim"
        out["agents"] = {"value": str(count), "sub": sub, "state": state}
    except Exception:
        pass

    # Secrets — key count from ~/.willow/secrets.json
    try:
        secrets_path = Path.home() / ".willow" / "secrets.json"
        if secrets_path.exists():
            data = json.loads(secrets_path.read_text())
            count = len(data) if isinstance(data, dict) else 0
            out["secrets"] = {"value": str(count), "sub": "vault", "state": "dim"}
        else:
            out["secrets"] = {"value": "—", "sub": "vault", "state": "dim"}
    except Exception:
        pass

    # Fleet — count non-empty WILLOW_*_KEY env vars
    try:
        count = sum(
            1 for k, v in os.environ.items()
            if k.startswith("WILLOW_") and k.endswith("_KEY") and v
        )
        out["fleet"] = {"value": str(count), "sub": "providers", "state": "dim"}
    except Exception:
        pass

    # MCP — server count from ~/.mcp.json
    try:
        mcp_path = Path.home() / ".mcp.json"
        if not mcp_path.exists():
            mcp_path = Path(__file__).parent.parent / ".mcp.json"
        if mcp_path.exists():
            data = json.loads(mcp_path.read_text())
            count = len(data.get("mcpServers", {}))
            out["mcp"] = {"value": str(count), "sub": "connected", "state": "dim"}
    except Exception:
        pass

    return out
