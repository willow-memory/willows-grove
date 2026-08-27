# Willow's Grove

The operator's seat for the Willow AI fleet — a loopback-only served page on
`127.0.0.1:8766`, hosting Grove Web Components that read live state from
Postgres, the Nestor store, and the willow-mcp `kb_journal` seam. No public
HTTP surface. The MCP server (`./run_mcp.sh`) is a separate process for
remote (claude.ai) tool access.

**Home:** `willow-memory/willows-grove`. Ratified by the human trust root,
not the fleet — see [`docs/INVARIANTS.md`](docs/INVARIANTS.md) §12.

## Entry points

| Command | Purpose |
|---|---|
| `python3 grove_serve.py` | Loopback-only served-page host on `127.0.0.1:8766` |
| `./run_mcp.sh` | Grove MCP server — stdio mode (Claude Code / Cursor spawns this) |
| `./run_mcp.sh --serve` | Grove MCP over HTTP+OAuth on `:8765` for remote clients behind a tunnel |
| `scripts/grove-serve {install\|on\|off\|status}` | Toggle the `--serve` systemd unit + `.mcp.json` entry together |

See [`docs/OPS_RUNBOOK.md`](docs/OPS_RUNBOOK.md) for boot preconditions,
health-check sweeps, and failure recovery.

## Architecture

| File / dir | What |
|---|---|
| `grove_serve.py` | Loopback-only served-page host on 127.0.0.1:8766 (Starlette + uvicorn; two placeholder routes) |
| `grove_html.py` | The served page's HTML shell |
| `grove_db.py` | Postgres reader (bounded `connect_timeout` + `statement_timeout`) |
| `grove_reader.py` | Reader helpers for channels, messages, agents, routing |
| `grove/` | Grove Python package (readers, endpoints, MCP serve-mode auth) |
| `web/components/*.js` | Web Components |
| `web/boot/*.js` | Page-level boot modules |
| `u2u/` | Signed LAN transport (see u2u section above) |
| `bridge/` | Matrix bridge |

## u2u — signed LAN transport (not encrypted)

The `u2u/` package carries signed (Ed25519) human-to-human DMs across the
LAN. Messages are cleartext on the LAN — u2u guarantees *who sent this* and
*that the message is intact*, not *that only the recipient can read it*.
See [`docs/design/u2u-security-limits.md`](docs/design/u2u-security-limits.md)
for the full statement of what u2u does and does not guarantee. Encryption is planned for Gate 6.

## Discipline

Twelve CI-enforced invariants in [`docs/INVARIANTS.md`](docs/INVARIANTS.md):

- **§1** three-state contract (populated / empty / unreachable — never collapsed)
- **§2** supersedes D7 ("absence is a state" no longer covers unreachable)
- **§3** doc discipline (citations resolve, CHANGELOG cites PR, sections name witnesses)
- **§4** reader/endpoint coverage
- **§5** u2u trust order (signature → consent → dispatch, in that sequence — see [`docs/design/u2u-security-limits.md`](docs/design/u2u-security-limits.md))
- **§6** manifests describe code, not aspirations
- **§7** consent flows are real, not automatic
- **§8** panels consume live endpoints
- **§9** seed reads real canon
- **§10** CI proves the invariants
- **§11** persona provenance (`Persona:` trailer on every code-changing commit)
- **§12** ratification (`Ratified-by:` line on every PR-open and merge)

Every section is enforced by at least one CI witness. The checkers live at
`scripts/check_*.py`; they run on every push through
`.github/workflows/tests.yml`.

## Getting started as a tester

```
git clone https://github.com/willow-memory/willows-grove.git
cd willows-grove
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
psql -c "CREATE DATABASE willow_20;" && psql -d willow_20 -f schema.sql
python3 -m pytest -x -q --ignore=tests/e2e --ignore=tests/e2e_ollama --ignore=tests/e2e_willow_mcp
```

Then `python3 grove_serve.py` and open http://127.0.0.1:8766 in a browser
running on the same box.

## The audit record

`docs/audits/loki-v0.9-audit.md` — Loki's v0.9 audit in his voice.
38 ranked findings from a seven-lens Loki-swarm, all resolved in the
build or refuted with reason.

`docs/audits/loki-swarm-measurement.md` — persona-discipline scored on
seven dimensions. The measurement research: register hold 0/41 florid,
deny-list hold 0/41 build proposals, three-column completeness 41/41,
softening 1/41, authority-as-correctness 0/41. Reproducibility layer at
`docs/audits/loki-swarm-metadata.md`.

## What's known-not-yet-done

`docs/design/pr14-carryovers.md` — the v0.10 punch list. Nothing here is
implemented yet; it names what v0.9 punted and why.
