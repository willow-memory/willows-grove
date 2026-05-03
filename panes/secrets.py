"""panes/secrets.py — Secrets vault viewer (key names only, never values).
b17: WGRV1  ΔΣ=42
"""
import json
from pathlib import Path

from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable, Label

_SECRETS_PATH = Path.home() / ".willow" / "secrets.json"


def _read_secrets() -> list[dict]:
    """Return list of {key, hint} — never exposes values."""
    try:
        raw = json.loads(_SECRETS_PATH.read_text())
        if not isinstance(raw, dict):
            return []
        out = []
        for k, v in raw.items():
            hint = ""
            if isinstance(v, str) and len(v) >= 8:
                hint = v[:4] + "…"
            out.append({"key": k, "hint": hint})
        return out
    except FileNotFoundError:
        return []
    except Exception as e:
        return [{"key": f"(error: {e})", "hint": ""}]


class _SecretsFetched(Message):
    def __init__(self, secrets: list[dict]) -> None:
        super().__init__()
        self.secrets = secrets


class SecretsPane(Container):
    def compose(self):
        yield Label("  Secrets — ~/.willow/secrets.json (keys only)", id="secrets-title")
        table = DataTable(id="secrets-table", cursor_type="row")
        table.add_columns("Key", "Prefix")
        yield table

    def on_mount(self) -> None:
        self._fetch()

    def refresh_data(self) -> None:
        self._fetch()

    @work(thread=True)
    def _fetch(self) -> None:
        self.post_message(_SecretsFetched(_read_secrets()))

    def on__secrets_fetched(self, event: _SecretsFetched) -> None:
        from textual.css.query import NoMatches
        try:
            table = self.query_one("#secrets-table", DataTable)
        except NoMatches:
            return
        table.clear()
        if not event.secrets:
            table.add_row("[dim]no secrets found[/]", "")
            return
        for s in event.secrets:
            table.add_row(s["key"], f"[dim]{s['hint']}[/]" if s["hint"] else "")
