# Phase 4d: Settings + Help ContextPanel Nav — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add interactive consent toggles to the Settings pane and a scrollable reference guide to the Help pane, each with a left-panel status/nav widget.

**Architecture:** `_read_consent`/`_write_consent` live in `panes/settings.py` and are locally imported by `SettingsNav`; `ConsentToggleRow` widgets post `_ConsentChanged` messages handled by `SettingsPane`; `HelpNavRow` widgets post `HelpSectionSelected` handled by `WillowGrove` which calls `HelpPane.jump_to_section`. All four new files follow the established widget/pane patterns from phases 4a–4c.

**Tech Stack:** Python 3.11, Textual (Widget, Container, VerticalScroll, Message, @work, Static, ComposeResult), pathlib, json.

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `panes/settings.py` | `_read_consent`, `_write_consent`, `ConsentToggleRow`, `SettingsPane` |
| Create | `widgets/settings_nav.py` | `SettingsNav` — read-only consent status dots |
| Create | `widgets/help_nav.py` | `HelpSectionSelected`, `HelpNavRow`, `HelpNav` |
| Create | `panes/help.py` | `HelpPane` — scrollable reference content |
| Modify | `app.py` | Imports, ContextPanel, ctx_map, two event handlers, replace placeholder Statics |
| Create | `tests/test_panes_settings.py` | Tests for consent I/O + toggle widget |
| Create | `tests/test_widgets_help_nav.py` | Tests for HelpSectionSelected + HelpNavRow |

---

### Task 1: `_read_consent` + `_write_consent` + `ConsentToggleRow` + `SettingsPane`

**Files:**
- Create: `panes/settings.py`
- Create: `tests/test_panes_settings.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_panes_settings.py`:
```python
"""tests/test_panes_settings.py
b17: WGRV1  ΔΣ=42
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panes.settings import _read_consent, _write_consent, ConsentToggleRow


def test_read_consent_defaults_when_missing(tmp_path):
    result = _read_consent(tmp_path / "consent.json")
    assert result == {"internet": True, "cloud_llm": True, "lan": True}


def test_read_consent_returns_values(tmp_path):
    p = tmp_path / "consent.json"
    p.write_text(json.dumps({"internet": False, "cloud_llm": True, "lan": False}))
    result = _read_consent(p)
    assert result["internet"] is False
    assert result["cloud_llm"] is True
    assert result["lan"] is False


def test_read_consent_defaults_on_malformed(tmp_path):
    p = tmp_path / "consent.json"
    p.write_text("not json{{{")
    result = _read_consent(p)
    assert result == {"internet": True, "cloud_llm": True, "lan": True}


def test_write_consent_roundtrip(tmp_path):
    p = tmp_path / "consent.json"
    _write_consent({"internet": False, "cloud_llm": False, "lan": True}, p)
    result = _read_consent(p)
    assert result["internet"] is False
    assert result["cloud_llm"] is False
    assert result["lan"] is True


def test_write_consent_never_raises(tmp_path):
    _write_consent({"internet": True}, tmp_path / "nonexistent" / "consent.json")


def test_consent_toggle_row_stores_fields():
    row = ConsentToggleRow("internet", "Internet", "Allow outbound internet", True)
    assert row._key == "internet"
    assert row._label == "Internet"
    assert row._enabled is True


def test_consent_toggle_row_toggle_flips():
    row = ConsentToggleRow("lan", "LAN", "Local network", False)
    row._enabled = True
    assert row._enabled is True
```

- [ ] **Step 2: Run tests to verify they fail**

```
cd /home/sean-campbell/github/safe-app-willow-grove
pytest tests/test_panes_settings.py -v
```
Expected: `ModuleNotFoundError: No module named 'panes.settings'`

- [ ] **Step 3: Create `panes/settings.py`**

