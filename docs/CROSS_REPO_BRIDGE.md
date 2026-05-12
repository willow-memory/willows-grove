# Cross-repo bridge — Grove ↔ Willow

**b17:** XRB01 · ΔΣ=42  

## Boundary

| Layer | Repo | Responsibility |
|-------|------|----------------|
| **Comms + UI surface** | `safe-app-willow-grove` | Channels/messages, dashboard/TUI, MCP “Grove” tools, LISTEN/NOTIFY wiring |
| **System layer (KB, tasks, routing PG schema)** | `willow-1.9` | `pg_bridge.py` public schema, embeddings, Kart-facing tables, routing_decisions shape used by tools |

**Ground truth split:** Grove is the **human+agent message bus** and holds **`grove.messages`**. Willow owns **`public.knowledge`**, extended task/dispatch tables, and the richer **`routing_decisions`** row shape when both stacks share one Postgres (`willow_19`).

## Shared database

Both codebases assume (by default) database **`willow_19`**. Connection precedence:

1. `WILLOW_DB_URL` if set  
2. Else `dbname=$WILLOW_PG_DB` + `user=$WILLOW_PG_USER` (peer auth common locally)

## What not to duplicate

- **Do not** paste full `public.knowledge` DDL into `safe-app-willow-grove/schema.sql` — the standalone file documents this explicitly; drift silently breaks the dashboard.
- **Do** link to [`willow-1.9/docs/db/WILLOW_SCHEMA.md`](../../willow-1.9/docs/db/WILLOW_SCHEMA.md) for KB/task/routing truth.

## MCP notes

Grove MCP (`python3 -m grove.mcp_local`) exposes messaging tools; it is **not** the full Willow MCP tool surface. Transport modes and env vars are documented in [`runbooks/mcp.md`](runbooks/mcp.md).

## Receipts

- `safe-app-willow-grove/schema.sql` — non-authoritative comment block on `public.knowledge`
- `willow-1.9/core/pg_bridge.py` — authoritative `CREATE TABLE knowledge …`
