---
name: grove-serve
description: Turn Grove MCP OAuth serve mode on or off on request, toggling both the systemd --user service and the .mcp.json client entry, and front it with a tunnel for claude.ai
---

@markdownai v1.0

# /grove-serve

Turns Grove's MCP OAuth serve mode **on** or **off** without hand-editing
config. Wraps `scripts/grove-serve`, which manages a systemd `--user` service
for the `--serve` process and adds/removes the matching http entry in
`.mcp.json` so a local MCP client connects only while serve is on.

This is the remote-Grove path: the serve process binds `127.0.0.1:8765` and a
tunnel (Pangolin/Newt, cloudflared, ngrok, Tailscale Funnel) fronts it so
claude.ai can reach it over OAuth.

## When to use this

- The user asks to "turn on/off", "start/stop", or "enable/disable" Grove serve
  mode, remote Grove, or the Grove OAuth server.
- The user wants remote Grove reachable from claude.ai.
- The user wants to check whether serve mode is currently running.

## Commands

```bash
# one-time install (point your tunnel at 127.0.0.1:8765 first, then):
GROVE_MCP_URL=https://<public-host> scripts/grove-serve install
scripts/grove-serve on         # start serve + add local .mcp.json entry
scripts/grove-serve status     # unit state + entry + claude.ai connector URL
scripts/grove-serve logs       # follow logs (journalctl -f)
scripts/grove-serve off        # stop serve + remove entry
```

After `on` or `off`, tell the user to run `/mcp` to reconnect the local client.

## Making it reachable from claude.ai

1. `GROVE_MCP_URL` must be a **stable** public HTTPS base — OAuth issuer,
   RFC 9728 resource metadata, and the Host/Origin allowlist all derive from it.
2. If the tunnel forwards a `Host` that is neither loopback nor the
   `GROVE_MCP_URL` netloc, allowlist it with `GROVE_MCP_EXTRA_HOSTS` /
   `GROVE_MCP_EXTRA_ORIGINS` (comma-separated) via a `systemctl --user edit
   grove-mcp-serve` drop-in — never by disabling DNS-rebinding protection.
3. In claude.ai: **Settings → Connectors → Add custom connector**, URL
   `https://<public-host>/mcp`. First connect runs OAuth; approve at the
   `/grove-approve` page. Tokens last 30 days (no auto-refresh).

Full guide: [`docs/runbooks/grove.md`](../docs/runbooks/grove.md) → "Remote access".

## Guardrails

- Do not enable auto-approve on a tunnelled deployment.
- Run exactly one serve process per host/port; a second instance does not share
  in-memory OAuth/session state.
- Keep the public URL stable — a rotating URL invalidates registrations and
  tokens on every restart.
