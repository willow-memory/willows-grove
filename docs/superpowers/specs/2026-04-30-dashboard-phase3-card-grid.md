# Willow Grove Dashboard — Phase 3: Card Grid
**Date:** 2026-04-30
**Author:** Heimdallr
**Status:** Approved
b17: WGRV1  ΔΣ=42

---

## What This Is

Replace the `HomeGrid` and `ProjectsGrid` static placeholders with live Textual card grids. `HomeGrid` shows 7 built-in system cards with live data. `ProjectsGrid` shows 5 launcher tiles that navigate to the internal panes. Cards are focusable and clickable — click or Enter navigates to the matching detail pane.

---

## Layout

```
┌─ HomeGrid ─────────────────────────────────┐
│ ┌─────────────┐ ┌─────────────┐ ┌─────────┐│
│ │ KART QUEUE  │ │  KNOWLEDGE  │ │YGGDRASIL││
│ │          12 │ │       3,847 │ │sonnet-4 ││
│ │   2 running │ │    14 today │ │  model  ││
│ └─────────────┘ └─────────────┘ └─────────┘│
│ ┌─────────────┐ ┌─────────────┐ ┌─────────┐│
│ │    AGENTS   │ │   SECRETS   │ │  FLEET  ││
│ │           3 │ │           9 │ │       4 ││
│ │   h active  │ │    vault    │ │providers││
│ └─────────────┘ └─────────────┘ └─────────┘│
│ ┌─────────────┐                             │
│ │ MCP SERVERS │                             │
│ │           7 │                             │
│ │   connected │                             │
│ └─────────────┘                             │
└─────────────────────────────────────────────┘

┌─ ProjectsGrid ─────────────────────────────┐
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐│
│ │Tasks │ │Agents│ │Route │ │Skill │ │Logs││
│ │  →   │ │  →   │ │  →   │ │  →   │ │ → ││
│ └──────┘ └──────┘ └──────┘ └──────┘ └────┘│
└─────────────────────────────────────────────┘
```

---

## Architecture

### New file: `widgets/card_grid.py`

Contains `CardActivated`, `CardCell`, `CardGrid`, and `fetch_runtime_card_values()`.

```python
class CardActivated(Message):
    def __init__(self, card_id: str, nav_target: str) -> None:
        super().__init__()
        self.card_id = card_id
        self.nav_target = nav_target
```

`CardCell(Widget)` — one focusable card tile. Displays label, value, sub, state color. `BINDINGS = [("enter", "activate", "Open")]`. Posts `CardActivated` on key enter or click.

`CardGrid(Widget)` — composes N `CardCell` children via CSS grid layout. Has a `@work(thread=True)` worker that runs `refresh_card_values(cards)` + `fetch_runtime_card_values()` every 30 seconds. Posts `_CardsRefreshed` (private message) to main thread when done; main thread updates each `CardCell`.

### Modified: `panes/home.py`

`HomeGrid` changes from `Static` to `Container`. Its `compose()` yields a single `CardGrid` built from the 7 built-in `CardDef` seeds.

`ProjectsGrid` changes from `Static` to `Container`. Its `compose()` yields 5 hardcoded `CardCell` launcher tiles (no live data).

### Modified: `app.py`

Add `on_card_activated(event: CardActivated)` to `WillowGrove`:
- If `event.nav_target` starts with `#`: hide all panes, show that internal pane directly.
- Otherwise: call `action_nav(event.nav_target)` (existing content nav).

---

## Data Sources

### Cards with SQL queries (handled by `cards.py refresh_card_values`)

| Card | value | sub | state |
|------|-------|-----|-------|
| Kart Queue | `SELECT COUNT(*) FROM public.tasks WHERE status='pending'` | `SELECT COUNT(*) FROM public.tasks WHERE status='running'` → `"{} running"` | amber if >10 pending, green if >0, dim otherwise |
| Knowledge | `SELECT COUNT(*) FROM public.knowledge` | count added in last 24h → `"{} today"` | `blue` |

### Runtime-only cards (handled by `fetch_runtime_card_values` in `widgets/card_grid.py`)

| Card | value | sub | state |
|------|-------|-----|-------|
| Yggdrasil | `os.environ.get("WILLOW_MODEL", "—")` | `"active model"` | `dim` |
| Agents | `len(grove_reader.grove_agents())` | most recent sender or `"none"` | green if any agent age_secs < 120, yellow if < 900, dim otherwise |
| Secrets | count keys in `~/.willow/secrets.json` if exists, else `"—"` | `"vault"` | `dim` |
| Fleet | count non-empty `WILLOW_*_KEY` env vars | `"providers"` | `dim` |
| MCP Servers | count servers in `.mcp.json` `mcpServers` dict | `"connected"` | `dim` |

All failures default to value `"—"`, sub `""`, state `""`.

---

## Navigation Map

| Card / Tile | `nav_target` | Handler |
|---|---|---|
| Kart Queue | `#pane-tasks` | show internal pane |
| Knowledge | `knowledge` | `action_nav("knowledge")` |
| Yggdrasil | `providers` | `action_nav("providers")` |
| Agents | `#pane-agents` | show internal pane |
| Secrets | `""` | no navigation |
| Fleet | `providers` | `action_nav("providers")` |
| MCP Servers | `providers` | `action_nav("providers")` |
| Tasks (launcher) | `#pane-tasks` | show internal pane |
| Agents (launcher) | `#pane-agents` | show internal pane |
| Routing (launcher) | `#pane-routing` | show internal pane |
| Skills (launcher) | `#pane-skills` | show internal pane |
| Logs (launcher) | `#pane-logs` | show internal pane |

---

## State Colors

| State string | Color |
|---|---|
| `green` | `#3fb950` |
| `amber` | `#d29922` |
| `red` | `#f85149` |
| `blue` | `#58a6ff` |
| `dim` / `""` | `#8b949e` |

---

## Refresh

- Interval: 30 seconds
- First fetch on `on_mount` (immediate)
- All I/O in `@work(thread=True)` worker
- No crashes when Postgres is down — all sources individually guarded

---

## Files

### New
| File | Responsibility |
|---|---|
| `widgets/card_grid.py` | `CardActivated`, `CardCell`, `CardGrid`, `fetch_runtime_card_values` |
| `tests/test_widgets_card_grid.py` | Unit tests for `fetch_runtime_card_values` and `CardCell` rendering logic |

### Modified
| File | Change |
|---|---|
| `panes/home.py` | `HomeGrid` → Container with `CardGrid`; `ProjectsGrid` → Container with 5 launcher `CardCell` tiles |
| `app.py` | Add `on_card_activated()` handler; add `_show_internal_pane()` helper |

### Untouched
`cards.py`, `grove_reader.py`, `panes/tasks.py` — read-only dependencies.

---

## What Phase 3 Does NOT Include

- Expanded card view (table rows, actions — Phase 4)
- SOIL-based optional cards (Projects, Goals, etc. — Phase 4)
- Keyboard arrow navigation within the grid (Tab only — Phase 4)
- Adding or editing cards from the UI (Phase 4)

---

## Definition of Done

- HomeGrid shows 7 live cards with correct values from DB/runtime sources
- ProjectsGrid shows 5 launcher tiles
- Clicking/Enter on a card navigates to the matching pane
- Cards with no `nav_target` do nothing on click
- State colors update on refresh
- No crash when Postgres is down (cards show `—`)
- Refresh every 30s confirmed by watching values update
- `fetch_runtime_card_values` is unit-tested with mock env/files
