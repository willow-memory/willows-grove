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

Design: [docs/design/seat-stack.md](../../docs/design/seat-stack.md) —
phone → Ratatosk → MCP / Grove bus → tier-0 homecoming.

## Assumptions

- Sibling layout: `willow-memory/{willows-grove,willow-mcp,.willow}/`
- Override with `WILLOW_HOME`, `WMCP_REPO`, `JELES_REPO` as needed
- Runtime store remains under `$WILLOW_HOME` (not this git tree)

## Quick start

```bash
cd ~/github/willow-memory/willows-grove
. ~/github/willow-memory/.willow/fleet.env   # vault + charter paths
bash seat/willow/scripts/willow-seat.sh probe
bash seat/willow/scripts/unblock-jeles-federation.sh   # when lease expired
```

Thin wrappers under `willow-memory/scripts/` still exec these paths for old habits.

## Opening the Desk

Open Claude Code **with this directory as the working directory**. That makes
`seat/willow/` the project root, so `seat/willow/.mcp.json` is the config that
loads and `session_enter` seats you as `willow` with
`WILLOW_HUMAN_ORCHESTRATOR=1`. The repo root is Heimdallr's Watch and boots the
`heimdallr` seat; which seat you get is decided by where you opened, not by a
file that claims an identity. See [`../../CLAUDE.md`](../../CLAUDE.md).

`.mcp.json` is **not tracked** — `**/.mcp.json` is ignored on an operator box
because it carries absolute paths and a seat identity. Copy
[`mcp.template.json`](mcp.template.json) and substitute `@HOME@` and
`@VAULT_BOX@`. Same rule as
[`deploy/kart-sandbox.template.json`](../../deploy/kart-sandbox.template.json):
the template travels, the wiring does not.

`WILLOW_PROJECT_ROOT` points at the grove root, so the Desk reasons over the
whole repository even though the seat is chosen from this subdirectory.

`.claude/settings.json` carries the willow-mcp PreToolUse guards. It resolves
the interpreter through `$CLAUDE_PROJECT_DIR/../../.venv`, so it needs the repo
venv to have willow-mcp installed with its dependencies — `forge-play` included.
An editable install pins its dependency set at install time, so a venv whose
`willow_mcp` import works can still be missing what `willow_mcp` requires.
