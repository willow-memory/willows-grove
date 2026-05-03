# Dashboard Phase 4a: Projects ContextPanel Nav — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a live Projects navigator to the left ContextPanel that shows the 5 internal panes (Tasks, Agents, Routing, Skills, Logs) with live count badges, navigating to the matching pane on activation.

**Architecture:** New `widgets/projects_nav.py` with two classes — `ProjectsNavRow` (focusable single-row widget) and `ProjectsNav` (container that polls counts every 10s via background worker). Navigation reuses the existing `CardActivated` message already wired in `app.py`. `ContextPanel` in `app.py` gains a third slot for `"projects"`.

**Tech Stack:** Textual (`Widget`, `Message`, `@work(thread=True)`), psycopg2, grove_reader, pathlib

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `widgets/projects_nav.py` | Create | `_fetch_nav_counts()`, `_NavRefreshed`, `ProjectsNavRow`, `ProjectsNav` |
| `app.py` | Modify (lines 119–147) | Add `ProjectsNav` to `ContextPanel.compose()` + wire `"projects"` in `_show_target()` |
| `tests/test_widgets_projects_nav.py` | Create | Unit tests for `_fetch_nav_counts`, `_NavRefreshed`, `ProjectsNavRow` |

---

### Task 1: `_fetch_nav_counts()` pure function + tests

**Files:**
- Create: `widgets/projects_nav.py`
- Create: `tests/test_widgets_projects_nav.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_widgets_projects_nav.py`:

```python
"""tests/test_widgets_projects_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.projects_nav import _fetch_nav_counts, _NavRefreshed

_ALL_IDS = ("tasks", "agents", "routing", "skills", "logs")


def test_fetch_returns_all_ids():
    result = _fetch_nav_counts()
    for cid in _ALL_IDS:
        assert cid in result, f"missing key: {cid}"


def test_fetch_values_are_strings():
    result = _fetch_nav_counts()
    for cid in _ALL_IDS:
        assert isinstance(result[cid]["count"], str), f"{cid}.count not str"
        assert isinstance(result[cid]["state"], str), f"{cid}.state not str"


def test_fetch_never_raises():
    result = _fetch_nav_counts()
    assert isinstance(result, dict)


def test_fetch_logs_always_live():
    result = _fetch_nav_counts()
    assert result["logs"]["count"] == "live"


def test_fetch_skills_missing_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    result = _fetch_nav_counts()
    assert result["skills"]["count"] == "—"


def test_fetch_skills_counts_md_files(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    skills_dir = tmp_path / ".willow" / "skills"
    skills_dir.mkdir(parents=True)
    (skills_dir / "a.md").write_text("skill a")
    (skills_dir / "b.md").write_text("skill b")
    (skills_dir / "ignore.txt").write_text("not a skill")
    result = _fetch_nav_counts()
    assert result["skills"]["count"] == "2"


def test_nav_refreshed_carries_data():
    data = {"tasks": {"count": "3", "state": "yellow"}}
    msg = _NavRefreshed(data)
    assert msg.data == data
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_widgets_projects_nav.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'widgets.projects_nav'`

- [ ] **Step 3: Create `widgets/projects_nav.py` with the pure function and message**

