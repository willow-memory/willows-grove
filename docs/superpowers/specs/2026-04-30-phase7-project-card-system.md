# Phase 7: Project Card System — Design Spec
b17: WGRV1  ΔΣ=42

## Goal

Add a `+` card to HomeGrid that launches a Heimdallr-driven interview for building new dashboard cards. Cards are stored in SOIL, loaded dynamically, and an optional catalog of disabled dev cards (git-status, open-prs, build, todos) is seeded on first run.

## Architecture

Four responsibilities, four boundaries:

1. **`widgets/card_store.py`** — SOIL r/w layer for card definitions. Pure data, no Textual imports.
2. **`widgets/card_grid.py`** (modified) — loads SOIL cards + built-ins dynamically; appends `+` card.
3. **`panes/home.py`** (modified) — `HomeGrid` seeds catalog on mount, pushes `CardBuilderModal` on `+`.
4. **`widgets/card_builder_modal.py`** — `CardBuilderModal(ModalScreen)`: chat log + input, LISTEN/NOTIFY on `#card-builder`, `card-def` block detection → SOIL write → HomeGrid reload on dismiss.

Supporting changes: `grove_db.py` gains `ensure_card_builder_channel()`, `app.py` gains `on_screen_dismiss` hook for HomeGrid reload.

---

## Components

### `widgets/card_store.py`

SOIL collection: `willow-dashboard/cards`

**Card schema:**
```python
{
    "id":               str,       # unique key, e.g. "git-status"
    "label":            str,       # display name
    "category":         str,       # "dev" | "tasks" | "knowledge" | etc.
    "built_in":         bool,      # True = not deletable
    "enabled":          bool,      # False = hidden from HomeGrid
    "order":            int,       # sort order
    "value_query":      str | None,
    "state_query":      str | None,
    "refresh_interval": int,       # seconds, default 30
    "nav_target":       str | None,
}
```

**API:**
```python
COLLECTION = "willow-dashboard/cards"

def load_cards() -> list[dict]:
    """Return all enabled cards sorted by order."""

def save_card(card: dict) -> None:
    """Upsert card by id."""

def seed_catalog() -> None:
    """Insert disabled catalog cards if not already present."""
```

**Catalog seeds** (all `enabled: False`, `order: 100+`):

| id | label | nav_target |
|----|-------|------------|
| `git-status` | Git Status | `#pane-git` |
| `open-prs` | Open PRs | `#pane-prs` |
| `build` | Build | `#pane-build` |
| `todos` | TODOs | `#pane-todos` |

Seeded once from `HomeGrid.on_mount()` — idempotent, skips existing ids.

---

### `widgets/card_grid.py` (modified)

`CardGrid.reload()` replaces hardcoded card list with:
```python
def reload(self) -> None:
    self._cards = card_store.load_cards() + BUILTIN_CARDS + [PLUS_CARD]
    self.refresh()
```

`PLUS_CARD`:
```python
CardCell(id="+", label="+", subtitle="Add card", nav_target="+")
```

`CardActivated(nav_target="+")` is already emitted by the existing click handler — no change needed there.

---

### `panes/home.py` (modified)

`HomeGrid.on_mount()`:
```python
def on_mount(self) -> None:
    card_store.seed_catalog()
    self.query_one(CardGrid).reload()
```

`HomeGrid.on_card_activated()`:
```python
def on_card_activated(self, event: CardActivated) -> None:
    if event.nav_target == "+":
        self.app.push_screen(CardBuilderModal())
```

`HomeGrid.refresh_cards()`:
```python
def refresh_cards(self) -> None:
    self.query_one(CardGrid).reload()
```

---

### `grove_db.py` (modified)

```python
def ensure_card_builder_channel() -> None:
    """Idempotent INSERT of #card-builder with agent_name='heimdallr'."""
```

Called once from `CardBuilderModal.on_mount()`.

---

### `widgets/card_builder_modal.py`

`CardBuilderModal(ModalScreen)` layout:
```
┌─────────────────────────────────────┐
│ RichLog  #cb-log                    │
│                                     │
│ Static   #cb-status                 │
│ Input    #cb-input                  │
└─────────────────────────────────────┘
```

**Mount sequence:**
1. `grove_db.ensure_card_builder_channel()`
2. Load last 20 messages from `#card-builder` → render into `#cb-log`
3. Start LISTEN/NOTIFY on `grove.messages` (same pattern as `ChatPane._start_listener`)
4. If channel is empty: dispatch Heimdallr intro via `grove_db.insert_dispatch()`

