# Canonical Architecture Reference — Willow Grove (willows-grove)

**b17:** CARWG · ΔΣ=42  

This document is the **canonical architecture reference (CAR)** for the **Grove app repo**: dashboard, database access patterns for Grove messaging, optional LAN surfaces (u2u, `grove_serve`), and MCP exposure of Grove to agents/editors.

## Scope

**In scope:** Grove messaging schema (`grove.*`), dashboard/TUI entrypoints, MCP transport modes for Grove tools, environment contracts (`WILLOW_DB_URL`), LISTEN/NOTIFY behaviour for live UI updates.

**Out of scope:** Full Willow KB/task pipelines owned by `willow-2.0/core/pg_bridge.py`; duplicate DDL for `public.knowledge` — see [`schema.sql`](../schema.sql) commentary and [`willow-2.0/docs/db/WILLOW_SCHEMA.md`](../../willow-2.0/docs/db/WILLOW_SCHEMA.md) in the sibling repo.

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

- Cross-repo bridge: [`CROSS_REPO_BRIDGE.md`](CROSS_REPO_BRIDGE.md)
- Extractor spec (Grove history → ADRs/digests): [`extractor/GROVE_DOCS_EXTRACTOR_SPEC.md`](extractor/GROVE_DOCS_EXTRACTOR_SPEC.md)
