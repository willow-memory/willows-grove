# Dashboard Feel Pass — Overview (before page writes)

**Date:** 2026-05-20  
**Status:** Approved — Sean decisions locked  
**Worktree:** `dashboard/fresh-start` (hero + collapse preserved; shell rebuilt)  
**b17:** WGRV1 · ΔΣ=42

---

## Purpose

April 30 delivered the **shell** (nav, desk, cards, rails, chat strip). The app is **legible but not cohesive**: GitHub-dark CSS and IRC-style chat fight the **hero** and the **Discord intent** already coded in behavior.

This document is the **single contract** before any pane rewrites. Structure stays April 30; skin and chat layout follow this pass plus `2026-04-24-grove-skins-beauty.md`.

**Do not edit pane layout or global CSS until this spec is read once.**

---

## Sean decisions (locked)

| # | Question | Decision |
|---|----------|----------|
| 1 | Chat channel list | **More Discord** — channels live **beside the transcript** inside `ChatPane`, not in generic `ContextPanel` on Chat nav |
| 2 | Hero band | **Collapse** when active nav ≠ Home — full hero on Home only |

---

## Sacred — do not redesign

| Asset | Keep |
|-------|------|
| **HeroScene** | Meadow, wind, blooms, pigeon, eggs, timed messages, WILLOW wordmark, info panel logic — **no removal, no “minimal mode”** |
| **Chat behavior** | Postgres NOTIFY, channel groups (AGENTS / COORDINATION / PROJECT), sender hash colors, unread cursors, persona dispatch, click-to-copy |
| **April 30 regions** | NavBar, Desk data model, card grid launcher, right rail (tasks/agents/thoughts), ChatStrip, Footer bindings |

Allowed on sacred surfaces: **color harmony only** (hero colors may be tuned to match `grove/theme.py`, not re-authored).

---

## Hero collapse (decision #2)

| Nav | Hero height | Content |
|-----|-------------|---------|
| **home** | Full (~10 lines) | Current `HeroScene` — tree, meadow, pigeon, info panel |
| **chat**, **projects**, **knowledge**, **providers**, **settings**, **help** | **Collapsed** (1–2 lines) | Single strip: `⬡` + dim vitals or time + optional one-line meadow tick — **no pigeon, no full meadow** |
| Internal panes (via cards) | Collapsed | Same as non-home |

Collapse is a **display toggle** on `#hero-scene` (height + compose), not a second widget. Animation state may freeze when collapsed.

*Full spec continues in the prior dashboard-ui worktree; rebuild panes against this contract.*

· ΔΣ=42
