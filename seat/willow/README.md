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
| `scripts/kart-watch-prs.sh` | Poll PR checks via `gh` (accepts `repo#num ...` args or `$WATCH_PRS`) |
| `willow-seat.sh pr-watch` | One-shot steward tick (`willow-bot-steward tick`; falls back to mcp `loki_pr_watch.sh`) |
| `willow-seat.sh pr-watch-loop` | Steward loop + `AGENT_LOOP_TICK_PR_AUDIT` (`willow-bot-steward loop`) |
| `willow-seat.sh heartbeat` | Curated MCP tool heartbeat (`willow-bot-steward heartbeat`) |
| `willow-seat.sh scan` | One-shot scan of open fleet PRs (`willow-bot-steward scan`) |
| `willow-seat.sh steward` | Run any `willow-bot-steward` command directly |
| `willow-seat.sh intake` | Run `jeles-intake.py` using seated Python environment |
| `scripts/jeles-intake.py` | Load / probe intake JSON (auto-resolves Jeles venv) |
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

**Open the repo root.** This is Willow's Grove, so the Desk is what you get by
opening it — there is no subdirectory to know about. The root
[`.mcp.json`](../../mcp.template.json) seats you as `willow` with
`WILLOW_HUMAN_ORCHESTRATOR=1`; Heimdallr's Watch is a lens you open on purpose
at [`seat/heimdallr/`](../heimdallr/). Ratified 2026-09-09. See
[`../../CLAUDE.md`](../../CLAUDE.md).

This directory holds desk **content** — seat scripts and `jeles-intake/`. It no
longer carries seat wiring; that moved to the root.

Each seat's `.mcp.json` is **not tracked** — `**/.mcp.json` is ignored on an
operator box because it carries absolute paths and a seat identity. Copy the
seat's `mcp.template.json` and substitute `@HOME@` and `@VAULT_BOX@`. Same rule
as [`deploy/kart-sandbox.template.json`](../../deploy/kart-sandbox.template.json):
the template travels, the wiring does not.

The root `.claude/settings.json` carries the willow-mcp SessionStart /
PreToolUse / SessionEnd hooks and pins `WILLOW_APP_ID` inline on each command —
the hook resolves the seat from its own process env, not from `.mcp.json`, so an
unpinned hook inherits whatever the launching shell exported. It resolves the
interpreter through `$CLAUDE_PROJECT_DIR/.venv`, so it needs the repo venv to
have willow-mcp installed with its dependencies — `forge-play` included. An
editable install pins its dependency set at install time, so a venv whose
`willow_mcp` import works can still be missing what `willow_mcp` requires.
