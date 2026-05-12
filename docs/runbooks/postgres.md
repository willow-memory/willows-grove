# Runbook — Postgres (`willow_19`)

**b17:** RBPGS · ΔΣ=42  

## Scope

Backup/restore, pool exhaustion, locks — **shared** by Grove and Willow when using one cluster.

## Symptoms → checks

| Symptom | Check |
|---------|--------|
| Dashboard hangs / MCP timeouts | `SELECT count(*) FROM pg_stat_activity WHERE datname = current_database();` |
| Pool exhaustion (`pool exhausted` in logs) | Increase pool sizes only after confirming leak; watch idle connections |
| Lock waits | `SELECT * FROM pg_locks WHERE NOT granted LIMIT 20;` |

## Verify Grove connectivity

```bash
psql "$WILLOW_DB_URL" -c "SET search_path=grove,public; SELECT COUNT(*) FROM messages;"
```

## Receipts

Populate **[INCIDENT]**-tagged Grove messages in `docs/generated/incident-candidates.md` via extractor (refs, not pasted chat).

## Escalation

If data loss risk: stop writers, take `pg_basebackup` / snapshot per your infra policy, then investigate.
