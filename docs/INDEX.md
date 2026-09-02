# Willow's Grove — documentation index

Ground truth is the code (this repo at v0.10.0, published to PyPI as
[`willows-grove`](https://pypi.org/project/willows-grove/)) plus the
tables Postgres actually holds (`grove.*` and `willow.*`). This tree
adds human-readable architecture, contracts, runbooks, and the design
decisions that shaped what got built.

## Start here

| Doc | Purpose |
|-----|---------|
| [`../README.md`](../README.md) | What Grove is, how to boot it, how to test it |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Canonical Architecture Reference — components, interfaces, ownership |
| [`INVARIANTS.md`](INVARIANTS.md) | The twelve CI-enforced invariants (§1–§12) — read before proposing changes |
| [`OPS_RUNBOOK.md`](OPS_RUNBOOK.md) | Boot preconditions, health-check sweeps, failure recovery |
| [`grove-served-page.md`](grove-served-page.md) | Operator guide for the served page on `127.0.0.1:8766` |
| [`TESTER_ONBOARDING.md`](TESTER_ONBOARDING.md) | Beta tester setup — clone → deps → smoke |

## Operator paths

| Area | Doc |
|------|-----|
| Postgres (`willow_20`) | [`runbooks/postgres.md`](runbooks/postgres.md) |
| Grove MCP (stdio vs `--serve` on `:8767`) | [`runbooks/mcp.md`](runbooks/mcp.md) |
| Grove messaging / LISTEN + NOTIFY | [`runbooks/grove.md`](runbooks/grove.md) |
| Curated incident receipts | [`runbooks/INCIDENT_INDEX.md`](runbooks/INCIDENT_INDEX.md) |

## Schema & contracts

| Topic | Doc |
|-------|-----|
| `grove.*` tables (channels, messages, agents) | [`db/GROVE_SCHEMA.md`](db/GROVE_SCHEMA.md) |
| Message envelope & bus fields | [`contracts/MESSAGE_ENVELOPE.md`](contracts/MESSAGE_ENVELOPE.md) |
| Routing: `willow.*` vs `public.routing_decisions` | [`verify/ROUTING_OBSERVABILITY.md`](verify/ROUTING_OBSERVABILITY.md) |
| u2u signed-not-encrypted LAN transport | [`design/u2u-security-limits.md`](design/u2u-security-limits.md) |

## Design

| Doc | Purpose |
|-----|---------|
| [`design/willow-grove-premise.md`](design/willow-grove-premise.md) | The founding premise — operator seat, composed not built |
| [`design/watcher-e2e-notes.md`](design/watcher-e2e-notes.md) | Resident watcher Ollama + Postgres LISTEN end-to-end notes |
| [`design/autonomous-continuity.md`](design/autonomous-continuity.md) | Autonomous continuity — the sealing question for Nestor |
| [`design/pr14-carryovers.md`](design/pr14-carryovers.md) | Punch list for v0.10 — what v0.9 punted and why |
| [`KNOWN_GAPS.md`](KNOWN_GAPS.md) | Gaps in the shipped build (rolls up into pr14-carryovers) |

## Audits (v0.9)

| Doc | Purpose |
|-----|---------|
| [`audits/loki-v0.9-audit.md`](audits/loki-v0.9-audit.md) | Loki's v0.9 audit — 38 ranked findings, all resolved or refuted |
| [`audits/loki-swarm-measurement.md`](audits/loki-swarm-measurement.md) | Persona-discipline measurement across seven lens agents |
| [`audits/loki-swarm-metadata.md`](audits/loki-swarm-metadata.md) | Swarm reproducibility metadata |
| [`audits/loki-swarm-raw.json`](audits/loki-swarm-raw.json) | Raw findings JSON |

## Not in this tree (by design)

Docs describing pre-v0.9 dashboard planning
(`superpowers/plans/*`, `superpowers/specs/*`), cross-repo synthesis
that spans Grove and other Willow surfaces (`synthesis/*`,
`CROSS_REPO_BRIDGE.md`, `AUTO_THIRD_PASS_AND_THREAD_PULL.md`), the
Grove-docs extractor tool (`extractor/*`), the ADR governance system
(`adrs/*`), and Forge-side design work
(`design/forge-convergence.md`) live at the old
`rudi193-cmd/safe-app-willow-grove` repo. Those cover work outside
what shipped as `willows-grove` 0.9.0 or belong to a sibling repo.
