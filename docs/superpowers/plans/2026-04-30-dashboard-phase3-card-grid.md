# Dashboard Phase 3 — Card Grid Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `HomeGrid` and `ProjectsGrid` static placeholders with live Textual card grids — 7 built-in system cards with live data on Home, 5 launcher tiles on Projects, all focusable and navigable.

**Architecture:** `widgets/card_grid.py` provides `CardCell` (focusable tile), `CardGrid` (grid container with background worker), `CardActivated` (navigation message), and `fetch_runtime_card_values()` (pure data function for all 7 built-in cards). `HomeGrid` and `ProjectsGrid` in `panes/home.py` become Containers that compose these widgets. `app.py` handles `CardActivated` to switch panes.

**Tech Stack:** Python 3.10+, Textual (existing version), psycopg2, pytest, `panes.tasks.fetch_tasks`, `grove_reader.grove_agents`.

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `widgets/card_grid.py` | `CardActivated`, `_STATE_COLORS`, `_CARD_NAV`, `BUILTIN_CARDS`, `LAUNCHER_CARDS`, `fetch_runtime_card_values`, `CardCell`, `_CardsRefreshed`, `CardGrid` |
| Create | `tests/test_widgets_card_grid.py` | Unit tests for `fetch_runtime_card_values` and message/constant correctness |
| Modify | `panes/home.py` | `HomeGrid` → Container with `CardGrid`; `ProjectsGrid` → Container with 5 `CardCell` launchers |
| Modify | `app.py` | Import `CardActivated`; add `_show_internal_pane()`; add `on_card_activated()` |

`cards.py`, `grove_reader.py`, `panes/tasks.py` — untouched.

---

## Task 1: `fetch_runtime_card_values` + constants

**Files:**
- Create: `widgets/card_grid.py`
- Create: `tests/test_widgets_card_grid.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_widgets_card_grid.py`:

```python
"""tests/test_widgets_card_grid.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from widgets.card_grid import (
    _STATE_COLORS, _CARD_NAV, BUILTIN_CARDS, LAUNCHER_CARDS,
    fetch_runtime_card_values,
)

# ── constants ─────────────────────────────────────────────────────────────────

def test_state_colors_has_required_keys():
    for key in ("green", "amber", "red", "blue", "dim", ""):
        assert key in _STATE_COLORS

def test_card_nav_covers_all_builtin_ids():
    builtin_ids = {cid for cid, _ in BUILTIN_CARDS}
    for cid in builtin_ids:
        assert cid in _CARD_NAV

def test_builtin_cards_has_seven():
    assert len(BUILTIN_CARDS) == 7

def test_launcher_cards_has_five():
    assert len(LAUNCHER_CARDS) == 5

def test_launcher_cards_all_have_nav():
    for _, _, nav in LAUNCHER_CARDS:
        assert nav.startswith("#pane-")

# ── fetch_runtime_card_values ─────────────────────────────────────────────────

def test_fetch_returns_dict_for_all_builtin_ids():
    result = fetch_runtime_card_values()
    builtin_ids = {cid for cid, _ in BUILTIN_CARDS}
    for cid in builtin_ids:
        assert cid in result

def test_fetch_values_are_strings():
    result = fetch_runtime_card_values()
    for cid, data in result.items():
        assert isinstance(data["value"], str), f"{cid}.value is not str"
        assert isinstance(data["sub"], str), f"{cid}.sub is not str"
        assert isinstance(data["state"], str), f"{cid}.state is not str"

def test_fetch_does_not_raise():
    """Must return safe defaults even when all sources fail."""
    result = fetch_runtime_card_values()
    assert isinstance(result, dict)

def test_fetch_yggdrasil_reads_env(monkeypatch):
    monkeypatch.setenv("WILLOW_MODEL", "claude-test-model")
    result = fetch_runtime_card_values()
    assert result["yggdrasil"]["value"] == "claude-test-model"
    assert result["yggdrasil"]["sub"] == "active model"

def test_fetch_fleet_counts_key_vars(monkeypatch):
    monkeypatch.setenv("WILLOW_ANTHROPIC_KEY", "sk-test-1")
    monkeypatch.setenv("WILLOW_OPENAI_KEY", "sk-test-2")
    result = fetch_runtime_card_values()
    assert int(result["fleet"]["value"]) >= 2
    assert result["fleet"]["sub"] == "providers"

def test_fetch_secrets_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    result = fetch_runtime_card_values()
    assert result["secrets"]["value"] == "—"
    assert result["secrets"]["sub"] == "vault"

def test_fetch_secrets_reads_file(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    willow_dir = tmp_path / ".willow"
    willow_dir.mkdir()
    (willow_dir / "secrets.json").write_text('{"KEY_A": "val1", "KEY_B": "val2"}')
    result = fetch_runtime_card_values()
    assert result["secrets"]["value"] == "2"

def test_fetch_mcp_reads_file(tmp_path, monkeypatch):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    mcp = {"mcpServers": {"willow": {}, "grove": {}}}
    import json
    (tmp_path / ".mcp.json").write_text(json.dumps(mcp))
    result = fetch_runtime_card_values()
    assert result["mcp"]["value"] == "2"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python3 -m pytest tests/test_widgets_card_grid.py -v 2>&1 | tail -10
```

