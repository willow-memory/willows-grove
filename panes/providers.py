"""panes/providers.py — Provider enable/disable pane.
b17: WGRV1  ΔΣ=42
"""
import json
import os
import sqlite3
from pathlib import Path

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import DataTable, Label

WILLOW_STORE = Path(os.environ.get("WILLOW_STORE_ROOT", Path.home() / ".willow" / "store"))


def _read_providers() -> list[dict]:
    col_dir = WILLOW_STORE / "willow" / "providers"
    if not col_dir.exists():
        return []
    providers = []
    try:
        db = col_dir / "store.db"
        if db.exists():
            conn = sqlite3.connect(str(db), check_same_thread=False)
            rows = conn.execute("SELECT data FROM records WHERE deleted = 0").fetchall()
            conn.close()
            for row in rows:
                try:
                    providers.append(json.loads(row[0]))
                except Exception:
                    pass
    except Exception:
        pass
    return providers


class ProvidersPane(Container):
    BINDINGS = [
        Binding("e", "enable_selected",  "Enable"),
        Binding("d", "disable_selected", "Disable"),
    ]

    def compose(self):
        yield Label("  Providers  (e=enable  d=disable)", id="prov-title")
        table = DataTable(id="prov-table", cursor_type="row")
        table.add_columns("Provider", "Status", "Type", "Models")
        yield table

    def refresh_data(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        table.clear()
        providers = _read_providers()
        if not providers:
            table.add_row("No provider data", "run willow providers list", "", "")
            return
        for p in providers:
            status = "[green]ON[/]" if p.get("enabled") else "[red]OFF[/]"
            ptype  = "local" if p.get("local") else "cloud"
            models = ", ".join(p.get("models", [])[:2])
            table.add_row(p["name"], status, ptype, models)

    def action_enable_selected(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        row   = table.cursor_row
        if row < 0:
            return
        name = str(table.get_cell_at((row, 0)))
        os.system(f"willow providers enable {name} &")
        self.refresh_data()

    def action_disable_selected(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        row   = table.cursor_row
        if row < 0:
            return
        name = str(table.get_cell_at((row, 0)))
        if name == "ollama":
            self.app.notify("Ollama cannot be disabled — it's the default provider.", severity="warning")
            return
        os.system(f"willow providers disable {name} &")
        self.refresh_data()

    def select_provider(self, name: str) -> None:
        table = self.query_one("#prov-table", DataTable)
        for i in range(table.row_count):
            if str(table.get_cell_at((i, 0))) == name:
                table.move_cursor(row=i)
                return
