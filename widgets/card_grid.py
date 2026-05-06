"""widgets/card_grid.py — CardCell, CardGrid, CardActivated for Textual.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os

import grove_db
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
    "kart":       "#pane-tasks",
    "knowledge":  "knowledge",
    "yggdrasil":  "providers",
    "agents":     "#pane-agents",
    "secrets":    "#pane-secrets",
    "fleet":      "#pane-agents",
    "mcp":        "#pane-mcp",
    "git-status": "#pane-git",
    "open-prs":   "#pane-prs",
}

# (card_id, label) — order controls grid position
BUILTIN_CARDS: list[tuple[str, str]] = [
    ("kart",      "Kart Queue"),
    ("knowledge", "Knowledge"),
    ("yggdrasil", "Yggdrasil"),
    ("agents",    "Agents"),
    ("secrets",   "Secrets"),
    ("fleet",     "Keys"),
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
    conn = None
    try:
        conn = grove_db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.knowledge")
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM public.knowledge"
            " WHERE created_at > NOW() - INTERVAL '24 hours'"
        )
        today = cur.fetchone()[0]
        out["knowledge"] = {"value": str(total), "sub": f"{today} today", "state": "blue"}
    except Exception:
        pass
    finally:
        if conn is not None:
            grove_db.release_connection(conn)

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
        out["fleet"] = {"value": str(count), "sub": "api keys", "state": "dim"}
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

    # Git Status — dirty file count in the dashboard repo
    try:
        from panes.git import fetch_git_status
        gs = fetch_git_status()
        dirty = gs.get("dirty", 0)
        state = "amber" if dirty > 0 else "green"
        sub = gs.get("branch", "")
        out["git-status"] = {"value": str(dirty) + " changed", "sub": sub, "state": state}
    except Exception:
        pass

    # Open PRs — count via gh CLI
    try:
        from panes.prs import fetch_open_prs
        prs = fetch_open_prs()
        count = len(prs)
        state = "amber" if count > 0 else "green"
        out["open-prs"] = {"value": str(count), "sub": "open PRs", "state": state}
    except Exception:
        pass

    return out


class CardActivated(Message):
    """Posted by CardCell when the user activates a card (Enter or click)."""

    def __init__(self, card_id: str, nav_target: str) -> None:
        super().__init__()
        self.card_id    = card_id
        self.nav_target = nav_target


class CardCell(Widget):
    """A single focusable card tile showing label / value / sub-text."""

    can_focus = True

    BINDINGS = [("enter", "activate", "Open")]

    DEFAULT_CSS = """
    CardCell {
        border: solid #30363d;
        padding: 1 1;
        height: 7;
        background: #161b22;
    }
    CardCell:focus {
        border: solid #58a6ff;
    }
    CardCell .card-label {
        color: #58a6ff;
        text-style: bold;
    }
    CardCell .card-sub {
        color: #8b949e;
    }
    """

    def __init__(
        self,
        card_id: str,
        label: str,
        nav_target: str = "",
        value: str = "—",
        sub: str = "",
        state: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._card_id    = card_id
        self._label      = label
        self._nav_target = nav_target
        self._value      = value
        self._sub        = sub
        self._state      = state
        # Widget IDs must be [a-zA-Z0-9_-] only — strip everything else.
        import re as _re
        self._safe_id = _re.sub(r"[^a-zA-Z0-9_-]", "-", card_id).strip("-") or "card"

    def compose(self) -> ComposeResult:
        yield Static(self._label, classes="card-label", markup=False)
        v = Static(self._value, id=f"cv-{self._safe_id}", classes="card-value", markup=False)
        v.styles.color      = _STATE_COLORS.get(self._state, "#8b949e")
        v.styles.text_style = "bold"
        v.styles.height     = "auto"
        yield v
        yield Static(self._sub, id=f"cs-{self._safe_id}", classes="card-sub", markup=False)

    def update_card(self, value: str, sub: str, state: str) -> None:
        """Update the displayed value, sub-text, and state color."""
        from textual.css.query import NoMatches
        color = _STATE_COLORS.get(state, "#8b949e")
        try:
            v = self.query_one(f"#cv-{self._safe_id}", Static)
            v.update(value)
            v.styles.color = color
        except NoMatches:
            pass
        try:
            self.query_one(f"#cs-{self._safe_id}", Static).update(sub)
        except NoMatches:
            pass

    def action_activate(self) -> None:
        if self._nav_target:
            self.post_message(CardActivated(self._card_id, self._nav_target))

    def on_click(self) -> None:
        self.action_activate()


class _CardsRefreshed(Message):
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data


class CardGrid(Widget):
    """Grid of CardCell widgets. Fetches live data every 30s via background worker."""

    DEFAULT_CSS = """
    CardGrid {
        layout: grid;
        grid-size: 3;
        grid-gutter: 1 1;
        height: 1fr;
        width: 1fr;
        padding: 1 1;
    }
    """

    def __init__(self, cards: list[tuple[str, str]], **kwargs) -> None:
        super().__init__(**kwargs)
        self._cards: list[tuple[str, str]]  = cards
        self._nav_cache: dict[str, str]     = {cid: _CARD_NAV.get(cid, "") for cid, _ in cards}

    def compose(self) -> ComposeResult:
        for card_id, label in self._cards:
            nav = self._nav_cache.get(card_id, "")
            yield CardCell(card_id, label, nav_target=nav)

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(30, self._fetch)

    def reload(self) -> None:
        """Rebuild cells from SOIL enabled cards + built-ins + plus card.

        Cells are created without widget IDs to avoid Textual's ID-registry
        conflict when remove_children() + mount() are called synchronously.
        on__cards_refreshed iterates query(CardCell) instead.
        """
        from widgets import card_store
        soil_cards = [
            (c["id"], c["label"], c.get("nav_target") or "")
            for c in card_store.load_cards()
        ]
        builtin    = [(cid, lbl, _CARD_NAV.get(cid, "")) for cid, lbl in BUILTIN_CARDS]
        all_entries = soil_cards + builtin + [("+", "+ Add Card", "+")]

        self._cards     = [(cid, lbl) for cid, lbl, _ in all_entries]
        self._nav_cache = {cid: nav for cid, _, nav in all_entries}

        self.remove_children()
        # No id= kwarg — avoids duplicate-ID errors when IDs from the prior
        # compose() or reload() haven't been fully deregistered yet.
        cells = [
            CardCell(cid, lbl, nav_target=self._nav_cache[cid])
            for cid, lbl in self._cards
        ]
        self.mount(*cells)
        self._fetch()

    @work(thread=True)
    def _fetch(self) -> None:
        data = fetch_runtime_card_values()

        # Execute value_query / state_query for non-builtin SOIL cards.
        builtin_ids = {cid for cid, _ in BUILTIN_CARDS}
        try:
            from widgets import card_store
            soil_cards = card_store.load_cards()
        except Exception:
            soil_cards = []

        for card in soil_cards:
            cid = card.get("id")
            if not cid or cid in builtin_ids:
                continue
            value_q = card.get("value_query")
            state_q = card.get("state_query")
            if not value_q and not state_q:
                continue
            # Only SELECT queries — SOIL records are local but defense-in-depth matters.
            if value_q and not value_q.strip().upper().startswith("SELECT"):
                value_q = None
            if state_q and not state_q.strip().upper().startswith("SELECT"):
                state_q = None
            if not value_q and not state_q:
                continue
            entry = data.get(cid, {"value": "—", "sub": "", "state": ""})
            if value_q or state_q:
                conn = None
                try:
                    conn = grove_db.get_connection()
                    cur  = conn.cursor()
                    if value_q:
                        try:
                            cur.execute(value_q)
                            row = cur.fetchone()
                            entry["value"] = str(row[0]) if row else "—"
                        except Exception:
                            pass
                    if state_q:
                        try:
                            cur.execute(state_q)
                            row = cur.fetchone()
                            entry["state"] = str(row[0]) if row else ""
                        except Exception:
                            pass
                except Exception:
                    pass
                finally:
                    if conn is not None:
                        grove_db.release_connection(conn)
            data[cid] = entry

        self.post_message(_CardsRefreshed(data))

    def on__cards_refreshed(self, event: _CardsRefreshed) -> None:
        for cell in self.query(CardCell):
            cid = cell._card_id
            if cid == "+":
                continue
            card_data = event.data.get(cid, {})
            cell.update_card(
                card_data.get("value", "—"),
                card_data.get("sub",   ""),
                card_data.get("state", ""),
            )
