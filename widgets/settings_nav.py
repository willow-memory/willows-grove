"""widgets/settings_nav.py — Settings/consent status left-panel.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class _ConsentStatusFetched(Message):
    def __init__(self, consent: dict) -> None:
        super().__init__()
        self.consent = consent


class SettingsNav(Widget):
    DEFAULT_CSS = """
    SettingsNav {
        width: 1fr;
        height: 1fr;
        padding: 1 1;
    }
    SettingsNav #sn-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 0 1 0;
    }
    SettingsNav #sn-status {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("CONSENT", id="sn-header")
        yield Static("", id="sn-status", markup=True)

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(15, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        from panes.settings import _read_consent
        consent = _read_consent()
        self.post_message(_ConsentStatusFetched(consent))

    def on__consent_status_fetched(self, event: _ConsentStatusFetched) -> None:
        from textual.css.query import NoMatches
        c = event.consent
        lines = []
        for key, label in (("internet", "internet"), ("cloud_llm", "cloud llm"), ("lan", "lan")):
            ok = c.get(key, True)
            dot = "[green]●[/]" if ok else "[red]●[/]"
            lines.append(f"{dot} [dim]{label}[/]  {'on' if ok else 'off'}")
        try:
            self.query_one("#sn-status", Static).update("\n".join(lines))
        except NoMatches:
            pass
