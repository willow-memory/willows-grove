# Phase 7: Project Card System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add SOIL-backed dynamic card loading to HomeGrid, a `+` card that launches a Heimdallr-driven `CardBuilderModal`, and `card-def` block detection that saves new cards to SOIL and reloads the grid.

**Architecture:** Six independent tasks — SOIL layer first (tested in isolation), then `grove_db` channel provisioning, then `CardGrid` dynamic reload, then `HomeGrid` wiring, then the `CardBuilderModal` itself, and finally `app.py` dismiss hook. SOIL uses `WILLOW_STORE_ROOT` env var so tests can redirect to `tmp_path`. LISTEN/NOTIFY in the modal follows the identical pattern to `ChatPane._start_listener`.

**Tech Stack:** Textual 8.2.4, Python 3.11+, psycopg2, soil.py (`put`/`get`/`all_records`), `textual.screen.ModalScreen`, `textual.work` background worker, `re` for card-def detection, `select.select` for pg notify loop.

---

## File Map

| File | Change |
|------|--------|
| `widgets/card_store.py` | **Create** — SOIL r/w + catalog seeding + card-def validation |
| `tests/test_card_store.py` | **Create** — unit tests for all card_store functions |
| `grove_db.py` | **Modify** — add `ensure_card_builder_channel()` |
| `widgets/card_grid.py` | **Modify** — add `reload()`, `_nav_cache`, `PLUS_CARD` constant |
| `panes/home.py` | **Modify** — `HomeGrid.on_mount`, `on_card_activated`, `refresh_cards` |
| `widgets/card_builder_modal.py` | **Create** — `CardBuilderModal` + `CardDefDetected` message |
| `app.py` | **Modify** — import modal, add `on_screen_dismiss` |

---

## Task 1: `widgets/card_store.py` — SOIL card layer + tests

**Files:**
- Create: `widgets/card_store.py`
- Create: `tests/test_card_store.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_card_store.py`:

```python
"""tests/test_card_store.py
b17: WGRV1  ΔΣ=42
"""
import os
import pytest


@pytest.fixture(autouse=True)
def soil_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("WILLOW_STORE_ROOT", str(tmp_path))


from widgets.card_store import (
    load_cards, save_card, seed_catalog, validate_card_def, COLLECTION
)


def test_save_and_load_card():
    save_card({"id": "test-card", "label": "Test", "enabled": True, "order": 10})
    cards = load_cards()
    assert any(c["id"] == "test-card" for c in cards)


def test_load_cards_only_enabled():
    save_card({"id": "enabled-card",  "label": "On",  "enabled": True,  "order": 1})
    save_card({"id": "disabled-card", "label": "Off", "enabled": False, "order": 2})
    ids = [c["id"] for c in load_cards()]
    assert "enabled-card"  in ids
    assert "disabled-card" not in ids


def test_load_cards_sorted_by_order():
    save_card({"id": "c3", "label": "C", "enabled": True, "order": 30})
    save_card({"id": "c1", "label": "A", "enabled": True, "order": 10})
    save_card({"id": "c2", "label": "B", "enabled": True, "order": 20})
    ids = [c["id"] for c in load_cards()]
    assert ids.index("c1") < ids.index("c2") < ids.index("c3")


def test_seed_catalog_inserts_four():
    seed_catalog()
    import soil
    all_recs = soil.all_records(COLLECTION)
    ids = [r["id"] for r in all_recs]
    assert "git-status" in ids
    assert "open-prs"   in ids
    assert "build"      in ids
    assert "todos"      in ids


def test_seed_catalog_idempotent():
    seed_catalog()
    seed_catalog()
    import soil
    all_recs = soil.all_records(COLLECTION)
    git_recs = [r for r in all_recs if r["id"] == "git-status"]
    assert len(git_recs) == 1


def test_seed_catalog_inserts_disabled():
    seed_catalog()
    import soil
    all_recs = soil.all_records(COLLECTION)
    for r in all_recs:
        if r["id"] in ("git-status", "open-prs", "build", "todos"):
            assert r["enabled"] is False


def test_save_card_upserts():
    save_card({"id": "my-card", "label": "Original", "enabled": True, "order": 1})
    save_card({"id": "my-card", "label": "Updated",  "enabled": True, "order": 1})
    cards = [c for c in load_cards() if c["id"] == "my-card"]
    assert len(cards) == 1
    assert cards[0]["label"] == "Updated"


def test_validate_card_def_rejects_missing_id():
    assert validate_card_def({"label": "No ID"}) is None


def test_validate_card_def_rejects_missing_label():
    assert validate_card_def({"id": "no-label"}) is None


def test_validate_card_def_defaults_order():
    card = validate_card_def({"id": "x", "label": "X"})
    assert card is not None
    assert card["order"] == 50


def test_validate_card_def_defaults_enabled():
    card = validate_card_def({"id": "x", "label": "X"})
    assert card is not None
    assert card["enabled"] is True
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/sean-campbell/github/safe-app-willow-grove
python -m pytest tests/test_card_store.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'widgets.card_store'`

