# Anti-Slop — Grove Dashboard Design Gate

**Branch:** `dashboard/fresh-start`  
**Worktree:** `worktrees/dashboard-fresh`  
**b17:** WGRV1 · ΔΣ=42

Read this before adding panes, CSS, chat layout, cards, or nav. If a change fails the slop detector, it does not ship.

---

## What slop is

**Slop** is the generic SaaS dashboard skin: copied palettes, marketing tiles, emoji section headers, icon grids, and “AI mission control” cosplay assembled from parts nobody authored.

Slop optimizes for screenshots. Grove optimizes for **living in the terminal**.

Sean spent months on the hero — meadow, wind, blooms, pigeon, eggs, collapse. Slop treats that band as interchangeable chrome. It is not.

---

## Sacred — do not redesign

| Asset | Rule |
|-------|------|
| **HeroScene** | Meadow, wind, blooms, pigeon, eggs, timed messages, WILLOW wordmark, info panel — **no removal, no “minimal mode”** |
| **Collapse** | Full hero on Home only; collapsed strip (`⬡` + time + meadow tick) elsewhere — display toggle, not a second product |
| **Egg triggers** | New motion needs a trigger class (probability, clock, metric, geometry, lifecycle) — see `seed_kb.py` / `hero_db.py` |
| **Grove chat behavior** | Postgres NOTIFY, channel groups, sender hash colors, unread cursors — behavior unchanged; layout/skin may evolve |

Allowed on sacred surfaces: **color harmony only** — tune hero colors to match `grove/theme.py`, do not re-author the scene.

---

## Kill list (global slop)

Burn on sight:

- Hardcoded GitHub palette in `app.py` (`#0d1117`, `#58a6ff`, `#8b949e`, `#30363d`, …)
- Desk emoji headers (`⚡` `▶` `✓` `⚙`)
- One-line IRC messages (`time  name  body`)
- Fat marketing card tiles (large subcopy, SaaS layout, “Welcome back” copy)
- Full-height hero on every nav target
- Homarr / Dashy / bookmark-launcher icon grids
- Generic “AI Mission Control” 32-panel SPA layouts
- shadcn/Vercel admin kit aesthetics pasted into Textual
- Modal confirm spam (prefer in-context verbs like k9s/lazygit)
- Gratuitous spinners and animation without triggers
- Nerd Font icon walls where a glyph contract suffices (`●` `▌` `⬡` `↳`)
- Toast spam (“Refreshed”) instead of a stable vitals line

---

## Slop vs handmade

| Slop (burn) | Handmade (Grove) |
|-------------|------------------|
| Copied GitHub/Vercel/shadcn palette | `grove/theme.py` → Textual tokens; hero greens `#0a0f07`, `#1e3a1e`, authored blooms |
| Dashboard = app launcher tile grid | Home = desk data + dense cells, not marketing subcopy |
| Emoji section headers | Plain labels (`ATTENTION`, `RUNNING`, `SYSTEM`) or columns |
| IRC one-liners | Discord blocks: sender bold left, `HH:MM` right, body indented 4 spaces |
| Hero everywhere or hero deleted | Collapse on nav — hero **earns** Home |
| Bloomberg / 32-widget density | k9s-*lite* rail + 5–8 row dispatch strip |
| Animation for “delight” | Animation with **stories** (pigeon @ 17, bloop 1-in-500, Gerald at midnight) |
| Assembled from npm/templates | Authored — one palette, one chat shape, one hero scene |

---

## Palette authority

**Source of truth:** `grove/theme.py` (and `grove/theme_textual.py` when present).

| Token | Role |
|-------|------|
| `bg` | Screen background |
| `border` | Rules, strip borders |
| `secondary` | Timestamps, hints, collapsed meadow |
| `primary` | Body text |
| `accent` | Active nav, channel title |
| `unread` | Unread count + badge |
| `healthy` / `degraded` / `down` | Vitals, status |
| Agent hash | Same sender = same color everywhere (87, 213, 227, 120, 111, 209, 51) |

**Rule:** If a color is not derived from this table, it does not ship in `app.py` or pane CSS.

Textual CSS is **generated or copied from this table** — not GitHub defaults.

---

## Glyphs & typography

- Mono throughout; **no emoji section headers**
- Status: `●` online · `◐` busy · `○` idle · `·` unknown
- Active row: `▌` prefix (channel, nav item)
- Unread: `{n}●` right-aligned in channel row
- Vitals canonical line: `pg● olla● kart {r}/{q} soil●` (+ optional model suffix, dim)
- Desk: plain labels or columnar layout; one blank line between sections max

---

## Chat contract (Discord, not IRC)

```text
  hanuman                              13:04
    routed "debug gleipnir" → ganesha
```

1. Line 1: sender bold, agent color, **left**; `HH:MM` **right-aligned**
2. Line 2+: body indented **4 spaces**, primary color
3. **Collapse:** same sender within 5 minutes → body lines only (no repeated header)
4. Tool/dispatch: `  ↳ …` in dim (optional)

