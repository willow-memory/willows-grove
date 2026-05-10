# Runbook — Grove MCP Server

**b17:** RBG1W · ΔΣ=42

---

## Local access (default)

Grove MCP runs on `localhost:8765`. No additional config needed for local Claude Code sessions.

`.mcp.json` (local):
```json
{
  "mcpServers": {
    "grove": {
      "type": "http",
      "url": "http://127.0.0.1:8765/mcp"
    }
  }
}
```

Start the server:
```bash
python3 -m grove.mcp_local --serve
# or via systemd:
systemctl --user start grove-mcp
```

---

## Remote access (claude.ai, external clients)

To expose Grove to remote clients, you need a tunnel (ngrok, Cloudflare Tunnel, etc.).

**Step 1 — Start your tunnel pointing at port 8765:**
```bash
ngrok http 8765
# → https://your-tunnel.ngrok-free.app
```

**Step 2 — Set `GROVE_MCP_URL` before starting the server:**

Via systemd drop-in (recommended — persists across reboots):
```bash
systemctl --user edit grove-mcp
```
Add:
```ini
[Service]
Environment=GROVE_MCP_URL=https://your-tunnel.ngrok-free.app
```

Or export in your shell for a one-off run:
```bash
GROVE_MCP_URL=https://your-tunnel.ngrok-free.app python3 -m grove.mcp_local --serve
```

**Step 3 — Configure the remote client's `.mcp.json`:**
```json
{
  "mcpServers": {
    "grove": {
      "type": "http",
      "url": "https://your-tunnel.ngrok-free.app/mcp"
    }
  }
}
```

For claude.ai: add this under **Settings → Integrations → MCP servers**.

---

## Notes

- `GROVE_MCP_URL` is read by `grove/mcp_local.py` at startup. If unset, the server starts but won't advertise a public URL.
- Each user sets their own tunnel URL — there is no shared/default public URL.
- The systemd drop-in is per-user (`~/.config/systemd/user/grove-mcp.service.d/override.conf`) and is not committed to git.
