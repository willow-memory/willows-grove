# Willow Grove Dashboard — Phase 1: Shell Restructure
**Date:** 2026-04-30  
**Author:** Heimdallr  
**Status:** Draft — pending Sean review  
b17: WGRV1  ΔΣ=42

---

## What This Is

Replace the current tab-switching `app.py` with a persistent shell layout. The current design hides the system status behind a tab and treats all panes as equal. The new design gives every region a permanent purpose and lets content swap in the center without disrupting the frame.

This is structural only. No new data sources. No new panes. The 10 existing panes are untouched — they just get a new home.

---

## Layout

```
┌─ NavBar ──────────────────────────────────────────── VitalsBar ─┐
│  ◆ Home  Chat  Projects  Knowledge  Providers  Health  Settings  Help  │
├─ HeroScene (full width) ────────────────────────────────────────┤
│                         ,                                        │
│                        /|\       ☁  ☁       ☀ 18°C  09:41      │
│                       / | \                                      │
│               ƒ  ƒ  ƒ  ║  ƒ  ƒ  ƒ                              │
│                       |   |                                      │
│  ▣ | ⬡ | ♟ | ♜ | ✿ | | ✿ | ⌁ | ✦ | ♞ | ✿ | | ✿ | ⬡ |         │
│  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~│
│  ▣ Postgres 209K  ⬡ Ollama 18  ⌁ Grove live  ♟ hanuman  …      │
├─ ContextPanel ──┬─── ContentArea (1fr) ──────┬─ RightPanel ─────┤
│ (home=The Desk) │  (home=card grid)          │  Tasks           │
│ (app=app nav)   │  (app=app TUI pane)        │  Agents          │
│                 │                            │  Thought stream  │
│                 │                            │  Session stats   │
├─────────────────┴────────────────────────────┴──────────────────┤
│ ChatStrip  #general  hanuman: …message…              ▶ open     │
└─ Footer ────────────────────────────────────────────────────────┘
```

---

## Regions

### NavBar
A single-row `Horizontal` widget replacing `TabbedContent`'s built-in tab strip. Left side: `◆` logo button (home shortcut) followed by nav labels — **Home, Chat, Projects, Knowledge, Providers, Health, Settings, Help**. Right side: `VitalsBar` content inlined. Clicking a label sets `ContentArea`'s active pane and triggers a `NavChanged` message that the `ContextPanel` and `ChatStrip` listen to.

Not a Textual `TabbedContent` — a custom `NavBar` widget that emits `NavChanged(target: str)` messages.

**What is NOT in the nav bar:** Tasks, Agents, Routing, Skills, Logs. Tasks and Agents are always visible in `RightPanel`. Routing, Skills, and Logs are internal views reachable from the Projects card grid or the left `ContextPanel` — they do not need top-level slots.

### HeroScene
Full-width band below the NavBar. Fixed height: 10 lines.

Contains three sub-regions laid out as a `Horizontal`:
- **HeroTree** (left, width ~24): the existing `WillowHero` animated willow tree widget
- **GroundStrip** (center, 1fr): a single-row animation of scene elements — grass blades (`|`), flowers (`✿`), agent glyphs, service icons. Each element maps to a live system signal (agent presence, service health). Weather/time float in the upper-right of this region.
- **Nothing else** — the legend strip (tooltips) appears on hover/focus only, not always rendered

The ground line (`~~~`) is the bottom border of the hero band.

Animation and exact scene element placement are out of scope for Phase 1. Phase 1 delivers the widget skeleton and static placeholder content. Animations are a Phase 1.5 / later pass.

### ContextPanel
Left column, fixed width 26. Content is determined by the active nav target:

