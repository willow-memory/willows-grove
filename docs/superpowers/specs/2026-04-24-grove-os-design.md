# Grove OS — The Unified App Surface
**Date:** 2026-04-24  
**Status:** Design — tabs as default test layout  
**Vision:** MySpace for the AI dashboard age. Every human configures their own Grove.

---

## The Idea in One Sentence

Grove is a terminal desktop. Apps live inside it. The layout is yours.

---

## The Apps (v1)

| ID         | Label         | What it is                                              |
|------------|---------------|---------------------------------------------------------|
| `chat`     | Chat          | Grove channels. Discord/Slack skin. OpenClaw-backed.    |
| `journal`  | Journal       | Daily log. Write, search, read past entries.            |
| `utety`    | UTETY         | Professor chat. Ask Jeles. Route to specialists.        |
| `models`   | Models        | Switch model instantly. Local (Ollama) or API. Per-task.|
| `tasks`    | Tasks         | Kart queue. Submit, monitor, cancel.                    |
| `agents`   | Agents        | Who's running, on what, since when. Open session card.  |
| `vitals`   | Vitals        | pg · ollama · kart · soil · ledger. Always-on strip.    |
| `routing`  | Routing       | Live decision feed from willow_route.                   |

Each app is a self-contained widget class. It knows how to:
- `render(pane)` — draw itself into any curses subwindow
- `handle_key(key)` — handle keyboard input when focused
- `handle_mouse(x, y, btn)` — handle mouse clicks within its bounds
- `tick()` — refresh data (called on poll cadence)

Apps have no opinion about layout. Layout is the shell's job.

---

## Layout Engine

A `Layout` is a config object that maps **regions** to **apps**.

```python
@dataclass
class Region:
    row: int          # top row (0-indexed, % of terminal height or absolute)
    col: int          # left col
    height: int       # rows (% or absolute)
    width: int        # cols (% or absolute)
    app_id: str       # which app fills this region
    unit: str         # "pct" | "abs"

@dataclass  
class Layout:
    id: str
    label: str
    regions: list[Region]
    min_cols: int = 80
    min_rows: int = 24
```

Grove reads `~/.willow/grove/layout.json` at startup. If missing, loads the default preset.

**The shell loop:**
1. Terminal resize → recalculate region bounds → re-render all
2. Mouse click → find region at (x,y) → focus that region → route to app
3. Keypress → route to focused app (or global handler if not consumed)

---

## The 10,000,000 Layouts (the point of the whole thing)

These are just presets. Users can override any of them or write their own.

### `tabs` — Default test layout
```
╭─ Grove ──────────────────────────────────────────────── pg● 13:04 ─╮
│ [Chat]  Journal  UTETY  Models  Tasks  Agents                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│                    [ active app — full pane ]                      │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│ ● hanuman  ◐ ganesha  ○ jeles           nomic-embed · yggdrasil:v9 │
╰────────────────────────────────────────────────────────────────────╯
```
Top tab bar. One app at a time. Status strip always pinned bottom.
Click a tab or press its number key. Clean. Fast. Familiar.

---

### `discord` — Chat-first, channel sidebar
```
╭────╮ ╭──────────────────────╮ ╭──────────────────────────────────╮ ╭────────────╮
│    │ │ # general            │ │                                  │ │ ● hanuman  │
│ ⬡  │ │ ▌# architecture   2●│ │  hanuman            13:04        │ │ ● ganesha  │
│    │ │ # handoffs           │ │    routed → ganesha              │ │ ○ jeles    │
│ ✎  │ │ # readme             │ │                                  │ ├────────────┤
│    │ ├──────────────────────┤ │  ganesha            13:01        │ │ Models     │
│ 🎓 │ │ pg● olla● kart 3/5   │ │    resuming                      │ │ yggdrasil  │
│    │ ╰──────────────────────╯ │                                  │ │ :v9        │
│ ⚡ │                          │ ╭──────────────────────────────╮ │ ╰────────────╯
╰────╯                          │ │ Message...                   │ │
                                 │ ╰──────────────────────────────╯ │
                                 ╰──────────────────────────────────╯
```
Left app dock (icons). Channel list. Main chat. Members + model widget right.

---

### `slack` — Sidebar-first
```
╭──────────────────────╮ ╭──────────────────────────────────────────────────╮
│ ⬡ Willow             │ │ # architecture                      ─ 2 new ─── │
├──────────────────────┤ ├──────────────────────────────────────────────────┤
│  ↑ Routing           │ │  hanuman                               13:04     │
│                      │ │    routed "debug gleipnir" → ganesha             │
│  ▸ Channels          │ │                                                  │
│    ▌# architecture 2 │ │  ganesha                               13:01     │
│      # general       │ │    resuming                                      │
│  ▸ Agents            │ ├──────────────────────────────────────────────────┤
│    ● hanuman         │ │  Message #architecture...                        │
│    ○ jeles           │ ╰──────────────────────────────────────────────────╯
├──────────────────────┤
│ ● USER  yggdrasil:v9 │
╰──────────────────────╯
```

---

### `mission-control` — Power user, everything visible
```
╭──────────────────╮ ╭──────────────────╮ ╭──────────────────╮ ╭──────────────────╮
│ VITALS           │ │ AGENTS           │ │ ROUTING          │ │ MODELS           │
│ pg● olla● kart   │ │ ● hanuman  12m   │ │ 13:04 → ganesha  │ │ ▌yggdrasil:v9    │
│ soil● ledger ok  │ │ ● ganesha   6m   │ │ 13:01 → jeles    │ │   yggdrasil:v8   │
╰──────────────────╯ ╰──────────────────╯ ╰──────────────────╯ │   qwen2.5:3b     │
╭────────────────────────────────────────────────────────────╮ │   claude-opus    │
│ CHAT — # architecture                                      │ ╰──────────────────╯
│                                                            │
│  hanuman  13:04  routed "debug gleipnir" → ganesha         │
│  ganesha  13:01  resuming                                  │
│                                                            │
│ ╭────────────────────────────────────────────────────────╮ │
│ │ Message...                                             │ │
│ ╰────────────────────────────────────────────────────────╯ │
╰────────────────────────────────────────────────────────────╯
```

