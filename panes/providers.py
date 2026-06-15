"""panes/providers.py — Provider health from Ollama, env keys, SOIL.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import urllib.request
from pathlib import Path

from textual.binding import Binding
from textual.containers import Container
from textual.widgets import DataTable, Label

from grove.paths import resolve_willow_cli
from grove.theme_textual import DOWN, HEALTHY

_PROVIDER_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
_WILLOW_STORE = Path(os.environ.get("WILLOW_STORE_ROOT", Path.home() / ".willow" / "store"))


def _ollama_models() -> list[str]:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
            data = json.loads(r.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def read_providers() -> list[dict]:
    providers: list[dict] = []

    models = _ollama_models()
    providers.append({
        "name": "ollama",
        "enabled": bool(models),
        "local": True,
        "models": models,
    })

    for name, env_key in (
        ("anthropic", "ANTHROPIC_API_KEY"),
        ("openai", "OPENAI_API_KEY"),
        ("groq", "GROQ_API_KEY"),
    ):
        if os.environ.get(env_key):
            providers.append({
                "name": name,
                "enabled": True,
                "local": False,
                "models": [],
            })

    col_dir = _WILLOW_STORE / "willow" / "providers"
    try:
        db = col_dir / "store.db"
        if db.exists():
            conn = sqlite3.connect(str(db), check_same_thread=False)
            rows = conn.execute("SELECT data FROM records WHERE deleted = 0").fetchall()
            conn.close()
            known = {p["name"] for p in providers}
            for row in rows:
                try:
                    p = json.loads(row[0])
                    if p.get("name") not in known:
                        providers.append(p)
                except Exception:
                    pass
    except Exception:
        pass

    return providers


class ProvidersPane(Container):
    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("e", "enable_selected", "Enable"),
        Binding("d", "disable_selected", "Disable"),
    ]

    DEFAULT_CSS = """
    ProvidersPane {
        height: 1fr;
        padding: 0 1;
    }
    ProvidersPane #prov-title {
        height: 1;
        margin-bottom: 1;
    }
    ProvidersPane #prov-table {
        height: 1fr;
    }
    """

    def compose(self):
        yield Label("  Providers  (e=enable  d=disable  r=refresh)", id="prov-title")
        table = DataTable(id="prov-table", cursor_type="row")
        table.add_columns(
            ("Provider", "name"),
            ("Status", "status"),
            ("Type", "type"),
            ("Models", "models"),
        )
        yield table

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        table = self.query_one("#prov-table", DataTable)
        table.clear()
        providers = read_providers()
        if not providers:
            table.add_row("No provider data", "run willow providers list", "", "")
            return
        for p in providers:
            status = f"[{HEALTHY}]ON[/]" if p.get("enabled") else f"[{DOWN}]OFF[/]"
            ptype = "local" if p.get("local") else "cloud"
            models = ", ".join(p.get("models", [])[:2])
            table.add_row(p["name"], status, ptype, models)

    def action_refresh(self) -> None:
        self.refresh_data()

    def action_enable_selected(self) -> None:
        name = self._selected_name()
        if not name or not _PROVIDER_NAME_RE.match(name):
            return
        subprocess.Popen([*resolve_willow_cli(), "providers", "enable", name])
        self.refresh_data()

    def action_disable_selected(self) -> None:
        name = self._selected_name()
        if not name:
            return
        if name == "ollama":
            self.app.notify("Ollama cannot be disabled — it's the default provider.", severity="warning")
            return
        if not _PROVIDER_NAME_RE.match(name):
            return
        subprocess.Popen([*resolve_willow_cli(), "providers", "disable", name])
        self.refresh_data()

    def _selected_name(self) -> str | None:
        table = self.query_one("#prov-table", DataTable)
        row = table.cursor_row
        if row < 0:
            return None
        return str(table.get_cell_at((row, 0)))
