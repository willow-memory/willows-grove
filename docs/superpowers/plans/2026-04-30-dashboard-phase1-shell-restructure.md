# Dashboard Phase 1 — Shell Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current tab-switching `app.py` with a persistent shell layout: NavBar + HeroScene + three-column body (ContextPanel / ContentArea / RightPanel) + ChatStrip, wiring all existing panes into the new structure without modifying their internals.

**Architecture:** Five new widget files provide self-contained building blocks; `app.py` is rewritten to compose them into the new layout. `panes/chat.py` gains a standalone `ChannelList` widget that `ContextPanel` uses alongside the unchanged `ChatPane`. `TabbedContent` is removed entirely. All panes mount once and toggle `display` on `NavChanged`.

**Tech Stack:** Python 3.10+, Textual (existing version in repo), psycopg2, pytest

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `widgets/nav_bar.py` | `NavChanged` message + `NavBar` horizontal nav strip |
| Create | `widgets/hero_scene.py` | `HeroScene` full-width band with `WillowHero` + `GroundStrip` |
| Create | `widgets/chat_strip.py` | `ChatStrip` persistent 1-line bottom bar |
| Create | `widgets/thought_stream.py` | `ThoughtStream` RichLog + `SessionStats` + helper fns |
| Create | `panes/home.py` | `DeskPane`, `HomeGrid`, `ProjectsGrid` placeholders |
| Modify | `panes/chat.py` | Extract `ChannelList` as a standalone widget; `ChatPane` unchanged |
| Rewrite | `app.py` | New `compose()`, CSS, bindings, `on_nav_changed`, `ContextPanel` class, updated `GroveRightPanel` |
| Create | `tests/test_widgets_nav_bar.py` | NavBar pure-logic tests |
| Create | `tests/test_widgets_hero_scene.py` | HeroScene pure-logic tests |
| Create | `tests/test_widgets_chat_strip.py` | ChatStrip pure-logic tests |
| Create | `tests/test_widgets_thought_stream.py` | ThoughtStream pure-logic tests |
| Create | `tests/test_panes_home.py` | Home panes content tests |

---

## Task 1: NavChanged message and NavBar widget

**Files:**
- Create: `widgets/nav_bar.py`
- Create: `tests/test_widgets_nav_bar.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_widgets_nav_bar.py
"""tests/test_widgets_nav_bar.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.nav_bar import NAV_TARGETS, NavChanged

def test_nav_targets_exact():
    assert NAV_TARGETS == ["home", "chat", "projects", "knowledge",
                           "providers", "health", "settings", "help"]

def test_nav_targets_no_internal_panes():
    for forbidden in ("tasks", "agents", "routing", "skills", "logs", "overview"):
        assert forbidden not in NAV_TARGETS

def test_nav_changed_target():
    msg = NavChanged("chat")
    assert msg.target == "chat"

def test_nav_changed_all_targets():
    for t in NAV_TARGETS:
        msg = NavChanged(t)
        assert msg.target == t
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python -m pytest tests/test_widgets_nav_bar.py -v
```

Expected: `ModuleNotFoundError` — `widgets/nav_bar.py` does not exist.

- [ ] **Step 3: Create `widgets/nav_bar.py`**

```python
"""widgets/nav_bar.py — NavBar: horizontal nav strip + NavChanged message.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Static


NAV_TARGETS: list[str] = [
    "home", "chat", "projects", "knowledge",
    "providers", "health", "settings", "help",
]


class NavChanged(Message):
    def __init__(self, target: str) -> None:
        self.target = target
        super().__init__()


class NavBar(Horizontal):
    """Single-row nav strip. Emits NavChanged on click or highlight()."""

    DEFAULT_CSS = """
    NavBar {
        height: 1;
        background: #161b22;
        border-bottom: solid #30363d;
        padding: 0 1;
    }
    NavBar Button {
        height: 1;
        min-width: 0;
        border: none;
        background: transparent;
        color: #8b949e;
        padding: 0 1;
    }
    NavBar Button:hover {
        background: #21262d;
        color: #c9d1d9;
    }
    NavBar Button.-active-nav {
        color: #58a6ff;
        text-style: bold;
    }
    NavBar #nav-logo {
        color: #3fb950;
        text-style: bold;
        padding: 0 2 0 0;
    }
    NavBar #nav-vitals {
        width: 1fr;
        text-align: right;
        color: #8b949e;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("◆", id="nav-logo")
        for target in NAV_TARGETS:
            yield Button(target.capitalize(), id=f"nav-{target}")
        yield Static("", id="nav-vitals")

    def on_mount(self) -> None:
        self.highlight("home")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id or ""
        if btn_id == "nav-logo":
            self.highlight("home")
            self.post_message(NavChanged("home"))
        elif btn_id.startswith("nav-"):
            target = btn_id[4:]
            if target in NAV_TARGETS:
                self.highlight(target)
                self.post_message(NavChanged(target))

    def highlight(self, target: str) -> None:
        """Update visual active state without emitting NavChanged."""
        for t in NAV_TARGETS:
            try:
                btn = self.query_one(f"#nav-{t}", Button)
                if t == target:
                    btn.add_class("-active-nav")
                else:
                    btn.remove_class("-active-nav")
            except Exception:
                pass

    def set_vitals(self, text: str) -> None:
        try:
            self.query_one("#nav-vitals", Static).update(text)
        except Exception:
            pass
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python -m pytest tests/test_widgets_nav_bar.py -v
```