- [ ] **Step 3: Create `widgets/card_store.py`**

```python
"""widgets/card_store.py — SOIL-backed card definition store.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import soil

COLLECTION = "willow-dashboard/cards"

_CATALOG: list[dict] = [
    {"id": "git-status", "label": "Git Status", "category": "dev",   "nav_target": "#pane-git",   "order": 100},
    {"id": "open-prs",   "label": "Open PRs",   "category": "dev",   "nav_target": "#pane-prs",   "order": 101},
    {"id": "build",      "label": "Build",       "category": "dev",   "nav_target": "#pane-build", "order": 102},
    {"id": "todos",      "label": "TODOs",       "category": "tasks", "nav_target": "#pane-todos", "order": 103},
]


def load_cards() -> list[dict]:
    """Return all enabled cards sorted by order."""
    records = soil.all_records(COLLECTION)
    enabled = [r for r in records if r.get("enabled", False)]
    return sorted(enabled, key=lambda r: r.get("order", 50))


def save_card(card: dict) -> None:
    """Upsert card by id."""
    soil.put(COLLECTION, card["id"], card)


def seed_catalog() -> None:
    """Insert disabled catalog cards if not already present."""
    existing_ids = {r["_id"] for r in soil.all_records(COLLECTION)}
    for template in _CATALOG:
        if template["id"] not in existing_ids:
            soil.put(COLLECTION, template["id"], {
                **template,
                "built_in": False,
                "enabled": False,
                "value_query": None,
                "state_query": None,
                "refresh_interval": 30,
            })


def validate_card_def(raw: dict) -> dict | None:
    """Validate and normalize a card-def dict. Returns normalized dict or None."""
    card_id = raw.get("id")
    label   = raw.get("label")
    if not card_id or not isinstance(card_id, str):
        return None
    if not label or not isinstance(label, str):
        return None
    return {
        "id":               card_id,
        "label":            label,
        "category":         raw.get("category", "custom"),
        "built_in":         False,
        "enabled":          bool(raw.get("enabled", True)),
        "order":            int(raw.get("order", 50)),
        "value_query":      raw.get("value_query"),
        "state_query":      raw.get("state_query"),
        "refresh_interval": int(raw.get("refresh_interval", 30)),
        "nav_target":       raw.get("nav_target"),
    }
```

- [ ] **Step 4: Run tests — all 11 should pass**

```bash
python -m pytest tests/test_card_store.py -v
```

Expected:
```
PASSED tests/test_card_store.py::test_save_and_load_card
PASSED tests/test_card_store.py::test_load_cards_only_enabled
PASSED tests/test_card_store.py::test_load_cards_sorted_by_order
PASSED tests/test_card_store.py::test_seed_catalog_inserts_four
PASSED tests/test_card_store.py::test_seed_catalog_idempotent
PASSED tests/test_card_store.py::test_seed_catalog_inserts_disabled
PASSED tests/test_card_store.py::test_save_card_upserts
PASSED tests/test_card_store.py::test_validate_card_def_rejects_missing_id
PASSED tests/test_card_store.py::test_validate_card_def_rejects_missing_label
PASSED tests/test_card_store.py::test_validate_card_def_defaults_order
PASSED tests/test_card_store.py::test_validate_card_def_defaults_enabled
11 passed
```

- [ ] **Step 5: Commit**

```bash
git add widgets/card_store.py tests/test_card_store.py
git commit -m "feat(cards): SOIL card store — load, save, seed, validate"
```

---

## Task 2: `grove_db.py` — `ensure_card_builder_channel()`

**Files:**
- Modify: `grove_db.py`

- [ ] **Step 1: Add `ensure_card_builder_channel()` to `grove_db.py`**

Append this function after the `archive_channel` function (after line 184):

```python
def ensure_card_builder_channel() -> None:
    """Idempotent: create #card-builder channel with agent_name='heimdallr' if absent."""
    import os
    import psycopg2
    try:
        pg_db   = os.environ.get("WILLOW_PG_DB", "willow_19")
        pg_user = os.environ.get("WILLOW_PG_USER", os.environ.get("USER", ""))
        conn = psycopg2.connect(dbname=pg_db, user=pg_user, connect_timeout=2)
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO grove.channels (name, channel_type, description, agent_name)
            VALUES ('card-builder', 'group', 'Heimdallr card builder interview', 'heimdallr')
            ON CONFLICT (name) DO NOTHING
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass
```