```python
"""widgets/projects_nav.py — ProjectsNavRow, ProjectsNav for ContextPanel.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label, Rule, Static

from widgets.card_grid import CardActivated


# (card_id, label, nav_target)
_NAV_ROWS: list[tuple[str, str, str]] = [
    ("tasks",   "Tasks",   "#pane-tasks"),
    ("agents",  "Agents",  "#pane-agents"),
    ("routing", "Routing", "#pane-routing"),
    ("skills",  "Skills",  "#pane-skills"),
    ("logs",    "Logs",    "#pane-logs"),
]

_ROW_COLORS: dict[str, str] = {
    "green":  "#3fb950",
    "yellow": "#d29922",
    "dim":    "#8b949e",
    "":       "#8b949e",
}


def _fetch_nav_counts() -> dict[str, dict]:
    """Return live counts for all 5 nav rows. Never raises.

    Returns {card_id: {"count": str, "state": str}}.
    """
    out: dict[str, dict] = {cid: {"count": "—", "state": "dim"} for cid, _, _ in _NAV_ROWS}

    # Tasks — running count
    try:
        from panes.tasks import fetch_tasks
        t = fetch_tasks()
        running = t.get("running", 0)
        out["tasks"] = {"count": str(running), "state": "yellow" if running > 0 else "dim"}
    except Exception:
        pass

    # Agents — active count
    try:
        import grove_reader
        agents = grove_reader.grove_agents()
        count = len(agents)
        out["agents"] = {"count": str(count), "state": "green" if count > 0 else "dim"}
    except Exception:
        pass

    # Routing — recent decision count
    try:
        import grove_reader
        decisions = grove_reader.routing_decisions()
        out["routing"] = {"count": str(len(decisions)), "state": "dim"}
    except Exception:
        pass

    # Skills — count .md files in ~/.willow/skills/
    try:
        skills_dir = Path.home() / ".willow" / "skills"
        if skills_dir.exists():
            count = len(list(skills_dir.glob("*.md")))
            out["skills"] = {"count": str(count), "state": "dim"}
        else:
            out["skills"] = {"count": "—", "state": "dim"}
    except Exception:
        pass

    # Logs — always live
    out["logs"] = {"count": "live", "state": "dim"}

    return out


class _NavRefreshed(Message):
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_widgets_projects_nav.py -v
```

Expected: all 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add widgets/projects_nav.py tests/test_widgets_projects_nav.py
git commit -m "feat(projects-nav): _fetch_nav_counts pure function + _NavRefreshed + tests"
```

---

### Task 2: `ProjectsNavRow` widget + tests

**Files:**
- Modify: `widgets/projects_nav.py`
- Modify: `tests/test_widgets_projects_nav.py`

- [ ] **Step 1: Add tests for `ProjectsNavRow`**

Append to `tests/test_widgets_projects_nav.py`:

```python
from widgets.projects_nav import ProjectsNavRow


def test_row_stores_card_id():
    row = ProjectsNavRow("tasks", "Tasks", "#pane-tasks")
    assert row._card_id == "tasks"


def test_row_stores_nav_target():
    row = ProjectsNavRow("agents", "Agents", "#pane-agents")
    assert row._nav_target == "#pane-agents"


def test_row_stores_label():
    row = ProjectsNavRow("routing", "Routing", "#pane-routing")
    assert row._label == "Routing"


def test_update_row_accepts_call():
    row = ProjectsNavRow("tasks", "Tasks", "#pane-tasks")
    row._count = "0"
    row._state = "dim"
    row.update_row("3", "yellow")
    assert row._count == "3"
    assert row._state == "yellow"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_widgets_projects_nav.py::test_row_stores_card_id -v