Expected: 4 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add widgets/nav_bar.py tests/test_widgets_nav_bar.py
git commit -m "feat(nav): NavBar widget + NavChanged message"
```

---

## Task 2: HeroScene widget

**Files:**
- Create: `widgets/hero_scene.py`
- Create: `tests/test_widgets_hero_scene.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_widgets_hero_scene.py
"""tests/test_widgets_hero_scene.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.hero_scene import GROUND_LINE, make_ground_content

def test_ground_line_contains_tilde():
    assert "~" in GROUND_LINE

def test_make_ground_content_contains_grass():
    content = make_ground_content()
    assert "|" in content

def test_make_ground_content_is_string():
    assert isinstance(make_ground_content(), str)

def test_make_ground_content_contains_flower():
    content = make_ground_content()
    assert "✿" in content
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python -m pytest tests/test_widgets_hero_scene.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Create `widgets/hero_scene.py`**

```python
"""widgets/hero_scene.py — HeroScene: full-width band with willow tree + ground strip.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from .hero import WillowHero


GROUND_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

_SCENE_ELEMENTS = [
    "✿", "|", "✿", "|", "⬡", "|", "♟", "|", "✿", "|",
    "⌁", "|", "✦", "|", "✿", "|", "⬡", "|", "♞", "|", "✿",
]


def make_ground_content() -> str:
    """Return the static ground strip text for Phase 1."""
    scene_row = "  " + " ".join(_SCENE_ELEMENTS) + "  "
    return f"{scene_row}\n  {GROUND_LINE}"


class GroundStrip(Static):
    """Phase 1: static scene strip. Phase 1.5 adds animation."""

    DEFAULT_CSS = """
    GroundStrip {
        width: 1fr;
        height: 10;
        color: #3fb950;
        padding: 2 2 0 2;
        content-align: left bottom;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(make_ground_content(), **kwargs)


class HeroScene(Horizontal):
    """Full-width band: WillowHero (left) + GroundStrip (center, 1fr)."""

    DEFAULT_CSS = """
    HeroScene {
        height: 10;
        background: #0d1117;
        border-bottom: solid #30363d;
    }
    HeroScene WillowHero {
        width: 28;
    }
    """

    def compose(self) -> ComposeResult:
        yield WillowHero()
        yield GroundStrip()
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python -m pytest tests/test_widgets_hero_scene.py -v
```

Expected: 4 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add widgets/hero_scene.py tests/test_widgets_hero_scene.py
git commit -m "feat(hero): HeroScene widget with GroundStrip placeholder"
```

---

## Task 3: Home panes — DeskPane, HomeGrid, ProjectsGrid

**Files:**
- Create: `panes/home.py`
- Create: `tests/test_panes_home.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_panes_home.py
"""tests/test_panes_home.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from panes.home import DESK_PLACEHOLDER, HOMEGRID_PLACEHOLDER, PROJECTS_PLACEHOLDER

def test_desk_placeholder_is_string():
    assert isinstance(DESK_PLACEHOLDER, str)
    assert len(DESK_PLACEHOLDER) > 0

def test_homegrid_placeholder_mentions_phase():
    assert "Phase" in HOMEGRID_PLACEHOLDER or "home" in HOMEGRID_PLACEHOLDER.lower()

def test_projects_placeholder_lists_internal_panes():
    text = PROJECTS_PLACEHOLDER.lower()
    for pane in ("tasks", "agents", "routing", "skills", "logs"):
        assert pane in text, f"Expected '{pane}' in ProjectsGrid placeholder"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python -m pytest tests/test_panes_home.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Create `panes/home.py`**

```python
"""panes/home.py — Placeholder panes for Home, HomeGrid, and Projects.
b17: WGRV1  ΔΣ=42
"""
from textual.widgets import Static


DESK_PLACEHOLDER = (
    "[ The Desk ]\n\n"
    "  ⚡ Needs Attention\n"
    "  ▶ In Progress\n"
    "  ✓ Done Today\n"
    "  📅 Calendar\n\n"
    "  Phase 2 fills this with live data."
)

HOMEGRID_PLACEHOLDER = (
    "[ Home Grid ]\n\n"
    "  Card grid launcher — Phase 3.\n\n"
    "  Each card opens an app or shows a live data feed.\n"
    "  Cards defined in cards.py are loaded here."
)

PROJECTS_PLACEHOLDER = (
    "[ Projects ]\n\n"
    "  Click a card to open the pane:\n\n"
    "  [Tasks]      [Agents]     [Routing]\n"
    "  [Skills]     [Logs]\n\n"
    "  Phase 3 adds live card grid from cards.py."
)


class DeskPane(Static):
    """Left column for Home. Phase 2 fills with live calendar/tasks/email."""

    DEFAULT_CSS = """
    DeskPane {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(DESK_PLACEHOLDER, **kwargs)


class HomeGrid(Static):
    """Center area for Home. Phase 3 replaces with live Textual card grid."""

    DEFAULT_CSS = """
    HomeGrid {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(HOMEGRID_PLACEHOLDER, **kwargs)


class ProjectsGrid(Static):
    """Center area for Projects nav. Phase 3 replaces with live card grid."""

    DEFAULT_CSS = """
    ProjectsGrid {
        width: 1fr;
        height: 1fr;
        padding: 1 2;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(PROJECTS_PLACEHOLDER, **kwargs)
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python -m pytest tests/test_panes_home.py -v
```

