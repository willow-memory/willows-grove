# Runbook — Grove MCP

**b17:** RBMCP · ΔΣ=42  

## Modes (contract)

| Mode | Invocation | Auth |
|------|------------|------|
| **stdio** (default) | `python3 -m grove.mcp_local` | Implicit local trust |
| **serve** | `python3 -m grove.mcp_local --serve` | OAuth 2.0 PKCE |
| **serve + reload (dev)** | `python3 -m grove.mcp_local --serve --watch` | Same — parent **supervises a child** `--serve` process and restarts it when `grove/*.py` changes (`mcp.run` blocks in-process, so a subprocess is required). |

Set **`GROVE_MCP_URL`** to the public base URL when using serve mode (tunnel/ngrok). Source: [`grove/mcp_local.py`](../../grove/mcp_local.py) module docstring.

## Health checks

- **stdio:** process exits if imports/db fail — watch Claude/Code logs.
- **serve:** hit configured HTTP port (`GROVE_MCP_PORT`, default `8767`) per FastMCP deployment.

## LISTEN/NOTIFY thread

Serve mode starts a background Postgres **`LISTEN grove_channel`** thread; if DB is down it sleeps/backoffs — expect delayed push notifications.

## Failure modes

| Failure | Likely cause | Mitigation |
|---------|----------------|------------|
| OAuth errors | `GROVE_MCP_URL` mismatch | Align tunnel URL with issuer settings |
| No live updates | DB disconnect | Check Postgres; thread reconnects on backoff |

## Receipts

See [`../contracts/MESSAGE_ENVELOPE.md`](../contracts/MESSAGE_ENVELOPE.md) + extractor incidents list.