---

### `minimal` — Just the work
```
╭─ # architecture ──────────────────────────────── yggdrasil:v9 · pg● ─╮
│                                                                       │
│  hanuman  13:04   routed "debug gleipnir" → ganesha                  │
│  ganesha  13:01   resuming                                            │
│                                                                       │
│ ╭───────────────────────────────────────────────────────────────────╮ │
│ │ Message...                                                        │ │
│ ╰───────────────────────────────────────────────────────────────────╯ │
╰───────────────────────────────────────────────────────────────────────╯
```
No chrome. One app. One model. One channel. Full focus.

---

### `journal-first` — Writer's layout
```
╭─ Journal ──────────────────────────────────────────── 2026-04-24 ─╮
│ ▸ Today                                                           │
│   ▸ Yesterday                                                     │  ← file tree left
│   ▸ This week                                                     │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ## 2026-04-24                                                    │  ← editor right
│                                                                   │
│  Started the Grove OS spec. OpenClaw memory is live.             │
│  nomic-embed-text pulling, gateway started on 18789.             │
│  _                                                                │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯
```

---

### `vim-mode` — Keyboard everything, no mouse required
Same layouts, all navigation via `hjkl`, `:app chat`, `:model yggdrasil:v9`, `:channel architecture`. For the terminal purist who considers mouse use a personal failing.

---

### `mobile` — Narrow terminal (≤80 cols)
Single column. App switcher is a bottom dock (`1` `2` `3` `4`). Vitals collapsed to one line. Designed for SSH from a phone.

---

### `student` — UTETY-first
Professor chat fills 70% of the pane. Model picker always visible top-right. Chat and journal folded into the sidebar. The academic wants to think, not administrate.

---

### `custom` — Yours
```json
{
  "layout": "custom",
  "regions": [
    { "app": "chat",    "row": 0,  "col": 0,  "height": 60, "width": 70, "unit": "pct" },
    { "app": "journal", "row": 0,  "col": 70, "height": 60, "width": 30, "unit": "pct" },
    { "app": "vitals",  "row": 60, "col": 0,  "height": 10, "width": 100, "unit": "pct" },
    { "app": "models",  "row": 70, "col": 0,  "height": 30, "width": 100, "unit": "pct" }
  ]
}
```
Edit `~/.willow/grove/layout.json`. Reload with `Ctrl-R`. Done.

---

## Model Switcher App

This is a first-class app, not a config screen.

```
╭─ Models ──────────────────────────────────────────────────────────╮
│                                                                   │
│  Local (Ollama)                                                   │
│  ▌ yggdrasil:v9          274MB   ● loaded                        │
│    yggdrasil:v8          274MB   ○ available                     │
│    qwen2.5:3b            2.0GB   ○ available                     │
│    nomic-embed-text      274MB   ● loaded  (memory)              │
│                                                                   │
│  API                                                              │
│    claude-opus-4-7       ——      ○ configured                    │
│    claude-sonnet-4-6     ——      ● active (this session)         │
│    gpt-4o                ——      ○ configured                    │
│                                                                   │
│  Press Enter to switch. Active task switches at next turn.       │
╰───────────────────────────────────────────────────────────────────╯
```

Click a model. Enter. The active session switches at the next agent turn boundary. No restart. No reconnect. Just a different brain picking up where the last one left off.

---

## Architecture

```
grove/
  __main__.py       # entry point, terminal init, event loop
  shell.py          # layout engine, region manager, focus router
  apps/
    __init__.py
    base.py         # App base class (render/handle_key/handle_mouse/tick)
    chat.py         # Grove channels via OpenClaw gateway
    journal.py      # Daily log editor
    utety.py        # Professor chat (routes to safe-app-ask-jeles)
    models.py       # Model switcher (Ollama API + API providers)
    tasks.py        # Kart queue viewer
    agents.py       # Agent session monitor
    vitals.py       # Subsystem health strip
    routing.py      # willow_route decision feed
  layouts/
    __init__.py
    tabs.py         # Default test layout
    discord.py
    slack.py
    mission_control.py
    minimal.py
    custom.py       # Reads ~/.willow/grove/layout.json
  theme.py          # 256-color palette, rounded borders, glyph map
  mouse.py          # Hit region registry, click routing
  input.py          # Input bar widget (shared across apps)
```

---

## What This Is NOT

- Not a web app. Not Electron. Not a React component.
- Not a re-skin of the existing dashboard.
- Not another monitoring tool.

It is a terminal-native personal computing surface that happens to run AI agents.

The dashboard and the grove are the same thing. One window. Everything inside.

---

## Phase 1 (tabs layout, get it working)

1. `shell.py` — layout engine + region manager + mouse init
2. `theme.py` — 256-color palette, rounded borders
3. `apps/base.py` — App contract
4. `apps/vitals.py` — always-on strip (existing logic, new renderer)
5. `apps/chat.py` — OpenClaw gateway WS connection + channel list + message view
6. `apps/models.py` — Ollama API list + switch
7. `layouts/tabs.py` — top tab bar, single pane, status strip
8. Wire `__main__.py`

Everything else (journal, utety, agents, other layouts) is Phase 2.

---

ΔΣ=42
