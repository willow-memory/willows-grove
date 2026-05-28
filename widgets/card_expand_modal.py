"""widgets/card_expand_modal.py — Expand view for data cards.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Static


class CardExpandModal(ModalScreen):
    """Modal showing the expand rows for a data card."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]

    DEFAULT_CSS = """
    CardExpandModal {
        align: center middle;
    }
    CardExpandModal > Vertical {
        width: 80%;
        height: 80%;
        max-width: 120;
        background: #161b22;
        border: solid #58a6ff;
        padding: 1 2;
    }
    CardExpandModal #modal-title {
        color: #58a6ff;
        text-style: bold;
        margin-bottom: 1;
    }
    CardExpandModal #modal-hint {
        color: #8b949e;
        margin-top: 1;
    }
    """

    def __init__(self, card_id: str, label: str) -> None:
        super().__init__()
        self._card_id = card_id
        self._label   = label

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self._label, id="modal-title", markup=False)
            yield DataTable(id="expand-table", show_cursor=True)
            yield Static("Esc to close", id="modal-hint", markup=False)

    def on_mount(self) -> None:
        self._load()

    def _load(self) -> None:
        table = self.query_one("#expand-table", DataTable)
        rows, columns = self._fetch_rows()
        if not columns:
            table.add_columns("(no data)")
            table.add_row("No records found.")
            return
        table.add_columns(*[c.replace("_", " ").title() for c in columns])
        for row in rows:
            table.add_row(*[str(row.get(c, "")) for c in columns])

    def _fetch_rows(self) -> tuple[list[dict], list[str]]:
        try:
            cid = self._card_id
            if cid == "todos":
                return self._soil_rows("willow-dashboard/todos", ["title", "status"])
            if cid == "projects":
                return self._soil_rows("willow-dashboard/projects", ["name", "status"])
            if cid == "kart":
                return self._pg_rows(
                    "SELECT id, title, status, priority FROM kart.tasks ORDER BY created_at DESC LIMIT 50",
                    ["id", "title", "status", "priority"],
                )
            if cid == "knowledge":
                return self._pg_rows(
                    "SELECT id, title, domain FROM public.knowledge WHERE invalid_at IS NULL ORDER BY created_at DESC LIMIT 50",
                    ["id", "title", "domain"],
                )
            if cid == "agents":
                return self._soil_rows("agents/hanuman/store", ["id", "status", "role"])
            if cid == "secrets":
                return self._soil_rows("willow-dashboard/secrets", ["name", "updated_at"])
            if cid in ("fleet", "mcp"):
                return self._soil_rows("willow-dashboard/config", ["key", "value"])
            if cid == "yggdrasil":
                return self._soil_rows("hanuman/atoms/store", ["id", "type", "domain"])
            # SOIL card from card store
            return self._soil_rows(f"willow-dashboard/cards/{cid}", [])
        except Exception as e:
            return [{"error": str(e)}], ["error"]

    def _soil_rows(self, collection: str, preferred_cols: list[str]) -> tuple[list[dict], list[str]]:
        import soil
        records = soil.all_records(collection) or []
        if not records:
            return [], []
        cols = preferred_cols or [k for k in records[0].keys() if not k.startswith("_")]
        cols = [c for c in cols if any(c in r for r in records)]
        if not cols:
            cols = [k for k in records[0].keys() if not k.startswith("_")]
        return records, cols[:6]

    def _pg_rows(self, query: str, cols: list[str]) -> tuple[list[dict], list[str]]:
        import psycopg2, os
        db   = os.environ.get("WILLOW_PG_DB",   "willow_20")
        user = os.environ.get("WILLOW_PG_USER", os.environ.get("USER", ""))
        conn = psycopg2.connect(dbname=db, user=user)
        with conn.cursor() as cur:
            cur.execute(query)
            desc = [d[0] for d in cur.description]
            rows = [dict(zip(desc, r)) for r in cur.fetchall()]
        conn.close()
        return rows, cols or desc