```python
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


class ConsentToggleRow(Widget):
    can_focus = True
    BINDINGS = [Binding("enter", "toggle", "Toggle")]

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
        self._render()

    def _render(self) -> None:
        from textual.css.query import NoMatches
        dot = "[green]●[/]" if self._enabled else "[red]●[/]"
        status = "ON" if self._enabled else "OFF"
        text = (f"{dot} [bold]{self._label}[/]  {status}\n"
                f"  [dim]{self._description}[/]")
        try:
            self.query_one(f"#ctr-{self._key}-label", Static).update(text)
        except NoMatches:
            pass

    def action_toggle(self) -> None:
        self._enabled = not self._enabled
        self._render()
        self.post_message(_ConsentChanged(self._key, self._enabled))

    def on_click(self) -> None:
        self.action_toggle()


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
        yield Label("CONSENT", id="sp-header")

    def on_mount(self) -> None:
        consent = _read_consent()
        for key, label, desc in self._ROWS:
            self.mount(ConsentToggleRow(
                key, label, desc, consent.get(key, True),
                id=f"ctr-row-{key}",
            ))

    def on__consent_changed(self, event: _ConsentChanged) -> None:
        consent = _read_consent()
        consent[event.key] = event.enabled
        _write_consent(consent)
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_panes_settings.py -v
```
Expected: 7 PASSED

- [ ] **Step 5: Commit**

```bash
git add panes/settings.py tests/test_panes_settings.py
git commit -m "feat(settings): _read_consent + _write_consent + ConsentToggleRow + SettingsPane"
```

---

### Task 2: `SettingsNav` widget

**Files:**
- Create: `widgets/settings_nav.py`

Context: `SettingsNav` is pure status display — same pattern as `HealthNav` in `widgets/health_nav.py`. It locally imports `_read_consent` from `panes.settings` inside the `@work` method to avoid circular imports. No tests needed beyond what `test_panes_settings.py` already covers for `_read_consent`.

- [ ] **Step 1: Create `widgets/settings_nav.py`**

```python
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
```

- [ ] **Step 2: Run all tests to verify nothing broke**

```
pytest tests/ -v
```
Expected: all previously-passing tests still PASS

- [ ] **Step 3: Commit**

```bash
git add widgets/settings_nav.py
git commit -m "feat(settings): SettingsNav widget with 15s consent polling"
```

---

### Task 3: `HelpSectionSelected` + `HelpNavRow` + `HelpNav`

**Files:**
- Create: `widgets/help_nav.py`
- Create: `tests/test_widgets_help_nav.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_widgets_help_nav.py`:
```python
"""tests/test_widgets_help_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.help_nav import HelpSectionSelected, HelpNavRow


def test_help_section_selected_stores_section():
    msg = HelpSectionSelected("shortcuts")
    assert msg.section == "shortcuts"


def test_help_nav_row_stores_section():
    row = HelpNavRow("overview", "Overview")
    assert row._section == "overview"
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_widgets_help_nav.py -v
```
Expected: `ModuleNotFoundError: No module named 'widgets.help_nav'`

- [ ] **Step 3: Create `widgets/help_nav.py`**

```python
"""widgets/help_nav.py — Help section nav left-panel.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class HelpSectionSelected(Message):
    """Posted when the user selects a help section."""

    def __init__(self, section: str) -> None:
        super().__init__()
        self.section = section


class HelpNavRow(Widget):
    can_focus = True
    BINDINGS = [Binding("enter", "activate", "Go")]

    DEFAULT_CSS = """
    HelpNavRow {
        height: 1;
        width: 1fr;
        padding: 0 1;
    }
    HelpNavRow:hover {
        color: #c9d1d9;
        background: #21262d;
    }
    HelpNavRow:focus {
        background: #21262d;
    }
    """

    def __init__(self, section: str, label: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._section = section
        self._label = label

    def compose(self) -> ComposeResult:
        yield Static(self._label, id=f"hnr-{self._section}-label")

    def action_activate(self) -> None:
        self.post_message(HelpSectionSelected(self._section))

    def on_click(self) -> None:
        self.action_activate()


class HelpNav(Widget):
    DEFAULT_CSS = """
    HelpNav {
        width: 1fr;
        height: 1fr;
        padding: 1 0;
    }
    HelpNav #hn-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 1;
    }
    """

    _SECTIONS: list[tuple[str, str]] = [
        ("overview",    "Overview"),
        ("navigation",  "Navigation"),
        ("shortcuts",   "Shortcuts"),
        ("privacy",     "Privacy & Consent"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("HELP", id="hn-header")
        for section, label in self._SECTIONS:
            yield HelpNavRow(section, label, id=f"hnr-row-{section}")
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_widgets_help_nav.py -v
```
Expected: 2 PASSED

