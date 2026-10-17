---
kind: doc
name: box-build-spec-documented
description: The box build's joins J1 to J9 pinned to what the fleet already wrote down, with the documented names, row shapes, homes and break tests, and every place the docs are silent or disagree.
b17: BOXB1
---

@markdownai v1.0

# Box build — the documented spec

§1 Ground · §2 Waves · §3 Doc conflicts · §4 BRIEF §4 guesses · §5 Questions · §6 J1 · §7 J2 · §8 J3 · §9 J4 · §10 J5 · §11 J6 · §12 J9 · §13 J7 · §14 J8 · constraints at the end

*Spec writer, documented side, 2026-10-17. Agent-written, not ratified. Every
"(a)" quote is copied from the file and line named; every "pick" is a guess with
its percentage. Paths are relative to `/home/user/sandbox/repos/`. Questions sit in
§5, not at the very bottom, because `mai lint` refuses a second H2 after the last
`@phase`.*

## §1 Ground

| Thing | Where it is written | What it fixes for every join |
|---|---|---|
| The block | `willows-grove/docs/design/forge-convergence.md:540-681` (§6a, T1–T7) | The Table is the next build; T4 is the forecast lane |
| The three dares | `forge-convergence.md:642-645`; `willow-mcp/docs/story/chapter-08-the-table.md:154-207` | Names: `forecast()`, `seal_outcome()`, `read_misses()`. None exists in any repo (cbm `search_graph` over all five sandbox projects: 0 hits) |
| Who seals | `forge-convergence.md:571-573`: "The machine proposes; a named human seals. … Only the operator seals an outcome" | No code path writes a seal; `ai-game-master/docs/DECISION.md:112-115` "No machine-sealed canon. Ever." |
| Code first | `forge-convergence.md:574-578`: "Python does the growth: the world walk, the dice, canon read from the record, the forecasts and their backtests" | A model is called only where code returns ESCALATE |
| Score | `forge-convergence.md:647-649`: "The score is calibration (Brier, reliability), not hit rate alone." | J1's numbers |
| Ledger home | `forge-convergence.md:734` (row 11, settled): "The Table keeps the ai-game-master chain … The chain gains a head anchor." | J9 |
| Wager seal | `foreshadow-table-handoff-2026-10-17.md:47-49`: "a wager's outcome is inside what the human signs" | `reverse.outcome_subject` is the only outcome subject |
| One-script serving | `foreshadow-table-handoff-2026-10-16.md:39-44` (§3 table) | Record → piles → scope → serve → D0 → speak |
| Tools order | `box-build/BRIEF.md` §1 | cbm, then mai, then grep, for every builder |

## §2 Waves

Phases below run in wave order, not number order. Wave 1 has no dependency on
any other join, so three builders start at once.

| Wave | Joins | Needs | Lands in |
|---|---|---|---|
| 1 | J1 wagers + Brier, J2 seeded dice, J3 odds predictor | nothing | willow-bot, safe-app-store, willows-grove |
| 2 | J4 results as rows, J5 lore payload | J2 (J4 records the stream position); J5 needs nothing but is tested on J4's table record | safe-app-store, willow-bot |
| 3 | J6 D0 game class, J9 ledgers | J4 (verdict rows to read; the table identity that writes them); J9 needs J1's `seal-tip` verb | willow-bot, safe-app-store |
| 4 | J7 narrator, J8 table panel | J4, J5, J6 (J7); J4 and J1 (J8) | willows-grove, safe-app-store |

## §3 Doc conflicts

