# Phase 4c: Providers + Health ContextPanel Nav — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the left ContextPanel to show a live focusable provider list when on Providers, and live subsystem health status when on Health.

**Architecture:** Two new widget files (`providers_nav.py`, `health_nav.py`) with background-thread polling; `ProviderRowSelected` messages bubble up to `WillowGrove` which calls `ProvidersPane.select_provider(name)` to move the DataTable cursor. `HealthNav` is pure status display — no selection. Both widgets are added to `ContextPanel` and gated by `ctx_map` in `_show_target`.

**Tech Stack:** Python 3.11, Textual (Widget, Message, @work, Static, ComposeResult), psycopg2, urllib.request, pathlib, sqlite3 (via existing `_read_providers()`).

---

## File Map

| Action | Path | What changes |
|--------|------|-------------|
| Create | `widgets/providers_nav.py` | `ProviderRowSelected`, `ProvidersNavRow`, `ProvidersNav` |
| Create | `widgets/health_nav.py` | `HealthNav`, `_fetch_health_status()` |
| Modify | `panes/providers.py` | Add `select_provider(name)` method |
| Modify | `app.py` | Wire both widgets into `ContextPanel` + `WillowGrove` handler |
| Create | `tests/test_widgets_providers_nav.py` | Unit tests for nav message + row widget |
| Create | `tests/test_widgets_health_nav.py` | Unit tests for `_fetch_health_status()` |

---

### Task 1: `ProviderRowSelected` message + `ProvidersNavRow` widget

**Files:**
- Create: `widgets/providers_nav.py`
- Create: `tests/test_widgets_providers_nav.py`

- [ ] **Step 1: Write the failing tests**

`tests/test_widgets_providers_nav.py`:
```python
"""tests/test_widgets_providers_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.providers_nav import ProviderRowSelected, ProvidersNavRow


def test_provider_row_selected_stores_name():
    msg = ProviderRowSelected("ollama")
    assert msg.name == "ollama"


def test_providers_nav_row_stores_fields():
    row = ProvidersNavRow("claude", True, "cloud")
    assert row._name == "claude"
    assert row._enabled is True
    assert row._ptype == "cloud"


def test_providers_nav_row_update_row():
    row = ProvidersNavRow("claude", True, "cloud")
    row.update_row(False, "local")
    assert row._enabled is False
    assert row._ptype == "local"
```

- [ ] **Step 2: Run tests to verify they fail**

```
cd /home/sean-campbell/github/safe-app-willow-grove
pytest tests/test_widgets_providers_nav.py -v
```
Expected: `ModuleNotFoundError: No module named 'widgets.providers_nav'`

- [ ] **Step 3: Create `widgets/providers_nav.py` with message + row widget**

```python
"""widgets/providers_nav.py — Providers left-panel nav.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

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
        yield Static("", id="pnr-label", markup=True)

    def on_mount(self) -> None:
        self._render()

    def _render(self) -> None:
        from textual.css.query import NoMatches
        dot = "[green]●[/]" if self._enabled else "[red]●[/]"
        status = "ON" if self._enabled else "OFF"
        text = f"{dot} {self._name}  {status}  {self._ptype}"
        try:
            self.query_one("#pnr-label", Static).update(text)
        except NoMatches:
            pass

    def update_row(self, enabled: bool, ptype: str) -> None:
        self._enabled = enabled
        self._ptype = ptype
        self._render()

    def action_activate(self) -> None:
        self.post_message(ProviderRowSelected(self._name))

    def on_click(self) -> None:
        self.action_activate()
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_widgets_providers_nav.py -v
```
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add widgets/providers_nav.py tests/test_widgets_providers_nav.py
git commit -m "feat(nav): ProviderRowSelected + ProvidersNavRow"
```

---

### Task 2: `ProvidersNav` widget (polling + row management)

**Files:**
- Modify: `widgets/providers_nav.py` (add `ProvidersNav` class)

Context: `_read_providers()` lives in `panes/providers.py`. Import it locally inside the `@work` method to avoid circular imports (same pattern as `KnowledgeNav` importing `search_kb`). The internal message `_ProvidersRefreshed` carries a `list[dict]` snapshot.

- [ ] **Step 1: Add `_ProvidersRefreshed` message and `ProvidersNav` class to `widgets/providers_nav.py`**

Append to the bottom of `widgets/providers_nav.py`:

```python
from textual import work
from textual.containers import Vertical


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
            # Same set — update rows in place
            for p in providers:
                try:
                    row = self.query_one(f"#pnr-{p['name']}", ProvidersNavRow)
                    row.update_row(bool(p.get("enabled")), "local" if p.get("local") else "cloud")
                except Exception:
                    pass
            return

        # Provider list changed — full rebuild
        self._provider_names = new_names
        for child in list(self.query(ProvidersNavRow)):
            child.remove()
        for p in providers:
            row = ProvidersNavRow(
                p["name"],
                bool(p.get("enabled")),
                "local" if p.get("local") else "cloud",
                id=f"pnr-{p['name']}",
            )
            self.mount(row)