```

Expected: `ImportError` — `ProjectsNavRow` not defined yet

- [ ] **Step 3: Add `ProjectsNavRow` to `widgets/projects_nav.py`**

Append after the `_NavRefreshed` class:

```python
class ProjectsNavRow(Widget):
    """Single focusable nav row: dot + label + count badge."""

    can_focus = True

    BINDINGS = [("enter", "activate", "Open")]

    DEFAULT_CSS = """
    ProjectsNavRow {
        height: 1;
        width: 1fr;
        padding: 0 1;
    }
    ProjectsNavRow:focus {
        background: #21262d;
    }
    """

    def __init__(self, card_id: str, label: str, nav_target: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._card_id    = card_id
        self._label      = label
        self._nav_target = nav_target
        self._count      = "—"
        self._state      = "dim"

    def compose(self) -> ComposeResult:
        yield Static("", id=f"pnrt-{self._card_id}", markup=True)

    def on_mount(self) -> None:
        self._render()

    def _render(self) -> None:
        from textual.css.query import NoMatches
        color = _ROW_COLORS.get(self._state, "#8b949e")
        dot   = f"[{color}]●[/]"
        text  = f"{dot} {self._label:<12} [{color}]{self._count}[/]"
        try:
            self.query_one(f"#pnrt-{self._card_id}", Static).update(text)
        except NoMatches:
            pass

    def update_row(self, count: str, state: str) -> None:
        self._count = count
        self._state = state
        self._render()

    def action_activate(self) -> None:
        self.post_message(CardActivated(self._card_id, self._nav_target))

    def on_click(self) -> None:
        self.action_activate()
```

- [ ] **Step 4: Run all tests in the file**

```bash
python3 -m pytest tests/test_widgets_projects_nav.py -v
```

Expected: all 11 tests PASS

- [ ] **Step 5: Commit**

```bash
git add widgets/projects_nav.py tests/test_widgets_projects_nav.py
git commit -m "feat(projects-nav): ProjectsNavRow widget + tests"
```

---

### Task 3: `ProjectsNav` container widget

**Files:**
- Modify: `widgets/projects_nav.py`

No new tests needed — `ProjectsNav` composes `ProjectsNavRow` children and delegates to the already-tested worker. Textual widget composition is not unit-testable without a running app.

- [ ] **Step 1: Append `ProjectsNav` to `widgets/projects_nav.py`**

```python
class ProjectsNav(Widget):
    """Left-panel navigator for the Projects target. Polls counts every 10s."""

    DEFAULT_CSS = """
    ProjectsNav {
        width: 1fr;
        height: 1fr;
        padding: 1 0;
    }
    ProjectsNav #pn-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 1;
    }
    ProjectsNav Rule {
        margin: 0;
        color: #30363d;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("PROJECTS", id="pn-header")
        yield Rule()
        for card_id, label, nav in _NAV_ROWS:
            yield ProjectsNavRow(card_id, label, nav, id=f"pnrow-{card_id}")

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(10, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        data = _fetch_nav_counts()
        self.post_message(_NavRefreshed(data))

    def on__nav_refreshed(self, event: _NavRefreshed) -> None:
        from textual.css.query import NoMatches
        for card_id, _, _ in _NAV_ROWS:
            row_data = event.data.get(card_id, {})
            try:
                row = self.query_one(f"#pnrow-{card_id}", ProjectsNavRow)
                row.update_row(
                    row_data.get("count", "—"),
                    row_data.get("state", "dim"),
                )
            except NoMatches:
                pass
```

- [ ] **Step 2: Run full test suite to verify nothing broken**

```bash
python3 -m pytest tests/test_widgets_projects_nav.py tests/test_widgets_card_grid.py -v
```

Expected: all tests PASS

- [ ] **Step 3: Commit**

```bash
git add widgets/projects_nav.py
git commit -m "feat(projects-nav): ProjectsNav container with 10s polling worker"
```

---

### Task 4: Wire `ProjectsNav` into `ContextPanel` in `app.py`

**Files:**
- Modify: `app.py` (lines ~14–28 for import, lines ~119–147 for `ContextPanel`)

- [ ] **Step 1: Add import to `app.py`**

In `app.py`, the imports block currently has (around line 18):
```python
from panes.chat      import ChatPane, ChannelList, sender_color
```

Add after that line:
```python
from widgets.projects_nav import ProjectsNav
```

- [ ] **Step 2: Modify `ContextPanel.compose()` in `app.py`**

Current `compose` (lines ~122–125):
```python
    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-home")
        yield ChannelList(id="ctx-chat")
```

Replace with:
```python
    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-home")
        yield ChannelList(id="ctx-chat")
        yield ProjectsNav(id="ctx-projects")
```

- [ ] **Step 3: Add `"projects"` to `ctx_map` in `ContextPanel._show_target()`**

Current `ctx_map` (lines ~132–135):
```python
        ctx_map = {
            "home": "#ctx-home",
            "chat": "#ctx-chat",
        }
```

Replace with:
```python
        ctx_map = {
            "home":     "#ctx-home",
            "chat":     "#ctx-chat",
            "projects": "#ctx-projects",
        }
```

- [ ] **Step 4: Run full test suite**

```bash
python3 -m pytest tests/ -v
```

Expected: all tests PASS (no new tests for app.py — ContextPanel wiring is integration-only)

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat(projects-nav): wire ProjectsNav into ContextPanel for projects target"
```

---

## Done

After Task 4, navigating to Projects in the dashboard shows the live left-panel navigator. Each row shows a colored dot, label, and count badge. Tab moves focus between rows; Enter or click activates and navigates the main area to that pane.
