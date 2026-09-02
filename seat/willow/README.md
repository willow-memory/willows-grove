# Willow's seat home — operator desk artifacts inside Willow's Grove

Owner: **Willow** (desk). Heimdallr does **not** maintain this tree.

One Jarvis seat — not a Governance / PM / PA mode switch. See
[docs/design/grove-persona-partition.md](../../docs/design/grove-persona-partition.md).

## Layout

| Path | Purpose |
|------|---------|
| `scripts/willow-seat.sh` | Orchestrator probe / desk / jeles federation wrapper |
| `scripts/unblock-jeles-federation.sh` | Operator: consent.federation + egress lease |
| `scripts/setup-jeles.sh` | Install / seed / ratify jeles-corpus |
| `scripts/consent-reconcile.sh` | Reconcile consent mirror (TTY + sudo) |
| `scripts/kart-watch-prs.sh` | Poll PR checks via `gh` |
| `scripts/jeles-intake.py` | Load / probe intake JSON |
| `jeles-intake/` | Novel intake pairs (Paperclip, willow-local, …) |

## Assumptions

- Sibling layout: `willow-memory/{willows-grove,willow-mcp,.willow}/`
- Override with `WILLOW_HOME`, `WMCP_REPO`, `JELES_REPO` as needed
- Runtime store remains under `$WILLOW_HOME` (not this git tree)

## Quick start

```bash
cd ~/github/willow-memory/willows-grove
bash seat/willow/scripts/willow-seat.sh probe
bash seat/willow/scripts/unblock-jeles-federation.sh   # when lease expired
```

Thin wrappers under `willow-memory/scripts/` still exec these paths for old habits.