```

- [ ] **Step 2: Run existing tests to verify nothing broke**

```
pytest tests/test_widgets_providers_nav.py -v
```
Expected: 3 PASSED

- [ ] **Step 3: Commit**

```bash
git add widgets/providers_nav.py
git commit -m "feat(nav): ProvidersNav widget with 15s polling"
```

---

### Task 3: `_fetch_health_status()` + `HealthNav` widget

**Files:**
- Create: `widgets/health_nav.py`
- Create: `tests/test_widgets_health_nav.py`

- [ ] **Step 1: Write failing tests**

`tests/test_widgets_health_nav.py`:
```python
"""tests/test_widgets_health_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from widgets.health_nav import _fetch_health_status


def test_health_status_returns_required_keys():
    status = _fetch_health_status()
    for key in ("pg", "ollama", "kart", "soil"):
        assert key in status
        assert "ok" in status[key]
        assert "label" in status[key]


def test_health_status_ok_is_bool():
    status = _fetch_health_status()
    for key in ("pg", "ollama", "kart", "soil"):
        assert isinstance(status[key]["ok"], bool)


def test_health_status_label_is_str():
    status = _fetch_health_status()
    for key in ("pg", "ollama", "kart", "soil"):
        assert isinstance(status[key]["label"], str)


def test_health_status_never_raises():
    # Even with everything failing, must return a dict
    with patch("psycopg2.connect", side_effect=Exception("no db")):
        with patch("urllib.request.urlopen", side_effect=Exception("no net")):
            status = _fetch_health_status()
    assert isinstance(status, dict)
    assert status["pg"]["ok"] is False
    assert status["ollama"]["ok"] is False


def test_soil_false_when_missing(tmp_path):
    with patch("widgets.health_nav._SOIL_STORE", tmp_path / "nonexistent"):
        status = _fetch_health_status()
    assert status["soil"]["ok"] is False


def test_soil_true_when_present(tmp_path):
    store = tmp_path / "store"
    store.mkdir()
    with patch("widgets.health_nav._SOIL_STORE", store):
        status = _fetch_health_status()
    assert status["soil"]["ok"] is True


def test_kart_ok_with_mock_db():
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = (3,)
    mock_conn.cursor.return_value = mock_cur
    with patch("psycopg2.connect", return_value=mock_conn):
        status = _fetch_health_status()
    assert status["kart"]["ok"] is True
    assert "3" in status["kart"]["label"]
```

- [ ] **Step 2: Run tests to verify they fail**

```
pytest tests/test_widgets_health_nav.py -v
```
Expected: `ModuleNotFoundError: No module named 'widgets.health_nav'`

- [ ] **Step 3: Create `widgets/health_nav.py`**

```python
"""widgets/health_nav.py — Health subsystem status left-panel.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

