---
kind: doc
name: box-build
description: The deterministic-prediction / one-script / box / flowering / AI GM join, built and broken in a sandbox before anything reaches a branch.
b17: BOXB1
---

@markdownai v1.0

# Box build — the joins, in order

§1 Ground · §2 Loop · phases J1–J9 · constraints at the end

## §1 Ground

The design is already written: `willows-grove/docs/design/forge-convergence.md` §6a (T1–T7), `forge-convergence-flowering-experiment.md` §11, handoffs `foreshadow-table-handoff-2026-10-16.md` / `-10-17.md`. The build lands as close to those as it can; where it departs, it says where and why.

Tools, in this order, for every agent: **MarkdownAI** (`/home/user/tools/bin/mai`) for every document this build writes or reads by phase; **codebase-memory-mcp** for code lookup once it is built; grep/read after both.

## §2 Loop

Each round: builders (two or more, different models) → audits (different models from the builders) → an idea side (a rival design for the same join) → revisions → tests up and down (unit, cross-repo, break tests). Rounds repeat until two audits in a row find nothing blocking.

@phase J1-wagers-brier
Forecasts become one-script `wager` rows; outcomes sealed with `reverse.outcome_subject`; `reconcile_wagers` gains a Brier and log score from Forge `forge/calibration.py`, not a third copy. Inputs: `predictions-2026-10-17/play.py` rounds, the table ledger's f1/f2. Handoff 10-17 Q6, Q7, Q15.

@phase J2-seeded-dice
One dice stream for every game: an injected stream into `Engine.roll` (as `crazy_eights_adapter` and `dice5e` already take), using `play.py`'s SHA-256 `Stream` so a roll can be seeded by a drand beacon and replayed on any Python. The global `random.seed` trap in `game_engine_adapter.py` and `story_session.py` goes away.

@phase J3-odds-predictor
`peaks.py`'s exact-odds forecaster moves beside the-table and emits a wager distribution; onescript's `predict` takes a code-computed distribution where one exists instead of counting bite kinds. Foreshadow README §4: counting 0%, exact odds 8/8.

@phase J4-results-as-rows
`GameSession.step`/`result` and StorySession seals land in the one-script record as `verdict` and `seal` rows. Forge-convergence T3, handoff 10-16 Q10.

@phase J5-lore-payload
A world/lore field in `serve.PAYLOAD`, so a sealed `world/*.md` reaches the model and the claims check can strike what was not served. Handoff 10-17 Q12.

@phase J6-d0-game-class
A D0 resolver class for roll / rules-lookup / state-read in `resolvers.resolve_fixture`, so a table act closes in code instead of escalating.

@phase J7-narrator
Scene and roll facts become boxes; `seat_say.run_checks` checks the narrator's sentence; flowering only for set pieces, choosing from `legal_moves` as a closed menu.

@phase J8-table-panel
A GM/table surface in the box stream reading `table/box/record.jsonl`.

@phase J9-ledgers
ai-game-master's chain and the one-script record: anchor by head (forge-convergence row 11) or pick one; a sealed tip so a cut shows (A7).

@constraint severity=critical
Sandbox only: `/home/user/sandbox/`. No commit to a real branch, no push, no PR without the human's recorded word (CLAUDE.md rules 5, 9).
@constraint severity=critical
No machine-sealed canon. Code and models propose; only the human seals (ai-game-master DECISION.md §6, one-script seal proofs, PR 137).
@constraint severity=error
Deterministic first: code, then seeded simulation, then local model, then flowering. A model never invents a roll, a move, or a fact it was not served.
@constraint severity=error
Search before writing (safe-app-store CLAUDE.md rule 11): reuse Forge calibration, Nestor, Jeles, onescript before adding a new copy; say so in the commit when the house already knew.
@constraint severity=warning
Every document this build writes is a proper `@markdownai v1.0` doc and passes `mai lint`.