Expected: `ImportError: cannot import name '_STATE_COLORS' from 'widgets.card_grid'` (file doesn't exist yet).

- [ ] **Step 3: Create `widgets/card_grid.py` with constants + `fetch_runtime_card_values`**

```python
"""widgets/card_grid.py — CardCell, CardGrid, CardActivated for Textual.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import os

from textual import work
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


_STATE_COLORS: dict[str, str] = {
    "green":  "#3fb950",
    "amber":  "#d29922",
    "red":    "#f85149",
    "blue":   "#58a6ff",
    "yellow": "#d29922",
    "dim":    "#8b949e",
    "":       "#8b949e",
}

_CARD_NAV: dict[str, str] = {
    "kart":      "#pane-tasks",
    "knowledge": "knowledge",
    "yggdrasil": "providers",
    "agents":    "#pane-agents",
    "secrets":   "",
    "fleet":     "providers",
    "mcp":       "providers",
}

# (card_id, label) — order controls grid position
BUILTIN_CARDS: list[tuple[str, str]] = [
    ("kart",      "Kart Queue"),
    ("knowledge", "Knowledge"),
    ("yggdrasil", "Yggdrasil"),
    ("agents",    "Agents"),
    ("secrets",   "Secrets"),
    ("fleet",     "Fleet"),
    ("mcp",       "MCP Servers"),
]

# (card_id, label, nav_target)
LAUNCHER_CARDS: list[tuple[str, str, str]] = [
    ("tasks",   "Tasks",   "#pane-tasks"),
    ("agents",  "Agents",  "#pane-agents"),
    ("routing", "Routing", "#pane-routing"),
    ("skills",  "Skills",  "#pane-skills"),
    ("logs",    "Logs",    "#pane-logs"),
]


def fetch_runtime_card_values() -> dict[str, dict]:
    """Fetch live values for all 7 built-in cards. Never raises.

    Returns {card_id: {"value": str, "sub": str, "state": str}}.
    Defaults to {"value": "—", "sub": "", "state": ""} on any failure.
    """
    import json
    from pathlib import Path

    out: dict[str, dict] = {cid: {"value": "—", "sub": "", "state": ""} for cid, _ in BUILTIN_CARDS}

    # Kart Queue — pending/running counts from Kart task queue
    try:
        from panes.tasks import fetch_tasks
        t = fetch_tasks()
        pending = t.get("pending", 0)
        running = t.get("running", 0)
        state = "amber" if pending > 10 else "green" if pending > 0 else "dim"
        out["kart"] = {"value": str(pending), "sub": f"{running} running", "state": state}
    except Exception:
        pass

    # Knowledge — total atom count + today's additions
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.environ.get("WILLOW_PG_DB", "willow_19"),
            user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
            connect_timeout=2,
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM public.knowledge")
        total = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM public.knowledge"
            " WHERE created_at > NOW() - INTERVAL '24 hours'"
        )
        today = cur.fetchone()[0]
        conn.close()
        out["knowledge"] = {"value": str(total), "sub": f"{today} today", "state": "blue"}
    except Exception:
        pass

    # Yggdrasil — active model from env
    try:
        model = os.environ.get("WILLOW_MODEL", "—")
        out["yggdrasil"] = {"value": model, "sub": "active model", "state": "dim"}
    except Exception:
        pass

    # Agents — live agent count from Grove
    try:
        import grove_reader
        agents = grove_reader.grove_agents()
        count = len(agents)
        if agents:
            freshest = min(agents, key=lambda a: a.get("age_secs", 9999))
            sub   = freshest["sender"]
            age   = freshest.get("age_secs", 9999)
            state = "green" if age < 120 else "yellow" if age < 900 else "dim"
        else:
            sub, state = "none", "dim"
        out["agents"] = {"value": str(count), "sub": sub, "state": state}
    except Exception:
        pass

    # Secrets — key count from ~/.willow/secrets.json
    try:
        secrets_path = Path.home() / ".willow" / "secrets.json"
        if secrets_path.exists():
            data = json.loads(secrets_path.read_text())
            count = len(data) if isinstance(data, dict) else 0
            out["secrets"] = {"value": str(count), "sub": "vault", "state": "dim"}
        else:
            out["secrets"] = {"value": "—", "sub": "vault", "state": "dim"}
    except Exception:
        pass

    # Fleet — count non-empty WILLOW_*_KEY env vars
    try:
        count = sum(
            1 for k, v in os.environ.items()
            if k.startswith("WILLOW_") and k.endswith("_KEY") and v
        )
        out["fleet"] = {"value": str(count), "sub": "providers", "state": "dim"}
    except Exception:
        pass

    # MCP — server count from ~/.mcp.json
    try:
        mcp_path = Path.home() / ".mcp.json"
        if not mcp_path.exists():
            mcp_path = Path(__file__).parent.parent / ".mcp.json"
        if mcp_path.exists():
            data = json.loads(mcp_path.read_text())
            count = len(data.get("mcpServers", {}))
            out["mcp"] = {"value": str(count), "sub": "connected", "state": "dim"}
    except Exception:
        pass

    return out
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python3 -m pytest tests/test_widgets_card_grid.py -v 2>&1 | tail -20
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add widgets/card_grid.py tests/test_widgets_card_grid.py
git commit -m "feat(cards): fetch_runtime_card_values + constants"
```

---

## Task 2: `CardActivated` message + `CardCell` widget

**Files:**
- Modify: `widgets/card_grid.py`
- Modify: `tests/test_widgets_card_grid.py`

- [ ] **Step 1: Append failing tests**

Append to `tests/test_widgets_card_grid.py`:

```python
from widgets.card_grid import CardActivated

# ── CardActivated ─────────────────────────────────────────────────────────────

def test_card_activated_fields():
    msg = CardActivated("kart", "#pane-tasks")
    assert msg.card_id == "kart"
    assert msg.nav_target == "#pane-tasks"

def test_card_activated_empty_nav():
    msg = CardActivated("secrets", "")
    assert msg.nav_target == ""

def test_card_activated_content_nav():
    msg = CardActivated("knowledge", "knowledge")
    assert msg.nav_target == "knowledge"
```

- [ ] **Step 2: Run to confirm they fail**

```bash
python3 -m pytest tests/test_widgets_card_grid.py::test_card_activated_fields -v
```

Expected: FAIL with `ImportError`.

- [ ] **Step 3: Add `CardActivated` and `CardCell` to `widgets/card_grid.py`**

Append after `fetch_runtime_card_values` (before the end of file):

```python
class CardActivated(Message):
    """Posted by CardCell when the user activates a card (Enter or click)."""

    def __init__(self, card_id: str, nav_target: str) -> None:
        super().__init__()
        self.card_id    = card_id
        self.nav_target = nav_target


class CardCell(Widget):
    """A single focusable card tile showing label / value / sub-text."""

    can_focus = True

    BINDINGS = [("enter", "activate", "Open")]

    DEFAULT_CSS = """
    CardCell {
        border: solid #30363d;
        padding: 1 1;
        height: 7;
        background: #161b22;
    }
    CardCell:focus {
        border: solid #58a6ff;
    }
    CardCell .card-label {
        color: #58a6ff;
        text-style: bold;
    }
    CardCell .card-sub {
        color: #8b949e;
    }
    """

    def __init__(
        self,
        card_id: str,
        label: str,
        nav_target: str = "",
        value: str = "—",
        sub: str = "",
        state: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._card_id    = card_id
        self._label      = label
        self._nav_target = nav_target
        self._value      = value
        self._sub        = sub
        self._state      = state

    def compose(self) -> ComposeResult:
        yield Static(self._label, classes="card-label", markup=False)
        v = Static(self._value, id=f"cv-{self._card_id}", classes="card-value", markup=False)
        v.styles.color = _STATE_COLORS.get(self._state, "#8b949e")
        v.styles.text_style = "bold"
        v.styles.height = "auto"
        yield v
        yield Static(self._sub, id=f"cs-{self._card_id}", classes="card-sub", markup=False)

    def update_card(self, value: str, sub: str, state: str) -> None:
        """Update the displayed value, sub-text, and state color."""
        color = _STATE_COLORS.get(state, "#8b949e")
        try:
            from textual.css.query import NoMatches
            v = self.query_one(f"#cv-{self._card_id}", Static)
            v.update(value)
            v.styles.color = color
        except Exception:
            pass
        try:
            from textual.css.query import NoMatches
            self.query_one(f"#cs-{self._card_id}", Static).update(sub)
        except Exception:
            pass

    def action_activate(self) -> None:
        if self._nav_target:
            self.post_message(CardActivated(self._card_id, self._nav_target))

    def on_click(self) -> None:
        self.action_activate()
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
python3 -m pytest tests/test_widgets_card_grid.py -v 2>&1 | tail -20
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add widgets/card_grid.py tests/test_widgets_card_grid.py
git commit -m "feat(cards): CardActivated message + CardCell widget"
```

---

## Task 3: `CardGrid` widget

**Files:**
- Modify: `widgets/card_grid.py`

- [ ] **Step 1: Append `_CardsRefreshed` and `CardGrid` to `widgets/card_grid.py`**

Append after `CardCell`:

```python
class _CardsRefreshed(Message):
    def __init__(self, data: dict) -> None:
        super().__init__()
        self.data = data


class CardGrid(Widget):
    """Grid of CardCell widgets. Fetches live data every 30s via background worker."""

    DEFAULT_CSS = """
    CardGrid {
        layout: grid;
        grid-size: 3;
        grid-gutter: 1 1;
        height: 1fr;
        width: 1fr;
        padding: 1 1;
    }
    """

    def __init__(self, cards: list[tuple[str, str]], **kwargs) -> None:
        super().__init__(**kwargs)
        self._cards = cards  # list of (card_id, label)

    def compose(self) -> ComposeResult:
        for card_id, label in self._cards:
            nav = _CARD_NAV.get(card_id, "")
            yield CardCell(card_id, label, nav_target=nav, id=f"cell-{card_id}")

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(30, self._fetch)

    @work(thread=True)
    def _fetch(self) -> None:
        data = fetch_runtime_card_values()
        self.post_message(_CardsRefreshed(data))

    def on__cards_refreshed(self, event: _CardsRefreshed) -> None:
        from textual.css.query import NoMatches
        for card_id, _ in self._cards:
            card_data = event.data.get(card_id, {})
            try:
                cell = self.query_one(f"#cell-{card_id}", CardCell)
                cell.update_card(
                    card_data.get("value", "—"),
                    card_data.get("sub",   ""),
                    card_data.get("state", ""),
                )
            except NoMatches:
                pass
```

- [ ] **Step 2: Verify the full module imports cleanly**

```bash
python3 -c "from widgets.card_grid import CardGrid, CardCell, CardActivated, fetch_runtime_card_values, BUILTIN_CARDS, LAUNCHER_CARDS; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Run all card grid tests**

```bash
python3 -m pytest tests/test_widgets_card_grid.py -v 2>&1 | tail -20
```

Expected: all tests PASSED.

- [ ] **Step 4: Commit**

```bash
git add widgets/card_grid.py
git commit -m "feat(cards): CardGrid widget with 30s background worker"
```

---

## Task 4: Update `HomeGrid` and `ProjectsGrid` in `panes/home.py`

**Files:**
- Modify: `panes/home.py`

- [ ] **Step 1: Confirm existing tests still pass before changes**

```bash
python3 -m pytest tests/test_panes_home.py -v 2>&1 | tail -5
```

Expected: 31 passed.

- [ ] **Step 2: Replace `HomeGrid` and `ProjectsGrid` in `panes/home.py`**

Find and replace the `HomeGrid` and `ProjectsGrid` classes. The new versions import from `widgets.card_grid`.

Remove the `HOMEGRID_PLACEHOLDER` and `PROJECTS_PLACEHOLDER` constants **and** their classes. Replace with:

```python
# ── HomeGrid ──────────────────────────────────────────────────────────────────

class HomeGrid(Container):
    """Center area for Home — live card grid of 7 built-in system cards."""

    DEFAULT_CSS = """
    HomeGrid {
        width: 1fr;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        from widgets.card_grid import CardGrid, BUILTIN_CARDS
        yield CardGrid(BUILTIN_CARDS)


# ── ProjectsGrid ──────────────────────────────────────────────────────────────

class ProjectsGrid(Container):
    """Center area for Projects — launcher tiles for internal panes."""

    DEFAULT_CSS = """
    ProjectsGrid {
        width: 1fr;
        height: 1fr;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1 1;
        padding: 1 1;
    }
    """

    def compose(self) -> ComposeResult:
        from widgets.card_grid import CardCell, LAUNCHER_CARDS
        for card_id, label, nav in LAUNCHER_CARDS:
            yield CardCell(
                card_id, label,
                nav_target=nav,
                value="→",
                state="blue",
                id=f"cell-{card_id}",
            )
```

Also update the import at the top of `panes/home.py` — add `Container` to the `textual.containers` import (it's already there from DeskPane). Remove `Static` from the import if it's no longer used by HomeGrid/ProjectsGrid... actually `Static` is still used by `DeskPane`, so leave all imports as-is.

Also remove `HOMEGRID_PLACEHOLDER` and `PROJECTS_PLACEHOLDER` constants from `panes/home.py` (they are no longer referenced by any class).

- [ ] **Step 3: Update `tests/test_panes_home.py`**

The two placeholder tests now reference removed constants. Replace those two tests:

Find:

```python
def test_homegrid_placeholder_mentions_phase():
    assert "Phase" in HOMEGRID_PLACEHOLDER or "home" in HOMEGRID_PLACEHOLDER.lower()

def test_projects_placeholder_lists_internal_panes():
    text = PROJECTS_PLACEHOLDER.lower()
    for pane in ("tasks", "agents", "routing", "skills", "logs"):
        assert pane in text
```

Replace with:

```python
def test_homegrid_is_container():
    from textual.containers import Container
    assert issubclass(HomeGrid, Container)

def test_projectsgrid_is_container():
    from textual.containers import Container
    assert issubclass(ProjectsGrid, Container)
```

Also update the import at the top of `tests/test_panes_home.py` — remove `HOMEGRID_PLACEHOLDER` and `PROJECTS_PLACEHOLDER` from the import, add `HomeGrid` and `ProjectsGrid`:

```python
from panes.home import (
    DeskData, agent_dot, format_age, mini_bar,
    HomeGrid, ProjectsGrid,
)
```

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest tests/test_panes_home.py -v 2>&1 | tail -15
```

Expected: 31 passed (2 placeholder tests replaced by 2 new container tests — same count).

- [ ] **Step 5: Verify import from app.py's perspective**

```bash
python3 -c "from panes.home import DeskPane, HomeGrid, ProjectsGrid; print('ok')"
```

Expected: `ok`

- [ ] **Step 6: Commit**

```bash
git add panes/home.py tests/test_panes_home.py
git commit -m "feat(cards): HomeGrid + ProjectsGrid live card grids"
```

---

## Task 5: Update `app.py` — `on_card_activated` + `_show_internal_pane`

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add `CardActivated` import to `app.py`**

Find the existing widget imports block near the top of `app.py`:

```python
from widgets.nav_bar        import NavBar, NavChanged, NAV_TARGETS
from widgets.hero_scene     import HeroScene
from widgets.chat_strip     import ChatStrip
from widgets.thought_stream import ThoughtStream, SessionStats
```

Add one line:

```python
from widgets.card_grid      import CardActivated
```

- [ ] **Step 2: Add `_show_internal_pane` and `on_card_activated` to `WillowGrove`**

Find the `action_refresh` method in `WillowGrove` (around line 351). Add the two new methods directly before it:

```python
def _show_internal_pane(self, pane_id: str) -> None:
    """Hide all content + internal panes, then show the requested internal pane."""
    self._hide_all_content_panes()
    try:
        self.query_one(pane_id).display = True
    except NoMatches:
        pass

def on_card_activated(self, event: CardActivated) -> None:
    target = event.nav_target
    if not target:
        return
    if target.startswith("#"):
        self._show_internal_pane(target)
    else:
        self.action_nav(target)

```

- [ ] **Step 3: Verify the app imports cleanly**

```bash
python3 -c "import app; print('ok')"
```

Expected: `ok`

- [ ] **Step 4: Run the full test suite**

```bash
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -15
```

Expected: same pass count as before Task 5, no new failures.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat(cards): on_card_activated — card click navigates to pane"
```

---

## Task 6: Smoke test — verify the grids render in the running app

- [ ] **Step 1: Launch the app**

```bash
python3 app.py
```

- [ ] **Step 2: Check Home view (key `1`)**

- [ ] Center area shows 7 card tiles in a 3-column grid
- [ ] Cards show live values (Kart pending count, Knowledge atom count, active model name)
- [ ] Cards with no Postgres connection show `—`, no crash

- [ ] **Step 3: Check Projects view (key `3`)**

- [ ] Shows 5 launcher tiles: Tasks, Agents, Routing, Skills, Logs
- [ ] Each tile shows `→` in blue

- [ ] **Step 4: Test navigation**

- [ ] Tab to focus a card (blue border appears)
- [ ] Press Enter on Kart Queue → Tasks pane appears
- [ ] Press Enter on Knowledge → Knowledge pane appears
- [ ] Click Agents launcher in Projects → Agents pane appears
- [ ] Secrets card: Enter does nothing (no nav_target)

- [ ] **Step 5: Wait 30 seconds, confirm values refresh**

- [ ] **Step 6: Final commit if any minor fixes needed**

```bash
git add -p
git commit -m "fix(cards): smoke test fixes"
```

---

## Self-Review

**Spec coverage:**

| Spec requirement | Task |
|---|---|
| `CardCell` focusable, label/value/sub/state | Task 2 |
| `CardActivated(card_id, nav_target)` message | Task 2 |
| `CardGrid` 3-column grid layout | Task 3 |
| `@work(thread=True)` worker, 30s refresh | Task 3 |
| `fetch_runtime_card_values` for all 7 cards | Task 1 |
| Kart: pending count, running sub, amber/green/dim state | Task 1 |
| Knowledge: total + today, blue state | Task 1 |
| Yggdrasil: WILLOW_MODEL env | Task 1 |
| Agents: grove_reader count + freshest sender | Task 1 |
| Secrets: ~/.willow/secrets.json key count | Task 1 |
| Fleet: WILLOW_*_KEY env var count | Task 1 |
| MCP: .mcp.json mcpServers count | Task 1 |
| HomeGrid → Container with CardGrid(BUILTIN_CARDS) | Task 4 |
| ProjectsGrid → Container with 5 CardCell launchers | Task 4 |
| `_show_internal_pane` for #pane-* targets | Task 5 |
| `on_card_activated` dispatches to nav or internal pane | Task 5 |
| No crash when Postgres down | Task 1 (all sources individually guarded) |
| `fetch_runtime_card_values` unit-tested | Task 1 |

**Placeholder scan:** No TBDs, no vague steps, all code blocks complete.

**Type consistency:**
- `fetch_runtime_card_values() -> dict[str, dict]` defined Task 1, used Task 3 ✓
- `CardActivated(card_id: str, nav_target: str)` defined Task 2, handled in Task 5 ✓
- `CardCell(card_id, label, nav_target, value, sub, state)` defined Task 2, composed in Tasks 3 + 4 ✓
- `CardGrid(cards: list[tuple[str, str]])` defined Task 3, used in Task 4 ✓
- `BUILTIN_CARDS: list[tuple[str, str]]` defined Task 1, used in Tasks 3 + 4 ✓
- `LAUNCHER_CARDS: list[tuple[str, str, str]]` defined Task 1, used in Task 4 ✓
- `CardCell.update_card(value, sub, state)` defined Task 2, called in Task 3 ✓
