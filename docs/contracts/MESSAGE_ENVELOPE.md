# Message envelope & bus contract (`grove.messages`)

**b17:** MSGEV · ΔΣ=42  

## Purpose

Define the **compatibility contract** for rows in `grove.messages` consumed by the dashboard, MCP tools, and automation. Authoritative validation is in [`schema.sql`](../../schema.sql) CHECK constraints and [`grove_db.py`](../../grove_db.py) constants.

## Field semantics

| Field | Contract |
|-------|-----------|
| `content` | UTF-8 text. Optional **tag line** prefix for extraction: `[DECISION]`, `[ADR]`, `[INCIDENT]`, `[RUNBOOK]`, `[SCHEMA]`, `[GAP]` (see extractor spec). |
| `message_type` | `text` default; `system` for automation; `file_share` / `reaction` as typed extensions. |
| `to_agent` | Named agent or `__all__` for broadcast (see `grove_db.BUS_BROADCAST`). |
| `bus_type` | High-level bus classification. Application constants include `COMMAND`, `RESPONSE`, `EVENT`, `INTERRUPT`, `HEARTBEAT`, `ACK`, `DATA`, `SYNC` (`grove_db.BUS_TYPES`). DB allows broader text — treat unknown values as forward-compatible **opaque** labels until adopted. |
| `priority` | Integer; lower = more urgent in CAN-style mapping (`grove_db.BUS_PRIORITY`). Default **3** (`NORMAL`). |
| `correlation_id` | Optional string correlating COMMAND/RESPONSE pairs or tool chains. |
| `ttl` | Optional seconds-to-live hint for consumers (best-effort). |

## Compatibility rules

1. **Never remove columns** without an ADR and migration path; prefer additive changes.
2. **Consumers must tolerate** unknown `bus_type` strings (DB does not enumerate all values in CHECK).
3. **Soft delete:** `is_deleted` ≠ 0 means hidden from normal UI — automation should respect this.

## Receipts

- `grove_db.py` — `BUS_TYPES`, `BUS_PRIORITY`, `BUS_BROADCAST`
- `schema.sql` — `messages` CHECK constraints
