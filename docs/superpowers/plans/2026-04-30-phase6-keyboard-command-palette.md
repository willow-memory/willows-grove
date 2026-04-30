# Phase 6: Keyboard Polish + Command Palette Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fuzzy command palette (Ctrl+P), a `?` keybinding overlay, and j/k cursor aliases so the dashboard feels native to terminal users.

**Architecture:** Three independent pieces wired together in `app.py`. `WillowCommandProvider` (new file) supplies hits to Textual's built-in `CommandPalette`. `KeymapScreen` (inline in `app.py`) is a modal overlay showing all bindings. j/k are app-level bindings that forward cursor movement to whatever widget currently has focus.

**Tech Stack:** Textual 8.2.4, `textual.command.Provider` / `Hit` / `Hits`, `textual.screen.ModalScreen`, `contextlib.suppress`

---

## File Map

| File | Change |
|------|--------|
| `widgets/command_provider.py` | **Create** — pure helper functions + `WillowCommandProvider` class |
| `tests/test_widgets_command_provider.py` | **Create** — unit tests for pure functions |
| `app.py` | **Modify** — add imports, `KeymapScreen`, `COMMANDS`, BINDINGS, `action_keymap`, `action_cursor_down`, `action_cursor_up` |

---

## Task 1: Pure helper functions + tests

**Files:**
- Create: `widgets/command_provider.py`
- Create: `tests/test_widgets_command_provider.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_widgets_command_provider.py`:

```python
"""tests/test_widgets_command_provider.py
b17: WGRV1  ΔΣ=42
"""
from widgets.command_provider import _nav_hits, _action_hits, _channel_hits


def test_nav_hits_returns_eight():
    assert len(_nav_hits()) == 8


def test_nav_hits_have_required_keys():
    for hit in _nav_hits():
        assert "display" in hit
        assert "text" in hit
        assert "target" in hit


def test_nav_hits_include_home_and_help():
    targets = [h["target"] for h in _nav_hits()]
    assert "home" in targets
    assert "help" in targets


def test_action_hits_have_required_keys():
    for hit in _action_hits():
        assert "display" in hit
        assert "text" in hit
        assert "action" in hit


def test_action_hits_include_refresh_and_quit():
    actions = [h["action"] for h in _action_hits()]
    assert "refresh" in actions
    assert "quit" in actions


def test_channel_hits_returns_channels():
    channels = [{"name": "general"}, {"name": "architecture"}]
    hits = _channel_hits(lambda: channels)
    assert len(hits) == 2


def test_channel_hit_display_format():
    hits = _channel_hits(lambda: [{"name": "general"}])
    assert hits[0]["display"] == "Open #general"


def test_channel_hit_text_contains_name():
    hits = _channel_hits(lambda: [{"name": "general"}])
    assert "general" in hits[0]["text"]


def test_channel_hit_has_channel_key():
    hits = _channel_hits(lambda: [{"name": "general"}])
    assert hits[0]["channel"] == "general"


def test_channel_hits_empty_on_exception():
    def bad():
        raise RuntimeError("db down")
    assert _channel_hits(bad) == []
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python -m pytest tests/test_widgets_command_provider.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'widgets.command_provider'`

- [ ] **Step 3: Create `widgets/command_provider.py` with pure functions**

```python
"""widgets/command_provider.py — Willow command palette provider.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from typing import Callable


_NAV_COMMANDS = [
    ("Go to Home",      "home go home",        "home"),
    ("Go to Chat",      "chat messages grove",  "chat"),
    ("Go to Projects",  "projects tasks",       "projects"),
    ("Go to Knowledge", "knowledge kb atoms",   "knowledge"),
    ("Go to Providers", "providers models api", "providers"),
    ("Go to Health",    "health status vitals", "health"),
    ("Go to Settings",  "settings consent",     "settings"),
    ("Go to Help",      "help docs",            "help"),
]

_ACTION_COMMANDS = [
    ("Refresh", "refresh reload", "refresh"),
    ("Quit",    "quit exit",      "quit"),
]


def _nav_hits() -> list[dict]:
    """Return nav hit dicts — one per top-level tab."""
    return [
        {"display": label, "text": text, "target": target}
        for label, text, target in _NAV_COMMANDS
    ]


def _action_hits() -> list[dict]:
    """Return action hit dicts (refresh, quit)."""
    return [
        {"display": label, "text": text, "action": action}
        for label, text, action in _ACTION_COMMANDS
    ]


def _channel_hits(fetch_fn: Callable) -> list[dict]:
    """Return channel hit dicts. fetch_fn() must return list[dict] with 'name' key."""
    try:
        channels = fetch_fn()
        return [
            {
                "display": f"Open #{ch['name']}",
                "text":    f"open {ch['name']}",
                "channel": ch["name"],
            }
            for ch in channels
        ]
    except Exception:
        return []
```