Expected: 3 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add panes/home.py tests/test_panes_home.py
git commit -m "feat(panes): DeskPane, HomeGrid, ProjectsGrid placeholder panes"
```

---

## Task 4: ChatStrip widget

**Files:**
- Create: `widgets/chat_strip.py`
- Create: `tests/test_widgets_chat_strip.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_widgets_chat_strip.py
"""tests/test_widgets_chat_strip.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.chat_strip import format_strip_line, truncate_content

def test_format_strip_line_basic():
    line = format_strip_line("general", "hanuman", "hello world", 80)
    assert "#general" in line
    assert "hanuman" in line
    assert "hello world" in line
    assert "▶ open" in line

def test_format_strip_line_truncates_long_content():
    long_msg = "x" * 200
    line = format_strip_line("general", "hanuman", long_msg, 80)
    assert len(line) <= 80
    assert "…" in line

def test_format_strip_line_empty_content():
    line = format_strip_line("general", "hanuman", "", 80)
    assert "#general" in line
    assert "▶ open" in line

def test_truncate_content_short():
    assert truncate_content("hello", 20) == "hello"

def test_truncate_content_exact():
    assert truncate_content("hello", 5) == "hello"

def test_truncate_content_long():
    result = truncate_content("hello world", 8)
    assert len(result) <= 8
    assert result.endswith("…")
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python -m pytest tests/test_widgets_chat_strip.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Create `widgets/chat_strip.py`**

```python
"""widgets/chat_strip.py — ChatStrip: persistent 1-line bottom bar.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os

from textual.widgets import Static

import grove_reader