| # | Join | Doc A says | Doc B says | Pick | % |
|---|---|---|---|---|---|
| C1 | J1 | PLAN J1: Brier "from Forge `forge/calibration.py`, not a third copy" | BRIEF §4: vendor `brier`/`log_score` into onescript | Neither copy nor vendor: willow-bot takes `forge-play` the way willow-mcp did (`willow-mcp/pyproject.toml:100-115`: the modules it "used to OWN and the Forge used to vendor … now live there", re-export seams). `onescript/calibration.py` re-exports `forge.calibration` | 60% |
| C2 | J1 | Forge `calibration.py:36-38` and `calibration_ledger.py:75-91`: confidence lives in [0.5, 1.0], "a claim you think false is a true-claim restated" | `play.py:245-248` takes any p in [0, 1]; round 1 has the human at 0.12 | Fold each pair to the believed direction (p < 0.5 → (1−p, not outcome)) before `bins`; `brier` and `log_score` are unchanged by the fold | 85% |
| C3 | J1 | `reverse.py:254-255`: `reconcile_wagers` "Never grades: `graded_by` stays None" | T4: "The score is calibration (Brier, reliability)" | Score is not grade: add `brier`/`log_score` per reconciled row and keep `graded_by: None`; the human's sealed outcome is the grade (chapter 8 `seal_outcome()` writes HIT/MISS by a named human) | 85% |
| C4 | J1 | Handoff 10-17 Q15 (`:84`): forecasts "graded by the beacon instead of by hand" | `forge-convergence.md:572-573`: "Only the operator seals an outcome" | Code proposes the outcome from the beacon (`play.py` computes it); the human's proof over `outcome_subject` is still the only thing that counts | 80% |
| C5 | J1 | T4: `forecast()` "seals a prediction into the ledger before the outcome"; row 11 makes that ledger the ai-game-master chain | PLAN J1, handoff 10-17 Q6/Q15: forecasts become one-script `wager` rows | `forecast()` writes the one-script `wager` row (the record whose seals carry proofs); J9 anchors the ai-game-master head into it. "Seals" in T4 means "commits to the chain before", not a human seal | 75% |
| C6 | J1 | `api.checkout` (`api.py:402-409`) never hands a human key, and `run.py:681-683` counts a wager outcome only "when the caller handed the key over" | Handoff 10-17 `:30-33`: the table's keys file "holds no human key" | A read-only `reconcile` verb takes `--human-key FILE` from outside the box (mode 0600, refused inside it). Anchors sealed by Nestor pair are not covered by `covered_through`; that stays a recorded gap | 65% |
| C7 | J2 | PLAN J2: "an injected stream into `Engine.roll`" | `the-table/the_table/game_engine_adapter.py:9-11`: the-table "never modifies anything under `apps/game`"; README `:46` the same for bureau | No edit under `apps/game`. The adapter injects the stream by swapping `engine_v1_7.random` for a `StreamRandom` inside one `try/finally` per roll. The BRIEF's one-line edit is option B for the human | 55% |
| C8 | J2 | PLAN J2: "as `crazy_eights_adapter` and `dice5e` already take" | `crazy_eights_adapter.py:138`: `rng = random.Random(seed)` is owned inside `reset`, not injected; only `dice5e.py:25-27` takes an injected rng | Follow dice5e: an injected object with `randint`; crazy_eights keeps its own until asked | 70% |
| C9 | J2 | PLAN J2: the trap "goes away" | Recorded runs reproduce only under the old RNG: foreshadow README `:40` "Same seed, same result … reproduced exactly"; `baselines/baselines-N500.md` | New default is the stream; every verdict row and run report names `rng: "sha256-stream/v1"`. Old runs stay as written (archive, don't delete) with a note that they used `random/global` | 70% |
| C10 | J4 | PLAN J4: StorySession seals land as `seal` rows | One-script A5 (foreshadow README `:100`): a `seal` row without a proof was a forgery that "unlocked serve"; `StorySession.seal` (`story_session.py:362`) has a name and no proof | A decision beat becomes a one-script proposal (`world/<fact_id>.md`); the human's `proposal:<hash>` seal is the `seal` row; only after it verifies does code call `StorySession.seal(fact_id, by=…)`. Code never writes a `seal` row | 85% |
| C11 | J4 | PLAN J4: results enter as rows the narrator can read | `serve.py:218-228`: rows with `who == "run"` "are never served" | Verdict rows are written under a verified `table` identity (family `python`), like `desk`, so a sealed scope can serve them | 65% |
| C12 | J4 | Handoff 10-16 Q10 (`:62`) is still a question | PLAN J4 takes "yes" | Build it as PLAN says; the row shape keeps everything the human may strike later | 70% |
| C13 | J6 | PLAN J6: a new D0 class in `resolve_fixture` | `forge-convergence-flowering-experiment.md:241`: "Operator may add classes in §8 before run; not after." Handoff 10-16 `:43`: "D0 Classes G1–G5 only" | New classes are namespaced (`table.roll`, `table.rules`, `table.state`), never `G6`, and stay out of the flowering battery's scorer | 65% |
| C14 | J7 | PLAN J7: flowering "choosing from `legal_moves`" | `forge-convergence.md:598`: a decision beat "has no legal move"; T3 `:634-636` narration "at the escalation points only" | The menu applies to action beats only; a decision beat is never offered to a model, only to the human seal | 85% |
| C15 | J7 | PLAN J7 and T3 say "set piece" | No world JSON carries a set-piece marker (`worlds/*.json` beats are `action`/`decision` only) | Optional beat field `"set_piece": true`, default false; `load_world` accepts it | 60% |
| C16 | J8 | PLAN J8: a GM/table surface | `one-script/box-stream-surfaces.md` lists no table panel; its §4 `:46`: "A model sentence about seal state is the riskiest claim it could make" | Roll and scene boxes are narrated; seal, wager-outcome and anchor boxes are shown, never narrated | 80% |
| C17 | J1 | `seat/willow/experiments/foreshadow-2026-10-16/README.md:79-80`: "prediction f2 rest[s] on the agent's training" | Handoff 10-17 Q6 asks whether f1 and f2 both become wagers | f1 becomes a wager; f2 is held beside p3/p4 in `onescript_table.py`'s `HELD` until Q5/Q7 are ruled | 70% |
| C18 | J9 | Row 11: ai-game-master chain is the Table's ledger; T3 `:630-633` wants a durable seal "written through to the campaign box's canon table" | `ledger_sink.py:25-29`: the sink "never touches the `canon` table, never writes a SEALED/REJECTED status" | J9 anchors heads both ways and verifies; the canon write-through is not built here (it needs its own sink and the human's word) | 60% |
| C19 | J3 | Handoff 10-16 Q16 (`:68`) asks whether `peaks.py` moves into the-table | PLAN J3 moves it | Move only the pure `exact()` and `bucket_probs()`; `measured()` reads private `_current_beat`, `_tally`, `_scene_idx` and stays measurement in the experiment | 70% |

## §4 BRIEF §4 guesses against the docs

| BRIEF guess | Docs | Verdict |
|---|---|---|
| Vendor `brier`/`log_score` into onescript (70%) | Contradicted in part. PLAN J1 forbids "a third copy"; there are already two (`safe-app-store/apps/oakenscrolls-office/calibration.py`, `Forge/forge/calibration.py`; `forge-convergence.md:601` names a third canonical one in hornbook-knowledge). The fleet's recorded move is the other way: willow-mcp dropped its vendored copies for the `forge-play` dependency (`willow-mcp/pyproject.toml:100-115`). Supported in part: onescript is "stdlib only" (`one-script/README.md:653`) and Forge vendored "small enough to audit" (`calibration.py:2-16`). `forge-play` 0.8.1 is installed and its `calibration.py` is byte-identical to the Forge's | Pick C1 (take the dependency, re-export), 60%; vendoring stays the fallback if the human keeps onescript stdlib-only |
| Edit `apps/game/engine_v1_7.py`: `roll(..., rng=None)` (65%) | Contradicted: the-table "never modifies anything under `apps/game`" (`game_engine_adapter.py:9-11`), and its docs call the global RNG "a documented, deliberate coupling of `engine_v1_7.py` itself" (`:52-58`). The catalog marks `apps/game` `stalled` (`.willow/store/catalog.json`), which forbids nothing by itself. Supported: PLAN J2's wording "into `Engine.roll`" | Pick C7 (no edit, scoped swap in the adapter), 55%; the guess is option B |
| Exact-odds predictor at `apps/the-table/the_table/peaks.py`, emitting a wager distribution (70%) | Confirmed: handoff 10-16 Q16 names that exact path (`:68`); `peaks.py` `exact()` already returns `{"path", "p"}` rows (`peaks.py:93-139`), the wager distribution shape (`test_wagers.py` `DIST`) | Confirmed, with C19's narrowing |

## §5 Questions

1. C1: may willow-bot take `forge-play` (onescript stops being stdlib-only), or must Brier be vendored?
2. C7: may `apps/game/engine_v1_7.py` take one `rng=None` argument, or does the-table keep its no-edit rule?
3. C4: does a beacon-computed outcome still need the human's seal per question (28 seals for the seven rounds)?
4. C6: may the human's HMAC key be handed to `reconcile` from a file outside the box, or is the table box Nestor-only (handoff 10-17 Q2)?
5. C17: is f2 held with p3/p4?
6. C18: who builds the canon write-through for T3's durable seal, and when?

@phase J1-wagers-brier

## §6 J1 — Forecasts become wagers, scored by Brier

Wave 1. Repo: willow-bot (`one-script/onescript/`), willows-grove (importers).

### (a) Documented intent

| Quote | Where |
|---|---|
| "`forecast()` seals a prediction into the ledger before the outcome. `seal_outcome()` is the operator's seal on what happened. `read_misses()` clusters the misses, not only counts them." | `forge-convergence.md:643-645` |
| "The score is calibration (Brier, reliability), not hit rate alone." | `forge-convergence.md:648-649` |
| "Do f1 and f2 become one-script wagers, now that a wager's outcome is signed?" · "Should a verb exist to seal a wager outcome, by key and by Nestor pair (none does today)?" · "Should the game's forecasts become one-script `wager` rows, sealed `wager:` subjects graded by the beacon" | handoff 10-17 `:73`, `:74`, `:84` |
| "What the human signs to seal a wager's outcome: one hash over the wager's row hash and the outcome together" | `reverse.py:218-221` |
| "Brier score per question, `(p − outcome)²`, averaged; lower is better." | `predictions-2026-10-17/README.md:28-29` |
| "Count the hits. Read the misses. The misses are the map." | `chapter-08-the-table.md:269` |

### (b) What to build

| Name | Signature / CLI | Row or return shape |
|---|---|---|
| `onescript/calibration.py` | re-export: `from forge.calibration import brier, log_score, bins, summary` | A test proves they are the same objects (the `tests/test_forge_take.py` pattern). Import failure → `None`, and the report says `calibration: {"state": "unreachable", "why": "forge-play is not installed"}` |
| `Run.wager` (existing, `run.py:554-568`) | gains `by: str = "desk"`, `committed: dict | None = None` | `{"kind": "wager", "who": "run", "id", "distribution": [{"path", "p", "band"?}], "scores", "by", "committed"}`. `by` is a role from `{"human", "desk", "oracle", "coin"}`, never a person's name. `committed` carries a foreign commitment (`{"sha256", "beacon_then", "target"}`) when the forecast was made outside the record |
| `api.forecast` | `forecast(cfg, wid, distribution, *, by="desk", committed=None, argv=("forecast",)) -> {"row", "code"}` | Refuses: an empty distribution; a `p` outside [0, 1]; ps that don't sum to 1 within 1e-9; a duplicate `path`; a `wid` already on record (a forecast stands, `play.py:254-256`) |
| CLI `forecast` | `python3 -m onescript forecast <id> --dist FILE [--by ROLE] [--committed FILE]` | prints the wager row's hash, the subject an outcome seal names |
| `api.seal_outcome` | `seal_outcome(cfg, wager_hash, outcome, *, proof=None, pair=None, verifiers=None, argv=("seal-outcome",))` | Subject = `reverse.outcome_subject(wager_hash, outcome)`. By proof: `Run.seal` (existing). By Nestor pair: `Run.seal_nestor` gains `outcome`, writes `wager` and `outcome` beside the pair. Refuses an outcome naming no path of that wager before any seal row is written |
| CLI `seal-outcome` | `python3 -m onescript seal-outcome <wager-hash> --outcome '{"path_index": 0}' (--proof P | --pair FILE)` | Outcome keys: `path_index`, `path` or `winner` (`reverse.py:156-170`, `run.py:580-585`) |
| CLI `seal-tip` | `python3 -m onescript seal-tip --proof P` → `Run.seal_tip` (`run.py:627`) | Without a sealed tip no outcome counts (`reverse.covered_through`), so J1 is unreachable end to end without this verb |
| CLI `reconcile` | `python3 -m onescript reconcile [--human-key FILE]` → `Run.reconciled(human_key=…)`, read-only | Refuses a key file inside the box or readable by others (the A3/A4 rule, foreshadow README `:99`) |
| `reverse.reconcile_wagers` | unchanged signature | each reconciled distribution row gains `brier` (mean over its pairs) and `log_score` (`log_score(p_actual, True)`); `graded_by` stays `None` |
| `reverse.wager_pairs` | `wager_pairs(wager_row, path_index) -> list[tuple[float, bool]]` | 2 paths: one pair `(p of path 0, path 0 happened)`; n > 2 paths: one pair per path (one against the rest; their mean is the multi-class Brier over n). Each pair folded to [0.5, 1] (C2) |
| `reverse.calibration_of` | `calibration_of(wager_rows) -> {"all": summary, "by": {role: summary}, "bins": bins(all pairs)}` | added to `reconcile()`'s report as `"calibration"` |
| `reverse.read_misses` | `read_misses(wager_rows, wagers) -> {"misses": [{"id", "forecast", "happened", "p_happened", "tags"}], "clusters": [{"key", "ids"}]}` | A miss: a reconciled row whose actual path is not the most likely one (binary: p of what happened < 0.5). A cluster: two or more misses sharing a key, where keys are `forecast→happened` and each `tag` the wager's entries carry. Chapter 8's "Cluster detected." is `clusters != []` |
| `view.morning` GRADES | adds `brier 0.160 · log 0.49` to each reconciled wager line (`view.py:121-131`), then one `calibration` line per role and one `misses: N, clusters: K` line | "grade is yours" stays |
| `play.py export R` | prints one JSON line per (forecaster, question) of a revealed round | `{"id": "r001-3d6-human", "distribution": [{"path": "yes", "p": 0.12}, {"path": "no", "p": 0.88}], "by": "human", "committed": {"sha256", "beacon_then", "target"}, "proposed_outcome": {"path": "no"}}`; oracle and coin rows too. `proposed_outcome` is code's reading of the beacon, never a seal |
| `onescript_table.py wagers` | turns `ledger.json` `predictions` into binary wagers through `forecast` | f1 → `{"id": "f1", distribution yes 0.62 / no 0.38, "by": "desk"}`; f2 into `HELD` (C17) |

### (c) Lands in

`willow-bot/one-script/onescript/{calibration.py (new), run.py, api.py, __main__.py, reverse.py, view.py}`, `willow-bot/pyproject.toml` (`forge-play>=0.1.0,<1.0.0`), `willows-grove/seat/willow/experiments/predictions-2026-10-17/play.py`, `…/foreshadow-2026-10-16/table/onescript_table.py`.

### (d) Tests

| Test | Proves |
|---|---|
| `tests/test_wagers.py::test_calibration_is_forges_own_math` | `onescript.calibration.brier is forge.calibration.brier` |
| `test_wagers.py::test_brier_matches_play_board` | the 28 questions of `rounds/001..007.json`, exported, forecast, outcome-sealed with a throwaway human key and tip-sealed, give mean Brier 0.15971 (human), 0.15988 (oracle), 0.15991 (desk), 0.250 (coin), as `predictions-2026-10-17/README.md:47-52` records |
| `test_wagers.py::test_fold_keeps_brier_and_fills_bins` | a 0.12 forecast scores the same folded and unfolded; `bins` holds it in [0.8, 0.9) |
| `test_wagers.py::test_unsealed_outcome_has_no_score` | no seal → `escalate`, no `brier` key |
| `test_wagers.py::test_read_misses_clusters_chapter_eight` | the four chapter-8 forecasts, tagged `north`, give 3 misses and one cluster |
| `test_main.py::test_forecast_seal_outcome_seal_tip_reconcile_round_trip` | the four verbs end to end through the CLI |
| Break: `test_forged_seal.py::test_beacon_outcome_without_human_proof_counts_for_nothing` | a `seal` row carrying `proposed_outcome` and no proof leaves the wager escalated |
| Break: `test_forged_seal.py::test_outcome_proof_moved_to_other_wager_counts_for_nothing` | a proof copied onto a second wager row of the same distribution escalates |
| Break: `test_api.py::test_forecast_refuses_mass_not_one_and_duplicate_id` | p sum 1.1, duplicate path, reused id: each refused, nothing appended but the refusal |
| Break: `test_main.py::test_reconcile_refuses_human_key_inside_box` | key file under `--box`, or mode 0644, refused |

Suites: onescript 502 passed / 1 skipped → up; willow-bot at or above baseline.

### (e) Silent or split

C1, C2, C3, C4, C5, C6, C17. Silent: what `read_misses` clusters by (pick: `forecast→happened` and declared tags, 55%); how n-path wagers score (pick: one-against-the-rest pairs, 60%); whether imported forecasts keep their "before" property (the chain row is written after the beacon; pick: `committed.sha256` and `beacon_then` carry it and the test re-hashes the round file, 70%).

@phase J2-seeded-dice

## §7 J2 — One dice stream for every game

Wave 1. Repo: safe-app-store (`apps/the-table/`).

### (a) Documented intent

| Quote | Where |
|---|---|
| "`Engine.roll` draws from the GLOBAL `random` module … There is no way to seed *this* engine per-call without touching global state, so `reset(seed)` calls `random.seed(seed)` directly." | `game_engine_adapter.py:52-57` |
| "two scenes must be run to completion one at a time, never constructed up front and interleaved" | `the-table/README.md:96-98` |
| "The RNG stays the caller's: every path draws from the injected `rng` (a `random.Random`), never the global module" | `aetheris5e/dice5e.py:25-27` |
| "a stream of numbers from a seed, the same on every Python" · `below`: "Uniform in 0..k-1, by rejection: no modulo bias." | `play.py:55-80` |
| "Dice are plumbing; they are never stored as knowledge." | `ai-game-master/docs/DECISION.md:89-90` |

### (b) What to build

| Name | Signature | Notes |
|---|---|---|
| `the_table/stream.py` | `class Stream(seed: bytes)` with `u32()`, `below(k)`, `die(sides)`, `shuffle(xs)`, copied from `play.py:56-80` with a provenance comment naming it | the one home; `play.py` then imports it (`THE_TABLE_DIR`, the way `peaks.py` finds the-table) |
| `Stream.from_seed` | `from_seed(seed: int | bytes | str) -> Stream` | int → big-endian minimal bytes (0 → `b"\x00"`); str → `bytes.fromhex` of a drand `randomness`; bytes as given. Plus `label: bytes = b""` appended, the way `play.py:210,286` appends `b"pick"` and the question name |
| `StreamRandom` | wraps a `Stream`; `randint(a, b)`, `choice(seq)`, `shuffle(xs)` (in place), `random()` (`u32() / 2**32`) | the duck type `dice.roll(expr, random=…)` and `Engine.roll` call: the `dice` library calls only `randint` (`dice/elements.py:114-115`) |
| `the_table/dice_source.py` | `rolled_with(rng)`: a context manager that sets `engine_v1_7.random = rng` and restores it in `finally` | C7. The only place the engine's module name is touched; no file under `apps/game` changes |
| `SceneSession`, `StorySession` | `__init__(…, rng_factory: Callable[[int], StreamRandom] | None = None)`; `reset(seed)` builds `self._rng = rng_factory(seed)`; every `Engine.roll` runs inside `rolled_with(self._rng)` | `random.seed(seed)` is deleted from `game_engine_adapter.py:188` and `story_session.py:205`. Default factory: `lambda s: StreamRandom(Stream.from_seed(s))` |
| Draw position | `self._rng.stream.n` after each roll | J4 writes it on the verdict row so a roll replays from `(seed, n)` |
| `Observation.view` | adds `"rng": "sha256-stream/v1"` | C9 |

### (c) Lands in

`safe-app-store/apps/the-table/the_table/{stream.py (new), dice_source.py (new), game_engine_adapter.py, story_session.py}`, `willows-grove/seat/willow/experiments/predictions-2026-10-17/play.py` (imports, keeps its own copy only if the-table isn't beside it, and says so).

### (d) Tests

| Test | Proves |
|---|---|
| `tests/test_stream.py::test_stream_matches_play_rounds` | `Stream(bytes.fromhex(r["reveal"]["beacon"]["randomness"]) + q.encode())`, run through `play.py`'s `DECK` draws, reproduces every `answers` value in `rounds/001..007.json` |
| `test_stream.py::test_known_vector` | a fixed seed gives a fixed first ten `u32()`s (pinned bytes, any Python 3.10–3.14) |
| `test_stream.py::test_below_has_no_modulo_bias` | `below(3)` over a seed with forced rejections; chi-square under bound at N=30000 |
| `test_game_engine_adapter.py::test_interleaved_scenes_are_each_deterministic` | two scenes built up front, stepped alternately, equal each scene run alone (today's documented trap, now gone) |
| `test_story_session.py::test_global_random_untouched` | `random.getstate()` equal before and after a full story |
| Break: `test_game_engine_adapter.py::test_engine_random_restored_after_raise` | a roll that raises inside `rolled_with` leaves `engine_v1_7.random is random` |
| Break: `test_stream.py::test_below_refuses_zero_and_negative` | `below(0)` raises `ValueError`, never loops |
| Break: `test_game_engine_adapter.py::test_state_file_still_untouched` | the existing `TestGameEngineStateFileUntouched` holds with the new source |

Suites: the-table 152 passed / 2 skipped → up; ai-game-master 7 passed unchanged.

### (e) Silent or split

C7, C8, C9. Silent: whether a threaded caller is supported (pick: no; the swap is process-wide for the length of one roll, and the docstring says so, 70%); whether `play.py` drops its copy (pick: imports when the-table is beside it, 60%).

@phase J3-odds-predictor

## §8 J3 — The exact-odds forecaster, and predict that takes it

Wave 1. Repos: safe-app-store (`the-table`), willow-bot (`onescript/predict.py`).

### (a) Documented intent

| Quote | Where |
|---|---|
| "one-script `predict` foresaw the decision beat 0% of the time (it had never seen one)" · "Aetheris, tagging: Odds 8/8" | foreshadow README `:46`, `:49` |
| "Should the experiment scripts become a the-table module (`apps/the-table/the_table/peaks.py`), or stay here as measurement?" | handoff 10-16 `:68` |
| "The distribution is counted, not guessed: what kinds of bites followed before." | `onescript/predict.py:6` |
| "So a prediction is a **distribution**: the likely path, the median, and the outliers, each with its chance." | `one-script/workflow.md:115-116` |
| "`predict` counts the past. It can't say what the human wants next." | `one-script/next-pile.md:556-558` |

### (b) What to build

| Name | Signature | Shape |
|---|---|---|
| `the_table/peaks.py` | `bucket_probs(stat) -> {"strong", "weak", "miss"}`; `exact(world, sheets, policy="suggested") -> {"per_beat", "paths"}` | moved from the experiment's `peaks.py:46-139` with a provenance comment; exact arithmetic in `fractions.Fraction`, floats only at the edge |
| `peaks.distribution` | `distribution(world, sheets, policy="suggested", *, top=None) -> list[{"path", "p", "band"}]` | the wager distribution J1 takes. `band`: `likely` for the top path, `middle` for p ≥ 0.05, `outlier` below; every path kept, nothing smoothed (`predict.py:6-7`) |
| CLI | `python3 -m the_table.peaks <world.json> --wager` | prints the distribution as JSON for `onescript forecast <id> --dist -` |
| `predict.declare` | `declare(rows, given: list[dict] | None = None) -> {"likely", "median", "outliers", "n", "source"}` | `given` present: the same keys built from it, `source: "code"`, `n: None`; absent: today's count, `source: "counted"` |
| `Run.turn` | gains `forecast: list[dict] | None = None`, passed to `declare` | the `predict` row records `source`; grading by bite is unchanged |

### (c) Lands in

`safe-app-store/apps/the-table/the_table/peaks.py` (new), `willow-bot/one-script/onescript/{predict.py, run.py}`. The experiment's `peaks.py` keeps `measured()` and imports `exact` (C19).

### (d) Tests

| Test | Proves |
|---|---|
| `the-table/tests/test_peaks.py::test_bucket_probs_sum_to_one_exactly` | Fractions, every stat −5..+5 |
| `test_peaks.py::test_distribution_matches_recorded_runs` | Hasbeen and Ironworks paths equal `runs/*.json` exact columns to 4 places |
| `test_peaks.py::test_exact_agrees_with_measured_within_recorded_gap` | N=500 seeded StorySession runs within 0.037 (handoff 10-16 `:25`, "≤3.7 points") |
| `onescript/tests/test_onescript.py::test_declare_takes_code_distribution` | `source == "code"`, likely is the max-p path |
| Break: `test_onescript.py::test_declare_refuses_bad_given` | negative p, mass ≠ 1, empty list: `ValueError`, nothing recorded |
| Break: `test_peaks.py::test_world_with_no_action_beat` | a world opening on a decision gives one empty path with p 1, not a crash |

### (e) Silent or split

C19. Silent: the band cut-offs (pick 0.05, 50%); whether `predict` grades a code distribution against the bite text (pick: no, it grades through the wager in J1, 65%).

@phase J4-results-as-rows

## §9 J4 — Game results and story seals in the one-script record

Wave 2, after J2. Repos: safe-app-store (`the-table`), willow-bot (`onescript`).

### (a) Documented intent

| Quote | Where |
|---|---|
| "rule-engine results would enter as `verdict` rows" | handoff 10-16 `:48-49` |
| "Do rule-engine results enter the record as `verdict` rows written by code?" | handoff 10-16 `:62` (Q10) |
| "a decision beat has no legal move and `step()` raises on it, so only `seal()` by a named human passes it … `seal()` records in memory only" | `forge-convergence.md:598` |
| "The players are never written down." | `forge-convergence.md:638`; `storysession-design.md:27-28` |
| "`PAYLOAD` fields (`family, standing, turn, verdict, reason, intent, bite`)" | handoff 10-16 `:42`; `serve.py:61` |

### (b) What to build

| Name | Signature | Row shape |
|---|---|---|
| Identity | keys file entry `table`; `api.TABLE = ("table", "python")` beside `api.DESK` (`api.py:50`) | C11 |
| `api.verdict` | `verdict(cfg, row: dict, argv=("verdict",)) -> {"row", "code"}`; CLI `python3 -m onescript verdict --json FILE` | `{"kind": "verdict", "who": "table", "where": <scene place>, "turn": <one-script turn>, "game": "story", "beat": "b2", "seat": 0, "move": ["act", "Grit"], "total": 9, "verdict": "weak", "reason": "2d6+stat = 9: 7-9", "rng": "sha256-stream/v1", "seed": "<hex>", "draw_n": 14}` |
| Result row | same verb, `"what": "result"` | `{"kind": "verdict", "who": "table", "verdict": "result", "reason": <Result.summary>, "scores": {...}, "winners": []}` |
| `the_table/onescript_sink.py` | `OneScriptSink(onescript_cmd: list[str])` with the `LedgerSink` duck type: `open_session`, `snapshot`, `close_session` | Built from `Observation` and the adapter's last roll; `gm.run_session(…, sink=OneScriptSink(...))` unchanged (`gm.py:71-79`). Two sinks at once through a `Tee` sink |
| `seat` | the seat index and the character id only | no person, no attendance (Table law) |
| Decision beat | `pending_seal()` → a proposal row `{"path": "world/<fact_id>.md", "data": fact, "cites": [served id], "claim": "proposed by <proposed_by>; awaits the human's seal"}` through `turn --proposal` (the `onescript_table.py propose` path, `:150-177`) | C10 |
| After the human seals `proposal:<hash>` | the sink reads `seal_rows()` (`run.py:267`), and only for a verified row calls `StorySession.seal(fact_id, by=<the verified seal's verifier name, else "human">)` | a refused or unreachable seal leaves the story blocked |

### (c) Lands in

`willow-bot/one-script/onescript/{api.py, __main__.py}`, `safe-app-store/apps/the-table/the_table/onescript_sink.py` (new).

### (d) Tests

| Test | Proves |
|---|---|
| `the-table/tests/test_onescript_sink.py::test_story_turns_become_verdict_rows` | a seeded story writes one verdict row per action beat; replaying `(seed, draw_n)` reproduces each `total` |
| `test_onescript_sink.py::test_verdict_rows_are_served_once_scoped` | a scope over `who=table` serves them with `verdict`, `reason`, `turn` in the view |
| `test_onescript_sink.py::test_result_row_after_terminal` | one `what: result` row, summary verbatim |
| Break: `test_onescript_sink.py::test_hand_written_seal_row_never_advances_story` | a `seal` row appended by hand over the proposal's subject (A5 again) leaves `pending_seal()` set |
| Break: `test_onescript_sink.py::test_verdict_row_carries_no_person` | a world whose character is named like a player: the row holds `seat` and character id, no other name field |
| Break: `onescript/tests/test_api.py::test_verdict_refuses_unverified_table` | a verdict with a wrong `table` key is `refused` |
| Cross-repo: `test_onescript_sink.py::test_ledger_and_record_both_verify` | `Tee(LedgerSink, OneScriptSink)`: `verify_ledger.py --canon` passes and `Record.verify_chain()` is empty |

### (e) Silent or split

C10, C11, C12. Silent: the verdict row's `where` (pick: the scene's `place`, so a where-pile is a place, handoff 10-16 Q2 `:54`, 60%).

@phase J5-lore-payload

## §10 J5 — Sealed lore reaches the model

Wave 2. Repo: willow-bot (`onescript/serve.py`).

### (a) Documented intent

| Quote | Where |
|---|---|
| "Does lore get a `PAYLOAD` field, so a sealed `world/*.md` reaches the model?" | handoff 10-17 `:81` (Q12) |
| "A sealed `world/*.md` lands in the box as a file, but its text is not in serve's `PAYLOAD`, so lore is still not served" | foreshadow README `:76-78` |
| "a new field reaches the model only when someone adds it here" | `serve.py:59-61` |
| "Proposals p3, p4 and prediction f2 rest on the agent's training … Under one-script `serve` they would be struck" | foreshadow README `:79-80` |

### (b) What to build

| Name | Change | Rule |
|---|---|---|
| `serve.PAYLOAD` | adds `"lore"` | |
| `serve._serve` | for a served row with `kind == "proposal"`, `path` under `world/`, its `subject` in the held seals (`sealed_verified`), and `sha == h256(data)`: the view gets `lore: data` | Two seals, both checked: the scope seal over the table, and the proposal's own `proposal:` seal. An unsealed or own-idea proposal never gets `lore` |
| `serve.view` | unchanged except `lore` passes through `_scrub` and counts toward `max_chars` | Over the cap the answer is `empty`, never truncated (`api.serve` docstring) |
| Claims | the served doc's `lore` strings join the facts `gate.check_claims` and `seat_say` read | A sentence naming what no served row holds is struck |

### (c) Lands in

`willow-bot/one-script/onescript/serve.py`; no other file.

### (d) Tests

| Test | Proves |
|---|---|
| `tests/test_serve.py::test_sealed_world_proposal_serves_its_lore` | s1 sealed: its text in `lore` |
| `test_serve.py::test_unsealed_world_proposal_serves_no_lore` | p1 open: row served without `lore` |
| `test_serve.py::test_lore_hash_is_withheld` | a 64-hex string inside lore is `[hash withheld]` |
| Break: `test_serve.py::test_forged_proposal_seal_serves_no_lore` | a seal row without proof over the proposal: no `lore` |
| Break: `test_serve.py::test_edited_data_after_seal_serves_no_lore` | `data` changed after sealing (sha mismatch): no `lore`, and the chain break is reported |
| Break: `test_serve.py::test_unserved_training_is_struck` | a narrator sentence with "palantír" over a scope holding s1–s3 fails the claims check |

### (e) Silent or split

Silent: lore from Jeles (handoff 10-16 Q5 `:57`, Q6 `:58`, copyright) is out of this join; only the human-sealed `world/*.md` path is built (85%).

@phase J6-d0-game-class

## §11 J6 — A table act closes in code

Wave 3, after J4. Repo: willow-bot (`willow_bot/deterministic/resolvers.py`, `one-script/onescript/escalate.py`).

### (a) Documented intent

| Quote | Where |
|---|---|
| "A deterministic, per-scenario-class resolver reads the pool record … and returns an answer or `ESCALATE`." | flowering experiment `:170-174` |
| "resolver precision (must equal **1.0** — a resolved answer that is wrong is a defect, not a score; `ESCALATE` is never scored as a failure)" | flowering experiment `:178-182` |
| "D0 · Classes G1–G5 only … no class means `d0_escalate`" | handoff 10-16 `:43` |
| "Operator may add classes in §8 before run; not after." | flowering experiment `:241` |
| "the dice, canon read from the record" are Python's | `forge-convergence.md:574-575` |

### (b) What to build

| Class | Act brief | Closes in code when | Escalates (reason) when |
|---|---|---|---|
| `table.roll` | `table.roll: turn 3` | exactly one served `verdict` row for that turn: answer `{"total", "verdict"}`, cite its table id | none (`no_roll_on_record`); two that disagree (`conflicting_field`) |
| `table.rules` | `table.rules: weak` | a served excerpt of the world's rule rows names the bucket: answer its band text (`strong 10+ / weak 7-9 / miss 6-`, `story_session.py` docstring) | absent or two readings |
| `table.state` | `table.state: tally` | the latest served `verdict` `result` row, or the tally from verdict rows in order | a gap in turn numbers (`turns_missing`) |

Signatures: `resolvers._resolve_table_roll(fixture_id, excerpts) -> dict` and the two siblings, all returning `_record(...)` (`resolvers.py:251-266`); `resolve_fixture` dispatches on the `table.` prefix before `unknown_class`. `escalate._CLASS_PREFIX` (`escalate.py:263`) widens to `G[1-5]|table\.(roll|rules|state)`. A model never rolls: no resolver here draws a number.

### (c) Lands in

`willow-bot/willow_bot/deterministic/resolvers.py`, `willow-bot/one-script/onescript/escalate.py`.

### (d) Tests

| Test | Proves |
|---|---|
| `willow-bot/tests/test_resolvers_table.py::test_roll_reads_the_recorded_verdict` | resolved, cite is the served id |
| `test_resolvers_table.py::test_precision_is_one` | 30 fixtures with gold: every `resolved` equals gold |
| `test_resolvers_table.py::test_flowering_battery_unchanged` | the v2 fixtures score as in flowering §13 (13/13 D0) |
| Break: `test_resolvers_table.py::test_roll_absent_escalates_not_invents` | no verdict row: `escalate`, `no_roll_on_record`, answer `None` |
| Break: `test_resolvers_table.py::test_two_verdicts_one_turn_escalates` | a duplicated turn: `conflicting_field` |
| Break: `onescript/tests/test_escalate.py::test_G6_prefix_is_not_a_class` | `G6: …` stays classless and `d0_escalate`s |

### (e) Silent or split

C13. Silent: the rules excerpt format (pick: world rule rows served as excerpts with the existing closed key grammar extended by one text key `rule:`, 55%).

@phase J9-ledgers

## §12 J9 — Two chains, anchored by head

Wave 3, after J1 (`seal-tip`) and J4 (the `table` identity). Repos: safe-app-store (`the-table`), willow-bot (`onescript`).

### (a) Documented intent

| Quote | Where |
|---|---|
| "The Table keeps the ai-game-master chain … Writing through Nestor would need new `LEDGER_KINDS`, uses a different hash scheme … The chain gains a head anchor." | `forge-convergence.md:734` (row 11, settled) |
| "Should the human seal a tip on the table's box, so a cut can be seen (A7)?" | handoff 10-17 `:79` (Q10) |
| "A7 · With no sealed tip, cutting the record's last rows is not seen. One-script's documented limit" | handoff 10-17 `:95` |
| "this chain adds tamper-*evidence*. It seals nothing and grants no authority" | `ai-game-master/README.md:80-83` |

### (b) What to build

| Name | Signature | Row shape |
|---|---|---|
| `LedgerSink.head_n()` | `-> tuple[int, str]` (row count, `head()`) | read-only, beside `head()` (`ledger_sink.py:182-187`) |
| `api.ledger_head` | `ledger_head(cfg, ledger: str, n: int, head: str, argv=("ledger-head",))`; CLI `ledger-head --ledger ai-game-master --n N --head H` | `{"kind": "ledger_head", "who": "table", "ledger": "ai-game-master", "n": 41, "head": "<hex>", "db_sha": "<hex of campaign.db>"}` |
| Other direction | `LedgerSink.snapshot(state={"onescript_tip": {"n", "hash"}}, note="anchor")` | a `turn` row in the ai-game-master chain; no new kind, so `schema/01_ledger.sql` and `verify_ledger.py` stay as they are |
| `reverse.ledger_anchors` | `ledger_anchors(rows, read_head) -> list[{"ledger", "n", "verdict", "why"}]` | `read_head` is injected (the-table passes a reader over `campaign.db`); verdicts: `satisfied` (the chain still verifies and row n still has that hash), `failing` (fewer rows, or another hash at n), `unreachable` (db absent) |
| Closing A7 | the human runs `seal-tip` (J1) after the latest `ledger_head` row | the tip covers the head row, so a cut of either chain is seen |

### (c) Lands in

`safe-app-store/apps/the-table/the_table/{ledger_sink.py, onescript_sink.py}`, `willow-bot/one-script/onescript/{api.py, __main__.py, reverse.py}`. Nothing under `apps/ai-game-master` changes.

### (d) Tests

| Test | Proves |
|---|---|
| `the-table/tests/test_ledger_anchor.py::test_head_anchored_both_ways` | each chain names the other's tip; both verify |
| Break: `test_ledger_anchor.py::test_cut_ai_game_master_rows_is_seen` | delete the last two `ledger` rows: `failing`, "fewer rows than anchored" |
| Break: `test_ledger_anchor.py::test_cut_onescript_rows_after_sealed_tip_is_seen` | `seal-tip`, then truncate `record.jsonl`: `covered_through` is `None` and the morning screen says so |
| Break: `test_ledger_anchor.py::test_cut_without_sealed_tip_is_still_unseen` | pins A7 as documented: without a tip the cut passes (a test that the limit is still the limit) |
| Break: `test_ledger_anchor.py::test_rewritten_row_under_anchor_fails` | edit row n's note and re-hash forward: `failing` |
| `ai-game-master` suite | 7 passed, unchanged |

### (e) Silent or split

C18. Silent: whether `db_sha` belongs on the row (a later turn changes the file; pick: keep it as of the anchor and compare only `n`/`head`, 55%).

@phase J7-narrator

## §13 J7 — The narrator says the boxes, and code checks it

Wave 4, after J4, J5, J6. Repos: willows-grove (`grove/`), safe-app-store (`the-table`).

### (a) Documented intent

| Quote | Where |
|---|---|
| "Narration at the escalation points only: a local model voices a set piece or answers a join no rule covers, and its output is a draft the world does not depend on." | `forge-convergence.md:634-636` |
| "invokes **heavy models only for set-piece scenes** (flowering) while the **operator** remains the authority" | flowering experiment `:342-344` |
| "code makes the boxes; … a small model may say the boxes as one sentence; code checks that sentence (every cite served, every box cited, nothing the boxes lack, the human's words quoted exactly)" | `box-stream-surfaces.md:18-22` |
| `run_checks(sentence, boxes, human, claims, earlier) -> [cites served, boxes cited, nothing lacking, quotes]` | `grove/seat_say.py:358-372` |
| "No fleet nouns leak downward. Willow, Grove, Nestor, Jeles, SOIL, SAFE — none appear in anything a player sees." | `ai-game-master/docs/DECISION.md:79-82` |

### (b) What to build

| Name | Signature | Rule |
|---|---|---|
| `grove/table_boxes.py` | `scene_boxes(served_doc) -> list[Box]` | one `Box(kind="scene")` per served place, one `Box(kind="roll")` per verdict row (`value` = `"<total> <verdict>"`, `detail` = the beat's outcome text), one `Box(kind="lore")` per `lore`; ids are the served ids |
| `table_boxes.narrate` | `narrate(boxes, human, say=seat_say.ollama_say) -> {"sentence", "checks", "struck": bool}` | `qwen3:4b` through the seat's existing loopback path; a failed check or an unreachable model falls back to the code sentence (the CLAUDE.md seat rule) |
| `the_table/menu.py` | `menu_policy(choose: Callable[[list], int]) -> Policy` | action beats only: the model is handed the numbered `legal_moves` and returns an index; anything else (out of range, text, a move not listed) → `first_legal_policy()` and an `escalate` verdict row. Called only on a beat with `set_piece: true` (C15) |
| Decision beats | never on the menu | C14 |
| Player-facing words | `narrate` refuses a sentence holding a fleet noun (DECISION §3 list) | struck, code sentence used |

### (c) Lands in

`willows-grove/grove/table_boxes.py` (new), `safe-app-store/apps/the-table/the_table/{menu.py (new), worlds.py}` (accept `set_piece`).

### (d) Tests

| Test | Proves |
|---|---|
| `willows-grove/tests/test_table_boxes.py::test_roll_boxes_cite_served_ids` | every box id is a served id |
| `test_table_boxes.py::test_good_sentence_passes_all_four` | a sentence from the boxes passes `run_checks` |
| Break: `test_table_boxes.py::test_invented_roll_is_struck` | "you rolled 11" when the box says 9: check 3 fails, code sentence used |
| Break: `test_table_boxes.py::test_training_lore_is_struck` | "the palantír glows" over boxes without it: struck |
| Break: `test_table_boxes.py::test_fleet_noun_is_struck` | "Willow rolls" fails |
| Break: `the-table/tests/test_menu.py::test_off_menu_choice_falls_back_and_escalates` | index 7 of 4, `"Grit"` as text, `("act", "Fly")`: each falls back, one `escalate` row each |
| Break: `test_menu.py::test_decision_beat_never_reaches_choose` | `choose` is never called while `pending_seal()` is set |
| `test_menu.py::test_no_set_piece_no_model` | a world without `set_piece` never calls `choose` |

### (e) Silent or split

C14, C15. Silent: whether narration is written back to the record (pick: no; a draft the world does not depend on, T3 `:635-636`, 80%).

@phase J8-table-panel

## §14 J8 — The table as a box stream

Wave 4, after J4 and J1. Repo: willows-grove.

### (a) Documented intent

| Quote | Where |
|---|---|
| "A part of the UI fits when its data is already a set of structured facts." | `box-stream-surfaces.md:24` |
| "Governance answers ('may we?') · Seals belong to Nestor and the human. … show the seal card and its evidence boxes only." | `box-stream-surfaces.md:46` |
| "Every reader honors populated / empty / unreachable, never collapsed" | `willows-grove/CLAUDE.md`, Grove table |
| The dispatch rail sketch: a pile, boxes made by code, who wrote it, the sentence, the human action, the states | `box-stream-surfaces.md:70-77` |
| "`table/box/record.jsonl`: check-in …, one desk `turn` per human line with the bite verbatim, then the scope card. 27 rows, chain unbroken." | handoff 10-17 `:55` |

### (b) What to build

| Name | Signature | Shape |
|---|---|---|
| `grove/table_reader.py` | `read_table(box: Path) -> {"state": "populated" | "empty" | "unreachable", "why": str, "boxes": list[Box]}` | read-only; the chain checked through `onescript.record.Record.verify_chain` when willow-bot is beside the repo (`ONESCRIPT_DIR`), else `unreachable` with why. A broken chain is `unreachable`, never `populated` |
| Boxes | summary box (`role="count"`: turns, verdicts, open wagers, sealed scopes); roll and scene boxes (J7); wager boxes (id, forecaster role, p of the likeliest path, state, Brier when reconciled); seal and anchor boxes | seal, wager-outcome and anchor boxes carry `role="governance"` and are never narrated (C16) |
| Human lines | the human's `bite` rows stay plain lines, quoted exactly | §2 "the human's lines stay plain" |
| Sketch | `web/demo/box-stream/table-stream-v1.html` | the five states §7 sketches: populated, a turn arriving, a struck sentence, quiet table ❦ with no model asked, unreachable with its reason |
| Doc | `box-stream-surfaces.md` §9 "The table as a box stream", marked Proposal | the same table shape as §7/§8 |

### (c) Lands in

`willows-grove/grove/table_reader.py` (new), `willows-grove/web/demo/box-stream/table-stream-v1.html` (new), `willows-grove/docs/design/one-script/box-stream-surfaces.md` (§9 added).

### (d) Tests

| Test | Proves |
|---|---|
| `willows-grove/tests/test_table_reader.py::test_real_table_box_is_populated` | the 27-row `table/box/record.jsonl` reads populated |
| `test_table_reader.py::test_empty_box_is_empty` | no record → `empty` |
| `test_table_reader.py::test_no_onescript_is_unreachable` | `ONESCRIPT_DIR` unset and absent → `unreachable`, why names it |
| Break: `test_table_reader.py::test_edited_bite_is_unreachable_not_populated` | A6 on a scratch copy: `unreachable`, "chain broken at row n" |
| Break: `test_table_reader.py::test_seal_box_is_never_in_the_narrated_set` | `narrate` is handed no `governance` box |
| Break: `test_table_reader.py::test_human_line_quoted_exactly` | a bite with a doubled space and a CRLF renders byte-equal |

### (e) Silent or split

C16. Silent: whether the panel joins the served page on `:8766` or only the CLI seat (pick: CLI seat and sketch first, the page after the human asks; Rule 1, 65%).

@constraint severity=critical
Sandbox only: `/home/user/sandbox/repos/<repo>` on `box-build`. Never touch `/home/user/<repo>`; no push, no PR (BRIEF §2; CLAUDE.md rules 5, 9).
@constraint severity=critical
Code never writes a `seal` row and never seals canon. A beacon, an exact-odds oracle or a StorySession `seal(by=...)` call proposes; the human's proof or Nestor pair over the exact subject (`outcome_subject`, `proposal:`, `tip:`) is the only seal (DECISION.md §6; PR 137).
@constraint severity=critical
Nothing that grants authority rests on a row's own fields: `who`, `by`, `proposed_outcome` and `committed` are labels; only a re-checked proof counts (handoff 10-17 §2).
@constraint severity=error
One copy of each primitive: Brier math comes from `forge.calibration` (C1), the SHA-256 stream from `the_table/stream.py` (J2), exact odds from `the_table/peaks.py` (J3). A second copy names its source and has a test that diffs it (safe-app-store CLAUDE.md rule 11).
@constraint severity=error
A model never invents a roll, a move, a fact or a lore line it was not served: rolls come from the stream, moves from `legal_moves`, facts and lore from sealed rows; every narrated sentence passes `seat_say.run_checks`.
@constraint severity=error
The players are never written down: rows carry seat index, character id and a forecaster role, never a person's name, attendance or behaviour (`homestead-table-vision.md:71`).
@constraint severity=error
No file under `apps/game` or `apps/ai-game-master` changes unless the human rules otherwise (C7, C18).
@constraint severity=warning
Every reader returns populated, empty or unreachable, never collapsed; a broken chain is unreachable, never populated.
@constraint severity=warning
Every document this build writes is a `@markdownai v1.0` doc and passes `mai lint`; each suite touched ends at or above its BRIEF §3 baseline.