Implement via `format_message_block()` — unit tests with mock rows. Never regress to IRC one-liners.

---

## Cards & desk

- Shorter cells: **label + primary value + one dim subline max**
- State via color/glyph, not paragraphs
- No fat marketing tiles, no SaaS subcopy, no hero CTAs on cards

---

## Target shell (archetype mix)

Not Bloomberg. Not Homarr. **Chat-primary + collapsible hero + ops rail lite.**

```text
┌─ NavBar ─────────────────────── vitals (canonical line) ─┐
├─ HeroScene ─────────────────────────────────────────────┤
│  FULL (Home)  |  COLLAPSED (all other nav)               │
├─ ContextPanel ─┬─ ContentArea ──────────┬─ RightPanel ──┤
│  context-specific │  active pane         │  tasks, agents │
├─────────────────┴──────────────────────┴─────────────────┤
│ ChatStrip — last message, ▶ open                         │
└─ Footer (? help · bindings) ─────────────────────────────┘
```

| Nav | Hero |
|-----|------|
| **home** | Full (~10 lines) — tree, meadow, pigeon, info panel |
| **chat**, **projects**, **knowledge**, **providers**, **settings**, **help**, internal panes | **Collapsed** (1–2 lines) — `⬡` + time + meadow tick; no pigeon, no full meadow |

Collapse is a **display toggle** on `#hero-scene`, not a second widget. Animation may freeze when collapsed.

---

## Safe to steal (mechanics only — strip the skin)

| Reference | Take | Leave |
|-----------|------|-------|
| **k9s** | `:` palette, `Esc` stack, verb keys, watch refresh | K8s chrome, max density as default |
| **lazygit** | Master-detail, `?` contextual help, review-before-act | Git-specific panels |
| **Harlequin** | Collapsible sidebar / band toggle | SQL chrome |
| **Repartee / Muninn** | Chat stream + room list + nick hash colors | Generic branding |
| **Posting** | Command palette, keyboard contract | HTTP client framing |
| **bottom** | Sparkline *idea* for hero info | Widget grid layout |
| **asciiquarium / cbonsai** | Ambient band philosophy | — |

---

## Burn on sight (slop magnets)

| Reference | Why |
|-----------|-----|
| Homarr / Dashy / Flame / Heimdall tile grids | Bookmark SaaS, not operator terminal |
| Mission Control–style 32-panel agent SPAs | Template assembly |
| Grafana default / Bloomberg cosplay | Wrong voice for Grove |
| GitHub-dark Textual CSS | Fights meadow; already killed |
| shadcn admin kits | Every AI demo looks like this |
| Marketing card grids | Subcopy + CTA tiles |

---

## Build gates (check before merge)

1. **Hero sacred?** — No minimal mode, no logo strip replacement.
2. **Palette from `grove/theme.py`?** — No raw GitHub hex in new CSS.
3. **No emoji headers?** — Desk/chat sections use plain labels.
4. **Chat Discord-shaped?** — Block formatter + same-sender collapse; not IRC.
5. **Cards are cells?** — Label + value + one dim line; no marketing tiles.
6. **Delight is gated?** — New motion has a trigger class; no gratuitous spinners.
7. **Slop detector:** *Could this screen appear in a YC demo template?* — If yes, redo.
8. **Eggs reachable?** — `hero_test.py` keys still work; dashboard serves the scene.

---

## Keyboard contract (inherit, don’t reinvent)

Align with terminal idioms:

- `j` / `k` — list navigate
- `Enter` — drill / open
- `Esc` — pop stack / back
- `?` — contextual help (non-negotiable)
- `/` — filter
- `:` — command palette / resource jump
- `1`–`7` — top nav (April 30 contract)
- `q` — quit

Map Grove verbs onto k9s-style keys where natural: `l` logs, `d` describe, etc.

---

## What handmade feels like

- **Home:** meadow moves; WILLOW wordmark; sysinfo as comfort, not NOC panic.
- **Leave Home:** hero collapses to a breath — tree not deleted, room for work.
- **Chat:** one color per sender everywhere; messages read like a place people live.
- **Ops:** agent rail is scannable — name, trust, heartbeat — not a widget wall.
- **Idle:** rare egg fires; you smile because you **built** the trigger.

---

## References

| Doc | Role |
|-----|------|
| [FRESH_START.md](FRESH_START.md) | What survived the reset |
| [docs/superpowers/specs/2026-05-20-dashboard-feel-pass.md](docs/superpowers/specs/2026-05-20-dashboard-feel-pass.md) | Collapse + chat + palette contract |
| `grove/theme.py` | Palette numbers |
| `widgets/hero_scene.py` | Sacred hero implementation |
| `seed_kb.py` / `hero_test.py` | Egg taxonomy + harness |

---

*Handmade with love. Burn the template. · ΔΣ=42*