def truncate_content(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def format_strip_line(channel: str, sender: str, content: str, width: int) -> str:
    prefix = f"#{channel}  {sender}: "
    suffix = "  ▶ open"
    max_content = width - len(prefix) - len(suffix)
    if max_content < 4:
        return truncate_content(f"{prefix}{content}{suffix}", width)
    return f"{prefix}{truncate_content(content, max_content)}{suffix}"


class ChatStrip(Static):
    """Always-visible 1-line chat context bar at the bottom of the screen."""

    DEFAULT_CSS = """
    ChatStrip {
        height: 1;
        background: #161b22;
        border-top: solid #30363d;
        padding: 0 1;
        color: #8b949e;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self._channel = ""
        self._sender  = ""
        self._content = ""

    def on_mount(self) -> None:
        self.set_interval(10, self._poll)
        self._poll()

    def _poll(self) -> None:
        try:
            channels = grove_reader.grove_channels()
            if not channels:
                return
            ch = channels[0]["name"]
            msgs = grove_reader.grove_messages(ch, limit=1)
            if msgs:
                m = msgs[-1]
                self._channel = ch
                self._sender  = m.get("sender", "?")
                self._content = m.get("content", "")
                self._redraw()
        except Exception:
            pass

    def update_channel(self, channel: str) -> None:
        """Called by app when Chat pane changes active channel."""
        self._channel = channel
        self._redraw()

    def _redraw(self) -> None:
        width = self.size.width or 80
        line = format_strip_line(
            self._channel or "general",
            self._sender  or "—",
            self._content or "",
            width,
        )
        self.update(line)
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python -m pytest tests/test_widgets_chat_strip.py -v
```

Expected: 6 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add widgets/chat_strip.py tests/test_widgets_chat_strip.py
git commit -m "feat(chat-strip): persistent 1-line bottom chat bar"
```

---

## Task 5: ThoughtStream widget + session stats helpers

**Files:**
- Create: `widgets/thought_stream.py`
- Create: `tests/test_widgets_thought_stream.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_widgets_thought_stream.py
"""tests/test_widgets_thought_stream.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.thought_stream import is_agent_sender, parse_session_stats, KNOWN_AGENTS

def test_known_agents_not_empty():
    assert len(KNOWN_AGENTS) > 0

def test_is_agent_sender_known():
    for name in ("hanuman", "heimdallr", "ganesha"):
        assert is_agent_sender(name), f"{name} should be agent"

def test_is_agent_sender_human():
    assert not is_agent_sender("sean")
    assert not is_agent_sender("unknown_person")

def test_is_agent_sender_case_insensitive():
    assert is_agent_sender("HANUMAN")
    assert is_agent_sender("Heimdallr")

def test_parse_session_stats_full():
    data = {
        "written_at": "2026-04-30T09:00:00",
        "open_flags": 2,
        "handoff_summary": "Worked on dashboard.",
    }
    result = parse_session_stats(data)
    assert "flags" in result or "open" in result.lower() or "2" in result

def test_parse_session_stats_missing_keys():
    result = parse_session_stats({})
    assert isinstance(result, str)

def test_parse_session_stats_none():
    result = parse_session_stats(None)
    assert isinstance(result, str)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python -m pytest tests/test_widgets_thought_stream.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Create `widgets/thought_stream.py`**

```python
"""widgets/thought_stream.py — ThoughtStream: live agent message feed + SessionStats.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from textual.widgets import RichLog, Static

import grove_reader


KNOWN_AGENTS: frozenset[str] = frozenset([
    "hanuman", "heimdallr", "ganesha", "vishwakarma", "loki", "jeles",
])

_SESSION_ANCHOR = Path.home() / ".willow" / "session_anchor.json"


def is_agent_sender(sender: str, agents: frozenset[str] = KNOWN_AGENTS) -> bool:
    return sender.lower() in agents


def parse_session_stats(data: dict | None) -> str:
    if not data:
        return "[dim]no session data[/]"
    parts: list[str] = []
    written_at = data.get("written_at")
    if written_at:
        try:
            start = datetime.fromisoformat(written_at.replace("Z", "+00:00"))
            now   = datetime.now(tz=timezone.utc)
            delta = now - start.astimezone(timezone.utc)
            mins  = int(delta.total_seconds() // 60)
            parts.append(f"active {mins}m")
        except Exception:
            pass
    flags = data.get("open_flags")
    if flags is not None:
        color = "yellow" if flags > 0 else "green"
        parts.append(f"[{color}]{flags} flags[/{color}]")
    return "  ".join(parts) if parts else "[dim]session active[/]"


class ThoughtStream(RichLog):
    """Live feed of agent messages from grove.messages. Polls every 10s."""

    DEFAULT_CSS = """
    ThoughtStream {
        height: 6;
        border: round #30363d;
        margin: 1 0 0 0;
        padding: 0 1;
        overflow-y: auto;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(highlight=False, markup=True, wrap=True, **kwargs)
        self._last_id: int = 0

    def on_mount(self) -> None:
        self.set_interval(10, self._poll)
        self._poll()

    def _poll(self) -> None:
        try:
            msgs = grove_reader.grove_messages_all_agents(
                known_agents=KNOWN_AGENTS,
                last_id=self._last_id,
                limit=20,
            )
            for m in msgs:
                sender  = m.get("sender", "?")
                content = m.get("content", "")
                if len(content) > 60:
                    content = content[:59] + "…"
                self.write(f"[dim cyan]{sender}[/]  {content}")
                self._last_id = max(self._last_id, m.get("id", 0))
        except Exception:
            pass


class SessionStats(Static):
    """Session stats line: active time + open flag count. Refreshes every 30s."""

    DEFAULT_CSS = """
    SessionStats {
        height: 1;
        color: #8b949e;
        padding: 0 1;
        margin-top: 1;
    }
    """

    def on_mount(self) -> None:
        self.set_interval(30, self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        try:
            data = json.loads(_SESSION_ANCHOR.read_text())
        except Exception:
            data = None
        self.update(parse_session_stats(data))
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python -m pytest tests/test_widgets_thought_stream.py -v
```

Expected: 7 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add widgets/thought_stream.py tests/test_widgets_thought_stream.py
git commit -m "feat(thought-stream): agent feed RichLog + SessionStats widget"
```

---

## Task 6: Add grove_messages_all_agents to grove_reader

The `ThoughtStream` calls `grove_reader.grove_messages_all_agents()` — this function doesn't exist yet. Add it.

**Files:**
- Modify: `grove_reader.py`
- Modify: `tests/test_grove_reader.py`

- [ ] **Step 1: Read current grove_reader to find the right insertion point**

```bash
grep -n "def grove_" /home/sean-campbell/github/safe-app-willow-grove/grove_reader.py
```

- [ ] **Step 2: Write the failing test**

Add to `tests/test_grove_reader.py` (append after existing tests):

```python
def test_grove_messages_all_agents_returns_list():
    """grove_messages_all_agents must return a list even when DB is unreachable."""
    from grove_reader import grove_messages_all_agents
    from widgets.thought_stream import KNOWN_AGENTS
    # No DB needed — function must handle exceptions gracefully
    # If DB is up, it should return a list of dicts; if down, empty list
    result = grove_messages_all_agents(known_agents=KNOWN_AGENTS, last_id=0, limit=5)
    assert isinstance(result, list)
```

- [ ] **Step 3: Run the test to confirm it fails**

```bash
python -m pytest tests/test_grove_reader.py::test_grove_messages_all_agents_returns_list -v
```

Expected: `AttributeError` — `grove_messages_all_agents` does not exist.

- [ ] **Step 4: Add `grove_messages_all_agents` to `grove_reader.py`**

Read `grove_reader.py` first to find the correct location. Then append this function at the end of the file, before any `if __name__` block:

```python
def grove_messages_all_agents(
    known_agents: "frozenset[str]",
    last_id: int = 0,
    limit: int = 20,
) -> "list[dict]":
    """Return recent grove.messages from known agent senders, id > last_id."""
    try:
        import psycopg2, os
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        cur = conn.cursor()
        placeholders = ", ".join(["%s"] * len(known_agents))
        cur.execute(
            f"SELECT id, sender, content, created_at"
            f" FROM grove.messages"
            f" WHERE sender = ANY(%s::text[]) AND id > %s"
            f" ORDER BY id DESC LIMIT %s",
            (list(known_agents), last_id, limit),
        )
        rows = cur.fetchall()
        conn.close()
        return [
            {"id": r[0], "sender": r[1], "content": r[2], "created_at": r[3]}
            for r in reversed(rows)
        ]
    except Exception:
        return []
```

- [ ] **Step 5: Run the test — confirm it passes**

```bash
python -m pytest tests/test_grove_reader.py -v
```

Expected: all tests PASSED (including the new one).

- [ ] **Step 6: Commit**

```bash
git add grove_reader.py tests/test_grove_reader.py
git commit -m "feat(grove-reader): add grove_messages_all_agents for ThoughtStream"
```

---

## Task 7: Extract ChannelList from ChatPane

**Files:**
- Modify: `panes/chat.py`

The goal: create a standalone `ChannelList` widget that can be used independently by `ContextPanel`. `ChatPane` continues to work exactly as before — its internal sidebar is not removed, but it now uses `ChannelList` internally.

- [ ] **Step 1: Run existing ChatPane tests to establish baseline**

```bash
python -m pytest tests/test_panes_chat.py -v
```

All 5 tests should PASS. Note the count — they must all pass after the refactor too.

- [ ] **Step 2: Read the current ChatPane sidebar code**

Read `panes/chat.py` lines 130–170 to understand the current sidebar structure before modifying.

- [ ] **Step 3: Add `ChannelList` class to `panes/chat.py`**

Insert after the `ChannelItem` class (after line ~76) and before the `ChatPane` class definition. Add this class:

```python
class ChannelList(Vertical):
    """Standalone channel list widget — usable by ContextPanel independently of ChatPane."""

    DEFAULT_CSS = """
    ChannelList {
        width: 1fr;
        height: 1fr;
        background: $panel;
    }
    ChannelList #cl-label {
        padding: 1 1 0 1;
        color: $text-muted;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._channels: list[dict] = []
        self._cursors:  dict       = {}
        self._cursors_initialized  = False

    def compose(self):
        yield Label("CHANNELS", id="cl-label")
        yield ListView(id="cl-channel-list")

    def on_mount(self) -> None:
        self.set_interval(5, self._poll)
        self._poll()

    def _poll(self) -> None:
        try:
            channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            if not self._cursors_initialized:
                for ch in channels:
                    self._cursors[ch["name"]] = ch.get("max_id", 0)
                self._cursors_initialized = True
                channels = grove_reader.grove_channels(last_seen_ids=self._cursors)
            new = sort_channels(channels)
            new_snap = [(c["name"], c.get("unread", 0)) for c in new]
            old_snap = [(c["name"], c.get("unread", 0)) for c in self._channels]
            self._channels = new
            if new_snap != old_snap:
                lst = self.query_one("#cl-channel-list", ListView)
                lst.clear()
                for ch in self._channels:
                    lst.append(ChannelItem(ch))
        except Exception:
            pass
```

- [ ] **Step 4: Run existing tests — confirm no regressions**

```bash
python -m pytest tests/test_panes_chat.py -v
```

Expected: same 5 tests PASS as in Step 1.

- [ ] **Step 5: Confirm ChannelList is importable**

```bash
python -c "from panes.chat import ChannelList; print('ok')"
```

Expected: prints `ok`.

- [ ] **Step 6: Commit**

```bash
git add panes/chat.py
git commit -m "feat(chat): extract ChannelList as standalone widget for ContextPanel"
```

---

## Task 8: Rewrite app.py

This is the central integration task. It replaces the `TabbedContent` layout with the new persistent shell.

**Files:**
- Rewrite: `app.py`

- [ ] **Step 1: Run all tests to establish baseline before the rewrite**

```bash
python -m pytest tests/ -v --tb=short 2>&1 | tail -20
```

Record the number of passing tests. After the rewrite, this number must not decrease.

- [ ] **Step 2: Confirm the app currently starts**

```bash
python3 -c "import app; print('imports ok')"
```

- [ ] **Step 3: Write the new `app.py`**

Replace the entire file with:

```python
#!/usr/bin/env python3
"""
app.py — Willow Grove (Textual dashboard).
b17: WGRV1  ΔΣ=42

Run: python3 app.py
"""
import json
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Label, Rule, Static

from panes.chat      import ChatPane, ChannelList, sender_color
from panes.tasks     import TasksPane, fetch_backfill_progress, fetch_tasks
from panes.agents    import AgentsPane
from panes.routing   import RoutingPane
from panes.knowledge import KnowledgePane
from panes.providers import ProvidersPane
from panes.skills    import SkillsPane
from panes.health    import HealthPane
from panes.logs      import LogsPane
from panes.home      import DeskPane, HomeGrid, ProjectsGrid

from widgets.nav_bar      import NavBar, NavChanged, NAV_TARGETS
from widgets.hero_scene   import HeroScene
from widgets.chat_strip   import ChatStrip
from widgets.thought_stream import ThoughtStream, SessionStats

import grove_reader

WILLOW_ROOT = Path(os.environ.get("WILLOW_ROOT", Path.home() / "github" / "willow-1.9"))


def _pg_ok() -> bool:
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        conn.close()
        return True
    except Exception:
        return False


class VitalsBar(Static):
    def on_mount(self) -> None:
        self.set_interval(15, self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        pg    = "[green]pg:up[/]" if _pg_ok() else "[red]pg:down[/]"
        bp    = fetch_backfill_progress()
        if bp and bp.get("table") != "done":
            pct   = bp.get("pct", 0)
            embed = f"  embed [yellow]{pct:.1f}%[/]"
        else:
            embed = "  embed [green]done[/]"
        model = os.environ.get("WILLOW_MODEL", "claude-sonnet-4-6")
        self.update(f" [dim]model:[/] {model}  {pg}{embed}")


class GroveRightPanel(Container):
    def compose(self) -> ComposeResult:
        yield Label("TASKS", id="rp-tasks-label")
        yield Static("", id="rp-task-counts")
        yield Rule()
        yield Label("AGENTS", id="rp-agents-label")
        yield Static("", id="rp-agents-list")
        yield Rule()
        yield Label("THOUGHTS", id="rp-thoughts-label")
        yield ThoughtStream(id="rp-thought-stream")
        yield SessionStats(id="rp-session-stats")

    def on_mount(self) -> None:
        self.set_interval(10, self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        data = fetch_tasks()
        self._safe_update(
            "#rp-task-counts",
            f"[yellow]{data['running']}[/] running\n"
            f"[dim]{data['pending']}[/] pending\n"
            f"[green]{data['done']}[/] done",
        )
        lines = []
        try:
            for a in grove_reader.grove_agents():
                sender   = a["sender"]
                age_secs = a.get("age_secs", 9999)
                dot = "[green]●[/]" if age_secs < 120 else "[yellow]●[/]" if age_secs < 900 else "[dim]●[/]"
                color = sender_color(sender)
                lines.append(f"{dot} [{color}]{sender}[/]")
        except Exception:
            pass
        self._safe_update("#rp-agents-list", "\n".join(lines) or "[dim]no agents[/]")

    def _safe_update(self, selector: str, text: str) -> None:
        try:
            self.query_one(selector, Static).update(text)
        except Exception:
            pass


class ContextPanel(Vertical):
    """Left column — swaps content based on active nav target."""

    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-home")
        yield ChannelList(id="ctx-chat")

    def on_mount(self) -> None:
        self._show_target("home")

    def on_nav_changed(self, event: NavChanged) -> None:
        self._show_target(event.target)

    def _show_target(self, target: str) -> None:
        ctx_map = {
            "home": "#ctx-home",
            "chat": "#ctx-chat",
        }
        for widget_id in ctx_map.values():
            try:
                self.query_one(widget_id).display = False
            except Exception:
                pass
        active_id = ctx_map.get(target)
        if active_id:
            try:
                self.query_one(active_id).display = True
            except Exception:
                pass


# IDs for all content panes indexed by nav target
_CONTENT_PANES: dict[str, str] = {
    "home":      "#pane-home",
    "chat":      "#pane-chat",
    "projects":  "#pane-projects",
    "knowledge": "#pane-knowledge",
    "providers": "#pane-providers",
    "health":    "#pane-health",
    "settings":  "#pane-settings",
    "help":      "#pane-help",
}

# Internal panes reachable via Projects — not in top nav
_INTERNAL_PANES: list[str] = [
    "#pane-tasks", "#pane-agents", "#pane-routing",
    "#pane-skills", "#pane-logs",
]


class WillowGrove(App):
    CSS = """
    Screen { background: #0d1117; }

    Footer { background: #161b22; }

    #main-area {
        height: 1fr;
    }

    ContextPanel {
        width: 26;
        background: #161b22;
        border-right: solid #30363d;
    }

    #content-area {
        width: 1fr;
        height: 1fr;
    }

    GroveRightPanel {
        width: 30;
        background: #161b22;
        border-left: solid #30363d;
        padding: 0 1;
    }

    GroveRightPanel #rp-tasks-label,
    GroveRightPanel #rp-agents-label,
    GroveRightPanel #rp-thoughts-label {
        color: #58a6ff;
        text-style: bold;
        padding: 0 0 1 0;
    }

    GroveRightPanel #rp-task-counts,
    GroveRightPanel #rp-agents-list {
        padding: 0 0 0 1;
        color: #8b949e;
    }

    GroveRightPanel #rp-agents-list {
        height: auto;
    }

    Rule { margin: 1 0; color: #30363d; }

    WillowHero {
        height: 8;
        content-align: center middle;
        color: #3fb950;
        text-style: bold;
    }

    #pane-settings, #pane-help {
        padding: 2;
        color: #8b949e;
    }

    DataTable {
        height: 1fr;
        margin: 0 2;
    }

    #skill-detail {
        height: 12;
        margin: 1 2;
        border: round #30363d;
        padding: 1;
        color: #8b949e;
    }

    Log {
        margin: 0 2;
        height: 1fr;
        border: round #30363d;
    }

    ChatPane #channel-sidebar {
        width: 26;
        background: #161b22;
        border-right: solid #30363d;
    }

    ChatPane #sidebar-label {
        padding: 1 1 0 1;
        color: #8b949e;
        text-style: bold;
    }

    ChatPane #channel-title {
        background: #161b22;
        color: #58a6ff;
        border-bottom: solid #30363d;
    }

    ChatPane #msg-log {
        height: 1fr;
        padding: 1 2;
    }

    StatusRow {
        padding: 0 4;
        height: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit",            "Quit"),
        Binding("r", "refresh",         "Refresh"),
        Binding("1", "nav('home')",      "Home",      show=False),
        Binding("2", "nav('chat')",      "Chat",      show=False),
        Binding("3", "nav('projects')",  "Projects",  show=False),
        Binding("4", "nav('knowledge')", "Knowledge", show=False),
        Binding("5", "nav('providers')", "Providers", show=False),
        Binding("6", "nav('health')",    "Health",    show=False),
        Binding("7", "nav('settings')",  "Settings",  show=False),
        Binding("8", "nav('help')",      "Help",      show=False),
    ]

    TITLE     = "Willow Grove"
    SUB_TITLE = f"local-first AI stack — {WILLOW_ROOT}"

    def compose(self) -> ComposeResult:
        yield NavBar(id="nav-bar")
        yield HeroScene(id="hero-scene")
        with Horizontal(id="main-area"):
            yield ContextPanel(id="context-panel")
            with Vertical(id="content-area"):
                yield HomeGrid(id="pane-home")
                yield ChatPane(id="pane-chat")
                yield ProjectsGrid(id="pane-projects")
                yield KnowledgePane(id="pane-knowledge")
                yield ProvidersPane(id="pane-providers")
                yield HealthPane(id="pane-health")
                yield Static("[ Settings — coming soon ]", id="pane-settings")
                yield Static("[ Help — coming soon ]", id="pane-help")
                # internal panes — reachable via Projects card, not top nav
                yield TasksPane(id="pane-tasks")
                yield AgentsPane(id="pane-agents")
                yield RoutingPane(id="pane-routing")
                yield SkillsPane(id="pane-skills")
                yield LogsPane(id="pane-logs")
            yield GroveRightPanel(id="right-panel")
        yield ChatStrip(id="chat-strip")
        yield Footer()

    def on_mount(self) -> None:
        self._hide_all_content_panes()
        self._show_content_pane("home")
        self._do_refresh()
        self.set_interval(30, self._do_refresh)

    def _hide_all_content_panes(self) -> None:
        all_ids = list(_CONTENT_PANES.values()) + _INTERNAL_PANES
        for pane_id in all_ids:
            try:
                self.query_one(pane_id).display = False
            except Exception:
                pass

    def _show_content_pane(self, target: str) -> None:
        pane_id = _CONTENT_PANES.get(target)
        if pane_id:
            try:
                self.query_one(pane_id).display = True
            except Exception:
                pass

    def on_nav_changed(self, event: NavChanged) -> None:
        self._hide_all_content_panes()
        self._show_content_pane(event.target)

    def _do_refresh(self) -> None:
        for pane_id, pane_cls in [
            ("#pane-providers", ProvidersPane),
            ("#pane-skills",    SkillsPane),
            ("#pane-logs",      LogsPane),
        ]:
            try:
                self.query_one(pane_id, pane_cls).refresh_data()
            except Exception:
                pass

    def action_refresh(self) -> None:
        self._do_refresh()
        try:
            self.query_one(GroveRightPanel)._refresh()
        except Exception:
            pass
        self.notify("Refreshed")

    def action_nav(self, target: str) -> None:
        try:
            self.query_one(NavBar).highlight(target)
        except Exception:
            pass
        self.post_message(NavChanged(target))