- [ ] **Step 4: Run tests — all 10 should pass**

```bash
python -m pytest tests/test_widgets_command_provider.py -v
```

Expected:
```
PASSED tests/test_widgets_command_provider.py::test_nav_hits_returns_eight
PASSED tests/test_widgets_command_provider.py::test_nav_hits_have_required_keys
PASSED tests/test_widgets_command_provider.py::test_nav_hits_include_home_and_help
PASSED tests/test_widgets_command_provider.py::test_action_hits_have_required_keys
PASSED tests/test_widgets_command_provider.py::test_action_hits_include_refresh_and_quit
PASSED tests/test_widgets_command_provider.py::test_channel_hits_returns_channels
PASSED tests/test_widgets_command_provider.py::test_channel_hit_display_format
PASSED tests/test_widgets_command_provider.py::test_channel_hit_text_contains_name
PASSED tests/test_widgets_command_provider.py::test_channel_hit_has_channel_key
PASSED tests/test_widgets_command_provider.py::test_channel_hits_empty_on_exception
10 passed
```

- [ ] **Step 5: Commit**

```bash
git add widgets/command_provider.py tests/test_widgets_command_provider.py
git commit -m "feat(palette): pure helper functions + tests for command provider"
```

---

## Task 2: WillowCommandProvider class

**Files:**
- Modify: `widgets/command_provider.py` (append to existing file)

- [ ] **Step 1: Add imports and WillowCommandProvider to `widgets/command_provider.py`**

Append to the bottom of `widgets/command_provider.py` (after `_channel_hits`):

```python
from functools import partial

from textual.command import Hit, Hits, Provider


class WillowCommandProvider(Provider):
    """Supplies nav, action, and channel hits to the Willow command palette."""

    _channel_data: list[dict]

    async def startup(self) -> None:
        """Fetch channels once when the palette opens."""
        try:
            import grove_reader
            self._channel_data = _channel_hits(grove_reader.grove_channels)
        except Exception:
            self._channel_data = []

    async def search(self, query: str) -> Hits:
        """Yield hits matching query across nav targets, actions, and channels."""
        matcher = self.matcher(query)

        for hit in _nav_hits():
            score = matcher.match(hit["text"])
            if score > 0:
                target = hit["target"]
                yield Hit(
                    score=score,
                    match_display=hit["display"],
                    command=partial(self.app.action_nav, target),
                )

        for hit in _action_hits():
            score = matcher.match(hit["text"])
            if score > 0:
                action_name = hit["action"]
                yield Hit(
                    score=score,
                    match_display=hit["display"],
                    command=getattr(self.app, f"action_{action_name}"),
                )

        for hit in getattr(self, "_channel_data", []):
            score = matcher.match(hit["text"])
            if score > 0:
                channel = hit["channel"]
                yield Hit(
                    score=score,
                    match_display=hit["display"],
                    command=partial(self._open_channel, channel),
                )

    async def _open_channel(self, channel: str) -> None:
        from panes.chat import ChatPane
        self.app.action_nav("chat")
        try:
            self.app.query_one(ChatPane)._open_channel(channel)
        except Exception:
            pass
```

- [ ] **Step 2: Verify tests still pass (class addition must not break pure functions)**

```bash
python -m pytest tests/test_widgets_command_provider.py -v
```

Expected: `10 passed`

- [ ] **Step 3: Commit**

```bash
git add widgets/command_provider.py
git commit -m "feat(palette): WillowCommandProvider class — nav, action, channel hits"
```

---

## Task 3: j/k cursor navigation in `app.py`

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add `contextlib` import and `ModalScreen` import**

In `app.py`, change the imports section. Add `from contextlib import suppress` after the stdlib imports, and add `ModalScreen` to the textual.screen import:

```python
# After existing stdlib imports (json, logging, os, pathlib), add:
from contextlib import suppress

# Change the textual.app import line — ModalScreen comes from textual.screen:
from textual.screen import ModalScreen
```

The full import block at the top of `app.py` should now include:

```python
import json
import logging
import os
from contextlib import suppress
from pathlib import Path
```

and:

```python
from textual.screen import ModalScreen
```

- [ ] **Step 2: Add j/k bindings to `WillowGrove.BINDINGS`**

Locate the `BINDINGS` list in `WillowGrove` (currently at line ~303). Change it to:

```python
    BINDINGS = [
        Binding("q",      "quit",            "Quit"),
        Binding("r",      "refresh",         "Refresh"),
        Binding("?",      "keymap",          "Keys"),
        Binding("ctrl+p", "command_palette", "Commands", show=False),
        Binding("j",      "cursor_down",     show=False),
        Binding("k",      "cursor_up",       show=False),
        Binding("1", "nav('home')",      "Home"),
        Binding("2", "nav('chat')",      "Chat"),
        Binding("3", "nav('projects')",  "Projects"),
        Binding("4", "nav('knowledge')", "Knowledge"),
        Binding("5", "nav('providers')", "Providers"),
        Binding("6", "nav('health')",    "Health"),
        Binding("7", "nav('settings')",  "Settings"),
        Binding("8", "nav('help')",      "Help"),
    ]
```

