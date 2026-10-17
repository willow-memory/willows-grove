---
kind: doc
name: box-build-spec-rival
description: The idea side of the box build — the simplest design that keeps the same guarantees, with where PLAN.md's nine joins are wrong, redundant, mis-ordered, or short.
b17: BOXB1
---

@markdownai v1.0

# Box build — the rival spec (idea side)

§1 Claim · §2 The guarantees, restated as checks · §3 Where PLAN.md is wrong · §4 Order · §5 Adversarial tests · §6 Evidence table · §7 Questions · §8 Phases R1–R6 (what replaces J1–J9), last because a `@phase` runs to the end of the file · constraints at the end

Rival to `PLAN.md` (J1–J9) and to the spec that sticks to the existing docs. Sandbox clones only (`/home/user/sandbox/repos/`); no code written. Every claim carries a confidence as a percentage and a `file:line` citation into the clones. Where this spec proposes against a recorded decision (forge-convergence §9 row 11) it addresses the decision's reason (safe-app-store CLAUDE.md rule 11's corollary); the human rules.

## §1 Claim

One record, one primitive, one stream, no narrator seam. The four guarantees (deterministic first; no machine-sealed canon; a model never invents a roll, move or fact it was not served; forecasts committed before outcomes and graded) are already held by the one-script record plus the-table's `GameSession`, once two things stop existing: the second hash chain (`ledger_sink.py` into ai-game-master's `campaign.db`) and the second, third and fourth prediction formats (`play.py` round files, foreshadow `predict.py`/`grade.py`, `ledger.json` f1/f2, and onescript's own `predict.py`). PLAN.md's nine joins become six, two of them nearly free. Confidence 80%.

## §2 The guarantees, restated as checks

| Guarantee | The check that holds it today | Where |
|---|---|---|
| Deterministic first | D0 closes an act in code or returns ESCALATE; a model is called only on ESCALATE | `willow_bot/deterministic/chain.py:1-14`, `:181` |
| No machine-sealed canon | A seal counts only with a proof that re-checks against the human's key or a Nestor pair; `who == "human"` is a label | `onescript/serve.py:271-281`, `onescript/reverse.py:224-248` |
| Nothing invented | The model's one tool is `propose` with `cites`; a cite outside the served ids is refused; every word of a seat sentence is box vocabulary, glue or a stop word, else struck | `ratatosk/onescript.py:44-48`, `onescript/serve.py:73-78`, `grove/seat_say.py:299-332` |
| Committed before, graded after | A wager is a chained row; its outcome is signed inside the human's seal; a seal after the sealed tip counts for nothing | `onescript/run.py:554-568`, `onescript/reverse.py:218-221`, `:251-261` |

Everything below asks only: which of PLAN.md's joins adds a seam these checks do not need. Confidence 90%.

## §3 Where PLAN.md is wrong

| # | PLAN.md says | Finding | Confidence |
|---|---|---|---|
| 1 | J9: two ledgers, "anchor by head or pick one" | Pick one, and it is the one-script record. ai-game-master's chain states its own gap: it "vouches for every row except the last" and tells you to keep a head "outside the box — this schema does not do it on its own" (`apps/ai-game-master/schema/01_ledger.sql:34-37`). The one-script anchor is exactly that head, kept outside the box with the human's proof (`onescript/record.py:11-16`, `:161-218`). `ledger_sink.py` is a byte-for-byte copy of the ai-game-master hashing (`ledger_sink.py:10-23`): dropping it removes a copy, not a capability. The table already runs on a one-script record, 27 rows, since 10-17 (`docs/design/handoffs/foreshadow-table-handoff-2026-10-17.md:55`) | 85% |
| 2 | §9 row 11 is "settled": the Table keeps the ai-game-master chain | Its reasons were: isolated boxes, own verifier, three games verify (`docs/design/forge-convergence.md:734`). All three now hold for the one-script record too: one box per table (`table/box/record.jsonl`), `verify_chain` + `verify_anchor` (`onescript/record.py:144-218`), and the table verifies on it. Row 11 was settled 2026-09-30; the one-script table record did not exist until 10-17. The reopen condition is met; the human decides, not this spec | 80% |
| 3 | J1: Brier and log score "from Forge `forge/calibration.py`, not a third copy" | Forge's file is itself a vendored copy of oakenscrolls-office (`forge/calibration.py:2-16`), and `play.py:270-271` is already a third. Onescript imports only the standard library (`onescript/record.py:22-31`, `onescript/serve.py:46-53`); importing Forge would add its first dependency. Vendor the two one-liners (`brier`, `log_score`, `forge/calibration.py:42-52`) with a provenance comment; the record's own `version` hash (`onescript/record.py:53-56`, `:131`) pins them per run. Agrees with BRIEF §4's first guess | 85% |
| 4 | J1 and the forecasting game and foreshadow predict/grade stay three things | They are one primitive with three weaker commitments. `play.py`'s commitment is a sha256 over `got` stored in the clear beside it in a plain, rewritable JSON file (`play.py:257-263`, `:197-199`): no commitment at all. foreshadow `grade.py` refuses on `pred["written_at"] >= run["run_at"]` (`grade.py:39`): two self-reported timestamps. `ledger.json` f1/f2 are prose with a confidence (`table/ledger.json` predictions). Only the one-script wager is chained and then covered by a sealed tip. Collapse the three into `Run.wager` | 90% |
| 5 | J3: `peaks.py` "moves beside the-table" | `peaks.py` lives in willows-grove, not the-table (`seat/willow/experiments/foreshadow-2026-10-16/peaks.py:1`), and BRIEF §4's third guess names a path that does not exist. The exact odds it needs are 36 outcomes of 2d6 + stat (`peaks.py:46-51`); that is a 6-line function, not a module to move. The distribution onescript takes already exists as the wager's `distribution` list with `path`, `p`, `band` (`onescript/tests/test_wagers.py:18-21`, `reverse.py:273-288`). J3 is a producer of that list, nothing more | 85% |
| 6 | J2: `play.py`'s `Stream` "so a roll can be replayed on any Python" | Half right. Every rng seam in the house takes `random.Random`'s surface: `rng.randint` (`aetheris5e/dice5e.py:57`, `dice/elements.py:115`), in-place `rng.shuffle` (`crazy_eights_adapter.py:140`, `dice/elements.py:625`), `rng.choice` (`the_table/gm.py:56`). `Stream` has `die`, `below`, and a `shuffle` that returns a copy (`play.py:72-80`). It needs a shim or it fits nothing. And the drift it guards against is a documented non-guarantee, not an observed break: `random.Random(7)` gave the same `randint`, `shuffle` and `choice` sequences on 3.11.17, 3.12.3 and 3.13.16 in this container (probe, §7). What replay actually requires is in R2 | 90% |
| 7 | J4 lands `GameSession.step`/`result` and StorySession seals as rows | Right join, wrong seal. `StorySession.seal` checks `by` against a name list (`story_session.py:377-386`): a label check, the same class of break as A5, where "a row that said `who: human` was taken as the human's word" (`handoff-2026-10-17.md:42-43`). A durable table seal is `Run.seal` with the human's proof, not a name | 90% |
| 8 | J5: a lore field in `PAYLOAD` "so the claims check can strike what was not served" | The claims check named is `gate.check_claims`, which checks counts, a green sha, and quotes only (`onescript/gate.py:437-477`); it cannot strike a lore fact. What strikes is `serve.check_cites` on cites (`serve.py:480`) and `seat_say.check_nothing_lacking` on vocabulary (`seat_say.py:299-332`). Both work on rows, so lore must be rows, not a blob field: a served document over budget is replaced by `empty`, never truncated (`ratatosk/onescript.py:37-40`) | 85% |
| 9 | J6: a D0 "game class" inside `resolvers.resolve_fixture` | That resolver is a closed key/value grammar over excerpt text (`resolvers.py:10-20`, `:378-411`); pushing game state through it is a text round trip of the kind that already produced the G3 truncation defects (`forge-convergence-flowering-experiment.md:188-191`). `chain_act` hardcodes `resolve_fixture` and injects only `chat_fn` (`chain.py:172-181`). The D0 for a table act is `GameSession.step`: the roll resolves in code (`engine_v1_7.py:56-78`), rules-lookup is `legal_moves` (`game_session.py:47`), state-read is `observe`. Nothing new | 85% |
| 10 | J7: `seat_say.run_checks` checks the narrator; flowering for set pieces | By construction a set-piece sentence fails check 3: every word must be a box's, glue, or a stop word (`seat_say.py:325-332`). So either the narrator is code (`seat_boxes.compose`, `seat_boxes.py:687`) with the model as an optional rewrite that must pass, or set-piece prose is a `draft` box, "never a fact" (`seat_boxes.py:107-111`). J6 and J7 are one phase: the act (R5) | 85% |
| 11 | J7: "choosing from `legal_moves` as a closed menu" is new | The menu is already closed by the tool shape: the model has one tool, `propose(path, data, cites, claim)` (`ratatosk/onescript.py:44-48`); a move is `path == <move id>` and code checks membership in `legal_moves` or treats it as ESCALATE. No new seam | 80% |
| 12 | J8: "a GM/table surface in the box stream reading `table/box/record.jsonl`" | The seat does not read record files; it reads `api.needs` (`grove/seat_record.py:5-11`, `onescript/api.py:412-426`), and `view.needs_you` already prints wager rows as lines (`onescript/view.py:121-131`); `seat_record.item_box` turns lines into boxes (`seat_record.py:164-186`). The surface is the seat pointed at the table box plus one line pattern. Not a panel | 85% |
| 13 | Order J1 → J2 → J3 → J4 | A wager has nothing to reconcile against until results are rows, and a roll row needs the stream's seed and counter. J4 and J2 come before J1 (§4) | 80% |
| 14 | Missing: a wager seal moves the served scope | A tip or wager seal is content in the human's pile and moves its subject (`onescript/tests/test_serve.py:545-554`, `serve.py:125-134`); after an outcome seal the sealed scope no longer matches and `propose` serves `empty` until the human reseals it. PLAN.md never says who reseals, when | 85% |
| 15 | Missing: the creator roll consumes draws | `Engine.roll` draws two dice before the `is_creator` branch returns without using them (`engine_v1_7.py:57-58`, `:65-68`). A replay that skips creator rolls diverges from the original. The roll row must record draws consumed, not results only | 90% |
| 16 | Missing: a mid-session seed reveals every later roll | One beacon seeds a whole session; anyone who knows the seed can compute every roll. A forecast made after the seed is public is not a forecast. Either one beacon per forecast window (play.py's `open --ahead` shape, `play.py:206-227`) or no mid-session forecasts. The seed never reaches the model: `serve._scrub` withholds every 64-hex string (`serve.py:80-81`, `:102-110`), and the seed is not in `PAYLOAD` (`serve.py:61`) | 85% |

## §4 Order

| Step | Phase | Why here |
|---|---|---|
| 1 | R2-one-stream | A roll row needs a seed and a counter before anything records rolls |
| 2 | R3-one-record | Results as rows, one chain; the sink is three methods |
| 3 | R1-one-wager | A wager reconciles against `verdict` rows; without R3 it has nothing to line up with (PLAN.md's J1-first is the mis-order) |
| 4 | R4-lore-rows | Lore rows ride the same serve; after R3 so `where` names scene ids that exist |
| 5 | R5-the-act | Needs served roll and lore boxes to check against |
| 6 | R6-the-surface | Reads what the five above wrote |

Each step ends with the suites of BRIEF §3 at or above baseline. Confidence 80%.

## §5 Adversarial tests

Those marked *exists* already pass in onescript; the build must keep them green on the table box and add the rest.

| # | Attack | Expected | Where it is, or what to add |
|---|---|---|---|
| T1 | A forged `seal` row with `who: human` and no proof (A5) | Serves nothing; grades nothing | exists: `test_forged_seal.py:90-130` |
| T2 | The human's real proof copied onto a row with another outcome | The first outcome stands | exists: `test_wagers.py:296-310` |
| T3 | An outcome sealed over the bare wager hash | Escalate | exists: `test_wagers.py:312-327` |
| T4 | A wager row appended after the `verdict` row it claims to predict | Escalate: `wager.n > verdict.n` | add to `reconcile_wagers` (R1) |
| T5 | A wager inside no sealed tip when the verdict lands | Escalate: `through` is `None` (`reverse.py:236-237`) | exists in part: `test_wagers.py:59-66`; add the verdict-row case |
| T6 | The human seals a tip after the beacon published, covering a late wager | Reconciles: the trust root's own act, by design (CONSTITUTION V); the row shows the beacon round beside the tip's `ts` so a reader can see it | add: a visible, not a refused, case |
| T7 | Cut the last rows (A7) | Caught inside a sealed tip (`record.py:206-212`); on a box with no tip, nothing is graded (handoff 10-17 §1:36-37) | exists: `test_forged_seal.py:409`; add the table-box case |
| T8 | Reseed: two sessions alive, one calls `random.seed` | With R2 streams, each session's roll rows are identical to its solo run | add; the hazard is described at `proof.py:20-30` |
| T9 | Replay skips creator rolls | Diverges unless the roll row records draws consumed | add: `engine_v1_7.py:57-58`, `:65-68` |
| T10 | A `verdict` row whose `randomness` does not match the beacon fetched for its `round` | `unreachable`, never graded; BLS stays unverified and is said so (predictions README §4) | add |
| T11 | An outcome seal, then `propose` without resealing the scope | Serves `empty` until the human reseals; no model row cites a moved table | exists in part: `test_serve.py:545-554`; add the end-to-end case |
| T12 | The model proposes a move not in `legal_moves` | ESCALATE row, no step taken | add (R5) |
| T13 | A narrator sentence with a word no box holds; a number no box holds | Struck, code sentence shown | exists: `seat_say` tests; add with roll boxes |
| T14 | A `world/*.md` written as a file, not as `lore` rows | Not served; a sentence naming its facts is struck | add (R4) |
| T15 | `Stream.shuffle` copy versus in-place under the `dice` library | Identical sequences | add (R2) |
| T16 | A roll row from a different engine version hash | Replay refuses, names the hash | add (R2) |

Confidence that this list covers the four guarantees: 80%.

## §6 Evidence table

| Claim | Evidence | Confidence |
|---|---|---|
| `random.Random` sequences did not drift 3.11 → 3.13 | Probe in this container: `random.Random(7)` gave `[3, 2, 4, 6, 1, 1, 5, 1]`, shuffle `[1, 2, 9, 4, 7, 6, 8, 3, 0, 5]`, choices `a e d a e` on 3.11.17, 3.12.3, 3.13.16 alike; `Stream(b"seed")` gave `[1, 1, 1, 5, 3, 4, 2, 3]` on all three | 95% |
| The `dice` library needs `randint` and in-place `shuffle` | `dice/elements.py:115`, `:224-236`, `:625`, `:642`, `:667` | 95% |
| onescript's commitment is order under a sealed tip, not time | `reverse.py:251-261`, `:236-247`; `record.py:11-16` | 90% |
| The table already keeps a one-script record | `handoff-2026-10-17.md:55`; experiment README §5 | 95% |
| ai-game-master's chain asks for an outside head it does not keep | `schema/01_ledger.sql:34-37` | 95% |
| `ledger_sink.py` copies that scheme byte for byte | `ledger_sink.py:10-23`, `:59-78` vs `verify_ledger.py:59-81` | 95% |
| Forge's calibration is itself a vendored copy | `forge/calibration.py:2-16` | 95% |
| `gate.check_claims` checks counts, green sha, quotes only | `gate.py:437-477` | 90% |
| A set-piece sentence cannot pass check 3 | `seat_say.py:325-332` | 85% |
| `chain_act` does not inject the resolver | `chain.py:172-181` | 95% |
| `view.needs_you` prints wager rows | `view.py:121-131` | 95% |
| A wager seal moves the human pile's subject | `test_serve.py:545-554`; `serve.py:125-134` | 90% |

## §7 Questions

1. Does the human reopen §9 row 11 (one record, the one-script one), or keep `campaign.db` and take the `agm_head` row instead? Both are in R3; the spec does not choose.
2. Is a decision-beat seal a key proof or a Nestor pair on the table box (handoff 10-17 Q2)? R3 takes either; `Run.seal` and `Run.seal_nestor` both exist (`run.py:570-625`).
3. One beacon per forecast window, or no mid-session forecasts (§3 row 16)?

## §8 Phases R1–R6 (what replaces J1–J9)

@phase R2-one-stream
Replaces J2. A `Stream` shim with `random.Random`'s surface: `randint(a, b) = a + below(b - a + 1)`, `choice(seq) = seq[below(len(seq))]`, in-place `shuffle`, `random()` from `u32`. Kept pure stdlib, SHA-256 over `seed + counter` as `play.py:56-70`. Every seam takes it unchanged: `dice5e` (`dice5e.py:57`), the `dice` library (`elements.py:115`, `:625`), `random_policy` (`gm.py:56`), `CrazyEightsSession` (`crazy_eights_adapter.py:138-140`). The one backward-compatible change to `engine_v1_7.py` is `roll(stat, is_creator=False, rng=None)` falling back to the module `random` (BRIEF §4, second guess); `reset(seed)` in `game_engine_adapter.py:188` and `story_session.py:205` passes a stream instead of `random.seed`. Replay requires three things the stream alone does not give: the seed bytes and beacon round on a row; the engine's version hash on the same row (onescript stamps its own `version`, `record.py:131`, not the-table's); and every roll as a row with the counter before and after, so replay is re-verification of rows, never re-simulation. Confidence 85%.

@phase R3-one-record
Replaces J4 and J9. `gm.run_session` takes a `sink` with three methods: `open_session`, `snapshot`, `close_session` (`gm.py:95-113`). A `RecordSink` with those three methods that calls `Record.append("verdict", desk, ...)` is the whole join; `gm.py`, `proof.py` and every adapter are untouched. A `snapshot` is a `verdict` row with `where` = scene or beat id, carrying turn, seat, move, the roll (draws, counter, stat, result, status) and the view; `close_session` is a `verdict` row with `winners`, `scores`, `summary`. A decision beat (`story_session.py:338-360`) becomes a `proposal` the human seals with `Run.seal` and a proof; `StorySession.seal(fact_id, by)` is called by code only after that seal row verifies, so its name check is a second gate behind a real one, never the first. `ledger_sink.py` and its `campaign.db` chain go; `proof.py` verifies with `verify_chain` and `verify_anchor` instead of `verify_ledger.py`. If the human keeps `campaign.db` for canon, entities and rulings, one `verdict` row per session (`agm_head`: the ledger's last hash) puts that head inside the next sealed tip; that is "anchor by head" as one row, and still one sealed tip. Confidence 80%.

@phase R1-one-wager
Replaces J1, J3, the forecasting game's round files, foreshadow `predict.py`/`grade.py`, `ledger.json` f1/f2, and onescript's bite-count `predict.py` for table use. One primitive, four verbs, all existing or one line: predict = `Run.wager(id, distribution)` (`run.py:554-568`), the distribution from code where code has it (the 36-outcome table, `peaks.py:46-51`, emitted as `path`/`p`/`band`) and from a person or a model where it does not; commit = the wager's row inside a tip the human seals (`run.py:627-642`) before the reveal source exists, with the wager row naming the beacon round it awaits; reveal = a `verdict` row written by code carrying the beacon (`round`, `randomness`, `signature`) or the engine result (R3); grade = `reverse.reconcile_wagers` (`reverse.py:251-307`) lining each wager up with the human's outcome seal, plus `brier` and `log_score` vendored from `forge/calibration.py:42-52` as six lines with a provenance comment, computed only on a reconciled row and reported, never written as a grade (`graded_by` stays `None`, `reverse.py:264`). The twelve `DECK` questions (`play.py:124-185`) are a reader that turns a beacon into `verdict` rows; the round JSON files are retired. The commitment check is chain order under the human's tip, never a timestamp: `wager.n < tip_seal.n < verdict.n`; anything else escalates. Confidence 85%.

@phase R4-lore-rows
Replaces J5. One `lore` row per sealed world fact, `where` = the scene or place it belongs to, the fact in a new `PAYLOAD` field `fact` (one entry added to the tuple, `serve.py:61`). No blob field: a `world/*.md` written through `write_file` is a `write` row whose text is not served (`record.py:278-280`, experiment README §5), and a document over budget serves as `empty` (`ratatosk/onescript.py:37-40`). The strike is the existing one: a model row citing an unserved id is refused by `serve.check_cites` (`serve.py:480`), and a seat sentence with a word no served box holds fails `check_nothing_lacking` (`seat_say.py:299-332`). `gate.check_claims` is not touched; it never checked lore. Confidence 85%.

@phase R5-the-act
Replaces J6 and J7. A table act closes in `GameSession.step` (D0: the roll in code, `engine_v1_7.py:56-78`; rules in `legal_moves`, `game_session.py:47`). What a model may do is three things and only three: pick a move, by `propose(path=<move id>)` (`ratatosk/onescript.py:44-48`), which code accepts only if the id is in `legal_moves` for the current seat and otherwise treats as ESCALATE; rewrite the sentence `seat_boxes.compose` already built from the roll and scene boxes, under `run_checks` (`seat_say.py:358-372`), struck and replaced by the code sentence on any failure (`seat_say.py:5-9`); or, at a set piece, propose a `draft` box (`seat_boxes.py:107-111`) that the human reads as a draft and no later row depends on. A decision beat escalates to the human, never to a model (`story_session.py:362-364`). Flowering (`ratatosk --onescript --class flowering`, `onescript.py:24-31`) is the third rung for the draft box only. No class is added to `resolvers.py`; `chain_act` is not called for a table act. Confidence 80%.

@phase R6-the-surface
Replaces J8. The seat (`grove/seat_cli.py`) with its config pointed at the table box reads `api.needs` (`api.py:412-426`); `view.needs_you` already renders every wager row as a line (`view.py:121-131`); `seat_record.item_box` gains one pattern for `wager <id> …` beside `RECHECK` (`seat_record.py:164-186`). Three states hold as they do today (`seat_record.py:14-24`). No component, no panel, no file reader. Confidence 85%.

@constraint severity=critical
Sandbox only: `/home/user/sandbox/`. No commit to a real branch, no push, no PR without the human's recorded word (CLAUDE.md rules 5, 9). This spec changes no file under `/home/user/sandbox/repos/`.
@constraint severity=critical
No machine-sealed canon. A `verdict` row is code's record of what happened, never a seal; a decision beat passes only on a human seal whose proof re-checks (`onescript/serve.py:271-281`); `StorySession.seal`'s name check is never the first gate.
@constraint severity=error
Deterministic first: `GameSession.step` closes a table act; a model may only pick from `legal_moves`, rewrite a code sentence under `run_checks`, or propose a `draft` box. A roll, a move, or a fact the model was not served is struck or ESCALATE.
@constraint severity=error
Committed before, graded after, by chain order under the human's sealed tip (`wager.n < tip_seal.n < verdict.n`), never by a timestamp; `graded_by` stays `None`.
@constraint severity=error
One hash chain per table box, one sealed tip. A second chain exists only as a head recorded as a row inside the first.
@constraint severity=error
Search before writing: `brier` and `log_score` are vendored from `forge/calibration.py:42-52` with provenance, the way Forge vendored them; the commit says the house already knew.
@constraint severity=warning
Every document this build writes is a proper `@markdownai v1.0` doc and passes `mai lint`.
