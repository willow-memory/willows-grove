"""panes/secrets.py — Secrets vault viewer (key names only, never values).
b17: WGRV1  ΔΣ=42
"""
import os
from pathlib import Path

from textual import work
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import DataTable, Label, Static

from widgets.secrets_add_modal import SecretsAddModal, SecretAdded


def _read_secrets() -> list[dict]:
    """Return list of {key, status, hint} — never exposes values."""
    try:
        willow_root = os.environ.get("WILLOW_ROOT", str(Path.home() / "github" / "willow-1.9"))
        import sys
        if willow_root not in sys.path:
            sys.path.insert(0, willow_root)
        from core.vault import Vault

        vault = Vault()
        keys = vault.list_keys()
        out = []
        for k in keys:
            try:
                v = vault.read(k)
                hint = ""
                if isinstance(v, str) and len(v) >= 8:
                    hint = v[:8] + "…"
                    is_set = True
                else:
                    is_set = bool(v)
                out.append({"key": k, "hint": hint, "is_set": is_set})
            except Exception:
                out.append({"key": k, "hint": "(error reading)", "is_set": False})
        return out
    except Exception as e:
        return [{"key": f"(vault error: {e})", "hint": "", "is_set": False}]


class _SecretsFetched(Message):
    def __init__(self, secrets: list[dict]) -> None:
        super().__init__()
        self.secrets = secrets


class SecretsPane(Container):
    BINDINGS = [
        Binding("a", "add_secret", "Add secret"),
    ]

    DEFAULT_CSS = """
    SecretsPane {
        layout: vertical;
    }
    SecretsPane #secrets-title {
        height: auto;
    }
    SecretsPane #secrets-table {
        height: 1fr;
    }
    SecretsPane #secrets-witness {
        height: auto;
        text-align: right;
        color: #6b7280;
        margin: 0 1;
    }
    """

    def compose(self):
        yield Label("  Secrets — ~/.willow/vault.db (names only, redacted prefixes)", id="secrets-title")
        table = DataTable(id="secrets-table", cursor_type="row")
        table.add_columns("Key", "Status", "Prefix")
        yield table
        yield Static("ΔΣ=42", id="secrets-witness", markup=False)

    def on_mount(self) -> None:
        self._fetch()

    def refresh_data(self) -> None:
        self._fetch()

    def action_add_secret(self) -> None:
        self.app.push_screen(SecretsAddModal())

    def on_secret_added(self, event: SecretAdded) -> None:
        self.refresh_data()

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
            table.add_row("[dim]no secrets found[/]", "", "")
            return
        for s in event.secrets:
            status = "[green]●[/]" if s.get("is_set") else "[dim]○[/]"
            hint = f"[dim]{s['hint']}[/]" if s["hint"] else ""
            table.add_row(s["key"], status, hint)