_SOIL_STORE = Path(os.environ.get("WILLOW_STORE_ROOT", Path.home() / ".willow" / "store"))


def _fetch_health_status() -> dict:
    """Pure function — never raises. Returns status dict for pg, ollama, kart, soil."""
    status: dict = {}

    # pg
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        conn.close()
        status["pg"] = {"ok": True, "label": "up"}
    except Exception:
        status["pg"] = {"ok": False, "label": "down"}

    # ollama
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434", timeout=2)
        status["ollama"] = {"ok": True, "label": "up"}
    except Exception:
        status["ollama"] = {"ok": False, "label": "down"}

    # kart — count pending+running tasks
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.tasks WHERE status IN ('pending','running')")
        count = cur.fetchone()[0]
        conn.close()
        status["kart"] = {"ok": True, "label": f"{count} pending"}
    except Exception:
        status["kart"] = {"ok": False, "label": "down"}

    # soil
    ok = _SOIL_STORE.is_dir()
    status["soil"] = {"ok": ok, "label": "ok" if ok else "missing"}

    return status


class _HealthStatusFetched(Message):
    def __init__(self, health: dict) -> None:
        super().__init__()
        self.health = health


class HealthNav(Widget):
    DEFAULT_CSS = """
    HealthNav {
        width: 1fr;
        height: 1fr;
        padding: 1 1;
    }
    HealthNav #hn-header {
        color: #58a6ff;
        text-style: bold;
        padding: 0 0 1 0;
    }
    HealthNav #hn-status {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("HEALTH", id="hn-header")
        yield Static("", id="hn-status", markup=True)

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(15, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        health = _fetch_health_status()
        self.post_message(_HealthStatusFetched(health))

    def on__health_status_fetched(self, event: _HealthStatusFetched) -> None:
        from textual.css.query import NoMatches
        h = event.health
        lines = []
        for key in ("pg", "ollama", "kart", "soil"):
            entry = h.get(key, {"ok": False, "label": "?"})
            dot = "[green]●[/]" if entry["ok"] else "[red]●[/]"
            lines.append(f"{dot} [dim]{key}[/]  {entry['label']}")
        text = "\n".join(lines)
        try:
            self.query_one("#hn-status", Static).update(text)
        except NoMatches:
            pass
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_widgets_health_nav.py -v
```
Expected: 7 PASSED

- [ ] **Step 5: Commit**

```bash
git add widgets/health_nav.py tests/test_widgets_health_nav.py
git commit -m "feat(nav): HealthNav + _fetch_health_status()"
```

---

### Task 4: Add `select_provider(name)` to `ProvidersPane`

**Files:**
- Modify: `panes/providers.py`

Context: `DataTable` rows are added in the order returned by `_read_providers()`. `select_provider` must scan the DataTable's row keys to find the row index where column 0 matches `name`. Use `DataTable.move_cursor(row=idx)` (Textual built-in). The DataTable uses default row keys (integers starting at 0) — iterate `table.row_count` and check `table.get_cell_at((i, 0))`.

- [ ] **Step 1: Add `select_provider` to `ProvidersPane` in `panes/providers.py`**

After the `action_disable_selected` method, add:

```python
    def select_provider(self, name: str) -> None:
        table = self.query_one("#prov-table", DataTable)
        for i in range(table.row_count):
            if str(table.get_cell_at((i, 0))) == name:
                table.move_cursor(row=i)
                return
```

- [ ] **Step 2: Run all existing tests to verify nothing broke**

```
pytest tests/ -v
```
Expected: All previously-passing tests still PASS (no test written here — `select_provider` is a UI method that requires a running Textual app to test, and is covered by integration; the DataTable.move_cursor API is a Textual built-in).

- [ ] **Step 3: Commit**

```bash
git add panes/providers.py
git commit -m "feat(providers): add select_provider(name) to move DataTable cursor"
```

---

### Task 5: Wire `ProvidersNav` + `HealthNav` into `app.py`

**Files:**
- Modify: `app.py`

Context: `ContextPanel` already has `DeskPane`, `ChannelList`, `ProjectsNav`, `KnowledgeNav`. The `ctx_map` dict in `_show_target` controls which widget is visible. `WillowGrove` needs `on_provider_row_selected` to route `ProviderRowSelected` messages to `ProvidersPane.select_provider`. The existing `on_knowledge_atom_selected` is the exact pattern to follow.

- [ ] **Step 1: Add imports to `app.py`**

At line 20 (after the `from widgets.knowledge_nav import ...` line), add:

```python
from widgets.providers_nav import ProviderRowSelected, ProvidersNav
from widgets.health_nav     import HealthNav
```

- [ ] **Step 2: Update `ContextPanel.compose()` in `app.py`**

Replace:
```python
    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-home")
        yield ChannelList(id="ctx-chat")
        yield ProjectsNav(id="ctx-projects")
        yield KnowledgeNav(id="ctx-knowledge")
```
With:
```python
    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-home")
        yield ChannelList(id="ctx-chat")
        yield ProjectsNav(id="ctx-projects")
        yield KnowledgeNav(id="ctx-knowledge")
        yield ProvidersNav(id="ctx-providers")
        yield HealthNav(id="ctx-health")
```

- [ ] **Step 3: Update `ContextPanel._show_target()` ctx_map in `app.py`**

Replace:
```python
        ctx_map = {
            "home":      "#ctx-home",
            "chat":      "#ctx-chat",
            "projects":  "#ctx-projects",
            "knowledge": "#ctx-knowledge",
        }
```
With:
```python
        ctx_map = {
            "home":      "#ctx-home",
            "chat":      "#ctx-chat",
            "projects":  "#ctx-projects",
            "knowledge": "#ctx-knowledge",
            "providers": "#ctx-providers",
            "health":    "#ctx-health",
        }
```

- [ ] **Step 4: Add `on_provider_row_selected` to `WillowGrove` in `app.py`**

After `on_knowledge_atom_selected`, add:

```python
    def on_provider_row_selected(self, event: ProviderRowSelected) -> None:
        try:
            self.query_one(ProvidersPane).select_provider(event.name)
        except NoMatches:
            pass
```

- [ ] **Step 5: Run all tests**

```
pytest tests/ -v
```
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat(app): wire ProvidersNav + HealthNav into ContextPanel"
```

---

## Self-Review Checklist

**Spec coverage:**
- ✅ `ProviderRowSelected(name)` — Task 1
- ✅ `ProvidersNavRow(name, enabled, ptype)` with `can_focus`, `BINDINGS`, `update_row`, `action_activate`, `on_click` — Task 1
- ✅ `ProvidersNav` with `_fetch()`, `on__providers_refreshed`, 15s interval — Task 2
- ✅ `HealthNav` with `_fetch()`, `on__health_status_fetched`, 15s interval — Task 3
- ✅ `_fetch_health_status()` with pg/ollama/kart/soil sources — Task 3
- ✅ `ProvidersPane.select_provider(name)` — Task 4
- ✅ `ContextPanel` wired with `ctx-providers` + `ctx-health` — Task 5
- ✅ `WillowGrove.on_provider_row_selected` — Task 5
- ✅ CSS for `ProvidersNavRow`, `ProvidersNav`, `HealthNav` — embedded in DEFAULT_CSS in Tasks 1/2/3
- ✅ Tests for `ProviderRowSelected`, `ProvidersNavRow`, `_fetch_health_status()` — Tasks 1/3

**Placeholder scan:** None found.

**Type consistency:** `ProviderRowSelected.name: str` used in Task 1, consumed in Task 5 as `event.name` ✅. `ProvidersNavRow` constructor `(name, enabled, ptype)` defined Task 1, used in Task 2 ✅. `_fetch_health_status()` returns `dict` checked Task 3, consumed by `HealthNav` in Task 3 ✅.