- [ ] **Step 5: Commit**

```bash
git add widgets/help_nav.py tests/test_widgets_help_nav.py
git commit -m "feat(help): HelpSectionSelected + HelpNavRow + HelpNav"
```

---

### Task 4: `HelpPane`

**Files:**
- Create: `panes/help.py`

Context: `HelpPane` extends `VerticalScroll` (from `textual.containers`). It composes four named `Static` widgets. `jump_to_section(section)` calls `scroll_visible()` on the matching widget. The help content is static markup — it does not need to be tested beyond import-time correctness.

- [ ] **Step 1: Create `panes/help.py`**

```python
"""panes/help.py — Help reference pane.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

_OVERVIEW = """\
[bold #58a6ff]Willow Grove[/]

Local-first AI workspace. One surface for messaging, task coordination,
knowledge, and agent management. Everything runs on your machine.
Postgres holds the memory. Ollama runs the models. You hold the keys.\
"""

_NAVIGATION = """\
[bold #58a6ff]Navigation[/]

[bold]Home[/]       Dashboard — tasks, agents, active thoughts
[bold]Chat[/]       Grove channels — agent and human messaging
[bold]Projects[/]   Active projects and task queues
[bold]Knowledge[/]  Search and browse the knowledge base
[bold]Providers[/]  AI model providers — enable/disable
[bold]Health[/]     Subsystem status — pg, ollama, kart, SOIL
[bold]Settings[/]   Consent and security controls
[bold]Help[/]       This panel\
"""

_SHORTCUTS = """\
[bold #58a6ff]Keyboard Shortcuts[/]

[bold]q[/]       Quit
[bold]r[/]       Refresh
[bold]1–8[/]     Navigate to Home / Chat / Projects / Knowledge /
            Providers / Health / Settings / Help
[bold]e[/]       Enable selected provider (Providers pane)
[bold]d[/]       Disable selected provider (Providers pane)
[bold]Enter[/]   Confirm selection / toggle (nav rows, settings)
[bold]↑ ↓[/]     Move cursor (Knowledge search results)\
"""

_PRIVACY = """\
[bold #58a6ff]Privacy & Consent[/]

Willow runs locally. No data leaves your machine unless you explicitly
enable cloud features.

[bold]Internet[/]    Outbound internet connections. Off = fully air-gapped.
[bold]Cloud LLM[/]   Prompts sent to cloud AI providers (e.g. Anthropic).
                Off = local models only.
[bold]LAN[/]         Local network communication between your devices.
                Off = no outbound LAN traffic.

Consent state is stored at [dim]~/.willow/consent.json[/] and applies
system-wide to all apps installed through Willow Grove.

Authorization is enforced by the SAP gate — apps must present a
PGP-signed manifest to access any Willow tool.\
"""


class HelpPane(VerticalScroll):
    DEFAULT_CSS = """
    HelpPane {
        height: 1fr;
        padding: 1 2;
    }
    HelpPane Static {
        padding: 0 0 2 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(_OVERVIEW,    id="help-overview",    markup=True)
        yield Static(_NAVIGATION,  id="help-navigation",  markup=True)
        yield Static(_SHORTCUTS,   id="help-shortcuts",   markup=True)
        yield Static(_PRIVACY,     id="help-privacy",     markup=True)

    def jump_to_section(self, section: str) -> None:
        from textual.css.query import NoMatches
        try:
            self.query_one(f"#help-{section}", Static).scroll_visible()
        except NoMatches:
            pass
```

- [ ] **Step 2: Run all tests**

```
pytest tests/ -v
```
Expected: all tests PASS

- [ ] **Step 3: Commit**

```bash
git add panes/help.py
git commit -m "feat(help): HelpPane with scrollable reference content"
```

---

### Task 5: Wire everything into `app.py`

**Files:**
- Modify: `app.py`

Context: `app.py` currently yields `Static("[ Settings — coming soon ]", id="pane-settings")` and `Static("[ Help — coming soon ]", id="pane-help")` as placeholder panes (lines 315–316). These are replaced with `SettingsPane` and `HelpPane`. `ContextPanel` already has `ProvidersNav` and `HealthNav` as the last two items — add `SettingsNav` and `HelpNav` after them. The `ctx_map` in `_show_target` needs `"settings"` and `"help"` entries. `WillowGrove` needs `on_help_section_selected`.