| Active target | Content |
|---|---|
| Home | `DeskPane` — placeholder widget (Phase 2 fills it) |
| Chat | Channel list (extracted from `ChatPane`'s existing sidebar) |
| Tasks | Task filter/category list |
| Agents | Agent list with status dots |
| Knowledge | KB category/domain list |
| Providers | Provider list |
| Skills | Skill category list |
| Health | Service list |
| Logs | Log source list |

Phase 1 delivers the switching infrastructure and the Home (`DeskPane` placeholder) only. The per-pane nav implementations come in later phases or alongside their pane.

Listens for `NavChanged` messages and swaps its content via `ContentSwitcher` or `display` toggling.

### ContentArea
Center column, `width: 1fr`. Contains all 10 existing panes plus the new `HomeGrid` placeholder:

| Nav target | ContentArea shows |
|---|---|
| Home | `HomeGrid` (Phase 3 fills with live cards; Phase 1 = static placeholder grid) |
| Chat | `ChatPane` (existing, untouched) |
| Projects | `ProjectsGrid` — card grid launcher (Phase 3 live; Phase 1 = static placeholder). Cards include Agents, Tasks, Routing, Skills, Logs, and project-specific entries. |
| Knowledge | `KnowledgePane` (existing, untouched) |
| Providers | `ProvidersPane` (existing, untouched) |
| Health | `HealthPane` (existing, untouched) |
| Settings | `SettingsPane` (Phase 1 = static placeholder) |
| Help | `HelpPane` (Phase 1 = static placeholder) |

**Internal pane access:** `TasksPane`, `AgentsPane`, `RoutingPane`, `SkillsPane`, and `LogsPane` remain mounted but are reached via the Projects card grid (card click → show pane), not direct nav bar links. Tasks and Agents are also always visible in `RightPanel`.

Panes are mounted once at startup and shown/hidden via `display` toggling — not destroyed and recreated. This preserves pane state (scroll position, loaded data) across nav switches.

### RightPanel
Existing `GroveRightPanel` widget, unchanged. Fixed width 30. Tasks + agents list.

**Phase 1 addition:** A `ThoughtStream` static below the agent list — a small `RichLog` widget. Fed by the same Postgres LISTEN/NOTIFY connection already used by `ChatPane`: filter for `grove.messages` rows where sender matches a known agent name. Height 6, `overflow: hidden`. Session stats (active time, KB atoms today, messages today) below that, read from `session_anchor.json` on a 30s interval.

### ChatStrip
New persistent widget at the bottom of the screen. Always visible. Fixed height: 1 line. No expanded state in Phase 1 — pressing Enter or `▶ open` navigates to the Chat pane instead of expanding the strip.

Shows: `[channel/context] [sender]: [last message text, truncated] [▶ open]`

Listens for `NavChanged` messages and updates its context label:
- Home → last active Grove channel
- Chat → active channel (already selected in `ChatPane`)
- Any app pane → that pane's associated context (defined per-pane in Phase 4)

Pressing Enter or clicking `▶ open` switches `ContentArea` to the Chat pane (or app pane) and focuses the input. Does not send messages from the strip itself in Phase 1 — that is Phase 4 (per-app chat context).

### Footer
Existing Textual `Footer` widget, unchanged.

---

## Files

### New files
| File | Purpose |
|---|---|
| `widgets/nav_bar.py` | `NavBar` widget — horizontal nav labels, emits `NavChanged` |
| `widgets/hero_scene.py` | `HeroScene` widget — full-width band, `WillowHero` + `GroundStrip` |
| `widgets/chat_strip.py` | `ChatStrip` widget — persistent bottom bar |
| `widgets/thought_stream.py` | `ThoughtStream` widget — live agent activity feed |
| `panes/home.py` | `HomeGrid` placeholder + `DeskPane` placeholder |

### Modified files
| File | Change |
|---|---|
| `app.py` | Full rewrite of `compose()` and CSS. `WillowGrove` app class gets new layout. `TabbedContent` removed. `OverviewPane` removed from pane list (its data moves to `HeroScene` + `RightPanel`). |
| `widgets/hero.py` | No changes — `WillowHero` used as-is inside `HeroScene` |
| `panes/chat.py` | Extract channel sidebar into a standalone `ChannelList` widget reusable by `ContextPanel`. Existing `ChatPane` layout unchanged. |

### Untouched
All other pane files (`tasks.py`, `agents.py`, `routing.py`, `knowledge.py`, `providers.py`, `skills.py`, `health.py`, `logs.py`), `cards.py`, `grove_db.py`, `grove_reader.py`, `skins.py`, `soil.py`.

---

## Messages

```python
class NavChanged(Message):
    def __init__(self, target: str) -> None:
        self.target = target  # "home" | "chat" | "tasks" | ...
        super().__init__()
```

`NavBar` posts this. `ContentArea` (in `WillowGrove`), `ContextPanel`, and `ChatStrip` all handle it.

---

## CSS structure

All CSS lives in `app.py`'s `CSS` class variable (existing pattern). New rules added for `NavBar`, `HeroScene`, `ContextPanel`, `ChatStrip`, `ThoughtStream`. No external CSS files.

Approximate widths at 120-col terminal:
- `ContextPanel`: 26
- `ContentArea`: 1fr (~64 cols at 120 total)
- `RightPanel`: 30

---

## What Phase 1 does NOT include

- Live data in `HomeGrid` (static placeholder tiles — Phase 3)
- Live data in `DeskPane` (static placeholder — Phase 2)
- ChatStrip sending messages (display only — Phase 4)
- Per-app `ContextPanel` nav (only Home placeholder — Phase 4)
- Hero animations beyond existing `WillowHero` sway (Phase 1.5)
- Command palette (Phase 5)

---

## Definition of done

- `python3 app.py` starts without error
- All 8 nav targets accessible, content switches correctly
- Internal panes (Tasks, Agents, Routing, Skills, Logs) reachable via Projects card grid
- Hero scene renders (static ground strip acceptable for Phase 1)
- `ContextPanel` shows placeholder on Home, channel list on Chat
- `RightPanel` includes `ThoughtStream` and session stats
- `ChatStrip` shows last Grove message, updates on nav change
- No regressions in `ChatPane` behaviour (NOTIFY, badge, ListView)
- Keyboard bindings preserved (1-8 for nav, q=quit, r=refresh)
