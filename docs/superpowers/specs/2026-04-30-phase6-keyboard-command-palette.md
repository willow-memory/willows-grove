# Phase 6: Keyboard Polish + Command Palette — Design Spec
b17: WGRV1  ΔΣ=42

## Goal

Make the dashboard feel native to terminal users. Three additions: a command palette (Ctrl+P) for fuzzy nav and actions, a `?` keymap overlay for key discovery, and j/k cursor aliases in all list/table widgets.

## Architecture

Three changes, all contained:

1. **New file: `widgets/command_provider.py`** — `WillowCommandProvider(Provider)`. Registered on the app via `COMMANDS = {WillowCommandProvider}`. Textual handles the fuzzy match UI, keyboard navigation, and theming.

2. **`KeymapScreen(ModalScreen)`** — inline in `app.py` (~30 lines). Pushed with `?`, dismissed with `Esc` or `?`. No new file.

3. **BINDINGS additions in `WillowGrove`** — `?`, `ctrl+p`, `j`, `k`. Two new app-level actions forward cursor movement to the focused widget.

---

## Components

### `widgets/command_provider.py`

```python
from textual.command import Provider, Hit, Hits
```

`WillowCommandProvider(Provider)` yields three groups:

**Nav targets** (8, always present):

| Display | Fuzzy text | Callback |
|---------|-----------|----------|
| Go to Home | home | `app.action_nav("home")` |
| Go to Chat | chat | `app.action_nav("chat")` |
| Go to Projects | projects | `app.action_nav("projects")` |
| Go to Knowledge | knowledge | `app.action_nav("knowledge")` |
| Go to Providers | providers | `app.action_nav("providers")` |
| Go to Health | health | `app.action_nav("health")` |
| Go to Settings | settings | `app.action_nav("settings")` |
| Go to Help | help | `app.action_nav("help")` |

**Actions** (static):

| Display | Callback |
|---------|----------|
| Refresh | `app.action_refresh()` |
| Quit | `app.action_quit()` |

**Channels** (live, fetched once per search session):

| Display | Callback |
|---------|----------|
| Open #general | `app.action_nav("chat")` + `app.query_one(ChatPane)._open_channel("general")` |
| Open #architecture | same pattern |
| … | … |

Channels are fetched via `grove_reader.grove_channels()` in `search()`. Cached for the duration of the palette session. Failure is silent — channels omitted if Postgres is down.

Each hit: `match_display` (label shown), `text` (fuzzy match string), `callback` (runs on Enter).

---

### `KeymapScreen(ModalScreen)` — inline in `app.py`

Modal pushed by `action_keymap()`. Content:

```
  Keys        Action
  ──────────────────────────────
  1 – 8       Navigate to tab
  j / k       Move cursor down / up
  Ctrl+P      Command palette
  ?           This help
  r           Refresh
  q           Quit
  Enter       Select / open
  Esc         Close / back
```

Width: 44 cols, centered on screen. Background `#0d1117`, header `#58a6ff`, body `#8b949e`. Dismissed with `Esc` or `?`.

---

### `WillowGrove` BINDINGS additions

```python
Binding("?",      "keymap",          "Keys"),
Binding("ctrl+p", "command_palette", "Commands", show=False),
Binding("j",      "cursor_down",     show=False),
Binding("k",      "cursor_up",       show=False),
```

Existing `1`–`8` bindings: change `show=False` → `show=True` so they appear in the `?` overlay.

---

### j/k actions — `WillowGrove`

```python
def action_cursor_down(self) -> None:
    focused = self.focused
    if focused and not isinstance(focused, Input):
        with suppress(AttributeError):
            focused.action_cursor_down()

def action_cursor_up(self) -> None:
    focused = self.focused
    if focused and not isinstance(focused, Input):
        with suppress(AttributeError):
            focused.action_cursor_up()
```

`suppress` from `contextlib`. Works for `DataTable`, `ListView`, and any future focusable list. No-ops silently for widgets without cursor movement. No-ops when `Input` has focus so typing `j`/`k` in the message bar is unaffected.

---

## Files

### New
| File | Responsibility |
|------|---------------|
| `widgets/command_provider.py` | `WillowCommandProvider` — nav, action, and channel hits |
| `tests/test_widgets_command_provider.py` | Unit tests (see Testing) |

### Modified
| File | Change |
|------|--------|
| `app.py` | Add `KeymapScreen`, `action_keymap`, `action_cursor_down`, `action_cursor_up`; register `COMMANDS`; update BINDINGS |

---

## Testing

`tests/test_widgets_command_provider.py` — pure function tests, no Textual or DB required:

```python
def test_nav_hits_cover_all_targets():
    # WillowCommandProvider._nav_hits() returns 8 entries
    # one per NAV_TARGETS entry
    hits = _nav_hits()
    assert len(hits) == 8
    names = [h["text"] for h in hits]
    assert "home" in names
    assert "help" in names

def test_action_hits():
    hits = _action_hits()
    texts = [h["text"] for h in hits]
    assert "Refresh" in texts
    assert "Quit" in texts

def test_channel_hits_empty_on_failure():
    # grove_channels() raises → returns []
    hits = _channel_hits(lambda: (_ for _ in ()).throw(Exception("db down")))
    assert hits == []

def test_channel_hits_returns_open_prefix():
    channels = [{"name": "general"}, {"name": "architecture"}]
    hits = _channel_hits(lambda: channels)
    assert any("general" in h["text"] for h in hits)
    assert all(h["text"].startswith("Open #") or "general" in h["text"] for h in hits)

def test_channel_hit_display_format():
    channels = [{"name": "general"}]
    hits = _channel_hits(lambda: channels)
    assert hits[0]["display"] == "Open #general"
```

`_nav_hits()`, `_action_hits()`, `_channel_hits(fetch_fn)` are extracted pure functions in `command_provider.py` — `_channel_hits` takes a callable so tests can inject fake data without patching.

---

## Error Handling

- Postgres down → channel hits silently absent, nav and action hits unaffected
- `focused.action_cursor_down()` not present → `suppress(AttributeError)` catches it
- `KeymapScreen` is static markup — no failure path

---

## Out of Scope

- Palette actions that dispatch to Heimdallr (Phase 7 — once project cards exist, the palette will surface "enable git-status card" etc.)
- Palette history / recently used
- `gg` / `G` for first/last row (arrow keys suffice for now)
- Mouse click on `?` in the footer to open keymap