**Intro prompt** (sent once, when channel is empty):
> "The user wants to add a new card to their Willow Grove dashboard. Interview them: ask what they want to track, suggest from the catalog if relevant, then produce a `card-def` JSON block."

**LISTEN/NOTIFY callback:**
1. Append new message to `#cb-log`
2. Scan body for ` ```card-def ` fenced block
3. If found → validate → SOIL write → update `#cb-status` → set `self._card_saved = True`

**Validation** (minimal):
- `id` present, non-empty string
- `label` present, non-empty string
- `order` int (default 50 if absent)
- `enabled` bool (default `True` if absent)

Validation failure → log to `#cb-status`, continue listening. Heimdallr may produce a corrected block.

**card-def detection:**
```python
_CARD_DEF_RE = re.compile(r"```card-def\s*\n(.*?)\n```", re.DOTALL)

def _scan_for_card_def(self, body: str) -> dict | None:
    m = _CARD_DEF_RE.search(body)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
```

**On valid card-def:**
1. `card_store.save_card(card)`
2. Post confirmation to `#card-builder`: `"Card '[label]' saved. Press Esc to close or continue."`
3. Update `#cb-status`: `"[green]Card saved.[/] Press Esc to close."`
4. `self._card_saved = True`

**Dismissal:** `Esc` closes modal. `WillowGrove` calls `HomeGrid.refresh_cards()` after dismiss.

```python
BINDINGS = [Binding("escape", "dismiss", "Close")]
```

---

### `app.py` (modified)

Import `CardBuilderModal`. Add dismiss handler:

```python
def on_screen_dismiss(self, event) -> None:
    with suppress(NoMatches):
        self.query_one(HomeGrid).refresh_cards()
```

---

### `CardDefDetected` message

```python
class CardDefDetected(Message):
    def __init__(self, card: dict) -> None:
        self.card = card
        super().__init__()
```

Posted by modal on successful SOIL write. Available for future listeners (e.g., a catalog pane).

---

## Files

### New
| File | Responsibility |
|------|---------------|
| `widgets/card_store.py` | SOIL r/w for card defs; catalog seeding |
| `widgets/card_builder_modal.py` | `CardBuilderModal` — chat overlay + card-def detection |
| `tests/test_card_store.py` | Unit tests for card_store pure functions |

### Modified
| File | Change |
|------|--------|
| `widgets/card_grid.py` | Dynamic load from SOIL + built-ins; `+` card; `reload()` method |
| `panes/home.py` | Seed catalog on mount; push modal on `+`; `refresh_cards()` |
| `grove_db.py` | `ensure_card_builder_channel()` |
| `app.py` | Import modal; `on_screen_dismiss` → `refresh_cards()` |

---

## Testing

`tests/test_card_store.py` — pure function tests, no Textual or DB required:

```python
def test_save_and_load_card():
    # save a card, load_cards returns it

def test_load_cards_only_enabled():
    # disabled card not returned by load_cards()

def test_load_cards_sorted_by_order():
    # cards returned in order asc

def test_seed_catalog_inserts_four():
    # seed_catalog() inserts git-status, open-prs, build, todos

def test_seed_catalog_idempotent():
    # calling seed_catalog() twice doesn't duplicate

def test_save_card_upserts():
    # saving same id twice updates, doesn't duplicate

def test_card_def_validation_rejects_missing_id():
    # card without id fails validation

def test_card_def_validation_rejects_missing_label():
    # card without label fails validation

def test_card_def_validation_defaults_order():
    # card without order gets order=50

def test_card_def_validation_defaults_enabled():
    # card without enabled gets enabled=True
```

`card_store` tests use a temp SOIL path via monkeypatch to avoid polluting `~/.willow/store`.

---

## Error Handling

- Postgres down → modal shows error in `#cb-status`, user can close
- `ensure_card_builder_channel()` fails → modal catches, logs, continues (channel creation is best-effort)
- Heimdallr produces malformed `card-def` → validation fails silently, modal stays open
- SOIL write fails → `#cb-status` shows error, `_card_saved` stays False, HomeGrid not reloaded

---

## Out of Scope

- Editing or deleting existing cards from HomeGrid (Phase 8)
- Enabling catalog cards from a settings pane (Phase 8)
- Live card value queries (git-status, open-prs etc. need their own panes — shells exist as disabled seeds)
- Palette integration ("enable git-status card") — noted in Phase 6 spec as Phase 7 deliverable, deferred to Phase 8 now that the card system is scoped
