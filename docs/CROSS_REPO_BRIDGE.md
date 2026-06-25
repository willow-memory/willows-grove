# Cross-repo bridge — Grove ↔ Willow ↔ SAFE App Store

**b17:** XRB01 · ΔΣ=42  

## Boundary

| Layer | Repo | Responsibility |
|-------|------|----------------|
| **Operator + installer surface** | `safe-app-willow-grove` | Channels/messages, dashboard/TUI, installer/store pane, MCP “Grove” tools, LISTEN/NOTIFY wiring |
| **Catalog + app source + design contract** | `safe-app-store` | `catalog.json`, `apps/<id>/`, manifests, SCDS1 Era Skins — artifacts and vocabulary, not runtime orchestration |
| **System layer (KB, tasks, routing, install authority)** | `willow-2.0` | `pg_bridge.py` public schema, embeddings, Kart-facing tables, routing_decisions shape, `sap.installed_apps`, SAP gate/MCP install path, PGP/GPG manifest trust |

**Ground truth split:** Grove is the **human+agent message bus** and holds **`grove.messages`**. It is also the **operator/installer place** — the surface where fleet work and app install/discovery live together. Willow owns **`public.knowledge`**, extended task/dispatch tables, the richer **`routing_decisions`** row shape, and the **install authority path** (SAP registry + PGP trust) when both stacks share one Postgres (`willow_20`). The SAFE App Store repo is the **direct catalog/app source**; Grove reads it in place, with no store daemon or middle-manager service in between.

**One-line summary:** Grove is the operator/installer place; safe-app-store is the direct catalog/app source; SAP/PGP is the authority path.

## Grove ↔ SAFE App Store

Grove and the installer belong in the **same operator place**. The Grove app points directly at store apps (`catalog.json` + `apps/<id>/`), invokes the SAP/MCP install path, and emits Grove events. There is no separate store-orchestrator service between Grove and the catalog.

| Concern | Owner | Notes |
|---------|-------|-------|
| Browse/discover apps | Grove installer pane | Reads `safe-app-store/catalog.json` directly |
| App artifacts | `safe-app-store` | `apps/<id>/`, `safe-app-manifest.json` |
| Permission/gate UX language | SCDS1 design contract | Implemented in Grove's installer pane (Era Skins, gate panels, privacy meter) |
| Install write | Willow/SAP via MCP | `sap.register()`, `sap.installed_apps`; never direct SQL from UI |
| Trust chain | Willow/SAP + PGP | Folder at `~/SAFE/Applications/<id>/` + registry row + signed manifest trust stay in sync |
| Fleet comms | Grove | Install/uninstall events on the bus; Grove is not a passive launcher |

**Rules:**

- Grove reads `safe-app-store` as a catalog/source tree. No proxy through a store daemon.
- Install actions initiated in Grove can run against any MCP/KB. Non-Willow installs stage files + local `.install-state.json` only (`pending_trust`) — **no** `sap.installed_apps` row until Willow MCP auto-promotes after PGP verify/sign. See [`adrs/ADR-20260615-safe-app-install-trust.md`](adrs/ADR-20260615-safe-app-install-trust.md) (SITR1).
- `safe-app-store` provides app artifacts and design contracts; it does not own operator UX or fleet comms.
- SCDS1 (`docs/specs/store_console_design_spec.md`) defines how permission/gate surfaces should look and feel; Grove's installer pane implements that contract in the operator place.

**Local checkout:** `~/github/safe-app-store-public` (public mirror of `rudi193-cmd/safe-app-store`).

## Shared database

Both Grove and Willow codebases assume (by default) database **`willow_20`**. Connection precedence:

1. `WILLOW_DB_URL` if set  
2. Else `dbname=$WILLOW_PG_DB` + `user=$WILLOW_PG_USER` (peer auth common locally)

## What not to duplicate

- **Do not** paste full `public.knowledge` DDL into `safe-app-willow-grove/schema.sql` — the standalone file documents this explicitly; drift silently breaks the dashboard.
- **Do** link to [`willow-2.0/docs/db/WILLOW_SCHEMA.md`](../../willow-2.0/docs/db/WILLOW_SCHEMA.md) for KB/task/routing truth.
- **Do not** add a store-orchestrator service between Grove and `safe-app-store` — Grove reads the catalog directly.
- **Do not** bypass SAP/PGP on install — copying app files without registry + trust update is a partial install and must stay `pending_trust`.

## MCP notes

Grove MCP (`python3 -m grove.mcp_local`) exposes messaging tools; it is **not** the full Willow MCP tool surface. App install/discovery may run with any MCP and any KB, but trust promotion is Willow-specific: `pending_trust` is cleared only through the Willow MCP authority path (`app_install`, SAP gate, PGP/GPG verification/update). Transport modes and env vars are documented in [`runbooks/mcp.md`](runbooks/mcp.md).

## Receipts

- `safe-app-willow-grove/schema.sql` — non-authoritative comment block on `public.knowledge`
- `willow-2.0/core/pg_bridge.py` — authoritative `CREATE TABLE knowledge …`
- `safe-app-store-public/catalog.json` — app catalog index
- `safe-app-store-public/docs/specs/store_console_design_spec.md` — SCDS1 design contract (b17: SCDS1)
- `safe-app-willow-grove/docs/synthesis/store-console-source-map.md` — integration brief (b17: SCMAP)
- `safe-app-willow-grove/docs/adrs/ADR-20260615-safe-app-install-trust.md` — install/trust two-phase model (b17: SITR1)