- [ ] **Step 2: Verify the existing test suite still passes**

```bash
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -10
```

Expected: existing tests pass, no new failures.

- [ ] **Step 3: Commit**

```bash
git add grove_db.py
git commit -m "feat(cards): ensure_card_builder_channel() — idempotent #card-builder provisioning"
```

---

## Task 3: `widgets/card_grid.py` — dynamic reload + `+` card

**Files:**
- Modify: `widgets/card_grid.py`

- [ ] **Step 1: Add `reload()` and `_nav_cache` to `CardGrid`**

Replace the entire `CardGrid` class in `widgets/card_grid.py` (lines 252–297) with:

```python
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
        self._cards: list[tuple[str, str]] = cards
        self._nav_cache: dict[str, str]    = {cid: _CARD_NAV.get(cid, "") for cid, _ in cards}

    def compose(self) -> ComposeResult:
        for card_id, label in self._cards:
            nav = self._nav_cache.get(card_id, "")
            yield CardCell(card_id, label, nav_target=nav, id=f"cell-{card_id}")

    def on_mount(self) -> None:
        self._fetch()
        self.set_interval(30, self._fetch)

    def reload(self) -> None:
        """Rebuild cells from SOIL enabled cards + built-ins + plus card."""
        from widgets import card_store
        soil_cards = [
            (c["id"], c["label"], c.get("nav_target") or "")
            for c in card_store.load_cards()
        ]
        builtin = [(cid, lbl, _CARD_NAV.get(cid, "")) for cid, lbl in BUILTIN_CARDS]
        all_entries = soil_cards + builtin + [("+", "+ Add Card", "+")]

        self._cards      = [(cid, lbl) for cid, lbl, _ in all_entries]
        self._nav_cache  = {cid: nav for cid, _, nav in all_entries}

        self.remove_children()
        cells = [
            CardCell(cid, lbl, nav_target=self._nav_cache[cid], id=f"cell-{cid}")
            for cid, lbl in self._cards
        ]
        self.mount(*cells)
        self._fetch()

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

- [ ] **Step 2: Verify tests still pass**

```bash
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -10
```

Expected: all existing tests pass.

- [ ] **Step 3: Commit**

```bash
git add widgets/card_grid.py
git commit -m "feat(cards): CardGrid.reload() — dynamic SOIL + built-ins + plus card"
```

---

## Task 4: `panes/home.py` — seed catalog + push modal + `refresh_cards()`

**Files:**
- Modify: `panes/home.py`

- [ ] **Step 1: Replace `HomeGrid` class in `panes/home.py`**

The current `HomeGrid` class (lines 243–255) is:

```python
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
```

Replace it with:

```python
class HomeGrid(Container):
    """Center area for Home — live card grid backed by SOIL + built-ins."""

    DEFAULT_CSS = """
    HomeGrid {
        width: 1fr;
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        from widgets.card_grid import CardGrid, BUILTIN_CARDS
        yield CardGrid(BUILTIN_CARDS)

    def on_mount(self) -> None:
        from widgets import card_store
        from widgets.card_grid import CardGrid
        from textual.css.query import NoMatches
        card_store.seed_catalog()
        try:
            self.query_one(CardGrid).reload()
        except NoMatches:
            pass

    def on_card_activated(self, event) -> None:
        if getattr(event, "nav_target", None) == "+":
            from widgets.card_builder_modal import CardBuilderModal
            self.app.push_screen(CardBuilderModal())

    def refresh_cards(self) -> None:
        from widgets.card_grid import CardGrid
        from textual.css.query import NoMatches
        try:
            self.query_one(CardGrid).reload()
        except NoMatches:
            pass
```

- [ ] **Step 2: Verify tests still pass**

```bash
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -10
```

Expected: all existing tests pass.

- [ ] **Step 3: Commit**

```bash
git add panes/home.py
git commit -m "feat(cards): HomeGrid seeds catalog, handles + card, exposes refresh_cards()"
```

---

## Task 5: `widgets/card_builder_modal.py` — `CardBuilderModal`

**Files:**
- Create: `widgets/card_builder_modal.py`

- [ ] **Step 1: Create `widgets/card_builder_modal.py`**

```python
"""widgets/card_builder_modal.py — Heimdallr card builder interview modal.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

import json
import os
import re
import select

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Input, RichLog, Static

import grove_reader

_CARD_DEF_RE = re.compile(r"```card-def\s*\n(.*?)\n```", re.DOTALL)

