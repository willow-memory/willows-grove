"""panes/settings.py — Consent toggles + subsystem vitals.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import os
import sys
from contextlib import suppress
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.widgets import Label, Rule, Static
from textual import work

from grove.apps.vitals import fetch_vitals, format_vitals_line
from grove.theme_textual import ACCENT, PRIMARY, SECONDARY, markup_status_dot

_WILLOW_HOME = Path(os.environ.get("WILLOW_HOME", Path.home() / ".willow"))
_SETTINGS_GLOBAL = Path(
    os.environ.get("WILLOW_SETTINGS_GLOBAL", _WILLOW_HOME / "settings.global.json")
)
_CONSENT_LEGACY = Path(os.environ.get("WILLOW_CONSENT_PATH", _WILLOW_HOME / "consent.json"))
_DEFAULTS: dict[str, bool] = {"internet": True, "cloud_llm": True, "lan": True}


def _ensure_willow_import() -> bool:
    root = os.environ.get("WILLOW_ROOT", "").strip()
    if root and root not in sys.path:
        sys.path.insert(0, root)
    try:
        import willow.fylgja.global_settings  # noqa: F401
        return True
    except ImportError:
        return False


def read_consent(path: Path | None = None) -> dict:
    if path is None and _ensure_willow_import():
        from willow.fylgja.global_settings import read_consent as _read

        return _read(path=_SETTINGS_GLOBAL)
    target = path or _SETTINGS_GLOBAL
    if not target.is_file():
        if path is not None:
            return dict(_DEFAULTS)
        if _ensure_willow_import():
            from willow.fylgja.global_settings import read_consent as _read

            return _read(path=_SETTINGS_GLOBAL)
        if _CONSENT_LEGACY.is_file():
            target = _CONSENT_LEGACY
        else:
            return dict(_DEFAULTS)
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("consent"), dict):
            return {k: bool(data["consent"].get(k, v)) for k, v in _DEFAULTS.items()}
        if not isinstance(data, dict):
            return dict(_DEFAULTS)
        return {k: bool(data.get(k, v)) for k, v in _DEFAULTS.items()}
    except Exception:
        return dict(_DEFAULTS)


def write_consent(data: dict, path: Path | None = None) -> None:
    if path is None and _ensure_willow_import():
        from willow.fylgja.global_settings import write_consent as _write

        _write({k: bool(data.get(k, v)) for k, v in _DEFAULTS.items()}, path=_SETTINGS_GLOBAL)
        return
    target = path or _CONSENT_LEGACY
    try:
        if target == _SETTINGS_GLOBAL or target.name == "settings.global.json":
            existing: dict = {}
            if target.is_file():
                raw = json.loads(target.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    existing = raw
            existing.setdefault("version", 1)
            existing["consent"] = {k: bool(data.get(k, v)) for k, v in _DEFAULTS.items()}
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(".tmp")
            tmp.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
            tmp.replace(target)
            write_consent(existing["consent"], _CONSENT_LEGACY)
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        tmp.replace(target)
    except Exception:
        pass


def format_health_block(v: dict) -> str:
    pg = v.get("pg", {})
    olla = v.get("ollama", {})
    kart = v.get("kart", {})
    soil = v.get("soil", {})
    mcp = v.get("mcp", {})
    lines = [
        f"Postgres   {'ok' if pg.get('ok') else 'down'}  {pg.get('detail', '')}",
        f"Ollama     {'ok' if olla.get('ok') else 'down'}  {olla.get('count', 0)} models",
        f"Kart       {'ok' if kart.get('ok') else 'down'}  "
        f"{kart.get('running', 0)} running / {kart.get('queued', 0)} queued",
        f"SOIL store {'ok' if soil.get('ok') else 'missing'}",
        f"MCP        {mcp.get('count', 0)} configured"
        + ("  serve up" if mcp.get("serve_up") else ""),
    ]
    return "\n".join(lines)


class _ConsentChanged(Message):
    def __init__(self, key: str, enabled: bool) -> None:
        super().__init__()
        self.key = key
        self.enabled = enabled


class _HealthLoaded(Message):
    def __init__(self, line: str, block: str) -> None:
        super().__init__()
        self.line = line
        self.block = block


class ConsentToggleRow(Container):
    can_focus = True
    BINDINGS = [Binding("enter", "consent_toggle", "Toggle")]

    DEFAULT_CSS = """
    ConsentToggleRow {
        height: 3;
        width: 1fr;
        padding: 0 1;
    }
    """

    def __init__(self, key: str, label: str, description: str, enabled: bool, **kwargs) -> None:
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
        dot = markup_status_dot(self._enabled)
        status = "ON" if self._enabled else "OFF"
        text = (
            f"{dot} [bold {PRIMARY}]{self._label}[/]  {status}\n"
            f"  [dim {SECONDARY}]{self._description}[/]"
        )
        with suppress(Exception):
            self.query_one(f"#ctr-{self._key}-label", Static).update(text)

    def action_consent_toggle(self) -> None:
        self._enabled = not self._enabled
        self._update_label()
        self.post_message(_ConsentChanged(self._key, self._enabled))

    def on_click(self) -> None:
        self.action_consent_toggle()


class SettingsPane(Container):
    BINDINGS = [Binding("r", "refresh", "Refresh")]

    DEFAULT_CSS = f"""
    SettingsPane {{
        height: 1fr;
        padding: 1 2;
    }}
    SettingsPane #sp-header {{
        color: {ACCENT};
        text-style: bold;
        padding: 0 0 1 0;
    }}
    SettingsPane #sp-health-line {{
        color: {SECONDARY};
        margin-bottom: 1;
    }}
    SettingsPane #sp-health-block {{
        color: {PRIMARY};
        padding: 0 0 1 0;
    }}
    """

    _ROWS: list[tuple[str, str, str]] = [
        ("internet", "Internet", "Allow outbound internet connections"),
        ("cloud_llm", "Cloud LLM", "Send prompts to cloud AI providers"),
        ("lan", "LAN", "Allow local network communication between devices"),
    ]

    def compose(self) -> ComposeResult:
        consent = read_consent()
        yield Label("CONSENT", id="sp-header")
        for key, label, desc in self._ROWS:
            yield ConsentToggleRow(
                key, label, desc, consent.get(key, True),
                id=f"ctr-row-{key}",
            )
        yield Rule()
        yield Label("SUBSYSTEMS", id="sp-health-header")
        yield Static("loading vitals…", id="sp-health-line", markup=True)
        with VerticalScroll():
            yield Static("", id="sp-health-block")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self._fetch_health()

    @work(thread=True, exit_on_error=False)
    def _fetch_health(self) -> None:
        try:
            v = fetch_vitals()
            line = format_vitals_line(v)
            block = format_health_block(v)
        except Exception:
            line = "vitals unavailable"
            block = ""
        self.post_message(_HealthLoaded(line, block))

    def on__consent_changed(self, event: _ConsentChanged) -> None:
        consent = read_consent()
        consent[event.key] = event.enabled
        write_consent(consent)

    def on__health_loaded(self, event: _HealthLoaded) -> None:
        with suppress(Exception):
            self.query_one("#sp-health-line", Static).update(
                f"[dim {SECONDARY}]{event.line}[/]"
            )
            self.query_one("#sp-health-block", Static).update(event.block)

    def action_refresh(self) -> None:
        self.refresh_data()
