# Routing observability — dual write paths

**b17:** RTVB1 · ΔΣ=42  

Two different tables capture “routing” today:

| Location | Typical writers | Row shape |
|----------|-----------------|-----------|
| `willow.routing_decisions` | `willow.routing.oracle._write_decision` | `prompt_snippet`, `routed_to`, `rule_matched`, `latency_ms`, … |
| `public.routing_decisions` | `sap/sap_mcp.py` (`willow_route` tool) | `prompt_hash`, `session_id`, **`decision` JSONB** |

The dashboard **Routing** pane (`grove_reader.routing_decisions`) reads **`willow.routing_decisions`** only.

## Verify (run when Postgres is up)

```sql
-- Row counts
SELECT 'willow.routing_decisions' AS tbl, COUNT(*)::bigint AS n FROM willow.routing_decisions
UNION ALL
SELECT 'public.routing_decisions', COUNT(*) FROM public.routing_decisions;

-- Newest row per table
SELECT 'willow' AS tbl, MAX(ts) AS newest FROM willow.routing_decisions
UNION ALL
SELECT 'public', MAX(created_at) FROM public.routing_decisions;

-- Sample JSONB decisions from MCP path (last 5)
SELECT id, created_at, left(prompt_hash, 12) AS ph, decision
FROM public.routing_decisions
ORDER BY created_at DESC LIMIT 5;

-- Sample oracle-shaped rows (last 5)
SELECT id, ts, left(prompt_snippet, 40), routed_to, rule_matched, latency_ms
FROM willow.routing_decisions
ORDER BY ts DESC LIMIT 5;
```

If `willow.*` is empty but `public.*` grows, the dashboard feed will look silent — **expected** until unified or dual-sourced.
