"""panes/settings.py — Consent toggle pane + consent I/O.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label, Static

_CONSENT_PATH = Path(os.environ.get("WILLOW_CONSENT_PATH",
                                    Path.home() / ".willow" / "consent.json"))
_DEFAULTS: dict = {"internet": True, "cloud_llm": True, "lan": True}


def _read_consent(path: Path = _CONSENT_PATH) -> dict:
    """Pure function — never raises. Returns defaults if file absent or malformed."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return dict(_DEFAULTS)
        return {k: bool(data.get(k, v)) for k, v in _DEFAULTS.items()}
    except Exception:
        return dict(_DEFAULTS)


def _write_consent(data: dict, path: Path = _CONSENT_PATH) -> None:
    """Atomic write — never raises."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        pass


class _ConsentChanged(Message):
    def __init__(self, key: str, enabled: bool) -> None:
        super().__init__()
        self.key = key
        self.enabled = enabled


class ConsentToggleRow(Container):
    can_focus = True
    BINDINGS = [Binding("enter", "consent_toggle", "Toggle")]

    DEFAULT_CSS = """
    ConsentToggleRow {
        height: 3;
        width: 1fr;
        padding: 0 1;
        border-bottom: solid #30363d;
    }
    ConsentToggleRow:focus {
        background: #21262d;
    }
    """

    def __init__(self, key: str, label: str, description: str,
                 enabled: bool, **kwargs) -> None:
        super().__init__(**kwargs)
        self._key = key
        self._label = label
        self._description = description
        self._enabled = enabled

    def compose(self) -> ComposeResult:
        yield Static("", id=f"ctr-{self._key}-label", markup=True)

    def on_mount(self) -> None:
        self._update_label()

    def _update_label(self) -> None:
        from textual.css.query import NoMatches
        dot = "[green]●[/]" if self._enabled else "[red]●[/]"
        status = "ON" if self._enabled else "OFF"
        text = (f"{dot} [bold]{self._label}[/]  {status}\n"
                f"  [dim]{self._description}[/]")
        try:
            self.query_one(f"#ctr-{self._key}-label", Static).update(text)
        except NoMatches:
            pass

    def action_consent_toggle(self) -> None:
        self._enabled = not self._enabled
        self._update_label()
        self.post_message(_ConsentChanged(self._key, self._enabled))

    def on_click(self) -> None:
        self.action_consent_toggle()


class SettingsPane(Container):
    DEFAULT_CSS = """
    SettingsPane {
        height: 1fr;
        padding: 1 2;
    }
    SettingsPane #sp-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 0 1 0;
    }
    """

    _ROWS: list[tuple[str, str, str]] = [
        ("internet", "Internet",  "Allow outbound internet connections"),
        ("cloud_llm", "Cloud LLM", "Send prompts to cloud AI providers (e.g. Anthropic)"),
        ("lan",      "LAN",       "Allow local network communication between devices"),
    ]

    def compose(self) -> ComposeResult:
        consent = _read_consent()
        yield Label("CONSENT", id="sp-header")
        for key, label, desc in self._ROWS:
            yield ConsentToggleRow(
                key, label, desc, consent.get(key, True),
                id=f"ctr-row-{key}",
            )

    def on__consent_changed(self, event: _ConsentChanged) -> None:
        consent = _read_consent()
        consent[event.key] = event.enabled
        _write_consent(consent)