Note: `show=False` removed from `1`-`8` so they appear in the Footer and the `?` overlay.

- [ ] **Step 3: Add `action_cursor_down` and `action_cursor_up` to `WillowGrove`**

Add these two methods to the `WillowGrove` class, after `action_nav`:

```python
    def action_cursor_down(self) -> None:
        from textual.widgets import Input
        focused = self.focused
        if focused and not isinstance(focused, Input):
            with suppress(AttributeError):
                focused.action_cursor_down()

    def action_cursor_up(self) -> None:
        from textual.widgets import Input
        focused = self.focused
        if focused and not isinstance(focused, Input):
            with suppress(AttributeError):
                focused.action_cursor_up()
```

- [ ] **Step 4: Smoke test — launch the app and verify j/k work**

```bash
python3 app.py
```

- Navigate to the Tasks tab (press `3`, then click Tasks in the left panel, or press the number assigned to it).
- Confirm `j` moves cursor down and `k` moves cursor up in the DataTable.
- Confirm typing `j` or `k` in the chat message input does NOT trigger navigation.
- Press `q` to quit.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat(keyboard): j/k cursor aliases for DataTable and ListView"
```

---

## Task 4: KeymapScreen + CommandPalette registration

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add `WillowCommandProvider` import to `app.py`**

Add after the existing widget imports in `app.py`:

```python
from widgets.command_provider import WillowCommandProvider
```

- [ ] **Step 2: Add `KeymapScreen` class to `app.py`**

Add this class **before** the `WillowGrove` class definition:

```python
class KeymapScreen(ModalScreen):
    """Modal overlay showing all keybindings."""

    DEFAULT_CSS = """
    KeymapScreen {
        align: center middle;
    }
    KeymapScreen #keymap-dialog {
        width: 46;
        height: auto;
        background: #161b22;
        border: solid #30363d;
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("?",      "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="keymap-dialog"):
            yield Static(
                "[bold #58a6ff]Keybindings[/]\n\n"
                "[dim]Key         Action[/]\n"
                "[dim]─────────────────────────────[/]\n"
                "[#c9d1d9]1 – 8[/]       [#8b949e]Navigate to tab[/]\n"
                "[#c9d1d9]j / k[/]       [#8b949e]Move cursor down / up[/]\n"
                "[#c9d1d9]Ctrl+P[/]      [#8b949e]Command palette[/]\n"
                "[#c9d1d9]?[/]           [#8b949e]This help[/]\n"
                "[#c9d1d9]r[/]           [#8b949e]Refresh[/]\n"
                "[#c9d1d9]q[/]           [#8b949e]Quit[/]\n"
                "[#c9d1d9]Enter[/]       [#8b949e]Select / open[/]\n"
                "[#c9d1d9]Esc[/]         [#8b949e]Close / back[/]",
                markup=True,
            )
```

- [ ] **Step 3: Add `COMMANDS` and `action_keymap` to `WillowGrove`**

Inside the `WillowGrove` class, add `COMMANDS` as a class variable right after `SUB_TITLE`:

```python
    TITLE     = "Willow Grove"
    SUB_TITLE = f"local-first AI stack — {WILLOW_ROOT}"
    COMMANDS  = {WillowCommandProvider}
```

Add `action_keymap` method to `WillowGrove`, after `action_nav`:

```python
    def action_keymap(self) -> None:
        self.push_screen(KeymapScreen())
```

- [ ] **Step 4: Smoke test — verify ? overlay and Ctrl+P palette**

```bash
python3 app.py
```

- Press `?` → KeymapScreen modal appears with the keybinding table.
- Press `Esc` → modal dismisses.
- Press `?` again → modal appears. Press `?` again → modal dismisses.
- Press `Ctrl+P` → command palette popup appears with fuzzy search.
- Type `ch` → "Go to Chat" should appear. Press Enter → navigates to Chat tab.
- Press `Ctrl+P` again. Type `gen` → "Open #general" should appear (if Postgres is running). Press Enter → navigates to Chat and opens #general.
- Press `Ctrl+P`. Type `ref` → "Refresh" appears. Press Enter → app refreshes, notify "Refreshed" appears.

- [ ] **Step 5: Run full test suite to confirm no regressions**

```bash
python -m pytest tests/ -v --tb=short 2>&1 | tail -20
```

Expected: all existing tests pass plus the 10 new command provider tests.

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat(keyboard): KeymapScreen + command palette registration"
```
