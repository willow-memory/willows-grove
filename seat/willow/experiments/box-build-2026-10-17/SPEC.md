---
kind: doc
name: box-build-spec
description: The merged spec for the box build — documented side, rival side and tools side reconciled; every ruling is a recorded guess until the human rules.
b17: BOXB1
---

@markdownai v1.0

# Box build — merged spec (round 0)

§1 Sources · §2 Rulings · §3 Waves · §4 Open for the human · phases W1–W4 · constraints at the end

## §1 Sources

| Side | File | Weight |
|---|---|---|
| Documented | `SPEC-documented.md` — joins pinned to forge-convergence §6a, handoffs, chapter 8; 19 doc conflicts (C1–C19) | **Wins ties.** The human wants the result close to what is written |
| Rival | `SPEC-rival.md` — one record, one wager primitive, stream shim, J6+J7 as one act; 16 adversarial tests T1–T16 | Adopted where it is a correctness finding; held where it reopens a settled record |
| Tools | `SPEC-tools.md` — T-mai-1…5, T-cbm-1…4 | Adopted where code replaces a model or a hand check |

Builders read the phase of the source spec named in each ruling (`mai mai_resolve_phase`).

## §2 Rulings (recorded guesses, not decisions)

| # | Question | Ruling | From | Confidence |
|---|---|---|---|---|
| R1 | J1 verb names | `forecast`, `seal_outcome`, `read_misses` exactly as `forge-convergence.md:643-645`; plus `seal_tip` and `reconcile` because outcomes count only under a sealed tip (documented §5) | documented | 85% |
| R2 | Brier/log score source | Vendor the two pure functions into onescript with a provenance line naming `Forge/forge/calibration.py`, plus a drift test that compares them to Forge's when Forge is importable. Keeps onescript stdlib-only; the drift test answers "not a third copy" by pinning it | rival + BRIEF, C1 held open | 60% |
| R3 | Forecast commitment | Chain order under the human's tip (`wager.n < tip_seal.n < verdict.n`), never a timestamp | rival §3 | 85% |
| R4 | Who grades | Code computes the score; `graded_by` stays `None`; only a human seal makes an outcome count (C3, C4) | documented | 85% |
| R5 | Low-p forecasts vs Forge's [0.5,1] confidence | Restate to the complementary side for reliability bins only; Brier/log unchanged (C2) | documented | 85% |
| R6 | Dice stream | SHA-256 counter stream (`play.py:56`) behind a `random.Random`-shaped shim (`randint`, `choice`, in-place `shuffle`, `random`); rows carry seed, counter and generator id; old runs keep their generator (C9) | rival §4 + documented | 85% |
| R7 | `apps/game/engine_v1_7.py` | **Not edited.** The-table's adapter swaps the engine module's random source around one roll (context manager) and restores it; creator rolls still draw two dice (`engine_v1_7.py:57-58`) | documented C7, rival T9 | 60% |
| R8 | Exact-odds predictor | Only the pure part of `peaks.py` moves, to `safe-app-store/apps/the-table/the_table/peaks.py` (handoff 10-16 Q16), returning the wager `distribution` shape `{path, p, band}` | documented C19 | 75% |
| R9 | Two ledgers (J9) | Keep `campaign.db` (row 11 is settled); anchor its head into the one-script record as one `agm_head` verdict row before the next sealed tip. The rival's "drop the chain" goes to the human as a question | documented C5, rival fallback | 75% |
| R10 | Story seals (J4) | A decision beat becomes a one-script proposal the human seals; code never writes a `seal` row (C10, A5 class) | both | 90% |
| R11 | Lore (J5) | `lore` rows, one fact each, one new `PAYLOAD` entry `fact`; served only when the proposal carrying it is sealed (proof and hash checked); striking is `serve.check_cites` + `seat_say.check_nothing_lacking`, not `gate.check_claims` | rival §5 + documented §5 | 80% |
| R12 | J6 + J7 | One phase, "the act": the D0 for a table act is `GameSession.step`; resolver classes are named `table.*` (C13); a model may only pick a move id from `legal_moves`, rewrite the code sentence under `run_checks`, or propose a `draft` box; decision beats go to the human | rival §6 + documented C13/C14 | 80% |
| R13 | J8 | No new panel: one `wager` pattern in `seat_record.item_box`; the seat points at the table box | rival §7 | 75% |
| R14 | Rescope after an outcome seal | A seal moves the human pile's subject, so `seal_outcome` ends by printing the rescope step; a test proves `propose` serves `empty` until it is done (rival T11) | rival §8 | 80% |
| R16 | `play.py export R` | `play.py` and its round files are the game's frozen record (grove rule 12): a new `export.py` beside it does the export and re-derives every answer from the stored beacon | integrator, W1 | 70% |
| R17 | `seal-tip --proof P` | `seal-tip` takes the tip subject `tip:N:HASH` it is sealing, because every verb's `invocation` row moves the tip before the human can sign; asked without a proof it lists what the tip newly covers | J1 builder D3, W1 | 70% |
| R18 | Stale code graph | `graph_read` refuses a stale index with state `stale` (beside populated/empty/unreachable) instead of re-indexing silently; the caller decides to re-index | integrator, W3a | 70% |
| R19 | J9 reverse anchor and `LedgerSink.head_n` | Not built: one sealed one-script tip covers the `agm_head` row, and campaign.db stays free of one-script state (rival §2); the anchor check keeps the documented `satisfied / failing / unreachable` names plus `unanchored` as the empty arm | integrator, W2 | 75% |
| R20 | A `table.*` act D0 cannot close | Goes straight to the human card, never to a model rung (the "never" rung, rival R5) | integrator, W3b audit B1 | 80% |
| R21 | Table narrator check | Per-clause: each clause's numbers and verdict words must come from the one box that clause cites; no quotes in table narration; narratable = served fact boxes only (`kind pass`, no role); the extra seal-word check is removed because nothing-lacking already strikes words no fact box holds | integrator, W3b audit B5/S1 + idea side D5/D9 | 70% |
| R21a | Clause vocabulary | A clause may use only the cited box's value (a roll box: turn, total, verdict); its detail is code-sayable, never checkable; numbers exact, spelled numbers refused or normalised, verdict words exact (no stemming) | integrator, W3b re-audit NEW-1/2 | 75% |
| R21b | Lore and negation in narration | Lore boxes are said by code only, word for word (a model may cite a lore box only in a clause that is the box's exact value); negators and hedges (`not`, `no`, `nor`, `never`, n't forms, `but`, `yet`, `still`, `than`) are never free glue in a table clause | integrator, W3b round-3 hunt H1/H2 | 75% |
| R22 | When the model picks a move | Only on `set_piece: true` beats (documented C15/§13); other beats use the beat's own `suggested_policy` in code | documented, W3b idea side D1b | 65% |
| R23 | Seed grinding (break test) | A table forecast names a future drand `beacon_round`; that round's randomness is the session seed, carried on the open row (public once fired); an outcome counts only if the round fired after the tip seal and every roll re-reads (one seed id, continuous counters, total == dice, verdict == band). Beacon reader is opt-in (`--drand`); with none the outcome is `unreachable`. BLS still unverified (T10) | integrator, W4 break | 75% |
| R23a | Hardening R23 (break pass 2) | A forecast refuses any round the operator's reader can already read (no box clock trusted); outcome order uses the reader's round time, never a self-stamped `ts`; the dice re-read REPLAYS every roll from the open row's randomness and checks `generator_id`; the R3 hook is bound by the Run, never taken from a caller; one table forecast per beacon round | integrator, W4 break pass 2 | 75% |
| R15 | Tools in the flow | Adopt T-mai-1 (shape gate before a mai doc enters the record) and T-cbm-4 (graph read with freshness stamp, populated/empty/unreachable) in W3; T-cbm-1 (`symbol` cites) and T-mai-2 (rules by exact `@phase`) in W4; hold T-cbm-3, T-mai-3/4/5 | tools | 60–70% |