- [ ] **Step 1: Add imports to `app.py`**

After `from widgets.health_nav import HealthNav`, add:

```python
from widgets.settings_nav import SettingsNav
from widgets.help_nav     import HelpSectionSelected, HelpNav
from panes.settings       import SettingsPane
from panes.help           import HelpPane
```

- [ ] **Step 2: Replace placeholder Statics in `WillowGrove.compose()`**

Replace:
```python
                yield Static("[ Settings — coming soon ]", id="pane-settings")
                yield Static("[ Help — coming soon ]", id="pane-help")
```
With:
```python
                yield SettingsPane(id="pane-settings")
                yield HelpPane(id="pane-help")
```

- [ ] **Step 3: Add `SettingsNav` and `HelpNav` to `ContextPanel.compose()`**

Replace:
```python
        yield ProvidersNav(id="ctx-providers")
        yield HealthNav(id="ctx-health")
```
With:
```python
        yield ProvidersNav(id="ctx-providers")
        yield HealthNav(id="ctx-health")
        yield SettingsNav(id="ctx-settings")
        yield HelpNav(id="ctx-help")
```

- [ ] **Step 4: Update `ctx_map` in `ContextPanel._show_target()`**

Replace:
```python
            "providers": "#ctx-providers",
            "health":    "#ctx-health",
```
With:
```python
            "providers": "#ctx-providers",
            "health":    "#ctx-health",
            "settings":  "#ctx-settings",
            "help":      "#ctx-help",
```

- [ ] **Step 5: Add `on_help_section_selected` to `WillowGrove`**

After `on_provider_row_selected`, add:

```python
    def on_help_section_selected(self, event: HelpSectionSelected) -> None:
        try:
            self.query_one(HelpPane).jump_to_section(event.section)
        except NoMatches:
            pass
```

- [ ] **Step 6: Remove the now-unused `Static` import guard**

Check whether `Static` is still used in `app.py` after replacing the two placeholder yields. It is still used in `GroveRightPanel` and `VitalsBar`, so leave it.

- [ ] **Step 7: Run all tests**

```
pytest tests/ -v
```
Expected: all tests PASS

- [ ] **Step 8: Commit**

```bash
git add app.py
git commit -m "feat(app): wire SettingsNav + HelpNav + SettingsPane + HelpPane into dashboard"
```

---

## Self-Review

**Spec coverage:**
- ✅ `_read_consent()` defaults + malformed handling — Task 1
- ✅ `_write_consent()` atomic write, never raises — Task 1
- ✅ `ConsentToggleRow` with `_key`, `_label`, `_enabled`, `action_toggle`, `_ConsentChanged` — Task 1
- ✅ `SettingsPane` mounts three rows, handles `_ConsentChanged` → writes consent — Task 1
- ✅ `SettingsNav` with `_fetch()`, 15s polling, `on__consent_status_fetched` — Task 2
- ✅ `HelpSectionSelected(section)` — Task 3
- ✅ `HelpNavRow` stores `_section`, `action_activate`, `on_click` — Task 3
- ✅ `HelpNav` with four section rows — Task 3
- ✅ `HelpPane` as `VerticalScroll` with four named Statics — Task 4
- ✅ `jump_to_section(section)` → `scroll_visible()` — Task 4
- ✅ All four content sections (overview, navigation, shortcuts, privacy) — Task 4
- ✅ `ContextPanel` wired with `ctx-settings` + `ctx-help` — Task 5
- ✅ `WillowGrove.on_help_section_selected` — Task 5
- ✅ Placeholder Statics replaced with `SettingsPane` + `HelpPane` — Task 5

**Placeholder scan:** None found.

**Type consistency:** `HelpSectionSelected.section: str` defined Task 3, consumed in Task 5 as `event.section` ✅. `_read_consent()` returns `dict` defined Task 1, consumed in Task 2 `SettingsNav._fetch()` ✅. `ConsentToggleRow` constructor `(key, label, description, enabled)` defined Task 1, used in `SettingsPane.on_mount` Task 1 ✅. `jump_to_section(section: str)` defined Task 4, called in Task 5 ✅.
