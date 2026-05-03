# Dashboard Phase 4b: Knowledge Nav + Atom Viewer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Knowledge search navigator to the left ContextPanel and transform the main KnowledgePane into a single-atom detail viewer driven by selection.

**Architecture:** New `widgets/knowledge_nav.py` holds `KnowledgeAtomSelected` message + `KnowledgeNav` widget (search input + results list with up/down/enter nav). `panes/knowledge.py` gains pure functions `fetch_atom()` and `render_atom()` plus a `display_atom()` method on `KnowledgePane`; the old DataTable search UI is removed. `WillowGrove` in `app.py` routes `KnowledgeAtomSelected` to `KnowledgePane.display_atom()` — same pattern as `on_card_activated`.

**Tech Stack:** Textual (`Widget`, `Input`, `Static`, `Message`, `@work(thread=True)`), psycopg2, pytest

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `widgets/knowledge_nav.py` | Create | `KnowledgeAtomSelected`, `_KnowledgeSearchDone`, `KnowledgeNav` |
| `panes/knowledge.py` | Modify | Add `fetch_atom()`, `render_atom()`, `_AtomFetched`, `display_atom()`; gut old compose/handler |
| `app.py` | Modify | Wire `KnowledgeNav` into `ContextPanel`; add `WillowGrove.on_knowledge_atom_selected` |
| `tests/test_panes_knowledge.py` | Create | Tests for `fetch_atom`, `render_atom` |
| `tests/test_widgets_knowledge_nav.py` | Create | Tests for `KnowledgeAtomSelected`, `KnowledgeNav` constructor |

---

### Task 1: `fetch_atom()` + `render_atom()` pure functions + tests

**Files:**
- Modify: `panes/knowledge.py`
- Create: `tests/test_panes_knowledge.py`

- [ ] **Step 1: Create failing tests**

Create `tests/test_panes_knowledge.py`:

```python
"""tests/test_panes_knowledge.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock
from panes.knowledge import fetch_atom, render_atom


# ── render_atom ───────────────────────────────────────────────────────────────

def test_render_atom_is_string():
    atom = {"id": 1, "title": "T", "summary": "S", "domain": "d", "weight": 1}
    assert isinstance(render_atom(atom), str)


def test_render_atom_contains_title():
    atom = {"id": 1, "title": "My Atom", "summary": "", "domain": "test", "weight": 0}
    assert "My Atom" in render_atom(atom)


def test_render_atom_shows_id():
    atom = {"id": 42, "title": "", "summary": "", "domain": "d", "weight": 0}
    assert "42" in render_atom(atom)


def test_render_atom_missing_content_key():
    atom = {"id": 1, "title": "X", "summary": "s", "domain": "d", "weight": 0}
    out = render_atom(atom)
    assert isinstance(out, str)


def test_render_atom_includes_content():
    atom = {"id": 1, "title": "X", "summary": "", "domain": "d", "weight": 0,
            "content": "full text here"}
    assert "full text here" in render_atom(atom)


# ── fetch_atom ────────────────────────────────────────────────────────────────

def test_fetch_atom_returns_none_on_missing_row():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.fetchone.return_value = None
    result = fetch_atom(42, conn=conn)
    assert result is None


def test_fetch_atom_returns_dict_on_success():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.fetchone.return_value = (42, "My Title", "A summary", "test", 5, "full content")
    result = fetch_atom(42, conn=conn)
    assert result is not None
    assert result["id"] == 42
    assert result["title"] == "My Title"
    assert result["content"] == "full content"


def test_fetch_atom_returns_none_on_db_error():
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.execute.side_effect = Exception("db error")
    result = fetch_atom(42, conn=conn)
    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_panes_knowledge.py -v 2>&1 | head -20
```

Expected: `ImportError: cannot import name 'fetch_atom' from 'panes.knowledge'`

- [ ] **Step 3: Add `fetch_atom()` and `render_atom()` to `panes/knowledge.py`**

Add these two functions after `search_kb()` (before `class KnowledgePane`):

```python
def fetch_atom(atom_id: int, conn=None) -> dict | None:
    """Fetch a single knowledge atom by id. Returns None if not found or on failure."""
    close = conn is None
    if conn is None:
        try:
            conn = _pg_conn()
        except Exception:
            return None
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, title, summary, domain, weight, content "
                "FROM public.knowledge WHERE id = %s",
                (atom_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0], "title": row[1] or "", "summary": row[2] or "",
                "domain": row[3] or "", "weight": row[4] or 0, "content": row[5] or "",
            }
        except Exception:
            conn.rollback()
            cur.execute(
                "SELECT id, title, summary, domain, weight "
                "FROM public.knowledge WHERE id = %s",
                (atom_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0], "title": row[1] or "", "summary": row[2] or "",
                "domain": row[3] or "", "weight": row[4] or 0,
            }
    except Exception:
        return None
    finally:
        if close:
            try:
                conn.close()
            except Exception:
                pass


def render_atom(atom: dict) -> str:
    """Render a knowledge atom dict as Textual rich markup."""
    _H = "[bold #58a6ff]"
    _D = "[dim]"
    _V = "[#c9d1d9]"
    _E = "[/]"
    lines: list[str] = []

    lines.append(
        f"{_H}#{atom.get('id', '?')}[/]  "
        f"{_D}{atom.get('domain', '')}  w={atom.get('weight', 0)}{_E}"
    )
    lines.append("")

    title = atom.get("title", "")
    if title:
        lines.append(f"[bold]{title}[/]")
        lines.append("")

    summary = atom.get("summary", "")
    if summary:
        lines.append(f"{_D}SUMMARY{_E}")
        lines.append(summary)
        lines.append("")

    content = atom.get("content", "")
    if content:
        lines.append(f"{_D}CONTENT{_E}")
        lines.append(content)

    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_panes_knowledge.py -v
```

