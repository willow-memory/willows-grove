# Canonical Architecture Reference — Willow's Grove (willow-memory/willows-grove)

**b17:** CARWG · ΔΣ=42  

This document is the **canonical architecture reference (CAR)** for the **Grove app repo**: dashboard, database access patterns for Grove messaging, optional LAN surfaces (u2u, `grove_serve`), and MCP exposure of Grove to agents/editors.

## Scope

**In scope:** Grove messaging schema (`grove.*`), dashboard/TUI entrypoints, MCP transport modes for Grove tools, environment contracts (`WILLOW_DB_URL`), LISTEN/NOTIFY behaviour for live UI updates.

**Out of scope:** Full Willow KB/task pipelines owned by `willow-2.0/core/pg_bridge.py`; duplicate DDL for `public.knowledge` — see [`schema.sql`](../schema.sql) commentary and, for the `public` schema reference, [`docs/db/WILLOW_SCHEMA.md` in the archived `rudi193-cmd/willow-2.0`](https://github.com/rudi193-cmd/willow-2.0/blob/master/docs/db/WILLOW_SCHEMA.md).

> The willow-2.0 link was written as `../../willow-2.0/...`, which resolves only
> in a checkout where willow-2.0 sits beside this repo. That layout is gone —
> the 2026-08-10 move put every repo under its own org folder — so the relative
> path pointed at nothing. The document itself is real and still readable; the
> repo is public and **archived**, so treat it as a historical reference rather
> than a live one.

## Receipts

| Source | Role |
|--------|------|
| `schema.sql` | Idempotent bootstrap for `grove` + `willow.routing_decisions` stub + `public.tasks` |
| `grove_db.py` | Schema owner at runtime; bus constants (`BUS_TYPES`, priorities) |
| `grove/mcp_local.py` | MCP **stdio** vs **`--serve`** + `GROVE_MCP_URL` contract |

## System map

```text
Operators / agents
        │
        ▼
  Textual dashboard / curses TUI / standalone DM
        │
        ├──► psycopg2 pool ──► Postgres `grove.messages` (+ channels, flags, cursors)
        │
        ├──► LISTEN grove_channel ◄── trigger on INSERT (bridge to UI / MCP push)
        │
        └──► MCP (FastMCP) stdio or HTTP+OAuth serve mode
```

## Ownership rules

1. **Grove schema** — defined and migrated in **`grove_db.py`** / **`schema.sql`** for standalone installs. Do not fork DDL for `public.knowledge` here.
2. **`grove_reader.py`** — read-only helpers for the dashboard; writes go through **`grove_db.py`**.
3. **No web ports for the dashboard** — portless operation is a product constraint.

## Interfaces (see contracts)

- **Message envelope:** [`contracts/MESSAGE_ENVELOPE.md`](contracts/MESSAGE_ENVELOPE.md)
- **MCP deployment:** [`runbooks/mcp.md`](runbooks/mcp.md)

## How to verify

```sql
-- Message volume and newest ids (run in psql against willow_20)
SET search_path = grove, public;
SELECT COUNT(*) AS message_count FROM messages;
SELECT MAX(id) AS latest_message_id FROM messages;
SELECT id, name FROM channels ORDER BY id;
```

## Related

Two documents this file used to link as local siblings are **not in this tree,
by design** — [`INDEX.md`](INDEX.md) records the decision under *"Not in this
tree (by design)"*: cross-repo synthesis and the Grove-docs extractor cover work
outside what shipped as `willows-grove` 0.9.0, and live at the old
`rudi193-cmd/safe-app-willow-grove` repo.

| Document | Where it lives |
|---|---|
| `CROSS_REPO_BRIDGE.md` | `rudi193-cmd/safe-app-willow-grove` — **private, archived** |
| `extractor/GROVE_DOCS_EXTRACTOR_SPEC.md` (Grove history → ADRs/digests) | `rudi193-cmd/safe-app-willow-grove` — **private, archived** |

They are named rather than linked on purpose. That repository is private and
archived, so a URL would 404 for most readers — which is the same dead end the
relative links produced, dressed up as a working reference. If you need either
document, ask the operator for access to the archive; do not expect to reach it
from here.
