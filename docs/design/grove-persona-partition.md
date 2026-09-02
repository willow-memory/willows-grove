# Grove persona partition — Willow vs Heimdallr

b17: WGRV1 ΔΣ=42  
Status: **OPERATOR-RATIFIED** (2026-09-02) — desk vs watch ownership for Willow's Grove.  
Scope: **Willow + Heimdallr only.** Other personas deferred.

## The problem

Grove is named *Willow's* — the operator Jarvis seat; everything routes through her
([willow-grove-premise.md](willow-grove-premise.md) D1). On disk the same repo has
long been Heimdallr's watch post ([CLAUDE.md](../../CLAUDE.md)): served page honesty,
resident watcher, Gjallarhorn. Operator seat scripts and intake lived under
`willow-memory/scripts/` with **no git home**. Two legitimate claims on one noun
left Willow's desk artifacts homeless.

## Rule of thumb

**Willow decides what the desk is for. Heimdallr decides whether the surface is telling the truth.**

**Addendum (Jarvis, not mode switch — 2026-09-02):** Tony does not flip Jarvis into
“dinner mode” vs “time-travel mode.” One continuous seat. Governance / PM / PA
remain **back-of-house triage questions** Willow (and the fleet) may use when
composing priority — **not** a hero chrome toggle the operator must click.
C12’s operator-facing lens switch oversold P8; see [autonomous-continuity.md](autonomous-continuity.md)
C12 misfit note and [willow-grove-premise.md](willow-grove-premise.md) P8 clarification.

## Ownership table

| Slice | Owner | Home in repo |
|-------|--------|--------------|
| Operator seat scripts, intake JSON, seat probe / routing doctrine | **Willow** | [`seat/willow/`](../../seat/willow/) |
| Desk composition (what bubbles when); Governance / PM / PA as **internal triage vocabulary**; dispatch desk doctrine; federation unblock | **Willow** | `docs/design/` + `seat/willow/` |
| Served page `127.0.0.1:8766`, grove serve / readers / Web Components honesty | **Heimdallr** | `grove/`, `web/`, [CLAUDE.md](../../CLAUDE.md) |
| Resident watcher, channel watch, Gjallarhorn / `#alerts` | **Heimdallr** | `grove/resident_watcher.py`, ops runbooks |
| Persona roster file + visual tokens | **Shared read** — Willow curates entries; Heimdallr renders | [`governance/fleet_personas.json`](../../governance/fleet_personas.json) |
| Charter / constitution | **Neither** (face seat) | `willow-memory/Willow` |
| MCP muscle | **Neither** | `willow-mcp` — Grove consumes via tools |

## Explicit non-ownership

| Actor | Does **not** own |
|-------|------------------|
| **Heimdallr** | Operator seat scripts under `seat/willow/`; federation lease minting; intake JSON curation; orchestrator routing doctrine; inventing desk posture / mode switches for Tony |
| **Willow** | Watcher message classification; serve-mode OAuth; `grove_db` schema; Web Component rendering honesty; blowing the Gjallarhorn for noise |

## Relation to prior decisions

- **D1** ([premise](willow-grove-premise.md)): Grove = operator Jarvis seat (Willow's place).
- **D2** ([premise](willow-grove-premise.md)): Desktop code lives in this repo; charter in `Willow`; muscle in `willow-mcp`.
- This note **partitions personas inside D2's repo** — it does not move the charter or rename the package.

## Channels (live signal)

| Channel | Owner lens |
|---------|------------|
| `#willow` | Desk / orchestrator traffic |
| `#heimdallr` | Watch post |
| `#alerts` | Gjallarhorn / incidents |

## Verification (novel, not commons)

Desk vs watch ownership is **novel governance**. It must be human-sealed in Nestor
(not auto-promoted as commons). Candidate pairs (also in
[`seat/willow/jeles-intake/grove-persona-partition-seals.json`](../../seat/willow/jeles-intake/grove-persona-partition-seals.json)):

1. Source: `Who owns Willow's Grove desk?` → Target: Willow (operator seat)
2. Source: `Who owns the Grove watch post?` → Target: Heimdallr
3. Source: `Is Willow's Grove a mode switch for Governance / PM / PA?` → Target: No. One Jarvis seat; those offices are back-of-house triage questions, not operator chrome.

Seal **after** operator ratifies this addendum. Full fleet roster design intent
remains open; this seals only the Grove-slice claim.

## Deferred

- Ada / Loki / Hanuman / Jeles / … Grove-slice tables
- Adding Heimdallr to willow-mcp `specialists.json`
- Merging charter into Grove or renaming the repo
