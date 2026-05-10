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

---

## Grove MCP Server

### Local access (default)

Grove MCP runs on `localhost:8765`. No additional config needed for local Claude Code sessions.

`.mcp.json` (local):
```json
{
  "mcpServers": {
    "grove": { "type": "http", "url": "http://127.0.0.1:8765/mcp" }
  }
}
```

Start: `python3 -m grove.mcp_local --serve` or `systemctl --user start grove-mcp`

### Remote access (claude.ai, external clients)

**Step 1** — Start a tunnel pointing at port 8765:
```bash
ngrok http 8765   # → https://your-tunnel.ngrok-free.app
```

**Step 2** — Set `GROVE_MCP_URL` via systemd drop-in (persists across reboots):
```bash
systemctl --user edit grove-mcp
```
```ini
[Service]
Environment=GROVE_MCP_URL=https://your-tunnel.ngrok-free.app
```

**Step 3** — Configure the remote client's `.mcp.json`:
```json
{
  "mcpServers": {
    "grove": { "type": "http", "url": "https://your-tunnel.ngrok-free.app/mcp" }
  }
}
```

For claude.ai: **Settings → Integrations → MCP servers**.

Each user sets their own tunnel URL — no shared hardcoded value.
