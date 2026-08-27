# Grove ↔ Starter Pack — Borrow Map

**b17:** GSBRW · ΔΣ=42  
**Date:** 2026-06-24  
**Status:** Integration brief (patterns + priorities — no implementation)  
**Author:** Vishwakarma (with operator review)

## Purpose

The [SAFE App Store starter pack](../../../safe-app-store-public/docs/willow-compatible-projects.md#starter-pack-promote-first)
lists third-party TUIs worth promoting as standalone SAFE apps. **Willow Grove already overlaps**
several of those jobs (desk, Kart queue, vitals, KB browse, MCP ops).

This document answers:

1. Where Grove is **already better** than importing a scout.
2. Where scouts **do the job better** despite Grove having something similar.
3. What to **steal** (patterns into Grove panes) vs **wrap** (launch whole SAFE apps).
4. Prioritized borrow backlog for implementation.

**Companion docs:**

| Doc | Role |
|-----|------|
| [store-console-source-map.md](store-console-source-map.md) (SCMAP) | Grove ↔ store installer / SCDS1 |
| [CROSS_REPO_BRIDGE.md](../CROSS_REPO_BRIDGE.md) | Grove ↔ Willow ↔ safe-app-store boundaries |
| [willow-compatible-projects.md](../../../safe-app-store-public/docs/willow-compatible-projects.md) | Scout list, overlaps, starter pack |

---

## Layering (do not conflate)

```text
┌─────────────────────────────────────────────────────────────┐
│  Grove — operator plane (Postgres, fleet bus, desk, MCP)    │
├─────────────────────────────────────────────────────────────┤
│  SAFE flagships — sovereign plane (SQLite, domain workflows)  │
│  ask-jeles · law-gazelle · private-ledger · story-timeline  │
├─────────────────────────────────────────────────────────────┤
│  Starter pack — utility belt (manifest-only tools)          │
│  nvitop · visidata · calcure · toolong · …                  │
└─────────────────────────────────────────────────────────────┘
```

- **Grove** steals **horizontal UX** into panes.
- **Flagships** keep **vertical truth** (provenance, personas, domain logic).
- **Scouts** ship when the tool is too large to fork or reuse is “open in …” only.

---

## Where Grove is already better (do not replace)

| Grove surface | Code | Why scouts lose here |
|---------------|------|----------------------|
| **Chat** | `panes/chat.py` | Fleet bus, mod commands, agent dispatch, DMs — `endcord` / `tg` are external network clients |
| **Human** | `panes/human.py` | Consent · attestation · review queue — no scout equivalent; core SAFE honesty |
| **MCP** | `panes/mcp.py`, `grove/apps/mcp_catalog.py` | Serve lifecycle, live tools, **registry drift** vs `mcp_registry.json` |
| **Agents / routing** | `panes/agents.py`, `panes/routing.py` | Postgres fleet state — not a commodity TUI |
| **Install trust** | [ADR SITR1](../adrs/ADR-20260615-safe-app-install-trust.md) | Two-phase install + PGP — scouts have no manifest trust chain |

---

## Overlap scorecard (Grove pane vs starter pack)

| Starter / scout | Grove today | Scout does better | Verdict |
|-----------------|-------------|-------------------|---------|
| **nvitop** | `grove/apps/vitals.py`, `hero_stats.read_sysinfo` — CPU/RAM/disk/temp; Ollama model **count** only | Per-process **GPU VRAM**, sort/kill by GPU consumer | **Steal** GPU slice into vitals |
| **toolong** | `panes/tasks.py` — id/status/cmd/time table, refresh | Tail-follow, merge JSONL, search in log body | **Steal** task→tail; optional wrap |
| **kanban-tui** | `panes/user_todos.py` — flat DataTable by due date | Column board (todo/doing/done), `claude-skills` tag | **Steal** board view + status field |
| **taskdog** | My Desk + Kart Tasks; no agent API | **MCP tools** for tasks, schedule optimization | **Steal** tool schema |
| **calcure** | Due dates + urgency colors on desk | Month/week **calendar**, ICS import, recurrence | **Steal** ICS + week strip |
| **feeds.fun** | — | RSS + **local LLM tag on ingest** | **Steal** intake pattern (new card) |
| **parllama** | Providers pane; vitals Ollama dot | pull/rm models, simple model picker | **Steal** ops actions in Providers |
| **visidata** | `panes/knowledge.py` — KB atoms only | Open **any** tabular file; column ops | **Wrap** + preview steal |
| **sqlit** | — | Schema tree + SQL on arbitrary `.db` | **Wrap** from desk/KB links |
| **fast-resume** | — | Tantivy **session search** across agent JSONL | **Steal** — high operator leverage |
| **dooit** | SOIL todos, pipe quick-add | **Plugins** / per-item actions | **Steal** action hooks on todos |
| **botany** | — | Zero-stakes delight | **Wrap** as showcase SAFE app |

---

## Detailed borrow notes

### Kart queue — `TasksPane` ← **toolong**

**Grove:** `panes/tasks.py` — `fetch_tasks()` from `public.tasks`; DataTable columns ID / Status / Command / Time.

**Gap:** No stdout/stderr tail, no merge of run logs, no in-pane search when a Kart job fails.

**Steal:**

- `Enter` on row → tail task output (discover Kart log path convention; fallback spawn `toolong <path>`).
- **Merged log** mode: last N Kart runs + optional ratatosk session JSONL in one searchable buffer.
- Inline last 20 lines of stderr on `failed` rows (toolong’s “why did this die?” loop).

**Wrap:** Ship `toolong` as SAFE app; Grove is the launcher, not a second log viewer.

---

### My Desk — `user_todos` ← **kanban-tui**, **calcure**, **dooit**, **taskdog**

**Grove:** `grove/apps/user_board.py` + `panes/user_todos.py` — SOIL `willow-dashboard/todos` and `projects`; pipe-delimited quick-add; atom link on detail.

**kanban-tui — steal:**

- Add `status` (`todo` | `doing` | `done`) on SOIL todo records.
- Table ↔ **3-column board** toggle on My Desk.
- Optional `skill_id` / `claude-skills` metadata on cards for agent-readable WIP.

**calcure — steal:**

- Read **ICS** files into desk deadlines (import path, not full calendar app).
- **Week strip** on Home (`panes/home.py`) for at-a-glance dates — not a full month grid.

**dooit — steal:**

- Per-todo **actions**: open linked atom, `make run app=…`, queue Kart task — SOIL `actions[]` on todo row.

**taskdog — steal:**

- Expose desk + Kart as **MCP tools** (names TBD), e.g. `grove_desk_list`, `grove_desk_add`, `grove_kart_status` — same ergonomics ratatosk already expects from Willow.

---

### Vitals — NavBar ← **nvitop**, **s-tui**, **px**

**Grove:** `grove/apps/vitals.py` — `pg● olla● kart running/queued soil● mcp N`; `hero_stats.read_sysinfo` for home CPU/mem/disk/temp.

**nvitop — steal (P0):**

- Vitals segment: `gpu 2.1/4.0G` + top GPU consumer PID/name.
- **Pre-Kart guard:** dim or warn on Home/Kart cards when VRAM &gt; threshold (T500-specific).

**s-tui / px — steal (P2):**

- Optional expanded vitals popover (CPU freq, top processes) — layout borrow only.

**Wrap:** Full `nvitop` TUI as SAFE app for deep dives; vitals strip stays summary.

---

### Knowledge — `KnowledgePane` ← **visidata**, **sqlit**, Willow **kb_search**, **feeds.fun**

**Grove:** `panes/knowledge.py` — `ILIKE` on `title` / `summary` in `public.knowledge`.

**Gap:** Behind Willow’s own semantic `kb_search`; no arbitrary files; no SQL console.

**Steal:**

- Replace or augment ILIKE with **hybrid kb_search** (call Willow MCP or shared pg_bridge helper).
- Atom detail → **“Open export…”** spawns visidata on CSV/JSON path.
- Desk/KB link → **“Query DB…”** opens sqlit on known SQLite paths (`law-gazelle`, `private-ledger`, Nest).

**feeds.fun — steal (P2):**

- Intake card: RSS → local LLM tag → atoms → **Human pane** review queue (feeds.fun pattern, Grove + ask-jeles thesis).

**Wrap:** visidata, sqlit as catalog apps; Grove provides links, not reimplementation.

---

### Providers / Ollama ← **parllama**

**Grove:** `panes/providers.py`; vitals `_ollama_ok()` returns model count.

**parllama — steal:**

- Providers actions: **pull**, **list**, **unload**, set default model.
- Chat stays **ask-jeles** / fleet agents — parllama patterns are **ops**, not a second chat product.

---

### Sessions ← **fast-resume**

**Grove:** No first-class session search UI (ratatosk / Cursor / Claude JSONL lives elsewhere).

**fast-resume — steal (P1):**

- Home or dev card **“Resume sessions”** — Tantivy (or ripgrep MVP) over agent session paths.
- High leverage for cross-runtime handoffs already in fleet hooks.

---

### Delight ← **botany**

**Wrap only:** manifest + Home card launch — proves catalog breadth; no pane fork.

---

### Install / consent ← **SCDS1** (own repo, not a scout)

When installer pane ships, borrow **nutrition label**, locked gates, privacy meter from
`safe-app-store-public/docs/specs/store_console_design_spec.md` — not from starter pack.

---

## Borrow vs wrap decision rule

| Situation | Action |
|-----------|--------|
| Grove owns the **data model** (SOIL todos, `public.tasks`, vitals) | **Steal** UX into pane |
| Tool is **large / maintained upstream** (visidata, sqlit, toolong) | **Wrap** as SAFE app + Grove launcher |
| Feature is **fleet-native** (Human, MCP drift, bus) | **Keep in Grove** — do not scout |
| Feature is **domain-vertical** (legal workflow, timeline graph) | **Flagship app** — not Grove |

---

## Implementation backlog (prioritized)

| Priority | Borrow from | Into Grove | Effort | Receipt / touch files |
|----------|-------------|------------|--------|------------------------|
| **P0** | nvitop | GPU line on vitals + pre-Kart VRAM guard | Small | `grove/apps/vitals.py`, `panes/home.py` |
| **P0** | toolong | Task row → tail output; failed-row stderr snippet | Medium | `panes/tasks.py`, Kart log path contract |
| **P0** | Willow `kb_search` | Semantic/hybrid search in Knowledge pane | Small | `panes/knowledge.py` |
| **P1** | kanban-tui | SOIL `status` + board view toggle | Medium | `user_board.py`, `user_todos.py` |
| **P1** | taskdog | Desk/Kart MCP tools for agents | Medium | `grove/mcp_local.py` or Willow tool defs |
| **P1** | fast-resume | Session search card | Medium | `widgets/card_store.py`, new pane or modal |
| **P1** | calcure | ICS import + Home week strip | Medium | `user_board.py`, `home.py` |
| **P2** | feeds.fun | RSS → tag → Human queue pipeline | Large | new intake pane + ask-jeles hook |
| **P2** | parllama | Model pull/unload in Providers | Small–medium | `panes/providers.py` |
| **P2** | visidata / sqlit | “Open in…” / 10-row preview on exports | Thin wrap | Knowledge + desk detail actions |
| **P3** | botany | Delight card → `make run app=botany` | Trivial | `card_store.py` + store promote |

### Parallel SAFE app promotes (wrap path)

From [starter pack](../../../safe-app-store-public/docs/willow-compatible-projects.md#starter-pack-promote-first) — promote as standalone apps; Grove links to them:

1. nvitop, parllama (wave 1)  
2. visidata, sqlit (wave 2)  
3. calcure, taskdog (wave 3) — *partially redundant with steals above; promote for users outside Grove*  
4. feeds.fun, kanban-tui (wave 4)  
5. toolong, botany (wave 5)  

**Rule:** If P1 steal lands in Grove, still promote scout for **standalone** users and `make run` catalog breadth.

---

## What neither Grove nor scouts should take from flagships

Keep in sovereign apps (do not horizontalize away):

- Provenance atoms, ΔΣ honesty, Jeles citation behavior  
- law-gazelle case workflow, Nest PII boundaries  
- story-timeline narrative graph  
- Ratatosk agent loop (Grove coordinates; does not replace)  
- SITR1 install trust chain  

---

## Verification (when implementing)

| Borrow | Done when |
|--------|-----------|
| GPU vitals | NavBar shows VRAM; Kart card warns above threshold on T500 |
| Task tail | Failed Kart row shows stderr; Enter opens full log |
| kb_search | Knowledge query returns same top hit as `kb_search` MCP for test atom |
| Board view | Todo moves todo→doing→done in SOIL; persists across refresh |
| Session search | Query finds string in known ratatosk JSONL within 2s |

---

## Receipts

| Artifact | Location |
|----------|----------|
| This map | `willows-grove/docs/synthesis/grove-starter-borrow-map.md` |
| Scout starter pack | `safe-app-store-public/docs/willow-compatible-projects.md` |
| Grove vitals | `grove/apps/vitals.py` |
| Grove desk | `grove/apps/user_board.py`, `panes/user_todos.py` |
| Grove tasks | `panes/tasks.py` |
| Grove knowledge | `panes/knowledge.py` |

ΔΣ=42
