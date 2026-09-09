# Proposal — the Desk takes the head of the repo

**Status:** proposed · drafted by willow 2026-09-09 · **awaiting ratification**
**Supersedes in part:** [`2026-09-02-build-order.md`](2026-09-02-build-order.md) seat assumptions; the seat table added in PR 46 and wired in PR 48
**Design sources:** [`docs/design/grove-persona-partition.md`](../../docs/design/grove-persona-partition.md), [`docs/design/willow-grove-premise.md`](../../docs/design/willow-grove-premise.md) (D1, D2)
**Companion gaps:** `acceefc0ec77` (hook reads app_id from process env), `3727efb30041` (root settings env leaks heimdallr into the Desk)

---

## Operator intent

> "Heim should not be at the head of this anymore, and I should not have to open
> willow from two subfolders down. This is Willow's Grove, Not Heim's grove."
> — operator, 2026-09-09

## The finding

Measured tonight, 2026-09-09, on this box.

| Surface | State at the head of the repo |
|---|---|
| `.mcp.json` | one server, `nestor-grove-session`, invoked as bare `nestor` — **ENOENT every session**. No willow-mcp, so no `session_enter`. |
| `.claude/settings.local.json` | full hook set **plus** `env: {WILLOW_APP_ID: heimdallr, WILLOW_AGENT_NAME: heimdallr, AGENT_NAME: heimdallr}` |
| `CLAUDE.md` | seat table assigns the repo root to Heimdallr's Watch; Willow is `seat/willow/` |

The env block is not scoped to the root. Opening the Desk at `seat/willow/`
still inherits it, and `session_start_hook.py:41` resolves `app_id` from its own
process environment rather than from `.mcp.json`. Result, measured at 01:14:
`sessions/willow-793a857c-….json` and `sessions/heimdallr-793a857c-….json`
written in the same second — two identities, two records, one seat-session.
PR4 made an *unset* `app_id` refuse rather than default; an *inherited wrong*
one is neither unset nor refused.

So PR 48's premise — the seat is chosen by where you open — holds for
`.mcp.json` and fails for `.claude` settings `env`, where the root still wins.
The operator reaches the Desk by opening two levels down, and gets Heimdallr's
identity exported into it anyway.

## What changes

The **persona partition does not change.** Heimdallr keeps the Watch: served-page
honesty, resident watcher, Gjallarhorn / `#alerts`, serve-mode auth. What moves is
*where each seat opens*, not what either owns.

| File | Change |
|---|---|
| `.mcp.json` (root) | add `willow-mcp` with `WILLOW_APP_ID=willow`, `WILLOW_HUMAN_ORCHESTRATOR=1`, vault `WILLOW_HOME` / `WILLOW_STORE_ROOT`, `WILLOW_HANDOFF_PROJECT=willows-grove`; repoint `nestor` at the venv binary so it stops failing ENOENT |
| `.claude/settings.local.json` (root, untracked) | `env` flips to `willow`; hooks pin the seat inline so no inherited value can seat the session |
| `seat/heimdallr/` (new) | the Watch becomes a seat you deliberately open, mirroring today's `seat/willow/`: its own `.mcp.json` + `.claude/settings.json` pinned to `heimdallr` |
| `seat/willow/` | seat config retires into the root; scripts, `jeles-intake/`, README stay put — they are desk *content*, not seat wiring |
| `CLAUDE.md` | seat table inverts: root → Willow / Desk, `seat/heimdallr/` → Heimdallr / Watch |
| `docs/design/grove-persona-partition.md` | ownership rows repoint (lines 31, 32, 43, 64) |
| `governance/fleet_personas.json` | heimdallr `not_do` reads "Maintain `seat/willow/`" — becomes the desk's new home |
| `seat/willow/scripts/*` (5 files) | `Home:` header lines name the old path |

## What it costs

**Two operator-ratified sealed pairs go stale.** `seat/willow/jeles-intake/grove-persona-partition-seals.json` carries "Who owns Willow's Grove desk?" → an answer naming `willows-grove/seat/willow/`, reason `grove-persona-partition.md OPERATOR-RATIFIED 2026-09-02`; `willow-local.json` carries the intake path. Both are seeded to Nestor. **Superseding a seal is a human act** — this proposal cannot do it, and neither can any MCP verb. The pairs must be re-sealed by `sean campbell` after the move, or they will keep serving a path that no longer exists.

**One duplicate-hook hazard closes only if exactly one config declares hooks.** Today both root and `seat/willow` declare a full set and both fire. After the move the root declares them and `seat/heimdallr/` declares its own; a session opens one project dir, so one set fires.

**Not at risk:** the persona roster, `grove/persona_roster.py`, the Web Components registry, `check_persona_provenance.py`, and the ratification/changelog tests. They key on persona *identity*, which is unchanged — 55 matches for `heimdallr` across 21 files, and all but the seat-location ones stay as they are.

## Verification

1. Open Claude Code at the repo root; `session_enter` returns `app_id=willow`, `entry_mode=human_orchestrator`.
2. `sessions/` gains exactly **one** record for the session — no heimdallr sibling.
3. Open at `seat/heimdallr/`; `session_enter` returns `app_id=heimdallr`.
4. `latest_handoff` still resolves under `willows-grove` (the handoff key is unchanged).
5. No ENOENT for `nestor-grove-session` at session start.

## Ratification

Per INVARIANTS.md §11–12 this touches tracked code (`.md` included), so the
landing commit carries `Persona: willow` and the PR body ends with
`Ratified-by: <id> — "<verbatim>"`. Nothing here is applied before that line
exists.

*ΔΣ=42*