if __name__ == "__main__":
    WillowGrove().run()
```

- [ ] **Step 4: Confirm imports work**

```bash
python3 -c "import app; print('imports ok')"
```

Expected: `imports ok` with no errors.

- [ ] **Step 5: Run all tests — confirm no regressions**

```bash
python -m pytest tests/ -v --tb=short 2>&1 | tail -30
```

Expected: same or greater number of PASSED tests as the baseline from Step 1. Zero new failures.

- [ ] **Step 6: Start the app and verify the layout**

```bash
python3 app.py
```

Check each item in the definition of done:
- [ ] App starts without error
- [ ] NavBar shows: ◆ Home Chat Projects Knowledge Providers Health Settings Help
- [ ] Press `1` → HomeGrid placeholder shows in center
- [ ] Press `2` → ChatPane shows (with its channel sidebar + message area)
- [ ] Press `3` → ProjectsGrid placeholder with Tasks/Agents/Routing/Skills/Logs listed
- [ ] Press `4`–`8` → each respective pane shows
- [ ] HeroScene visible below NavBar — animated WillowHero tree + ground strip
- [ ] ContextPanel (left, width ~26) shows DeskPane on Home, ChannelList on Chat
- [ ] RightPanel (right, width ~30) shows Tasks + Agents + THOUGHTS (ThoughtStream) + SessionStats
- [ ] ChatStrip visible at bottom (1 line)
- [ ] `q` quits, `r` refreshes

- [ ] **Step 7: Commit**

```bash
git add app.py
git commit -m "feat(app): Phase 1 shell — NavBar+HeroScene+3-col layout+ChatStrip"
```

---

## Task 9: Wire VitalsBar into NavBar

`VitalsBar` currently was a standalone widget yielded by the app. In the new layout it belongs in `NavBar`'s right side (`#nav-vitals`). Wire it up.