_INTRO_PROMPT = (
    "The user wants to add a new card to their Willow Grove dashboard. "
    "Interview them: ask what they want to track, suggest from the available "
    "catalog (git-status, open-prs, build, todos) if relevant, then produce "
    "a ```card-def JSON block with at minimum 'id' and 'label' fields."
)


def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        dbname=os.environ.get("WILLOW_PG_DB",   "willow_19"),
        user=os.environ.get("WILLOW_PG_USER", os.environ.get("USER", "")),
    )


class CardDefDetected(Message):
    """Posted when a valid card-def block is detected and saved to SOIL."""
    def __init__(self, card: dict) -> None:
        self.card = card
        super().__init__()


class CardBuilderModal(ModalScreen):
    """Heimdallr interview modal — chat log + input + card-def detection."""

    DEFAULT_CSS = """
    CardBuilderModal {
        align: center middle;
    }
    CardBuilderModal #cb-dialog {
        width: 80;
        height: 40;
        background: #0d1117;
        border: solid #30363d;
    }
    CardBuilderModal #cb-log {
        height: 1fr;
        padding: 1 2;
    }
    CardBuilderModal #cb-status {
        height: 1;
        padding: 0 2;
        color: #8b949e;
    }
    CardBuilderModal #cb-input {
        height: 3;
        margin: 0 2 1 2;
        border: tall #30363d;
    }
    CardBuilderModal #cb-input:focus {
        border: tall #58a6ff;
    }
    """

    BINDINGS = [Binding("escape", "dismiss", "Close")]

    def __init__(self) -> None:
        super().__init__()
        self._channel_id:  int | None = None
        self._cursor:      int        = 0
        self._listening:   bool       = False
        self._card_saved:  bool       = False

    def compose(self) -> ComposeResult:
        with Vertical(id="cb-dialog"):
            yield RichLog(id="cb-log", highlight=False, markup=True, wrap=True)
            yield Static("[dim]Connecting to Heimdallr…[/]", id="cb-status", markup=True)
            yield Input(placeholder="Message Heimdallr…", id="cb-input")

    def on_mount(self) -> None:
        self._setup()

    @work(thread=True)
    def _setup(self) -> None:
        """Provision channel, load history, dispatch intro if new, start listener."""
        try:
            from grove_db import ensure_card_builder_channel
            ensure_card_builder_channel()
        except Exception:
            pass

        channel_id = None
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            cur.execute("SELECT id FROM grove.channels WHERE name = 'card-builder' LIMIT 1")
            row = cur.fetchone()
            if row:
                channel_id = row[0]
            conn.close()
        except Exception:
            pass

        if channel_id is None:
            self.app.call_from_thread(
                self._set_status, "[red]Could not connect to #card-builder[/]"
            )
            return

        self._channel_id = channel_id

        # Load history
        msgs = grove_reader.grove_messages("card-builder", limit=20)
        self.app.call_from_thread(self._load_history, msgs)

        # Dispatch intro if channel is empty
        if not msgs:
            self._dispatch_intro(channel_id)

        self._start_listener()

    def _dispatch_intro(self, channel_id: int) -> None:
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            cur.execute(
                "SELECT id FROM grove.channels WHERE name = 'dispatch' LIMIT 1"
            )
            row = cur.fetchone()
            if row:
                payload = json.dumps({
                    "to":            "heimdallr",
                    "prompt":        _INTRO_PROMPT,
                    "reply_channel": "card-builder",
                })
                cur.execute(
                    "INSERT INTO grove.messages (channel_id, sender, content)"
                    " VALUES (%s, %s, %s)",
                    (row[0], "dashboard", payload),
                )
                conn.commit()
            conn.close()
        except Exception:
            pass

    def _load_history(self, msgs: list[dict]) -> None:
        log = self.query_one("#cb-log", RichLog)
        log.clear()
        for m in msgs:
            self._append_message(m)
        if msgs:
            self._cursor = msgs[-1]["id"]
        self._set_status("[dim]Waiting for Heimdallr…[/]")

    def _append_message(self, m: dict) -> None:
        from panes.chat import format_ts, render_content, sender_color
        sender  = m.get("sender", "?")
        content = m.get("content", "")
        ts      = format_ts(m.get("created_at"))
        color   = sender_color(sender)
        log = self.query_one("#cb-log", RichLog)
        log.write(
            f"[dim]{ts}[/dim]  [{color} bold]{sender:<14}[/{color} bold]  {render_content(content)}"
        )

    def _set_status(self, text: str) -> None:
        from textual.css.query import NoMatches
        try:
            self.query_one("#cb-status", Static).update(text)
        except NoMatches:
            pass

    @work(thread=True)
    def _start_listener(self) -> None:
        self._listening = True
        try:
            conn = _pg_conn()
            conn.autocommit = True
            cur  = conn.cursor()
            cur.execute("LISTEN grove_channel")
            while self._listening:
                if select.select([conn], [], [], 1.0)[0]:
                    conn.poll()
                    while conn.notifies:
                        n = conn.notifies.pop(0)
                        try:
                            if int(n.payload) == self._channel_id:
                                self.app.call_from_thread(self._on_notify)
                        except (ValueError, TypeError):
                            pass
        except Exception:
            pass

    def _on_notify(self) -> None:
        msgs = grove_reader.grove_messages("card-builder", limit=50)
        new_msgs = [m for m in msgs if m["id"] > self._cursor]
        for m in new_msgs:
            self._append_message(m)
            self._scan_for_card_def(m.get("content", ""))
        if new_msgs:
            self._cursor = new_msgs[-1]["id"]

    def _scan_for_card_def(self, body: str) -> None:
        match = _CARD_DEF_RE.search(body)
        if not match:
            return
        try:
            raw = json.loads(match.group(1))
        except json.JSONDecodeError:
            self._set_status("[red]card-def block contained invalid JSON — waiting for correction…[/]")
            return

        from widgets.card_store import validate_card_def, save_card
        card = validate_card_def(raw)
        if card is None:
            self._set_status("[red]card-def missing required fields (id, label) — waiting…[/]")
            return

        save_card(card)
        self._card_saved = True
        self._post_confirmation(card["label"])
        self._set_status(f"[green]Card '{card['label']}' saved.[/] Press Esc to close or continue.")
        self.post_message(CardDefDetected(card))

    def _post_confirmation(self, label: str) -> None:
        if self._channel_id is None:
            return
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            sender = os.environ.get("GROVE_SENDER") or os.environ.get("USER", "dashboard")
            cur.execute(
                "INSERT INTO grove.messages (channel_id, sender, content)"
                " VALUES (%s, %s, %s)",
                (self._channel_id, sender,
                 f"Card '{label}' saved. Press Esc to close or continue the conversation."),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        body = event.value.strip()
        if not body or self._channel_id is None:
            return
        event.input.value = ""
        sender = os.environ.get("GROVE_SENDER") or os.environ.get("USER", "sean")
        try:
            conn = _pg_conn()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO grove.messages (channel_id, sender, content)"
                " VALUES (%s, %s, %s)",
                (self._channel_id, sender, body),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def on_unmount(self) -> None:
        self._listening = False
```

- [ ] **Step 2: Verify tests still pass**

```bash
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -10
```

Expected: all existing tests pass.

- [ ] **Step 3: Commit**

```bash
git add widgets/card_builder_modal.py
git commit -m "feat(cards): CardBuilderModal — Heimdallr interview + card-def detection + LISTEN/NOTIFY"
```

---

## Task 6: `app.py` — wire modal dismiss + import

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Add `CardBuilderModal` import to `app.py`**

In `app.py`, after the existing widget imports (after line 52, the `from widgets.command_provider` line), add:

```python
from widgets.card_builder_modal import CardBuilderModal
```

- [ ] **Step 2: Add `on_screen_dismiss` to `WillowGrove`**

In `app.py`, add this method to the `WillowGrove` class, after the `action_refresh` method:

```python
    def on_screen_dismiss(self, event) -> None:
        if isinstance(event.screen, CardBuilderModal):
            with suppress(NoMatches):
                self.query_one(HomeGrid).refresh_cards()
```

- [ ] **Step 3: Verify tests still pass**

```bash
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -10
```

Expected: all tests pass.

- [ ] **Step 4: Smoke test — launch and verify the + card and modal**

```bash
python3 app.py
```

- Navigate to Home (press `1` or it's the default).
- Confirm 8 cards are visible: 7 built-ins + `+ Add Card`.
- Click or focus `+ Add Card` and press Enter.
- `CardBuilderModal` overlay appears: chat log, status line, input.
- Press `Esc` → modal dismisses.
- HomeGrid still shows 8 cards (no crash on dismiss).
- Press `q` to quit.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat(cards): wire CardBuilderModal dismiss → HomeGrid.refresh_cards()"
```

---

## Full test suite

After all tasks:

```bash
python -m pytest tests/ -v --tb=short 2>&1 | tail -20
```

Expected: all existing tests pass + 11 new card_store tests. The pre-existing failure in `tests/test_grove_reader.py::test_grove_channels_with_unread` is unrelated to this phase and should be left as-is.
