# Runbook — Grove messaging

**b17:** RBGRV · ΔΣ=42  

## Scope

Message retention strategy (policy — ADR pending), search/index behaviour (`willow_indexed_at`), **`LISTEN/NOTIFY`** fan-out.

## NOTIFY path

On insert into `grove.messages`, trigger fires `pg_notify('grove_channel', channel_id)`. Dashboard/MCP subscribers filter by channel id.

## Verify message pipeline

```sql
SET search_path = grove, public;
SELECT id, name FROM channels ORDER BY id LIMIT 20;
SELECT MAX(id) AS newest_message_id FROM messages;
```

## Search / retention

- Full-text search specifics live in app code (`grove_reader`/dashboard filters) — not duplicated here.
- Long-term retention policy is an open decision; track via ADR if policy is set.

## Incident patterns

Correlate operational notes with **[INCIDENT]** candidates under [`../generated/`](../generated/README.md).

Curated entry points (with receipts): [`INCIDENT_INDEX.md`](INCIDENT_INDEX.md).