**Files:**
- Modify: `app.py` (small addition — call `nav_bar.set_vitals()` from VitalsBar)
- Modify: `widgets/nav_bar.py` (already has `set_vitals` method from Task 1)

- [ ] **Step 1: Update `VitalsBar._refresh` to push text to NavBar**

In `app.py`, change `VitalsBar._refresh`:

```python
class VitalsBar(Static):
    def on_mount(self) -> None:
        self.set_interval(15, self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        pg    = "[green]pg:up[/]" if _pg_ok() else "[red]pg:down[/]"
        bp    = fetch_backfill_progress()
        if bp and bp.get("table") != "done":
            pct   = bp.get("pct", 0)
            embed = f"embed [yellow]{pct:.1f}%[/]"
        else:
            embed = "embed [green]done[/]"
        model = os.environ.get("WILLOW_MODEL", "claude-sonnet-4-6")
        text  = f"[dim]{model}[/]  {pg}  {embed}"
        self.update(text)
        try:
            self.app.query_one(NavBar).set_vitals(text)
        except Exception:
            pass
```

Remove `VitalsBar` from `compose()` — it is now a background refresh source only, mounted as an invisible helper. Or keep it mounted with `display: none`.

Actually, the cleanest approach: keep `VitalsBar` as an internal `Static` mounted with `display: False` (so it still ticks) and push its text to NavBar's `#nav-vitals`. Add to `compose()`:

