# Dashboard Phase 4a: Projects ContextPanel Nav — Design Spec
b17: WGRV1  ΔΣ=42

## Goal

When the user navigates to **Projects**, the left `ContextPanel` shows a live navigator listing the 5 internal panes (Tasks, Agents, Routing, Skills, Logs) with count badges. Clicking or pressing Enter on a row navigates the main area to that pane.

## Architecture

### New file: `widgets/projects_nav.py`

Two classes:

**`ProjectsNavRow(Widget)`**
- `can_focus = True`
- `BINDINGS = [("enter", "activate", "Open")]`
- Constructor: `card_id: str`, `label: str`, `nav_target: str`
- Renders: colored dot + label + right-aligned count badge
- `update_row(count: str, state: str)` — refreshes badge and dot color
- `action_activate()` → posts `CardActivated(self.card_id, self.nav_target)`
- `on_click()` → `action_activate()`

**`ProjectsNav(Widget)`**
- Composes 5 `ProjectsNavRow` children (one per internal pane)
- `on_mount`: calls `_fetch()` + sets 10s interval
- `@work(thread=True) _fetch()` — gathers counts from all sources, posts `_NavRefreshed`
- `on__nav_refreshed()` — calls `row.update_row()` for each item

### Counts per row

| Row | `card_id` | `nav_target` | Count source | Badge color |
|-----|-----------|--------------|--------------|-------------|
| Tasks | `tasks` | `#pane-tasks` | `fetch_tasks()["running"]` | yellow if >0, dim if 0 |
| Agents | `agents` | `#pane-agents` | `len(grove_reader.grove_agents())` | green if >0, dim if 0 |
| Routing | `routing` | `#pane-routing` | `len(grove_reader.routing_decisions())` | dim |
| Skills | `skills` | `#pane-skills` | count `.md` files in `~/.willow/skills/` | dim |
| Logs | `logs` | `#pane-logs` | `"live"` (static) | dim |

All sources individually guarded — any failure returns `"—"` for that row's count.

### Modify `app.py` — `ContextPanel`

- `compose()` adds `ProjectsNav(id="ctx-projects")`
- `ctx_map` in `_show_target()` adds `"projects": "#ctx-projects"`

### CSS

`ProjectsNavRow` styled like a channel row: full width, 1-line height, padding `0 1`, focus highlight via `&:focus { background: #21262d; }`.

## Data Flow

```
ProjectsNav._fetch() [thread]
  → fetch_tasks(), grove_reader.grove_agents(), grove_reader.routing_decisions(), skills file count
  → post _NavRefreshed(counts)

ProjectsNav.on__nav_refreshed()
  → row.update_row(count, state) for each ProjectsNavRow

ProjectsNavRow.action_activate()
  → post CardActivated(card_id, nav_target)

app.py.on_card_activated()           [already wired]
  → _show_internal_pane("#pane-xxx")
```

## Testing

`tests/test_widgets_projects_nav.py`:
- `ProjectsNavRow` stores `card_id` and `nav_target`
- `update_row()` accepts count string and state without raising
- `_NavRefreshed` carries per-item dict with `count` and `state` keys
- `_fetch_nav_counts()` (extracted pure function) returns dict for all 5 IDs
- `_fetch_nav_counts()` never raises even when all sources fail
- Count values are strings
- Skills count returns `"—"` when directory missing

## Out of Scope

- Keyboard arrow-key navigation between rows (Tab suffices for now)
- Inline task creation from nav panel
- Filtering/sorting rows
