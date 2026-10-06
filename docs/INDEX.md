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
| [`design/grove-persona-partition.md`](design/grove-persona-partition.md) | Willow desk vs Heimdallr watch — persona ownership inside Grove |
| [`design/watcher-e2e-notes.md`](design/watcher-e2e-notes.md) | Resident watcher Ollama + Postgres LISTEN end-to-end notes |
| [`design/every-seat-hears-the-grove.md`](design/every-seat-hears-the-grove.md) | Grove traffic for any seat — one willow-mcp events verb and cursor, read by Ratatosk, the stream and the hook |
| [`design/autonomous-continuity.md`](design/autonomous-continuity.md) | Autonomous continuity — the sealing question for Nestor |
| [`design/pr14-carryovers.md`](design/pr14-carryovers.md) | Punch list for v0.10 — what v0.9 punted and why |
| [`design/forge-convergence.md`](design/forge-convergence.md) | The Forge convergence: one session machine; §6 the build order, §6a the Table |
| [`design/forge-convergence-flowering-experiment.md`](design/forge-convergence-flowering-experiment.md) | Experiment: growth, pools, and the flowering threshold (step 0, run and struck) |
| [`design/one-box/README.md`](design/one-box/README.md) | One box, every front end, portless: the build plan (proposal, 2026-10-01), with its review, session records, research, outside pass, partition, one-script join, crosslink appendix and verify note |
| [`design/one-box/outside-2026-10-02.md`](design/one-box/outside-2026-10-02.md) | Outside OW/F-chain (Jeles-first burn 2026-10-02) — V/S/? and born-next |
| [`design/one-box/parts-partition.md`](design/one-box/parts-partition.md) | Four live surfaces (bot UDS, gate library, Kart, mcp leases); Q1–Q2–Q11–Q13; D10 frp pin |
| [`design/one-box/one-script-join.md`](design/one-box/one-script-join.md) | One-script seven purposes ↔ one-box phases; nest P5–P7; Q14 wording |
| [`design/one-box/crosslink-appendix.md`](design/one-box/crosslink-appendix.md) | Strengthen vs contradict; three-dialect OUT; Q3–Q7–Q9 |
| [`design/one-box/session-2026-10-02.md`](design/one-box/session-2026-10-02.md) | Expand-pass session note (B1–B3, SOIL ids, next bite) |
| [`design/one-box/verify-2026-10-02.md`](design/one-box/verify-2026-10-02.md) | Kart re-check of one-box §1 V-facts |
| [`design/one-box/rules-cross-table-2026-10-06.md`](design/one-box/rules-cross-table-2026-10-06.md) | Boxes and branches on one 13 × 13 grid: 169 rules by address (A1–M13), each row with its source |
| [`../templates/cross-table/README.md`](../templates/cross-table/README.md) | The cross table as a template: a grid of addresses, a JSON map, and `cross_table.py`, which fills each cell by copying its source line (found / silent / unreachable / not found). The rules cross table is the worked example |
| [`design/one-box/boxes-outside-2026-10-06.md`](design/one-box/boxes-outside-2026-10-06.md) | The second grid: boxes from outside the system (words and myths, logic, made things, moving), 4 × 5 at rows N–Q after the first grid's A–M, the agent's own notes copied into the cross-table template; unattested |
| [`design/one-box/crosswalk-2026-10-06.md`](design/one-box/crosswalk-2026-10-06.md) | The crosswalk: 13 links from the second grid (N–Q) to the first (A–M), and 9 from the third grid's rows (R–Z) to the boxes they dripped from, every address checked by `cross_table.py link`; the readings are unattested |
| [`design/one-box/drip-2026-10-06.md`](design/one-box/drip-2026-10-06.md) | The third grid: the nine fattest boxes (G5, K10, L6, J2, J9, G4, J7, B11, P1) dripped into rows R–Z, one clause per box, each copied again from its source and pinned to its own place; the alphabet ends here |
| [`design/gerald/gerald-atoms-table-2026-10-06.md`](design/gerald/gerald-atoms-table-2026-10-06.md) | The Gerald project session's 134 atoms (version 2, all proposed, none ratified), one per box in rows AA–AL, kept beside the atom files unchanged |
| [`design/gerald/gerald-to-main-2026-10-06.md`](design/gerald/gerald-to-main-2026-10-06.md) | The Gerald atoms linked to the main table: 18 atoms name 36 of its boxes; four look-alike tokens (D10, D7, C3, B1) set aside |
| [`design/branches/branches-table-2026-10-06.md`](design/branches/branches-table-2026-10-06.md) | The open branches as a grid, rows AM–AR, copied from a ledger generated from git: head, ahead/behind, files, shared commits, conflicts, and what each merge would do to the grids (both ccr branches would leave G5 and R1–R6 no longer found) |
| [`design/handoffs/handoffs-table-2026-10-06.md`](design/handoffs/handoffs-table-2026-10-06.md) | Every handoff (three repos plus the Gerald session's) against 14 ideas from Draft 0.9, rows AS–BF, copied from a ledger of text-match counts: the old core travels, quorum and delegation never do, and ΔΣ=42 carries three meanings |
| [`design/coverage/coverage-table-2026-10-06.md`](design/coverage/coverage-table-2026-10-06.md) | Every clause of Draft 0.9 against the three repos, rows BG–EG, copied from the box's own coverage report: the grid is 99% full, the law is not (40 of 64 clauses cited nowhere; 77 of 78 verdicts undeclared) |
| [`design/coverage/coverage-layers-table-2026-10-06.md`](design/coverage/coverage-layers-table-2026-10-06.md) | The third axis: the coverage report at every branch head, each against its own law, rows EH–HG. Two laws (Draft 0.8 on the 10-04 branch: 13 clauses absent, not uncited); the ccr branches' heading links now count; no branch changes which clauses are covered |
| [`design/one-box/random-pull-2026-10-06.md`](design/one-box/random-pull-2026-10-06.md) | A random pull from the agent's general knowledge (Borges, Dewey 001.9, Korzybski, Voynich, Linnaeus, mise en place, Lisbon 1755, the rotisserie) and where each lands on the grids, rows HH–HJ; the agent's own notes, unchecked, unattested |
| [`design/one-script/README.md`](design/one-script/README.md) | The one script: four draft proposals from session 2026-10-02 (the workflow, the runtime as one script, a runnable skeleton, constitution amendments on Draft 0.7) |
| [`design/the-forge-shape.md`](design/the-forge-shape.md) | The Forge, the shape as talked out 2026-08-30 |
| [`design/approval-broker.md`](design/approval-broker.md) | Approval broker: how a human act reaches a sandboxed caller |
| [`design/fleet-wiring.md`](design/fleet-wiring.md) | How the fleet is wired |
| [`design/fleet-standup.md`](design/fleet-standup.md) | Standing the fleet up in one box |
| [`design/install-graph-survey-2026-09-08.md`](design/install-graph-survey-2026-09-08.md) | Install-graph survey: Grove docs vs this box |
| [`design/operator-tier-review.md`](design/operator-tier-review.md) | OPERATOR-tier `not_do` audit |
| [`design/seat-stack.md`](design/seat-stack.md) | Willow seat stack: phone, session, bus, desk |
| [`design/phone-seat-production.md`](design/phone-seat-production.md) | Phone seat: production name and serve URL |
| [`design/phone-surface-context.md`](design/phone-surface-context.md) | Phone surface: context for the remote UI session |
| [`design/phone-tier0-sync.md`](design/phone-tier0-sync.md) | Phone seat: tier 0 homecoming |
| [`design/vault-home-store.md`](design/vault-home-store.md) | Vault home store: the cut, two axes, not a move |
| [`design/willow-bot-box-spec.md`](design/willow-bot-box-spec.md) | willow-bot box spec (draft, operator shape 2026-09-28) |
| [`design/willow-bot-usable-build-brief.md`](design/willow-bot-usable-build-brief.md) | willow-bot usable build brief |
| [`ideas.md`](ideas.md) | The idea pile — every open item this repo can land, numbered once, read by `reconciler run` |
| [`KNOWN_GAPS.md`](KNOWN_GAPS.md) | The `GAP-00N` → pile-item map (the gaps themselves now live in `ideas.md`) |

## Audits (v0.9)

| Doc | Purpose |
|-----|---------|
| [`audits/loki-v0.9-audit.md`](audits/loki-v0.9-audit.md) | Loki's v0.9 audit — 38 ranked findings, all resolved or refuted |
| [`audits/loki-swarm-measurement.md`](audits/loki-swarm-measurement.md) | Persona-discipline measurement across seven lens agents |
| [`audits/loki-swarm-metadata.md`](audits/loki-swarm-metadata.md) | Swarm reproducibility metadata |
| [`audits/loki-swarm-raw.json`](audits/loki-swarm-raw.json) | Raw findings JSON |

## Proposals (`governance/proposals/`)

| Proposal | Status (as the file states it) |
|---|---|
| [`2026-08-21-registry-path-repoint`](../governance/proposals/2026-08-21-registry-path-repoint.md) | proposal · root's act (verb 12) |
| [`2026-08-22-governed-path-write-gate`](../governance/proposals/2026-08-22-governed-path-write-gate.md) | proposal · superseded by the 2026-09-02 v2 |
| [`2026-08-22-syscall-table-verb13-bounds`](../governance/proposals/2026-08-22-syscall-table-verb13-bounds.md) | proposal · root's act (verb 12) |
| [`2026-08-31-journal-seam-speaks-no-protocol`](../governance/proposals/2026-08-31-journal-seam-speaks-no-protocol.md) | proposal · awaiting root's ratification |
| [`2026-09-02-build-order`](../governance/proposals/2026-09-02-build-order.md) | index of the six 2026-09-02 proposals |
| [`2026-09-02-governed-path-write-gate-v2`](../governance/proposals/2026-09-02-governed-path-write-gate-v2.md) | proposal · root's decision, then a willow-mcp change |
| [`2026-09-02-grove-hooks-and-skills`](../governance/proposals/2026-09-02-grove-hooks-and-skills.md) | proposed · root ratifies |
| [`2026-09-02-local-inference-seam`](../governance/proposals/2026-09-02-local-inference-seam.md) | proposed · cross-repo |
| [`2026-09-02-mcp-jobs-ladder-test-plan`](../governance/proposals/2026-09-02-mcp-jobs-ladder-test-plan.md) | proposed · measurement; its `allow_localhost` ask is retired |
| [`2026-09-02-packet-lifecycle-adr`](../governance/proposals/2026-09-02-packet-lifecycle-adr.md) | proposed · willow-mcp change |
| [`2026-09-02-unit-retirement`](../governance/proposals/2026-09-02-unit-retirement.md) | proposed · operator's act |
| [`2026-09-09-grove-seat-inversion`](../governance/proposals/2026-09-09-grove-seat-inversion.md) | proposed · awaiting ratification |
| [`2026-09-26-manifest-grant-federated-tools`](../governance/proposals/2026-09-26-manifest-grant-federated-tools.md) | ruled A · built in willow-mcp |
| [`2026-09-27-node9-shadow-mode`](../governance/proposals/2026-09-27-node9-shadow-mode.md) | ruled · built in willow-mcp |

## Not in this tree (by design)

Docs describing pre-v0.9 dashboard planning
(`superpowers/plans/*`, `superpowers/specs/*`), cross-repo synthesis
that spans Grove and other Willow surfaces (`synthesis/*`,
`CROSS_REPO_BRIDGE.md`, `AUTO_THIRD_PASS_AND_THREAD_PULL.md`), the
Grove-docs extractor tool (`extractor/*`), and the ADR governance system
(`adrs/*`) live at the old `rudi193-cmd/safe-app-willow-grove` repo,
which is private and archived. Those cover work outside what shipped as
`willows-grove` 0.9.0 or belong to a sibling repo. The Forge convergence
design moved here: [`design/forge-convergence.md`](design/forge-convergence.md).