## §3 Waves

| Wave | Phases | Repos | Parallel? |
|---|---|---|---|
| W1 | J1 forecast lane · J2 stream · J3 odds | willow-bot one-script · the-table (`box-build`) · the-table (`box-build-j3` worktree) | yes |
| W2 | J4 results as rows · J9 agm head | the-table + one-script | after W1 |
| W3 | J5 lore · R12 the act · T-mai-1 · T-cbm-4 | one-script, willow-bot resolvers, the-table | after W2 |
| W4 | R13 surface · T-cbm-1 · T-mai-2 · end-to-end break test (T1–T16) | willows-grove, all | after W3 |

Each wave: builders → audits on a different model from the builder → idea-side challenge → revisions → tests. Next wave starts when two audits in a row find nothing blocking.

## §4 Open for the human (asked at the end, not blocking the sandbox)

| # | Question | Sandbox default |
|---|---|---|
| H1 | May willow-bot take `forge-play` (onescript no longer stdlib-only)? | R2 vendor + drift test |
| H2 | May `engine_v1_7.py` take `rng=None`? | R7 no edit |
| H3 | Every beacon-computed outcome needs its own human seal (28 for seven rounds)? | Yes, one seal each |
| H4 | Human HMAC key handed to `reconcile` from a file outside the box, or the table box Nestor-only? | Key file outside the box; Nestor tip gap recorded |
| H5 | Reopen row 11 and drop the-table's chain (rival)? | R9 keep both, anchor by head |
| H6 | f2 held back with p3/p4? | Held back |
| H7 | One beacon per forecast window, or no mid-session forecasts? | One beacon per window |

@phase W1-forecast-lane
J1. Sources: `SPEC-documented.md` phase J1, `SPEC-rival.md` §3, rulings R1–R5, R14.

@phase W1-stream
J2. Sources: `SPEC-documented.md` phase J2, `SPEC-rival.md` §4, rulings R6, R7.

@phase W1-odds
J3. Sources: `SPEC-documented.md` phase J3, ruling R8.

@phase W2-rows-and-head
J4 + J9. Rulings R9, R10.

@phase W3-lore-act-gates
J5 + J6/J7 + T-mai-1 + T-cbm-4. Rulings R11, R12, R15.

@phase W4-surface-and-break
J8 + T-cbm-1 + T-mai-2 + the full adversarial list T1–T16. Rulings R13, R15.

@constraint severity=critical
Sandbox only; no push, no PR, no edit to `/home/user/<repo>` originals.
@constraint severity=critical
Code never writes a `seal` row; only a human proof makes anything count.
@constraint severity=error
Every new row kind, verb and test cites the doc line or ruling it implements.
@constraint severity=warning
Every document the build writes is `@markdownai v1.0` and passes `mai lint`.