Expected: all 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add panes/knowledge.py tests/test_panes_knowledge.py
git commit -m "feat(knowledge): fetch_atom + render_atom pure functions + tests"
```

---

### Task 2: `KnowledgeAtomSelected` message + `KnowledgeNav` widget + tests

**Files:**
- Create: `widgets/knowledge_nav.py`
- Create: `tests/test_widgets_knowledge_nav.py`

- [ ] **Step 1: Create failing tests**

Create `tests/test_widgets_knowledge_nav.py`:

```python
"""tests/test_widgets_knowledge_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.knowledge_nav import KnowledgeAtomSelected, KnowledgeNav


def test_atom_selected_stores_id():
    msg = KnowledgeAtomSelected(42)
    assert msg.atom_id == 42


def test_knowledge_nav_constructs():
    nav = KnowledgeNav()
    assert nav._rows == []
    assert nav._cursor == -1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_widgets_knowledge_nav.py -v 2>&1 | head -10
```

Expected: `ModuleNotFoundError: No module named 'widgets.knowledge_nav'`

- [ ] **Step 3: Create `widgets/knowledge_nav.py`**

```python
"""widgets/knowledge_nav.py — KnowledgeNav for Knowledge ContextPanel slot.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Static


class KnowledgeAtomSelected(Message):
    """Posted when the user confirms a result row in KnowledgeNav."""

    def __init__(self, atom_id: int) -> None:
        super().__init__()
        self.atom_id = atom_id


class _KnowledgeSearchDone(Message):
    def __init__(self, rows: list[dict]) -> None:
        super().__init__()
        self.rows: list[dict] = rows


