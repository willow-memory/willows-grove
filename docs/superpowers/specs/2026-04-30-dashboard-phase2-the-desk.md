# Willow Grove Dashboard — Phase 2: The Desk
**Date:** 2026-04-30  
**Author:** Heimdallr  
**Status:** Approved  
b17: WGRV1  ΔΣ=42

---

## What This Is

Fill `DeskPane` — the left column on Home — with live data from sources already wired into the app. No new data bridges. No Gmail or Calendar (those require a file-based bridge deferred to a later phase). The Desk shows what's happening right now: unread channels, @mentions, running tasks, active agents, system load.

---

## Layout

```
┌─ ContextPanel (width 26) ──┐
│ ⚡ ATTENTION               │
│   # general  3             │
│   # architecture  1        │
│   @sean ← hanuman          │
│                             │
│ ▶ RUNNING                  │
│   2 running  4 pending     │
│   embed ████░ 94%          │
│                             │
│ ✓ DONE TODAY               │
│   5 tasks complete         │
│                             │
│ ⚙ SYSTEM                  │
│   ● hanuman  2m ago        │
│   cpu 12%  mem 44%         │
└─────────────────────────────┘
```

---

## Architecture

`DeskPane` is rewritten in `panes/home.py` from a static placeholder into a live `Container`. It holds a single `Static` child that displays the rendered markup string. The core of the pane is a pure function:

```python
def render_desk(data: DeskData) -> str
```

This function takes a `DeskData` dataclass and returns the full Rich markup string for the pane. It is the only testable unit — all widget lifecycle (mount, interval, worker) is glue around it.

A `@work(thread=True)` worker fetches all data off the main thread every 15 seconds. When done, it posts a `_DeskRefreshed` message (private, defined in `panes/home.py`) carrying the new `DeskData`. The main thread handler calls `render_desk` and updates the Static.

---

## Data Sources

| Field | Source | Default |
|---|---|---|
| `unread_channels` | `grove_reader.grove_channels()` — channels where `unread > 0` | `[]` |
| `mentions` | `grove_reader.grove_messages("general", limit=50)` + `grove_reader.grove_messages("architecture", limit=50)` — rows containing `@{sender_name}` | `[]` |
| `open_flags` | `~/.willow/session_anchor.json` → `open_flags` | `0` |
| `running_tasks` | `panes.tasks.fetch_tasks()` → `running` | `0` |
| `pending_tasks` | `panes.tasks.fetch_tasks()` → `pending` | `0` |
| `done_today` | `fetch_tasks()` rows — count where status in (complete, completed) and `ts` starts with today's date (`YYYY-MM-DD`) | `0` |
| `backfill` | `panes.tasks.fetch_backfill_progress()` — `{pct, table}` or `None` | `None` |
| `agents` | `grove_reader.grove_agents()` | `[]` |
| `sysinfo` | `panes.overview.fetch_sysinfo()` — `{cpu, mem, disk, temp}` | `{cpu:0, mem:0, disk:0, temp:0}` |

**@mention detection:** scan message `content` for the string `@` + the value of `GROVE_SENDER` env var, falling back to `GROVE_NAME`, then `USER`. Case-insensitive. Collect `{channel, sender, snippet}` — snippet is the first 20 chars of content.

All fetch failures are caught and leave fields at defaults. The pane never crashes; it just shows zeros.

---

## Rendering

`render_desk` builds four sections. Sections with nothing to show are omitted (except RUNNING and SYSTEM, which always render).

### ⚡ ATTENTION
Shown if: `unread_channels` is non-empty, OR `mentions` is non-empty, OR `open_flags > 0`.

- Each unread channel: `# {name:<14} {unread}` — name left-padded to 14, count right
- Each mention: `[yellow]@{target}[/] ← {sender}` truncated to 24 chars
- Open flags: `[yellow]{n} open flags[/]`

### ▶ RUNNING
Always shown.

- Task line: `{running} running  {pending} pending`
- If `backfill` is set and `table != "done"`: mini bar `embed {bar} {pct:.0f}%` where bar is `█` × floor(pct/20) + `░` × (5 − floor(pct/20))
- If running == 0 and pending == 0: `[dim]idle[/]`

### ✓ DONE TODAY
Shown only if `done_today > 0`.

- `{done_today} task{"s" if done_today != 1 else ""} complete`

### ⚙ SYSTEM
Always shown.

- One line per agent (up to 4): `{dot} {sender:<12} {age_str}` where dot is `[green]●[/]` (< 120s), `[yellow]●[/]` (< 900s), or `[dim]●[/]`; age_str is `{N}m ago` or `{N}h ago`
- If no agents: `[dim]no agents[/]`
- System line: `cpu {cpu}%  mem {mem}%`
- Temp line (only if temp > 0): `temp {temp}°C`

**Formatting constants:**
- Section headers: `[bold #58a6ff]{header}[/]`
- Normal values: `[#c9d1d9]{value}[/]`
- Muted: `[dim]{value}[/]`
- Alert: `[yellow]{value}[/]`
- Sections separated by a single blank line

All text truncated to 24 chars (26-col pane minus 2 padding).

---

## Files

### Modified
| File | Change |
|---|---|
| `panes/home.py` | Rewrite `DeskPane` — add `DeskData` dataclass, `_DeskRefreshed` message, `render_desk()` function, worker-based refresh. `HomeGrid` and `ProjectsGrid` unchanged. |
| `tests/test_panes_home.py` | Add tests for `render_desk` and `DeskData` construction. Existing placeholder tests removed (they test the old static string). |

### Untouched
All other files. `grove_reader.py`, `panes/tasks.py`, `panes/overview.py` are read-only dependencies.

---

## Messages

```python
class _DeskRefreshed(Message):
    def __init__(self, data: DeskData) -> None:
        super().__init__()
        self.data = data
```

Private to `panes/home.py`. Not exported. `DeskPane` posts and handles it internally.

---

## Refresh

- Interval: 15 seconds
- First fetch on `on_mount` (immediate)
- All DB/file I/O in `@work(thread=True)` worker
- No LISTEN/NOTIFY — polling only

---

## What Phase 2 Does NOT Include

- Gmail unread count (needs file-based bridge — Phase 2.5)
- Google Calendar events (same)
- Phone notifications (ntfy bridge — later)
- Clickable items in the Desk (navigation on click — Phase 4)
- Done Today showing task names (count only for Phase 2)

---

## Definition of Done

- `DeskPane` shows live data on Home (nav target 1)
- ATTENTION section appears when Grove has unread channels
- RUNNING section shows current Kart task counts
- DONE TODAY appears when tasks completed today > 0
- SYSTEM section shows active agents and CPU/mem
- `render_desk` is unit-tested with mock `DeskData`
- No crashes when Postgres is down (all sections show zeros/empty)
- Refresh every 15s confirmed by watching counts update
