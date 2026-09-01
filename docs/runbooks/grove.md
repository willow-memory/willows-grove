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

Correlate operational notes with **[INCIDENT]** candidates under
`docs/generated/` — specifically `docs/generated/incident-candidates.md`, which
[`INCIDENT_INDEX.md`](INCIDENT_INDEX.md) and [`postgres.md`](postgres.md) both
cite.

> **That directory is not in this tree, and is not missing.** It is *output*:
> the Grove-docs extractor writes it, and the extractor itself is recorded in
> [`INDEX.md`](../INDEX.md) under *"Not in this tree (by design)"*. Nothing here
> generates it, so the path is named rather than linked — a link would promise a
> file no checkout of this repository has.

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

The serve process **always binds `127.0.0.1:8765`** — it never listens on a
public interface itself (`grove/mcp_local.py`, `host="127.0.0.1"`). To reach it
from claude.ai you put a **tunnel** in front of loopback. The code is
tunnel-agnostic: Pangolin, ngrok, cloudflared, and Tailscale Funnel all work —
the server only cares about `GROVE_MCP_URL`.

Three things must line up:

1. The tunnel forwards a **stable public HTTPS host** → `127.0.0.1:8765`.
2. `GROVE_MCP_URL` is set to that public base URL, because OAuth derives its
   issuer, RFC 9728 resource metadata, and the Host/Origin allowlist from it. A
   rotating free-tier URL invalidates client registrations and tokens on every
   restart — use a reserved/stable hostname.
3. The tunnel's forwarded `Host` header is either loopback (`127.0.0.1:8765`) or
   the exact `GROVE_MCP_URL` netloc — both are allowlisted automatically. If a
   tunnel forwards some other host, allowlist it with `GROVE_MCP_EXTRA_HOSTS`
   (see "DNS-rebinding allowlist" below) rather than turning protection off.

#### Toggle it with `grove-serve`

`scripts/grove-serve` manages the systemd `--user` unit and the local `.mcp.json`
entry together, so serve mode is one command:

```bash
# one-time: reserve/point your tunnel at 127.0.0.1:8765 first, then:
GROVE_MCP_URL=https://grove.example.org scripts/grove-serve install
scripts/grove-serve on       # start serve + add local .mcp.json entry
scripts/grove-serve status   # unit state, entry presence, claude.ai connector URL
scripts/grove-serve logs     # journalctl -f
scripts/grove-serve off      # stop serve + remove entry
```

To change the public URL later without reinstalling:
```bash
systemctl --user edit grove-mcp-serve
```
```ini
[Service]
Environment=GROVE_MCP_URL=https://grove.example.org
```

#### Pangolin

Pangolin fronts loopback one of two ways.

**A. Newt (Pangolin's tunnel client, no inbound ports on the origin).** Register
a resource in the Pangolin dashboard for your public hostname, target
`http://127.0.0.1:8765`, then run Newt on the Grove host:
```bash
newt --id <resource-id> --secret <resource-secret> --endpoint https://pangolin.example.org
```
Set `GROVE_MCP_URL=https://<your-pangolin-hostname>`. Newt forwards the public
`Host`, which matches the `GROVE_MCP_URL` netloc — no extra config needed.

**B. Reverse-proxy target (Pangolin/Traefik in front, origin reachable on the
LAN).** Point the Pangolin resource at the Grove host's `:8765`. If the proxy
rewrites `Host` to an internal name (Traefik `passHostHeader: false`, or an
upstream service name), add that value:
```ini
[Service]
Environment=GROVE_MCP_EXTRA_HOSTS=grove.internal:8765
Environment=GROVE_MCP_EXTRA_ORIGINS=https://grove.internal:8765
```
Prefer preserving the original Host (`passHostHeader: true`) so no extra is
needed.

#### Other tunnels (drop-in)

```bash
ngrok http 8765                                  # → https://<sub>.ngrok-free.app
cloudflared tunnel --url http://127.0.0.1:8765   # named tunnel = stable host
tailscale funnel 8765                            # → https://<host>.<tailnet>.ts.net
```
Set `GROVE_MCP_URL` to whichever public base you get, then restart the unit.

#### DNS-rebinding allowlist

`_transport_security()` keeps DNS-rebinding protection **on in every
deployment** and allowlists: loopback (`127.0.0.1:*`, `localhost:*`, `[::1]:*`),
the `GROVE_MCP_URL` netloc, and anything in `GROVE_MCP_EXTRA_HOSTS` /
`GROVE_MCP_EXTRA_ORIGINS` (comma-separated). These extras are the supported way
to accommodate a tunnel that forwards a different Host — protection is never
disabled to make a tunnel work.

#### Point claude.ai at it

**Settings → Connectors → Add custom connector**, URL `https://<public-host>/mcp`.
On first connect claude.ai runs OAuth: it registers, hits `/authorize`, and your
browser lands on the **`/grove-approve`** consent page. Click **Allow** — no
token is issued until you do. Tokens last 30 days (claude.ai does not
auto-refresh).

Each user sets their own tunnel URL — no shared hardcoded value.

#### Read vs write scopes

Every token needs at least `grove:read` — that floor is enforced server-wide
(`required_scopes` in `AuthSettings`, `grove/mcp_local.py`), so an
unauthenticated or scope-less request is refused before it reaches any tool.
`grove:write` gates the 9 tools that mutate state (`grove_send_message`,
`grove_reply`, `grove_flag`, `grove_unflag`, `grove_bus_send`,
`grove_bus_delete`, `grove_ack`, `grove_heartbeat`, `grove_create_channel`) —
checked per call against the token that made *that* request, via the MCP
SDK's auth-context contextvar. Everything else (history, search, fleet
status, …) only needs `grove:read`.

`grove` is kept as a back-compat superscope implying both — a 30-day token
minted before this existed, or any client that still asks for plain `grove`,
keeps full access without re-authorizing.

An ordinary connect (no explicit `scope=` on `/authorize`) still gets full
access — `default_scopes` is `grove:read grove:write`. To grant a client
**read-only** access instead, have it request `scope=grove:read` explicitly
when it hits `/authorize` (most MCP clients expose this as a connector-level
scope setting, or it can be set on the client during dynamic registration via
the `scope` field). The `/grove-approve` consent page shows exactly which
scopes are being requested — check that line before clicking Allow if you
expect read-only.

Revoke and re-approve (delete `~/.willow/grove_mcp_token`, or the specific
token) to change a client's grant later; there is no in-place scope upgrade
short of re-running the OAuth flow.

#### Remote tool surface

Beyond messaging (`grove_send_message`, `grove_get_history`, `grove_search`,
`grove_reply`, `grove_watch*`, the bus tools), serve mode exposes fleet-awareness
and channel management to remote clients:

| Tool | What |
|------|------|
| `grove_agents` | Who is alive (latest HEARTBEAT per sender) |
| `grove_fleet_status` | Rich AGENTS-region rows: presence + what each agent is doing |
| `grove_mentions` | Recent messages @-mentioning a handle |
| `grove_human_required` | The human-required queue — work paused pending an operator |
| `grove_create_channel` | Create (or revive) a group text channel |
