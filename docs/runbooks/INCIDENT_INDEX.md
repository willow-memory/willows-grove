# Incident index (curated from Grove backfill)

**b17:** INCIX · ΔΣ=42  

First-pass **top 5** operational threads from `docs/generated/incident-candidates.md` (refs-not-blobs). Pull full text in psql by `id`.

| Priority | `grove.messages.id` | Topic | Runbook hook |
|---:|---:|---|---|
| 1 | 8482 | MCP systemd unit pointed at wrong repo / `PYTHONPATH` — session handoff | [`mcp.md`](mcp.md) |
| 2 | 8466 | CI / `embed()` blocked on Ollama — fail-fast vs long sleeps | [`postgres.md`](postgres.md) (dependency health) |
| 3 | 8548 | Run Ledger / `willow.runs` schema gate before wrappers | [`grove.md`](grove.md) + Willow schema docs |
| 4 | 8508 | Norn not running — who owns `run_id` at session start | [`grove.md`](grove.md) |
| 5 | 8511 | Fleet consensus — MCP fingerprints + message IDs in `run_events` | [`mcp.md`](mcp.md) |

## Verify

```sql
SET search_path = grove, public;
SELECT id, sender, left(content, 120) FROM messages WHERE id IN (8482, 8466, 8548, 8508, 8511);
```

_Update this index when incidents graduate into full runbook sections._