class KnowledgeNav(Widget):
    """Left-panel widget: search input + results list for the Knowledge pane.

    Up/Down arrows move cursor through results.
    Enter with text = search; Enter with empty input = confirm highlighted result.
    """

    DEFAULT_CSS = """
    KnowledgeNav {
        width: 1fr;
        height: 1fr;
    }
    KnowledgeNav #kn-results {
        height: 1fr;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._rows: list[dict] = []
        self._cursor: int = -1

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search knowledge…", id="kn-search")
        yield Static("", id="kn-results", markup=True)

    @on(Input.Submitted, "#kn-search")
    def _on_search(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            if self._cursor >= 0 and self._rows:
                self.action_confirm()
            return
        self._search(query)

    @work(thread=True)
    def _search(self, query: str) -> None:
        from panes.knowledge import search_kb
        rows = search_kb(query, limit=20)
        self.post_message(_KnowledgeSearchDone(rows))

    def on__knowledge_search_done(self, event: _KnowledgeSearchDone) -> None:
        self._rows = event.rows
        self._cursor = 0 if self._rows else -1
        self._render_results()

    def on_key(self, event) -> None:
        if event.key == "up":
            self.action_cursor_up()
            event.stop()
        elif event.key == "down":
            self.action_cursor_down()
            event.stop()

    def action_cursor_up(self) -> None:
        if self._rows and self._cursor > 0:
            self._cursor -= 1
            self._render_results()

    def action_cursor_down(self) -> None:
        if self._rows and self._cursor < len(self._rows) - 1:
            self._cursor += 1
            self._render_results()

    def action_confirm(self) -> None:
        if 0 <= self._cursor < len(self._rows):
            atom_id = self._rows[self._cursor]["id"]
            self.post_message(KnowledgeAtomSelected(atom_id))

    def _render_results(self) -> None:
        from textual.css.query import NoMatches
        if not self._rows:
            text = "[dim]no results[/]"
        else:
            lines = []
            for i, row in enumerate(self._rows):
                title = (row.get("title", "") or "—")[:16]
                atom_id = row.get("id", "?")
                if i == self._cursor:
                    lines.append(f"[reverse] {i + 1:2}. {atom_id} {title}[/]")
                else:
                    lines.append(f"[dim] {i + 1:2}.[/] [#58a6ff]{atom_id}[/] {title}")
            text = "\n".join(lines)
        try:
            self.query_one("#kn-results", Static).update(text)
        except NoMatches:
            pass
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
python3 -m pytest tests/test_widgets_knowledge_nav.py tests/test_panes_knowledge.py -v
```

Expected: all 10 tests PASS

- [ ] **Step 5: Commit**

```bash
git add widgets/knowledge_nav.py tests/test_widgets_knowledge_nav.py
git commit -m "feat(knowledge): KnowledgeAtomSelected + KnowledgeNav widget + tests"
```

---

### Task 3: Modify `KnowledgePane` to atom detail viewer

**Files:**
- Modify: `panes/knowledge.py`

No new tests — `KnowledgePane.display_atom()` calls `@work` which requires a running app.

- [ ] **Step 1: Replace `KnowledgePane` class in `panes/knowledge.py`**

The current file has these imports at the top:

```python
from textual import on
from textual.containers import Container
from textual.widgets import DataTable, Input, Label
```

Replace them with:

```python
from textual import work
from textual.containers import Container
from textual.message import Message
from textual.widgets import Static
```

- [ ] **Step 2: Replace `KnowledgePane` class**

Remove the existing `KnowledgePane` class (including the `@on(Input.Submitted)` handler) and replace with:

```python
class _AtomFetched(Message):
    def __init__(self, atom: dict | None) -> None:
        super().__init__()
        self.atom = atom


class KnowledgePane(Container):
    DEFAULT_CSS = """
    KnowledgePane {
        height: 1fr;
    }
    KnowledgePane #kb-atom {
        height: 1fr;
        padding: 1 2;
    }
    """

    def compose(self):
        yield Static(
            "[dim]Search knowledge in the left panel, then press Enter to view[/]",
            id="kb-atom",
            markup=True,
        )

    def display_atom(self, atom_id: int) -> None:
        self._fetch(atom_id)

    @work(thread=True)
    def _fetch(self, atom_id: int) -> None:
        atom = fetch_atom(atom_id)
        self.post_message(_AtomFetched(atom))

    def on__atom_fetched(self, event: _AtomFetched) -> None:
        from textual.css.query import NoMatches
        text = render_atom(event.atom) if event.atom else "[dim]Atom not found[/]"
        try:
            self.query_one("#kb-atom", Static).update(text)
        except NoMatches:
            pass
```

- [ ] **Step 3: Run full test suite**

```bash
python3 -m pytest tests/ -v 2>&1 | tail -10
```

Expected: all tests PASS (the existing KnowledgePane tests in test_panes_knowledge.py cover the pure functions; KnowledgePane widget is not unit-tested)

- [ ] **Step 4: Commit**

```bash
git add panes/knowledge.py
git commit -m "feat(knowledge): KnowledgePane becomes atom detail viewer"
```

---

### Task 4: Wire `KnowledgeNav` into `ContextPanel` and `WillowGrove`

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add imports to `app.py`**

Current imports block in `app.py` includes (around line 18–19):

```python
from panes.chat      import ChatPane, ChannelList, sender_color
from widgets.projects_nav import ProjectsNav
```

Add after those lines:

```python
from widgets.knowledge_nav import KnowledgeAtomSelected, KnowledgeNav
```

- [ ] **Step 2: Add `KnowledgeNav` to `ContextPanel.compose()`**

Current `ContextPanel.compose()`:

```python
    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-home")
        yield ChannelList(id="ctx-chat")
        yield ProjectsNav(id="ctx-projects")
```

Replace with:

```python
    def compose(self) -> ComposeResult:
        yield DeskPane(id="ctx-home")
        yield ChannelList(id="ctx-chat")
        yield ProjectsNav(id="ctx-projects")
        yield KnowledgeNav(id="ctx-knowledge")
```

- [ ] **Step 3: Add `"knowledge"` to `ctx_map` in `ContextPanel._show_target()`**

Current `ctx_map`:

```python
        ctx_map = {
            "home":     "#ctx-home",
            "chat":     "#ctx-chat",
            "projects": "#ctx-projects",
        }
```

Replace with:

```python
        ctx_map = {
            "home":      "#ctx-home",
            "chat":      "#ctx-chat",
            "projects":  "#ctx-projects",
            "knowledge": "#ctx-knowledge",
        }
```

- [ ] **Step 4: Add `on_knowledge_atom_selected` to `WillowGrove`**

In `WillowGrove` class, add after `on_card_activated`:

```python
    def on_knowledge_atom_selected(self, event: KnowledgeAtomSelected) -> None:
        try:
            self.query_one(KnowledgePane).display_atom(event.atom_id)
        except NoMatches:
            pass
```

- [ ] **Step 5: Run full test suite**

```bash
python3 -m pytest tests/ -v 2>&1 | tail -10
```

Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat(knowledge): wire KnowledgeNav into ContextPanel + route KnowledgeAtomSelected"
```

---

## Done

After Task 4, navigating to Knowledge shows a search input in the left panel. Type a query and press Enter to see up to 20 results. Arrow up/down to highlight a result. Press Enter (with empty input) to open the selected atom in the main panel.