```python
yield VitalsBar(id="vitals-source")  # hidden — pushes to NavBar
```

And add to CSS:

```css
#vitals-source { display: none; }
```

- [ ] **Step 2: Test the vitals text appears in the nav bar right side**

```bash
python3 app.py
```

The right side of the NavBar should show `claude-sonnet-4-6  pg:up  embed done` (or equivalent).

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat(vitals): wire VitalsBar refresh into NavBar right side"
```

---

## Task 10: Final smoke test + definition-of-done verification

- [ ] **Step 1: Run the full test suite**

```bash
python -m pytest tests/ -v 2>&1 | tail -30
```

Expected: all pre-existing tests pass + all new tests pass. Zero failures.

- [ ] **Step 2: Verify definition of done**

```bash
python3 app.py
```

Walk through the checklist from the spec:

- [ ] `python3 app.py` starts without error
- [ ] All 8 nav targets accessible, content switches correctly (keys 1-8)
- [ ] Internal panes reachable via Projects (press 3, note the listed panes)
- [ ] Hero scene renders with animated WillowHero + static ground strip
- [ ] ContextPanel shows DeskPane on Home (press 1), ChannelList on Chat (press 2)
- [ ] RightPanel includes ThoughtStream and session stats
- [ ] ChatStrip shows last Grove message, 1 line at bottom
- [ ] No regressions in ChatPane behaviour (press 2, select a channel, confirm messages load)
- [ ] Keyboard bindings: `q` quits, `r` refreshes, `1`-`8` nav

- [ ] **Step 3: Final commit**

```bash
git add -p  # stage any remaining changes
git commit -m "chore(phase1): final smoke test pass — shell restructure complete"
```

---

## Self-Review

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| NavBar with 8 items, emits NavChanged | Task 1 |
| HeroScene full-width band, WillowHero + GroundStrip | Task 2 |
| DeskPane, HomeGrid, ProjectsGrid placeholders | Task 3 |
| ChatStrip persistent 1-line bottom bar | Task 4 |
| ThoughtStream + SessionStats in RightPanel | Task 5 |
| grove_messages_all_agents for ThoughtStream | Task 6 |
| ChannelList extraction from ChatPane | Task 7 |
| app.py rewrite — new compose(), CSS, bindings | Task 8 |
| VitalsBar inlined into NavBar right side | Task 9 |
| Keyboard bindings 1-8, q, r preserved | Task 8 |
| ContextPanel swaps on NavChanged | Task 8 |
| ContentArea display toggling | Task 8 |
| No regressions in ChatPane | Tasks 7, 8, 10 |

**Type consistency check:**

- `NavChanged.target: str` — defined Task 1, consumed in Tasks 8 handlers ✓
- `ChannelList` uses `#cl-channel-list` (not `#channel-list` — avoids collision with ChatPane's `#channel-list`) ✓
- `grove_messages_all_agents(known_agents: frozenset, last_id: int, limit: int)` — defined Task 6, called in Task 5 with matching signature ✓
- `NavBar.highlight(target: str)` — defined Task 1, called in Task 8 `action_nav` ✓
- `NavBar.set_vitals(text: str)` — defined Task 1, called in Task 9 ✓
- `_CONTENT_PANES` keys match `NAV_TARGETS` ✓
- `ContextPanel._show_target` handles `"home"` and `"chat"` — all other targets fall through gracefully (no error, no widget shown — acceptable Phase 1 behavior) ✓

**Placeholder scan:** No TBDs, TODOs, or incomplete sections. All code blocks are complete.
