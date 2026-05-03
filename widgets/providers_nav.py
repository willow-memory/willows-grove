"""widgets/providers_nav.py — Providers left-panel nav.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class ProviderRowSelected(Message):
    """Posted when the user activates a provider row."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


class ProvidersNavRow(Widget):
    can_focus = True
    BINDINGS = [Binding("enter", "activate", "Select")]

    DEFAULT_CSS = """
    ProvidersNavRow {
        height: 1;
        width: 1fr;
        padding: 0 1;
    }
    ProvidersNavRow:focus {
        background: #21262d;
    }
    """

    def __init__(self, name: str, enabled: bool, ptype: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._name = name
        self._enabled = enabled
        self._ptype = ptype

    def compose(self) -> ComposeResult:
        yield Static("", id=f"pnr-{self._name}-label", markup=True)

    def on_mount(self) -> None:
        self._redraw()

    def _redraw(self) -> None:
        from textual.css.query import NoMatches
        dot = "[green]●[/]" if self._enabled else "[red]●[/]"
        status = "ON" if self._enabled else "OFF"
        text = f"{dot} {self._name}  {status}  {self._ptype}"
        try:
            self.query_one(f"#pnr-{self._name}-label", Static).update(text)
        except NoMatches:
            pass

    def update_row(self, enabled: bool, ptype: str) -> None:
        self._enabled = enabled
        self._ptype = ptype
        self._redraw()

    def action_activate(self) -> None:
        self.post_message(ProviderRowSelected(self._name))

    def on_click(self) -> None:
        self.action_activate()


class _ProvidersRefreshed(Message):
    def __init__(self, providers: list[dict]) -> None:
        super().__init__()
        self.providers = providers


class ProvidersNav(Widget):
    DEFAULT_CSS = """
    ProvidersNav {
        width: 1fr;
        height: 1fr;
        padding: 1 0;
    }
    ProvidersNav #pn-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._provider_names: list[str] = []

    def compose(self) -> ComposeResult:
        yield Static("PROVIDERS", id="pn-header")

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(15, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        from panes.providers import _read_providers
        providers = _read_providers()
        self.post_message(_ProvidersRefreshed(providers))

    def on__providers_refreshed(self, event: _ProvidersRefreshed) -> None:
        providers = event.providers
        new_names = [p["name"] for p in providers]

        if new_names == self._provider_names:
            for p in providers:
                try:
                    row = self.query_one(f"#pnr-row-{p['name']}", ProvidersNavRow)
                    row.update_row(bool(p.get("enabled")), "local" if p.get("local") else "cloud")
                except Exception:
                    pass
            return

        self._provider_names = new_names
        for child in list(self.query(ProvidersNavRow)):
            child.remove()
        for p in providers:
            row = ProvidersNavRow(
                p["name"],
                bool(p.get("enabled")),
                "local" if p.get("local") else "cloud",
                id=f"pnr-row-{p['name']}",
            )
            self.mount(row)
