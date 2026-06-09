# Grove Skins — Beauty Pass
**Date:** 2026-04-24  
**Status:** Design ready for implementation  
**Constraint change:** 256-color approved. ANSI-16 rule retired.

---

## The Problem With Right Now

The current dashboard is legible. It is not beautiful. Every border looks like a spreadsheet. The vitals strip reads like a log file. The card system feels like a status page from 2009.

The goal: a terminal you want to sit in front of.

---

## What Makes Terminal UI Beautiful

1. **Rounded borders** — `╭ ╮ ╰ ╯` everywhere. Box corners feel mechanical. Rounds feel intentional.
2. **Color hierarchy** — three levels: primary (bright), secondary (gray-245), ghost (gray-238). Not flat.
3. **Breathing room** — single empty rows between logical groups. Dense ≠ rich.
4. **Accent lines** — `▌` left-edge glyph on the active item. Better than bold alone.
5. **Status glyphs** — `●` online · `◐` busy · `○` idle · `·` absent. Not words.
6. **Message attribution** — username in agent-hash color, timestamp right-dim, message indented one level.
7. **Unread pills** — `2` in bright yellow, inline, right-aligned in channel row. Not a separate column.

---

## Discord Skin (≥160 cols)

Four columns. Left to right: server strip · channel list · main pane · member list.

```
╭────╮ ╭──────────────────────╮ ╭──────────────────────────────────────────────╮ ╭──────────────╮
│    │ │ WILLOW               │ │ # architecture                               │ │ Members      │
│ ⬡  │ ├──────────────────────┤ ├──────────────────────────────────────────────┤ ├──────────────┤
│    │ │                      │ │                                              │ │ ─ Online ─ 3 │
│ ·  │ │  ▌# general          │ │  hanuman                          13:04      │ │              │
│    │ │    # architecture  2●│ │    routed "debug gleipnir" → ganesha         │ │ ● hanuman    │
│ ·  │ │    # handoffs        │ │                                              │ │ ● heimdallr  │
│    │ │    # readme          │ │  ganesha                          13:01      │ │ ● ganesha    │
│    │ │                      │ │    rate limit closed, resuming               │ │              │
│    │ ├──────────────────────┤ │                                              │ │ ─ Idle ─── 1 │
│    │ │ pg● olla● kart 3/5   │ │  hanuman                          12:58      │ │              │
│    │ │ soil● ledger ok      │ │    queued 3 tasks, waiting on ganesha        │ │ ○ jeles      │
╰────╯ ╰──────────────────────╯ │                                              │ ╰──────────────╯
                                 │ ╭──────────────────────────────────────────╮ │
                                 │ │ Message #architecture...                 │ │
                                 │ ╰──────────────────────────────────────────╯ │
                                 ╰──────────────────────────────────────────────╯
```

**Color map (256-color xterm indices):**

| Element              | Color       | xterm |
|----------------------|-------------|-------|
| Background           | near-black  | 235   |
| Border/dim           | dark gray   | 238   |
| Secondary text       | mid gray    | 245   |
| Primary text         | off-white   | 253   |
| Accent (active)      | blurple     | 99    |
| Unread badge         | bright yel  | 220   |
| Online dot           | green       | 77    |
| Idle dot             | gray        | 243   |
| Agent: hanuman       | cyan        | 87    |
| Agent: ganesha       | magenta     | 213   |
| Agent: heimdallr     | yellow      | 227   |
| Vitals: healthy      | green       | 77    |
| Vitals: degraded     | amber       | 214   |
| Vitals: down         | red         | 203   |

**Column widths (160-col example):**  
Server strip: 6 · Channel list: 24 · Main: 100 · Members: 18 (remainder)

**Graceful degradation:**  
- ≥120 cols: drop server strip, keep 3 columns  
- ≥80 cols: drop members, 2 columns (channels + main)  
- <80 cols: single column main only, no sidebar

---

## Slack Skin (≥100 cols)

Two columns. Left sidebar owns navigation. Right owns content.

```
╭──────────────────────╮ ╭──────────────────────────────────────────────────────────╮
│ ⬡  Willow            │ │ # architecture                              ─ 2 new ──── │
├──────────────────────┤ ├──────────────────────────────────────────────────────────┤
│                      │ │                                                          │
│  ↑ Routing feed      │ │  hanuman                                       13:04     │
│                      │ │    routed "debug gleipnir rate limit" → ganesha          │
│  ▸ Channels          │ │                                                          │
│    ▌# architecture 2 │ │  ganesha                                       13:01     │
│      # general       │ │    rate limit window closed, resuming                    │
│      # handoffs      │ │                                                          │
│      # readme        │ │  hanuman                                       12:58     │
│                      │ │    queued 3 tasks, waiting on ganesha                    │
│  ▸ Agents            │ │                                                          │
│    ● hanuman         │ │                                                          │
│    ◐ ganesha         │ ├──────────────────────────────────────────────────────────┤
│    ○ jeles           │ │  Message #architecture...                                │
│                      │ ╰──────────────────────────────────────────────────────────╯
├──────────────────────┤
│ ● USER               │
╰──────────────────────╯
```

**Color map:** Same palette. Accent shifts to Slack aubergine (xterm 91) when skin is `slack`.

**Sidebar width:** 24 cols fixed. Main takes remainder.

---

## Message Rendering (both skins)

```
  hanuman                              13:04
    routed "debug gleipnir" → ganesha
```

- Username: agent-hash color, bold
- Timestamp: right-aligned to pane width, gray-245
- Body: indented 4 spaces, primary text
- Consecutive messages from same sender: suppress header, just indent body
- Reactions / tool results: `  ↳ tool: willow_route  3ms  ✓` in dim

---

## Mouse Regions

Every visible element gets a hit region. `curses.mousemask(curses.ALL_MOUSE_EVENTS)`.

| Click target         | Action                          |
|----------------------|---------------------------------|
| Channel row          | Open channel, advance cursor    |
| Agent row            | Open agent card                 |
| Message row          | Select / copy mode              |
| Input bar            | Focus input                     |
| Server icon          | Switch project (future)         |
| `2●` unread badge    | Jump to first unread            |

---

## What Changes in the Code

| File            | Change                                                    |
|-----------------|-----------------------------------------------------------|
| `skins.py`      | Add `color_bg`, `color_dim`, `color_secondary`, `accent` 256-color fields. Drop old ANSI-16 restriction. |
| `dashboard.py`  | Add `render_discord()` and `render_slack()` dispatch based on `layout_preset`. Mouse init. |
| `skins/discord.py` | New file. Discord 4-column renderer.                   |
| `skins/slack.py`   | New file. Slack 2-column renderer.                     |
| `cards.py`      | Rounded borders on all existing cards. No logic change.   |

---

## What Does NOT Change

- Data layer: same Postgres reads, same SOIL, same poll cadence
- Keyboard bindings: all existing keys preserved
- Card system: same cards, just gets rounded borders
- The reactor-door placard: untouched. It's already right.

---

## Acceptance

- [ ] Discord skin renders all 4 columns at ≥160 cols, degrades cleanly below
- [ ] Slack skin renders at ≥100 cols
- [ ] Mouse click on channel row opens that channel
- [ ] Agent names render in stable hash-color across restarts
- [ ] Unread badges advance and clear correctly
- [ ] Input bar accepts text, Enter sends via OpenClaw gateway
- [ ] `OPENCLAW_THEME=dark` env var honored; no light-mode at 256-color

---

ΔΣ=42
