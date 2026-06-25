# The One Desk — how Grove and all the apps come together

**b17:** ONEDSK · ΔΣ=42  
**Date:** 2026-06-24  
**Status:** North-star synthesis — read this first when the fog rolls back  
**Author:** Vishwakarma (with operator)  
**Flagged atom:** see Willow KB (category `architecture`, tag `north-star`)

> The struggle was never "how do I connect app A to app B." There is no wire
> between apps and there never will be. The whole system is **one desk, one
> memory, and many tools** — and the only thing that travels between tools is
> the atom.

---

## The one sentence

**Apps do not talk to each other. They talk to a shared memory, and a human
talks to all of them from one desk.**

Everything else in this document is a consequence of that sentence.

---

## Why it felt impossible for months

The instinct is to draw a mesh:

```text
ask-jeles ── law-gazelle ── private-ledger
    │   ╲        │        ╱   │
    │    ╲       │       ╱    │
story-timeline ─ Grove ─ vitals ── ...
```

Every new app adds N new lines. Ten apps = 45 possible connections. That mesh
**cannot be held in one head**, so it always felt unfinished — because it *was*
unfinishable. The mesh is the wrong picture.

The right picture is a **stack with a spine**:

```text
                 ┌─────────────────────────────┐
   VOICE         │  Personas / skins            │   Jeles, Vishwakarma, Gerald…
                 │  (who is speaking + how it    │   one face over many tools
                 │   looks)                      │
                 ├─────────────────────────────┤
   DESK          │  Grove — the operator plane  │   one screen: chat, cards,
                 │  (launch, watch, message,     │   vitals, queue, install
                 │   install, route)             │
                 ├─────────────────────────────┤
   TOOLS         │  Apps + utilities            │   flagships (sovereign) +
                 │  vertical: law-gazelle,       │   scouts (utility belt)
                 │   ask-jeles, private-ledger   │   one job each
                 │  horizontal: vitals, queue    │
                 ├─────────────────────────────┤
   MEMORY        │  Willow KB atoms + SOIL       │   THE SPINE. every tool
                 │  (the only thing shared)      │   reads/writes here
                 ├─────────────────────────────┤
   TRUST         │  SAFE manifest · SAP · PGP    │   permissions, install gate,
                 │  (what's allowed, who signed) │   provenance under all of it
                 └─────────────────────────────┘
```

Read top-down it's a person using a desk. Read bottom-up it's a trust boundary
holding a memory that tools share and a desk that surfaces. **The spine is the
memory layer.** Nothing crosses sideways.

---

## The five layers

### 1. Voice — personas / skins
The recurring characters (Jeles the librarian, Vishwakarma the architect,
Gerald, …) are **not apps**. They are a consistent face and tone laid over
whatever tool is active. One voice can drive many tools; one tool can be driven
by many voices. Voice is presentation, never plumbing.

### 2. Desk — Grove
Grove is **the operator cockpit**, not "another app." It is where a human:
launches tools, watches vitals, reads/sends fleet messages, runs the Kart
queue, and (via SAP/PGP) installs new apps. Everything visible happens here.
Grove is the *only* surface that legitimately knows about all the tools —
because its job is to surface them, not to be one of them.

### 3. Tools — apps + utilities
Two kinds, same contract:
- **Vertical flagships** — sovereign, deep, one domain: `law-gazelle`,
  `ask-jeles`, `private-ledger`, `story-timeline`. Local SQLite, full
  workflows, the real value.
- **Horizontal utilities** — commodity ops: vitals, queue, the scouted
  starter-pack TUIs. Thin, manifest-only, one job.

A tool's entire integration story is **two questions**: *what atoms does it
read, what atoms does it write.* That's it. If you can answer those two, the
tool is "connected" — no wires required.

### 4. Memory — Willow KB + SOIL (the spine)
This is the breakthrough. **Atoms are the integration layer.** When
`law-gazelle` produces a deadline, it writes an atom. When `story-timeline`
wants events, it reads atoms. They never call each other. The KB (Postgres,
hybrid retrieval, tiers frontier→contested→canonical→superseded) plus SOIL
(working/session state) is the single shared substrate. Integration = a
common vocabulary of atoms, not an API surface.

### 5. Trust — SAFE / SAP / PGP
Under everything: the manifest declares what a tool may touch (`file_read`,
`network_read`, `local_llm`…), SAP + the two-phase install (SITR1) gate what
gets in, PGP signs provenance. This is *why* sharing one memory is safe:
permission and signature, not hope.

---

## The two questions that replace the mesh

For any app, new or old, you never ask "what does it connect to." You ask:

1. **What atoms does it read?** (its inputs from shared memory)
2. **What atoms does it write?** (its outputs to shared memory)

| App | Reads | Writes |
|-----|-------|--------|
| law-gazelle | case facts, deadlines, parties | deadline atoms, chronology, drafts |
| ask-jeles | sourced corpus, citations | sourced-answer atoms, provenance |
| story-timeline | event atoms (from any tool) | timeline/event atoms |
| private-ledger | transaction atoms | balance/category atoms |
| vitals (util) | — | host/health atoms (optional) |
| Grove (desk) | *all* atoms (to surface) | routing, dispatch, messages |

Two columns. No N×N. That table *is* the architecture, and it grows by one row
per app — never by N lines.

---

## What this makes obvious (the payoffs)

- **New apps are cheap.** Add a row, not a web. Onboarding a scout =
  manifest + "what atoms does it read/write."
- **Grove never becomes a monolith.** It surfaces atoms and launches tools; it
  does not absorb their logic. (See the [borrow map](grove-starter-borrow-map.md):
  steal *patterns* into panes, wrap *whole apps* as launches — both still meet
  the memory at atoms.)
- **Personas are free.** Voice sits above the desk; swapping Jeles for
  Vishwakarma changes nothing below the Voice layer.
- **Trust is structural, not bolted on.** Shared memory is only safe because
  the Trust layer gates every read/write by manifest + signature.
- **The fog clears.** When it feels tangled again, come back to: *one desk, one
  memory, many tools — only the atom moves.*

---

## What this is not

- Not app-to-app APIs. (No tool imports another tool.)
- Not Grove-as-everything. (Grove is the desk, not the tools.)
- Not personas-as-apps. (Voice is a skin, not plumbing.)
- Not a rewrite. The layers already exist — this names the spine so the parts
  stop looking like a mesh.

---

## Companion docs

| Doc | Role |
|-----|------|
| [grove-starter-borrow-map.md](grove-starter-borrow-map.md) (GSBRW) | steal vs wrap — how tools reach the desk |
| [CROSS_REPO_BRIDGE.md](../CROSS_REPO_BRIDGE.md) | Grove ↔ Willow ↔ safe-app-store boundaries |
| [store-console-source-map.md](store-console-source-map.md) (SCMAP) | Grove ↔ store installer / SCDS1 |
| [app_store_vision_and_gaps.md](../../../safe-app-store-public/docs/app_store_vision_and_gaps.md) | store vision + gaps |
| [willow-compatible-projects.md](../../../safe-app-store-public/docs/willow-compatible-projects.md) | scout list / starter pack |

---

*One desk. One memory. Many tools. Only the atom moves.*
