# Changelog

All notable changes land here per INVARIANTS.md §3. Format follows Keep a Changelog v1.1.0.

## [Unreleased]

### Fixed

- **seat:** the opening says the sealed snapshot in the short form the cards use (`serve:9439efcacd2c`, not the whole 64-character hash), with or without the seal date (`seat_boxes.opening` reads `short`).

## [0.24.1](https://github.com/willow-memory/willows-grove/compare/v0.24.0...v0.24.1) (2026-10-14)


### Fixed

* **seat:** a shared last word is a verb only when it is a status word ([9a53fe0](https://github.com/willow-memory/willows-grove/commit/9a53fe082741c4ba22373ce3cca3ba971204057d))
* **seat:** a shared last word is a verb only when it is a status word ([#152](https://github.com/willow-memory/willows-grove/issues/152)) ([27c3347](https://github.com/willow-memory/willows-grove/commit/27c3347d5849cae5e6ffa0500f0b5849551ed74c))

## [0.24.0](https://github.com/willow-memory/willows-grove/compare/v0.23.0...v0.24.0) (2026-10-14)


### Added

* **seat:** the opening says when the human sealed ([6517f46](https://github.com/willow-memory/willows-grove/commit/6517f463555e9c5aa0b253b4bfe4024ff8a5ef4a))


### Fixed

* **seat:** no repeated lines, the chain count said alone, and the opening names the seal date ([#150](https://github.com/willow-memory/willows-grove/issues/150)) ([bcae31a](https://github.com/willow-memory/willows-grove/commit/bcae31a07b0a2de2689d03ab73d5585c093378d7))
* **seat:** the chain's count box is a count and is said on its own ([480bf21](https://github.com/willow-memory/willows-grove/commit/480bf212e44061bc5c1e52d79300fca23e15bc60))
* **seat:** the opening and closing do not repeat what a stage's plain line said ([7826292](https://github.com/willow-memory/willows-grove/commit/7826292e00d9234e8da8bd1bce4bea0797bcc72b))

## [0.23.0](https://github.com/willow-memory/willows-grove/compare/v0.22.0...v0.23.0) (2026-10-14)


### Added

* **seat:** check-out says what stays pooled for next time ([4621975](https://github.com/willow-memory/willows-grove/commit/46219758ba61e6251117f3e4e699e311d5259fac))
* **seat:** chips from the boxes, chip answers, follow-ups resolved against the last turn ([11f3090](https://github.com/willow-memory/willows-grove/commit/11f3090f7ab858a9805ef172e4485e2d206f0eb2))
* **seat:** greetings, acknowledgements, help and farewells are answered by code ([1f08219](https://github.com/willow-memory/willows-grove/commit/1f082190307bcd946c6f9f10cb0f897934622f86))
* **seat:** read a Nestor store as boxes (read-only) ([ed77297](https://github.com/willow-memory/willows-grove/commit/ed77297fa797b57f00b3c47f22d6669a79ed5379))
* **seat:** the CLI seat converses like the box-stream demo, and reads a Nestor store ([#147](https://github.com/willow-memory/willows-grove/issues/147)) ([3efcd2c](https://github.com/willow-memory/willows-grove/commit/3efcd2c67a439d6c868ebb0b80b312e32b60e78f))
* **seat:** the model sees the last two replies of the run ([57dd3fd](https://github.com/willow-memory/willows-grove/commit/57dd3fd9076e24ff1c5c1e4acfbc6590fc899ddb))
* **seat:** the run opens with one sentence that picks up from last time ([9ab6dea](https://github.com/willow-memory/willows-grove/commit/9ab6dea490be6676fedca4e2356904bb3e04e871))
* **seat:** the seat picks up from last time, carries the pool over, and the model sees the thread ([#148](https://github.com/willow-memory/willows-grove/issues/148)) ([044e4d1](https://github.com/willow-memory/willows-grove/commit/044e4d159ba267eb12d349fc108c8a7a71339f7a))
* **seat:** where are we and what needs me are read from the Nestor store ([5b8b73b](https://github.com/willow-memory/willows-grove/commit/5b8b73b7cd1c324a413eb637180c076f40d91491))
* **seat:** where are we leads with the store's count, then what is open ([9558651](https://github.com/willow-memory/willows-grove/commit/955865180a7c51caa9ed36f09ae03edb07e8ec48))
* **seat:** where are we pages four boxes at a time, count plus open items first ([8990518](https://github.com/willow-memory/willows-grove/commit/89905186f304adf8d5161a68e89e696093ac5723))


### Fixed

* **seat:** a failed check-in line is blocked, not a routine pass ([3e11168](https://github.com/willow-memory/willows-grove/commit/3e1116807cbc18395df11c37eec83cb8272ad8e3))
* **seat:** a pair of changed or routine boxes has a verb; the count is never grouped ([efb4e5c](https://github.com/willow-memory/willows-grove/commit/efb4e5c4731b49c05cfe494dd6b9ddfa82863ac9))
* **seat:** a run of three changed or routine boxes has a verb ([54a6bb4](https://github.com/willow-memory/willows-grove/commit/54a6bb46780cc702a633f54517f3a42605f4765f))
* **seat:** a run of three decided boxes has a verb ([cb0e981](https://github.com/willow-memory/willows-grove/commit/cb0e981528c4dd0be94d5df3991d029f1c197c97))
* **seat:** a show-me that reads as a task reaches the chain after a turn ([d86136e](https://github.com/willow-memory/willows-grove/commit/d86136e49065dae331fe0a514d9cfdd57f4534a1))
* **seat:** an unmatched "show me X" is a plain code line, not an escalation ([de46023](https://github.com/willow-memory/willows-grove/commit/de4602356c608900df7c882ca9278b16e9e8b9b2))
* **seat:** counts the code says are pluralised (1 box, 2 boxes, 1 row) ([6c448cb](https://github.com/willow-memory/willows-grove/commit/6c448cb587dae541a8044f6523f221d6bf1e42ef))
* **seat:** names keep their capital, drafts and counts are not said as facts ([cdcda7d](https://github.com/willow-memory/willows-grove/commit/cdcda7dde4b817a44aaf7d24606e203cf0ad0400))
* **seat:** phrasing on real data - needs-you values, show-me refs, chain count, one No rush per turn ([08da613](https://github.com/willow-memory/willows-grove/commit/08da613fa252de9858df06b3f51b620f35bc6915))
* **seat:** stage prompts state their default; a refused answer is said plainly and re-asked ([2a5c1d2](https://github.com/willow-memory/willows-grove/commit/2a5c1d22651077b6e1927060b05b6f34500fe237))
* **seat:** the gate checks the venv the seat runs in ([5ca6114](https://github.com/willow-memory/willows-grove/commit/5ca61142ee4590a47ea47bab1d9209c605012269))
* **seat:** the unmatched show-me line lists box ids when a box has no better ref ([9cf4ad1](https://github.com/willow-memory/willows-grove/commit/9cf4ad154c9ab9bc81b7107891f85cf985b71711))
* **seat:** why says the reason, not every detail line; no doubled full stop ([f5e342c](https://github.com/willow-memory/willows-grove/commit/f5e342c4a1001c3d898838e15727fdc7b9d1d2dd))

## [0.22.0](https://github.com/willow-memory/willows-grove/compare/v0.21.0...v0.22.0) (2026-10-13)


### Added

* **seat:** --no-say and --model NAME ([94b91f2](https://github.com/willow-memory/willows-grove/commit/94b91f2d189877f5c37ca76fff4987cd0c2363c5))
* **seat:** flags that write nothing, --no-say/--model, still-pooled card; seat-stack names the CLI seat ([#145](https://github.com/willow-memory/willows-grove/issues/145)) ([649ce82](https://github.com/willow-memory/willows-grove/commit/649ce82600c9b376cf673cc667821b69b34fc5d6))
* **seat:** flags that write nothing: --help, --version, --check ([ea82178](https://github.com/willow-memory/willows-grove/commit/ea82178f74d27212ee88c4a1bc658e01e9a1e691))
* **seat:** show what is still pooled at start ([af59418](https://github.com/willow-memory/willows-grove/commit/af59418ee665b329d238c961c50be14f4b84d467))

## [0.21.0](https://github.com/willow-memory/willows-grove/compare/v0.20.0...v0.21.0) (2026-10-12)


### Added

* **seat:** serve the sealed snapshot via api.resume (B part 2) ([00b7968](https://github.com/willow-memory/willows-grove/commit/00b7968d55b28d1e50d55b25a53d969651044787))
* **seat:** serve the sealed snapshot via api.resume (B part 2); venv default follows D2 ([#143](https://github.com/willow-memory/willows-grove/issues/143)) ([3039c28](https://github.com/willow-memory/willows-grove/commit/3039c28683082d4601c48b161cfe83a7966dc7a3))


### Fixed

* **seat:** bot venv default follows seal D2 ([4c2b3d4](https://github.com/willow-memory/willows-grove/commit/4c2b3d4de12a2ec6d3b2b23da835e035173285ad))

## [0.20.0](https://github.com/willow-memory/willows-grove/compare/v0.19.0...v0.20.0) (2026-10-11)


### Added

* **seat:** GROVE_SAY_MODEL picks the reply model; qwen3 gets /no_think ([24a277a](https://github.com/willow-memory/willows-grove/commit/24a277a10771f71d4ef4133dfcb17a580cf8f5f5))
* **seat:** selectable reply model (GROVE_SAY_MODEL) + qwen3 /no_think ([#141](https://github.com/willow-memory/willows-grove/issues/141)) ([1869768](https://github.com/willow-memory/willows-grove/commit/1869768910e314b6aceadd465677ebc5faed9e5c))


### Fixed

* **changelog:** dash bullet under [Unreleased] so the §3 check counts it ([64196ee](https://github.com/willow-memory/willows-grove/commit/64196ee6ac82f1d98498d975f5f3daeca52a9a9c))

## [Unreleased]

### Added

- **seat:** `grove/seat_nestor.py` reads a Nestor sqlite store as seat boxes, read-only (`mode=ro`, `query_only`, stdlib only, older schemas tolerated): a live sealed pair is decided (the verifier and her reason quoted exactly), a replaced one is changed (both reasons), a waiting draft is changed and marked a draft (never said as fact; `needs you` only when asked), a rejection is blocked verbatim (a `reopen_when` makes it a "not yet" with her condition), and one count box. No path, a missing file or a file that is not a Nestor store is `unreachable`; a readable store with no rows is `empty`; `fixture:` origins stay on the card. Each kind is capped with a counted `more` box (PR 147).
- **seat:** `where are we` and `what needs me` are answered from the Nestor store at the config's `nestor_db` (`api.default_nestor_db()`) through the same ranked converse, chips and follow-ups as a chain turn, so `show me`, `why`, `the second one` and `go on` work on its boxes; they no longer go to the chain, and `help` says so. Unconfigured is one `unreachable` box, and asking again after the store changed is a fresh read (PR 147).
- **seat:** a reply ends with chips built from the boxes it showed, as in the sketch: `show me <ref>` for the blocked box (else the first box) with a detail to open, by a ref only that box answers to (a number of two digits or more, an id-like token or the box's short id, never the first words of its value), the options of a needs-you box whose one-line detail splits on ` · ` into three or more short digit-free parts (taken as the box says them, so "put it back · keep as a grant · block · stop" offers those four), then always `later` and `thanks`; the row is capped at six chips, choices cut first (`seat_boxes.chips`), and plain mode carries no escape code (PR 147).
- **seat:** a typed line that is a chip just offered is answered by code, not the chain: `thanks` "Anytime.", `later` "Got it. It stays in the pile.", any offered choice "Got it: <choice>." It is only acknowledged: it changes no record, seals nothing and writes no row (PR 147).
- **seat:** a follow-up is resolved against the last reply's boxes by fixed rules before the chain: `show me 712`, `open 712`, a box id, `the first/second/third (one)`, and `that` (the box last opened, else the first of the last page) show that box again in full with a code sentence; `why`, `what's that` and `tell me more` say its detail; `go on`, `more` and `next` show the next page by code or say nothing is left. It never asks a model or calls `api.escalate`; an ordinal past what was shown or a ref that fits two boxes is a plain line, not a guess; a `show me X` / `open X` / `show X` that no shown box answers to is a plain line too when X reads as a reference, a task otherwise (see Fixed); any other unmatched line goes to the chain as before (PR 147).
- **seat:** a reply's boxes are ranked before they page: a heads-up (`empty` or `unreachable`) first, then needs you, blocked, decided, changed, routine pass, stable within a kind, so `more?` pages the ranked list (`seat_boxes.rank`, after the box-stream sketch's priority) (PR 147).
- **seat:** the code sentence reads like the sketch: a short sentence per box with one phrasing per kind, built only from the box's own label, value and detail plus the sketch's glue list ("You need to ratify the work order. PR 712's still waiting, 126 tests pass."), `Morning.` on the run's first reply when the turn's clock time is before noon, `Oh, and` / `Also,` on a continuation page, `both` for a pair of one kind, `Looks like` on an all-routine first page, `Heads up:` before a problem, and `No rush.` only when nothing needs the human, blocks, or went wrong; the model is told the boxes arrive ranked, and its allowed glue is the same `GLUE` tuple.
- **seat:** an `unreachable` or `empty` card is also said in a plain code line, as in the sketch ("I can't read the record right now. <why>."; "<Label> is empty: <why>."), for a reply and for a stage; the three states stay distinct and the card is unchanged (PR 147).
- **seat:** at start, after resume or scope, the seat reads `api.pooled` once and shows ONE `still pooled` card for the proposals earlier runs left unsealed (the count and a couple of subjects), in its own `populated`, `empty` or `unreachable` state; a raise or a missing `pooled` on an older willow-bot is an `unreachable` card, never a crash. It seals and deposits nothing and leaves the resume snapshot as it was (PR 145).
- **seat:** flags that write nothing: `grove-seat --help` and `--version` print and exit 0, an unknown flag or argument exits 2 before the bot loads (it used to ignore argv and open a session, whose `api.checkin` writes record rows), and `--check` probes the bot root, the python in use, whether `ratatosk` resolves and whether the Ollama loopback holds the reply model, each shown `populated`, `empty` or `unreachable`, exit 0 only if all are populated. None of them calls `api.checkin` (PR 145).
- **seat:** `--no-say` runs the seat code only (no model is asked), and `--model NAME` picks the reply model for this run, winning over `GROVE_SAY_MODEL`; a `qwen3*` model still gets `/no_think`, and the two flags together exit 2 (PR 145).
- **seat:** serve the sealed snapshot via `api.resume` (B part 2): at start the seat serves the human's newest sealed scope pinned at its `upto`, skipping the group-by prompt, so the subject holds still while the desk adds rows; an unreachable or missing `resume` shows an `unreachable` card and scopes fresh; at close-out a grown scope's subject joins the one `seal ↗` offer. The seat still seals and mints nothing (PR 143).
- **seat:** `GROVE_SAY_MODEL` picks the reply-sentence model (default `qwen3:4b`), and a `qwen3*` model gets `/no_think` appended so it returns instead of running away thinking (PR 141).
- **seat:** more small talk is answered by code, never the chain: greetings (`hi`, `hello`, `hey`, `morning`, `good morning`) get one fixed line, acknowledgements (`ok`, `okay`, `cool`, `got it`, `sure`) get "Got it.", and `help` / `what can you do` get a fixed line of what the seat understands (a task, `show me 712`, `why`, `the second one`, `go on`; `thanks` and `later` are only acknowledged); `bye`, `done` and `quit` check out like an empty line. A closing `?`, `!` or `.` is ignored, and a declined `more?` still says the pile keeps it (PR 147).
- **seat:** `why` says the reason naturally instead of reading out every detail line: the human's own quoted words, led by who said them (`Nieves said no: "Not little. She never once called me little." (fixture).`, `Nieves sealed it: "..."`, `Nieves said not yet: "..." Reopen when: "..."`), a chain box's plain reason as `Reason: empty_scope.`, and any other detail as the box has it; provenance lines (origin, the fixture note) stay on the card and out of the sentence, but a fixture box's sentence ends `(fixture)`. A sentence code ends never doubles its full stop after a closing quote (`seat_boxes.terminate`, used by `compose`, the plain lines and the follow-up replies) (PR 147).
- **seat:** a count the code says is pluralised: `the pile · 1 box on the record`, `agent · code · said 1 box, no model asked` (it said `1 boxes`), `I showed 1 box`, `1 row` for a one-row table and `1 in Nestor as a draft`, beside `2 boxes` and `10 more sealed` (`seat_boxes.plural`) (PR 147).
- **seat:** `where are we` leads with the store's count, as the shoebox sketch does, not with the refusals: page one is the count ("14 sealed, 1 replaced, 3 drafts, 1 retired, 2 rejected (fixture)", the fixture tag kept, no `Looks like`, no `No rush.` over a store that holds a refusal) plus the first four open items (`STORE_PAGE`), then the waiting drafts, the refusals, the decided and the other changes, each kind's counted `more` box last in its group (`seat_nestor.lead_rank`); `what needs me` and chain turns keep the generic rank, and the store is still only read (PR 147).
- **seat:** the run opens with one code sentence that picks up from last time, built only from what `api.resume` and `api.pooled` already returned (no new call, no model, no row): "Picking up from the sealed snapshot serve:9439efca (rows up to 41); 2 proposals still pooled from earlier runs.", "No snapshot has been sealed yet, so I'm scoping fresh; nothing is pooled from earlier runs.", and for an unreadable resume or pool "I couldn't read the last sealed snapshot, so I'm scoping fresh" / "I couldn't read the pool, so I can't say what is still pooled", never "nothing to pick up". It carries the run's one `Morning.` (before noon), so the first reply no longer repeats it (`seat_boxes.opening`) (PR 148).
- **seat:** check-out ends with a closing that carries over, beside the one `seal ↗` offer, on exit, EOF, Ctrl-C and `bye` alike: one code sentence from the pool the close-out already read, "2 proposals stay pooled for next time.", "Nothing stays pooled for next time.", or "I couldn't read the pool, so I can't say what stays pooled for next time." (a raise, a refusal or a non-record is never said as empty). It seals, deposits and writes nothing more (`seat_boxes.carry_over`) (PR 148).
- **seat:** the model sees the thread: its prompt carries the last two replies of this run (`seat_say.THREAD_TURNS`) as box facts with their tags plus the human's earlier lines as context, so a sentence can say "that" or "still". The four checks are as strict as before: a cite to a box in that window was served, a cite to any other box (never shown, older than the window, or from a previous run, since the thread dies with the run) is struck; `every box cited` is about the current page only; an earlier box's facts count toward `nothing the boxes lack` only when the sentence cites it; quotes come from the current line alone. The code-only path is unchanged (PR 148).

### Fixed

- **seat:** `scripts/grove-seat` bot-venv default follows seal D2: `$WILLOW_HOME/willow-bot/venvs/willow-bot` first, then the legacy `$WILLOW_HOME/venvs/willow-bot` with a one-line stderr warning naming the new home (`GROVE_VENV` still wins) (PR 143).
- **seat:** the gate's venv is the seat's venv: `Config.venv` (where `api.checkin` looks for the toolchain) was the legacy `$WILLOW_HOME/venvs/willow-bot` while `scripts/grove-seat` runs the bot by seal D2, so the check pointed at a different venv than the seat ran in. `seat_cli.resolve_venv` now gives the running interpreter's venv when it is one, else the launcher's order (`GROVE_VENV`, `$WILLOW_HOME/willow-bot/venvs/willow-bot`, legacy, `./.venv`), else the D2 path (PR 147).
- **seat:** a check-in line takes its card kind from the row's own status, not a default `pass`: a line made by a `failing` or `unreachable` gate ("tests: onescript: failed: 23 failed", "toolchain: ruff: ... not installed") is a `blocked` card, as is any other line of a hard-closed report (a record break, a turn never closed); only a line of a report that did not hard-close, from a gate that is not bad, stays a `routine pass` (`seat_cli.checkin_kind`) (PR 147).
- **seat:** the stage prompts state their default plainly (`group by (enter = who)`, `cap in characters (enter = 48000)`) and a refused answer is said as what it is, not as a broken record: a group-by the api refuses as a usage error is "Group by takes who, what, when or where; you said \"where are we\"." (the names read from the refusal itself) and asked again, not an `unreachable` card and not "I can't read the record right now"; a cap that is not a whole number of 1 or more is said the same way and asked again, no longer a `blocked` card. Any other scope refusal is still the `refused` card. The module docstring now names the group-by prompt (PR 147).
- **seat:** a needs-you box whose value is long or has `: ; , ( )` inside is no longer given a dangling " needs you": it reads `This needs you: <value>.` (the value as the box has it); a short value (up to six words, no inner punctuation) still reads `<value> needs you`, and a verb phrase still `You need to ...` (PR 147).
- **seat:** a `show me <ref>` chip's ref is a meaningful token, never the first words of a value: a number of two digits or more (not part of a version or a hash), an id-like token (`PR 712`, `ABC-123`), or the box's short id (`b4`), and only one no other shown box answers to; a box with none gets no `show me` chip (`seat_boxes.ref_tokens`). Typed `show me pr 712` finds the box the same way.
- **seat:** the chain's `answered N, escalated M` summary is said alone as "The chain answered N and escalated M." and is not flagged `Heads up:` before a bare count; an escalation still counts as a problem for reassurance, so no `No rush.` follows it, and the escalated piece's own box carries the flag (PR 147).
- **seat:** `No rush.` is said at most once per turn: a later page (`more?` or `go on`) of a turn that already said it leaves it off (`compose(rush=False)`) (PR 147).
- **seat:** a name keeps its capital and a draft is not a task: the sentence only lowercases a first word that is a known common word (`the`, `both`, or a task verb such as `ratify`), so `Tony (draft)` is no longer said as "Also, tony (draft)."; "You need to <verb>" is said only of a value that starts with a task verb, and a waiting draft that needs you reads "Tony (draft) is waiting on you." (`seat_boxes.lead`, `is_verb_phrase`) (PR 147).
- **seat:** draft pairs and lists have a verb and keep the `(draft)` marker, after the sketch: "Tony (draft) is waiting.", "Both drafts are waiting: X (draft) and Y (draft).", "The drafts are waiting: X (draft), Y (draft) and Z (draft)."; a waiting draft is never calm, so no `Looks like` or `No rush.` is said over one (`Box.role == "draft"`) (PR 147).
- **seat:** a counted `more` box is said apart as a count, never paired into a decided or changed fact: "10 more sealed are in the store.", "1 more draft or change is in the store." (it used to read "me hago cargo → I understand and 10 more sealed are both decided"). The seat marks these boxes by what the reader built (`Box.role` `more`, `draft`, `count`, set in `grove/seat_nestor.py`), not by their words; the store's count is its own sentence (PR 147).
- **seat:** the store's count and a `more` box are never a `show me` ref: `ref_tokens` is empty for them, so no `[show me 14]` chip is built from "14 sealed, ..." and `show me 14` does not open the count box (it still opens by its own box id) (PR 147).
- **seat:** `where are we` takes two `more?` presses on the shoebox instead of six: page one is the count plus the first four open items (waiting drafts, then refusals), and a store turn pages four boxes at a time (`STORE_PAGE`); the chain's two-box `PAGE`, `more?`, chips, follow-ups, ordinals and "as noted at" replay are unchanged (PR 147).
- **seat:** `show me 14` (or `open X`, `show X`) after a turn, when no shown box answers to it, no longer falls through to the chain and an `empty_scope` escalation: it is a follow-up that found nothing, so code says `Nothing I showed answers to "14"; I showed: b5, 712, b1, 127 and 1 more.` (on the store, the boxes' ids) (the human's words quoted exactly, at most four refs or box ids, the rest counted), with no model, no `api.escalate` and no row. This holds only when X reads as a reference: a number, an id-like token (`PR 712`, `#714`, `ABC-123`, `pull request #714`), a box id (`b4`, `n4ee2a`), an ordinal (`the 5th one`), or a phrase of at most two words (`the stack`); a longer phrase that reads like a task (`show me the tests that failed`) still goes to the chain, as does any `show me X` before a turn (`seat_boxes.looks_like_ref`, `REF_WORDS`, `Seat.unmatched`, `Seat.follow_up`); `help` says so.
- **seat:** a run of three or more decided boxes says so ("a → b, c → d and e → f are all decided.") instead of ending with no verb, as a pair already does (`seat_boxes._run`) (PR 147).
- **seat:** a run of three or more changed or routine boxes ends with a verb too, as a pair and a decided run do: "PR 1, PR 2 and PR 3 are all open." when every value ends in the same word (the word is theirs), else a fixed neutral word, "... are all changed." / "... are all routine." (`seat_boxes._run`, `RUN_VERB`); a draft run keeps "The drafts are waiting:".
- **seat:** a pair of changed or routine boxes with no status word in common ends with a verb too, as a pair of decided or blocked boxes does: "PR 1 open and tests ok are both changed." / "... are both routine." (it used to read "both A and B" with no verb); a shared last word is still theirs ("PR 0 and PR 1 are both open."). The pair reads the same fixed words as a run (`seat_boxes._pair`, `RUN_VERB`), and the store's count (`role="count"`) is never grouped into a pair or a run, as a `more` box is not: it is said on its own (`seat_boxes.compose`).
- **seat:** the opening and closing sentences are not said twice: the `resume` and `still pooled` cards at start, and the `pool` card and an empty `deposit` at check-out, keep their cards (populated, empty and unreachable stay three visible states) but lose the plain code line the sentence already covers ("Still pooled is empty: nothing pooled from earlier runs." before "Morning. ...; nothing is pooled from earlier runs."; "Deposit is empty: the pool is empty." before "Nothing stays pooled for next time."); an unreadable read is still said in words exactly once, and the reason stays on its card. A resume that cannot be read and ends the run before any opening is still said in its plain line (PR 150).
- **seat:** the chain's `answered N, escalated M` summary is a count box (`role="count"`, as the Nestor store's count is) and is said on its own, never grouped into a pair or a run with a piece: "Looks like the chain answered 1 and escalated 0. Local: d. No rush." replaces "Looks like answered 1, escalated 0 and local: d are both routine. No rush."; pieces after it still pair by their kind's verb ("Oh, and local: d and d0: d are both routine.") and the count is still never a `show me` ref (PR 150).
- **seat:** the opening names when the human sealed, from `api.resume`'s `sealed_at` (the seal row's own stamp, UTC with an explicit `Z`): "Picking up from the snapshot you sealed on 12 October (serve:9439efca, rows up to 41); 2 proposals still pooled from earlier runs.", "earlier today" when the stamp's date is today's, the year added when it is not this year's. The date is read as the record wrote it, not converted to a local zone, and never taken from the clock (the clock only picks "earlier today" over the date); an older willow-bot with no `sealed_at`, or a stamp that is not the record's form, keeps "the sealed snapshot serve:9439efca (rows up to 41)" with no date and no crash (`seat_boxes.sealed_on`) (PR 150).
- **seat:** a pair or a run of changed or routine boxes says a shared last word as its verb only when that word is a status word (`seat_boxes.STATUS_WORDS`: open, merged, closed, blocked, waiting, pending, failed, passed, done, sealed and the like); free text that ends alike, "local: a short answer and local: another answer", now reads the fixed word ("... are both changed." / "... are both routine."), not "are both answer" (`seat_boxes._shared_status`, one rule for `_pair` and `_run`) (PR 152).

## [0.19.0](https://github.com/willow-memory/willows-grove/compare/v0.18.0...v0.19.0) (2026-10-11)


### Added

* **seat:** bot-venv default, ratatosk beside python, 300s say timeout ([e507417](https://github.com/willow-memory/willows-grove/commit/e5074178fff126a6ba0750ba7fcfb86b7e656c16))
* **seat:** default to the bot venv, resolve ratatosk, raise the model timeout ([#139](https://github.com/willow-memory/willows-grove/issues/139)) ([07bd745](https://github.com/willow-memory/willows-grove/commit/07bd745a4e10b22dac455bdfb883ca76adfa1d37))

## [0.18.0](https://github.com/willow-memory/willows-grove/compare/v0.17.0...v0.18.0) (2026-10-09)


### Added

* **seat:** a local model says the reply sentence and code checks it ([121dccf](https://github.com/willow-memory/willows-grove/commit/121dccf2a710c764f55771ef8014de11c479be7e))
* **seat:** a quoted number still comes from a box; fail closed on unread scripts ([a281c7f](https://github.com/willow-memory/willows-grove/commit/a281c7f1c0378a2133f6dc1f16a7fa9ed080438a))
* **seat:** the model says one sentence, code checks it against the boxes ([#137](https://github.com/willow-memory/willows-grove/issues/137)) ([1af5cb8](https://github.com/willow-memory/willows-grove/commit/1af5cb8370efb9a809250cd12c5478781934c19d))

## [0.17.0](https://github.com/willow-memory/willows-grove/compare/v0.16.0...v0.17.0) (2026-10-09)


### Added

* **seat:** the seat prints the deterministic box stream ([c49a33f](https://github.com/willow-memory/willows-grove/commit/c49a33f858f48a3b4ccdc0377ee95d9435627238))
* **seat:** the seat prints the deterministic box stream ([#135](https://github.com/willow-memory/willows-grove/issues/135)) ([83a3226](https://github.com/willow-memory/willows-grove/commit/83a3226570d100d1fdeb0b45c6b51574ebb2562e))

## [0.16.0](https://github.com/willow-memory/willows-grove/compare/v0.15.0...v0.16.0) (2026-10-09)


### Added

* **seat:** the seat pools and deposits, it never seals ([944cfa1](https://github.com/willow-memory/willows-grove/commit/944cfa1a5af60579668a901e9e9a7f1dbecc2843))
* **seat:** the seat pools and deposits, it never seals ([#133](https://github.com/willow-memory/willows-grove/issues/133)) ([fbc114c](https://github.com/willow-memory/willows-grove/commit/fbc114c6a35a80be4aa0740e0f84048ee88824b6))

## [0.15.0](https://github.com/willow-memory/willows-grove/compare/v0.14.0...v0.15.0) (2026-10-09)


### Added

* **seat:** the desk's CLI seat, the one script at a terminal ([378f5ae](https://github.com/willow-memory/willows-grove/commit/378f5ae1cf04c9d7493f81bfda8aff2be2880380))
* **seat:** the desk's CLI seat, the one script at a terminal ([#131](https://github.com/willow-memory/willows-grove/issues/131)) ([b66b6b7](https://github.com/willow-memory/willows-grove/commit/b66b6b747fc79ad209c2c43ea89b3650018a98cb))

## [Unreleased]

### Added

- **one-script:** deterministic P1 reconcile grader + test, and the 2026-10-08 Haiku fold (PR 130)
- **seat:** the desk's CLI seat (`scripts/grove-seat`, `grove/seat_cli.py`): the one script at a terminal beside the web and APK; flowering turns go through Rat's ladder (`ratatosk --onescript --class flowering`, willow-memory/ratatosk#85) (PR 131)
- **seat:** the CLI seat pools its proposals and deposits them at close-out (ProposeOnly), with no inline seal (`grove/seat_cli.py`, `tests/test_seat_cli.py`) (PR 133)
- **seat:** the CLI seat prints the deterministic box stream, mirroring `box-stream-v1.3`: box cards, the pile header, three states never collapsed, who-wrote-it, `more?`, chips and asked-again, plain ASCII under `NO_COLOR` or a non-tty; a raising `api.pooled` at close-out is now `unreachable`, not a traceback (`grove/seat_boxes.py`, `grove/seat_cli.py`, `tests/test_seat_cli.py`) (PR 135)
- **seat:** the CLI seat's reply sentence is said by a local model (`qwen3:4b` on the Ollama loopback, an injected `say`) and checked by code (every cite served, every box cited, nothing the boxes lack, the human's words quoted exactly); a failed check strikes it and code's sentence stands, an unreachable model is an `unreachable` card and the code sentence; Willow voice on the glue words only; `api.checkout` raising is `unreachable` not a traceback; `No rush.` follows content, not kind; `scripts/grove-seat` defaults to the `willow-mcp` venv ahead of the bot venv (`grove/seat_say.py`, `grove/seat_cli.py`, `grove/seat_boxes.py`, `scripts/grove-seat`, `tests/test_seat_cli.py`) (PR 137)
- **seat:** `scripts/grove-seat` defaults to the bot venv again (`GROVE_VENV`, then `$WILLOW_HOME/venvs/willow-bot`, `./.venv`, `python3`; the mcp-venv rung is gone), the seat resolves `ratatosk` beside `sys.executable` (PATH fallback) for both escalate and flowering, and the qwen3 say timeout is 300s, overridable by `GROVE_SAY_TIMEOUT` (`scripts/grove-seat`, `grove/seat_cli.py`, `grove/seat_say.py`, `tests/test_seat_cli.py`) (PR 139)

## [0.14.0](https://github.com/willow-memory/willows-grove/compare/v0.13.1...v0.14.0) (2026-10-08)


### Added

* **demo:** split the box stream sketches into a demo Grove serves ([ed10c54](https://github.com/willow-memory/willows-grove/commit/ed10c54582ceb7f6134908123aa51bef07ca42ba))
* **demo:** the Assembly for serious readers, with Publius; the Bell a side piece ([698b7f4](https://github.com/willow-memory/willows-grove/commit/698b7f41faae6e6f54e6580295a4a1143a622a7c))
* **demo:** the Assembly of Groves, a UN-style session on the real one script ([f7ff5e5](https://github.com/willow-memory/willows-grove/commit/f7ff5e5209a4e200e5b876f1eee31c70e79f75ca))
* **demo:** the box stream demo, from chat to three lives, Jeles and the intern's desk ([#128](https://github.com/willow-memory/willows-grove/issues/128)) ([9e164f5](https://github.com/willow-memory/willows-grove/commit/9e164f5d50c3b28a793e632209996d23d4f9088d))
* **demo:** the Liberty Bell rings, grudgingly, at the Assembly of Groves ([02ace97](https://github.com/willow-memory/willows-grove/commit/02ace970653fa8616d97e6b420545a115cfd2cc0))

## [0.13.1](https://github.com/willow-memory/willows-grove/compare/v0.13.0...v0.13.1) (2026-10-07)


### Fixed

* **templates:** copied links still resolve; the tests read UTF-8 ([b6b1f6f](https://github.com/willow-memory/willows-grove/commit/b6b1f6f3a1d67117f576583e22bf6887e33f529a))

## [0.13.0](https://github.com/willow-memory/willows-grove/compare/v0.12.2...v0.13.0) (2026-10-05)


### Added

* **design:** the bare hook, and the hook on two foundations ([a6a2fa3](https://github.com/willow-memory/willows-grove/commit/a6a2fa31e77558d0361449599a9109376d5a69ac))


### Fixed

* **design:** the one hook never fails open ([aea0c64](https://github.com/willow-memory/willows-grove/commit/aea0c64d022728fc4439780affb8608f7d687037))

## [0.12.2](https://github.com/willow-memory/willows-grove/compare/v0.12.1...v0.12.2) (2026-09-30)


### Fixed

* **deps:** raise cryptography, aiohttp and starlette floors above the 2026 CVEs ([#97](https://github.com/willow-memory/willows-grove/issues/97)) ([7005893](https://github.com/willow-memory/willows-grove/commit/70058935e168910d01aa6bc84ccf9596bffb828b))
* **deps:** raise floors above the 2026 CVEs (starlette, cryptography, aiohttp) ([3317ad8](https://github.com/willow-memory/willows-grove/commit/3317ad8ef00c01e07e8f609918942c0057290426))
* **deps:** raise the same three floors in requirements.txt ([c70c3e8](https://github.com/willow-memory/willows-grove/commit/c70c3e8d8589937da747d9820fc3c265ede5aa9d))

## [Unreleased]

### Changed

- **demo:** `web/demo/box-stream/`, served by Grove at `/web/demo/box-stream/index.html`: every box stream sketch in one demo with an index. The chat as a conversation (v1.2) and a repeated question shown again with its time (v1.3); the dispatch rail and envelope panel as box streams; the lives from Nestor's demos (Big Jim, the shoebox, June after the Bombardment); two groves linked; Jeles, real and simulated on the three lives (`jeles-lives-corpus-2026-10-08.json`); and the intern's desk with real early-October 2026 headlines. The sketches moved here from `docs/design/one-script/`. Sketches, not Grove code: no model runs and the checks are written in. (PR 128)
- **docs:** `docs/design/one-script/box-stream-surfaces.md`: which parts of the Grove UI can run as a box stream (six fit fully, five take boxes without narration, three not at all) and the order to take them; `local-flow-and-ui.md` §5 records each sketch's decisions and findings. (PR 128)
- **docs:** `docs/design/one-script/box-stream-v1.1.html`, the box stream v1.1: sentences that use only what the boxes hold, the human line drawn plain and the sentence labelled agent with its model, a fifth check (the human's words quoted exactly), check chips labelled as example results, and a time stamp per turn; v1 kept as it was. (PR 127)
- **docs:** `docs/design/one-script/box-stream-v1.html`, the box stream v1: a clickable sketch of Grove chat for small local models, where served boxes stream from the pile into the chat, a small model says them in one sentence and code checks it; linked from `local-flow-and-ui.md` §5. A sketch, not Grove code. (PR 127)
- **docs:** one-box grid rows JE–JI, `docs/design/one-box/ui-apk-review-2026-10-08.md` with its map and snapshot: the UI and APK review run checks first, the phone only proposes, the one script's box flow and willow-mcp PR 712, and chat for small models as five served boxes said in one sentence; relay Baton 9, next free row JJ. Agent-reported; every box unattested. (PR 127)
- **docs:** `CLAUDE.md` rule 14 (was 7): search local documents before the internet; a document the operator asks for exists, so find it locally first. (PR 118)
- **docs:** `CLAUDE.md` rule 15 (was 8): no leading questions at the end of an output; end on the result. (PR 118)
- **docs:** `CLAUDE.md` rule 16 (was 9): output is a README-style Markdown document with numbered sections and a contents line at the top; questions and comments go at the bottom. (PR 118)
- **docs:** `docs/design/agnostic-rules.md`: every rule in force, agent- and system-agnostic, split only by who set it (human or agent); listed in `docs/INDEX.md`. (PR 118)
- **docs:** `CLAUDE.md` rule 17 (was 10; H10 in `agnostic-rules.md`): diffs shown in Markdown when 500 characters or less, else document name and section number; a shown diff is cited by label ("see Table 3"), not "below", and captioned above with file, section and subsection. (PR 118)
- **design:** the one-script code (`onescript/` and its tests, `hook.py`, `foundation/`, `scripts/`, `deep_thought.py`) moved to willow-bot `one-script/` (willow-bot PR 88, under D2) and is removed here; the design docs stay, and the one-script README points at the new home. (PR 122)
- **design:** serve, the fourth piece. `onescript/serve.py` writes one file holding only the tables in a scope the human sealed: a stack of who/what/when/where piles whose receipts are checked against the chain, proposed on a card that lists the joins the model could make. The model reads a view (the four W's and a named payload; row numbers, hashes, digests and receipts stay in the record), by ids keyed with a serve key made fresh at each check-in, with one fixed return line. Every record row now carries `where`. `hook.py` allows Read only on the served file. Q19 accepted. (PR 121)
- **governance:** constitution Draft 0.9. The ten 2026-10-02 amendments (renumbered IV.7, IV.8, VI.6 where 0.8 had taken the number), the neutral-language proposal merged three ways onto 0.8 (*fleet* becomes *system* in the body; 0.8 stands where it had settled a point), and the outside pass (Ground ages, capacity is not merit, the Hold, Escalation Budget and backpressure, unanimity recorded, a missing coverage report). None ratified; Article 0 and the Preamble unchanged; the coverage test's clause count moves from 51 to 64. (PR 112)
- **docs:** the one-script README gains four new sections: how the tables group by who/what/when/where (with the `where` gap named — only `write` rows carry `path`); the escalation ladder for fuzzy W-matching (exact hash → code → nomic embedder → small model → cloud → human, each rung writes back by hash); who wrote it (the model writes markdown, the human doesn't — verified on this session's own transcript with `md_split.py`); the shared phrases across 33 documents ("fails closed" leads at 9); and the table-only rule (all model output goes into the session's table; prose that doesn't fit any column gets a `kind = note` row, never free text below). Three new stdlib-only scan scripts: `four_ws.py` (W coverage across 260 tables), `md_split.py` (markdown vs plain by role in a transcript), `shared_phrases.py` (phrase frequency across a doc tree). Agent-reported; not ratified as a build. (PR 111)
- **docs:** the one-script README gains the stack and the security core. The stack lays the hashing handoff, the one-script docs, the operator's words and the flowering experiment over each other; the five tallest rows read as picture, cite, seal. The security core: the model is served only in-scope hashed points and returns only proposed rows, code fills every box, and the human seal is the only write; with a leak table, the rule that a seal binds to one hash, and prior art read from abstracts (gap f8680acc08e6, open). Agent-reported, not ratified as a build. (PR 106)
- **docs:** Kaggle escalation benchmark Day 3. `docs/design/one-script/posts/` holds the published Day 3 DEV post source (the floor across 12 hosted models, two-run consistency for four frontier models, and the infrastructure bugs that looked like results), its cover prompt, and the dataset metadata patch applied to the Kaggle dataset. `day-3/predictions.json` retracts P2's "grade": the desk had recorded a late-night line as the operator's grade and the Day 2 post carried it in the operator's voice; P2 is ungraded. (PR 104)
- **hooks:** `_nestor_ask` keeps populated/empty/unreachable distinct; `before_stop` composes lint then green-claim gate; sealed rows and `wiring.json` match; client-parity test pins the contract. (PR 101)
- **mcp template:** desk `nestor` keyring paths point at the vault operator-box ring (`config/verifiers.json`), and `JELES_CORPUS_APP_ID` is set; Grove seal-prove worksheet under `seat/willow/jeles-intake/`. (PR 99)
- **docs:** `forge-convergence.md` §6a is code-first. Python does the growth and local models are the escalation, per the sealed code-first ruling. StorySession is recorded as built (the fourth adapter; only a named human's `seal()` passes a decision beat), with durable persistence and the store seam marked not built. The fleet-campaign forecast engines are recorded as stdlib Python with backtests. T3 and T4 now say what remains. §6a also records UTETY's learner model, the story-timeline suggestion pipeline, willow-bot's `chain_act` as the escalation ladder and OakenScrolls as the canonical calibration math; T6 says the public the-binder has no recognition code; T7's subject is staged (fictional characters first, then the operator behind a `subject_consent` grant); §9 row 11 is settled (the Table keeps the ai-game-master chain). (PR 93)
- **docs:** stale claims corrected from the convergence docs survey. `docs/INDEX.md` stops listing `design/forge-convergence.md` as not in this tree, and gains the 14 unlisted design docs and a proposals table. The manifest-grant-federated-tools and node9-shadow-mode proposals now say built (both are in willow-mcp master). The mcp-jobs-ladder test plan notes `allow_localhost` is retired. `forge-convergence.md`'s status line and its step-0 gate now say what has landed. (PR 94)
- **deploy:** retire `allow_localhost` from the Kart sandbox template — `deploy/kart-sandbox.template.json`'s `localhost_tier` note described it as a working local-only mode; it is retired (governance record `retire-allow-localhost-2026-09-23`, amends sealed 9fe5e179) and refused by name in both willow-mcp and kartikeya. (PR 86)
- **deploy:** the Kart sandbox template stops binding anything the host later executes. `/run/user` and `XDG_RUNTIME_DIR` are unbound, `~/.local` is read-only, `.git/hooks` and `.git/config` are overlaid read-only, and `.npmrc` is dropped (Ada audit 385FBA31). The loopback-tier note cites its sealed shape, pair 3ef0211f. (PR 88)
- **mcp template:** the desk's `nestor` entry sets `WILLOW_HOME`, `WILLOW_MCP_APPS_ROOT` and `WILLOW_STORE_ROOT`, so jeles-corpus stops falling back to the tombstoned `~/.willow` (gap 02a4de282956). (PR 88)
- **jeles-intake:** two seed pairs corrected: the fifth federation key names which tools need a lease, and the Jeles app id is `jeles-corpus`. (PR 88)
- **docs:** `forge-convergence.md` §6 step 0 is struck, and the flowering experiment's status line and §9 verdict record pair bfe001f7 as sealed ("Step 0 is struck"). §13's open list strikes the two items willow-bot #79 closed (G2 cite scoring; the prompt and the pool agree), audited by Loki F48383F4 and B2FF599B. (PR 90)
- **docs:** `forge-convergence.md` §6 step 1 ("Papers agree with the code") is struck, and §9 row 10 is settled: willow-mcp's `human_required_*` verbs write through `forge.human_loop`. willow-mcp's `willow-gate-seam.md` status and the Forge's `the-session-entry.md` pointer land in their own repos. (PR 91)

### Added

- **templates:** the cross table. `templates/cross-table/cross_table.py` (stdlib, deterministic) fills a grid of addresses by copying passages from source files, never writing them; `measure` reports what each box holds against a snapshot, `drip` cuts a fat box into clauses, `link` writes a crosswalk between grids, and rows run past Z without renumbering. A copied passage keeps its words, and its relative links are re-pointed from the source's folder to the document's, so they still resolve. The one-box grids built with it run through row IL (rules, boxes outside, crosswalk, drip, Gerald atoms, open branches, handoffs, Draft 0.9 coverage across the repos and at every branch head), with the relay that lets each session add the next rows. `governance/scripts/const_coverage.py` reads every spelling of a citation. `tests/test_cross_table.py` and `tests/test_const_coverage.py`, 25 tests. Agent-reported; not ratified as a build. (PR 119)
- **design:** the record's two remaining holes are closed. A tip the human seals (`Run.seal_tip`, proof from the human's key over the row number and its full hash) is kept outside the box in an anchor file beside the keys; check-in hard-closes when the chain no longer reaches it (rows cut), reaches it with a different hash (rows rewritten and rehashed), the anchor is missing while a seal row names a tip, the anchor is unreadable, or, where the human's key is present, its proof doesn't verify. A broken chain is never sealed, and an anchor inside the box is refused. A line in `record.jsonl` that isn't a row (not JSON, not an object, missing a stamp key, not UTF-8) is reported as a break by line number instead of crashing check-in. Rows after the last sealed tip stay open to a cut or a rewrite; the CLI has no seal command yet, so its check-in screen says `anchor: never sealed`. 15 new tests; 11 mutants, each failing at least one. (PR 115)
- **design:** the one script runs. `python3 -m onescript checkin | turn "<bite>" | checkout` from `docs/design/one-script/` is one run across invocations: the record persists in the repo's git-excluded `.flow/onescript/`, and the HMAC keys sit beside it in `.flow/onescript-keys/` (0600; a keys path inside the box is refused). Every command first writes an `invocation` row naming the command, root, box, venv and the hash of each input it read (the constitution, the CI workflow, the script's own code), so a replay names the input that moved. The toolchain gate checks the tools in the bot's venv (`$WILLOW_HOME/venvs/willow-bot`, D2) against the CI pin, never whatever is first on PATH. A hard close holds across invocations: a breached check-in is recorded as a closed boot, `turn` refuses (and records the refusal) with no check-in on record or after a hard-closed one, and `checkout` rebuilds the boot report, grades, claims and acts from the record. The law's trace IDs are read as the constitution writes them (`CONST-0`, `CONST-0-1`, `CONST-I-1`). A keys file readable beyond its owner is refused. The tests gate never nests: an unguarded check-in → suite → check-in loop in an audit mutant took the box's memory (2026-10-06). First run on the box: probes 4/4 held, tests and freshness satisfied, one hard close (ruff 0.15.0 on Kart's PATH against the 0.16.7 pin). `onescript/tests/test_main.py`, 16 tests, each fix with a mutant that fails it. (PR 114)
- **docs:** one hook across every CLI. `docs/design/one-box/research-2026-10-06.md` holds the pre-tool gate matrix for 22 agent CLIs, each claim tagged by source (vendor docs read directly, the vendor's official repo with file:line and commit, or search extract only), the polyhook re-check (reference only: an "ask" becomes allow, unknown callers fail open, Cursor and Windsurf blocking broken), what `hook.py` covers unchanged (Claude Code; Factory, Qwen and Junie pending one captured payload; Codex a trap), and corrections to earlier one-box notes. Not wired. (PR 112)
- **design:** `onescript/xref.py`, the cross-reference index. Each tracked file arrives with git's blob id, the same id recomputed from the bytes on disk, and the system's own full SHA-256; a mismatch is recorded and left out. Ids, links, `file:line` citations and commit SHAs are checked across the repos, written through the record, and sliced for people. Same repos at the same commits give the same bytes. 12 tests, on Python 3.9 and 3.11. (PR 112)
- **docs:** the bare hook. `docs/design/one-script/hook.py` lets the model read and asks the user before a write; every other tool is denied, including ones that don't exist yet, and unreadable input exits 2 so it never fails open. No hashing, record or vault check (the vault is handled separately). `foundation/` compares the earlier record-lookup hook on CPython 3.9.0 (signature-verified tag) and 3.16.0a0: 2,293 identical hashes, identical `realpath`, every difference an integer over 4,300 digits and failing safe. The Day 5 outline in `next-pile.md` is a desk draft in the operator's register. Not wired into any settings. (PR 107)
- **docs:** the one-script pile. `docs/design/one-script/` gains `deep_thought.py` (a read-only probe that carries the sealed D1, D2, D9 and Q13 and prints the box against them as the morning screen), the capability door in `onescript/gate.py` (run once, for the session, permanently, or no; only a seal proof from the human's key answers a card) with 24 tests, the flow scripts (`scripts/flow/`, session maps and the cross-session merge), `scripts/scan/pr_scan.py`, the prompt-arms table, the Day 3 cover prompt, and `next-pile.md` through 2026-10-03. The 2026-10-05 hashing session handoff is moved in, and the README now opens with its two steps (take a picture, then compare), maps the 1992 Tripwire against the add-backs (explain, accept, seal), and lists what the box already has. One-box is expanded from the box (outside pass, partition, join), and `deploy/` gains an experiment-only telephone-game socket unit template. A private person named in `next-pile.md` is redacted. Nothing built into a runtime or sealed. (PR 105)
- **docs:** `docs/design/one-script/`, four draft proposals from session 2026-10-02, each in its own commit: the workflow (boot to the reverse pass); the runtime as one script (seven parts by purpose plus `run`, the stamp, citations, the close's four gates with push as a grant card; three more layers: claims, boundaries, mandate); a runnable stdlib skeleton with 53 tests that carries the four gates (tests, toolchain, freshness, reachability) and three layers (claims checked against the record; push cards grouped by provenance; every act traced to a human mandate); constitution amendments built on Draft 0.7, to be redone against 0.8; and `incoming/`, three outside passes (an Opus session's six proposals against Draft 0.8, a cold Haiku session's three, and a pointer to "Basins, Not Walls") reconciled against the record, with queue age, unknown enforcement status and recorded dissent adopted into the skeleton. Nothing built into a runtime or sealed. (PR 103)
- **docs:** `docs/design/one-box/`, the one-box build plan (proposal, not ratified beyond landing): one local runtime (Rat) behind every front end over a peer-checked Unix socket, with the box rules (every gate fails closed and loud; reading is open and saving is guarded; egress means outbound; the willow seat is wherever the human is; no front end is primary; a standing grant is the human's auto-merge), ten operator decisions, phases 0–9, and an adopt-don't-write table. It also adds the review of willow-mcp #706 and Grove #101, the session's discussion record, the web research (a front-end hook matrix, ACP, licences, ingress) and tested sketches. (PR 102)
- **governance:** proposal `2026-09-30-kaggle-escalation-benchmark.md` publishes the jobs-ladder plan's escalation column as a public Kaggle benchmark for the DEV × Kaggle challenge (closes 2026-10-11). Fixtures are synthetic and public-domain only, and a local-ladder arm runs beside Kaggle's hosted models. Four operator decisions and four pre-registered seat forecasts are included. (PR 95)
- **docs:** `forge-convergence.md` §6a, "The Table: proving it for a human on local models", seven steps (T1–T7) that run before §6 step 2. It moves the AI-Gamemaster test up from the flowering experiment's far-horizon §11: fix the story's one-hit invariant, grade the fleet-campaign forecast already due, play StorySession on the story (a world file, a durable seal, narration only at escalation points), the forecast lane into OakenScrolls calibration, outside facts from local almanac-data first and Jeles under a lease second, hornbook at the table, then an operator-signed test. Run as fiction, in isolation, with no PII in any push. (PR 92)
- **seat/willow:** flowering step 0 is run and struck. Adds the v2 fixture set, the design-doc vs Nestor-seal G5 batches, D0, local-tier and cloud-arm run rows, and the operator's blind rubric sheets, plus the §9 verdict (keep the tree, sealed bfe001f7). The v1 fixtures, generator and aggregator are kept as the record of the superseded run. (PR 88)
- **docs:** the willow-bot box spec (ideas #33) and the manifest-grant-federated-tools and node9 shadow-mode proposals. (PR 88)
- **docs:** the flowering experiment gains §13, the first runs of the deterministic chain (D0, then local, then flowering): 15/15 v2 acts grown at cloud/act 0.0 on the GPU after the cite-example fix, with the operator's G3 rubric still pending. The three chain runs are committed under `seat/willow/experiments/flowering-2026-09/runs/`. The v2 README notes the chain results and that its item 3 is superseded. (PR 90)
- **docs:** `every-seat-hears-the-grove.md`, queued as `forge-convergence.md` §6 step 10: grove traffic for any seat, not only an IDE seat with a Monitor. willow-mcp holds one `grove_events` verb and each seat's cursor, Ratatosk reads it between model calls, and Grove's `/events/<seat>` stream and the reinject row read through the same cursor. Forge project: fleet-spine, joint 8. (PR 90)

### Fixed

- **design:** the one script's leftovers from PR 114 (gap f58dd6dac53a). A check-in nested inside the tests gate says so on its screen. A breached check-in records every probe's result, so checkout no longer reads `probes 0/0`. A turn after a checkout is refused, and recorded, until a new check-in opens. Checkout's boot report keeps the `at` of the last reconcile, as boot wrote it. Every boot row's `options` is pinned by a test (none when open, the four when hard-closed, `stop here` on a breach). 5 new tests; 5 mutants, each failing at least one. (PR 115)
- **design:** `md_split.py` no longer counts a background task finishing as the human typing. `<task-notification>` turns are now classed as harness; on the finished transcript of desk session 024cf297 (2026-10-06), typed prompts went from 27 to 17 (exactly the operator's prompts) and harness from 0 to 10. `onescript/tests/test_md_split.py` pins the four classes (typed, harness, attached, model); with the fix removed, 3 of its 5 tests fail, and removing any one harness opening fails at least one. `next-pile.md` gains two 2026-10-06 sections: the pile caught up through PR 112, and the day's pieces replayed on the box (every miss was an input the piece didn't declare). (PR 113)
- **design:** `record.py` keeps every hash at full width: `h16` (SHA-256 cut to 64 bits) is now `h256`, and a hash cut back to 64 bits reads as a chain break. One of the three `record.py` holes the Day 5 handoff named; the other two stay open. (PR 112)
- **seat/willow:** the flowering aggregator's G1 check no longer passes an F-negative that names a seat. When the gold is `ESCALATE`, an answer naming any seat the brief offered fails `names_no_offered_seat`, even if it also says "escalate" (gap 0871bb83d7d5). Seats match as whole words. (PR 89)
- **tests:** `tests/test_flowering_aggregate_g1.py` pins that G1 rule against the real S-growth-16 fixture: a seat plus an "escalation note" fails, a clean escalation passes, a non-ESCALATE row is unchanged (gap 0871bb83d7d5). (PR 96)

## [0.12.1](https://github.com/willow-memory/willows-grove/compare/v0.12.0...v0.12.1) (2026-09-22)


### Fixed

* **serve:** declare a WebSocket library so /events/{seat} can upgrade at all ([e95b702](https://github.com/willow-memory/willows-grove/commit/e95b70293884f988b11876128009f7af00db7491))
* **serve:** grove-serve-run execs anyway when its self-install fails offline ([78defab](https://github.com/willow-memory/willows-grove/commit/78defab90486aa135a6a45641d52c57840fb3b62))
* **serve:** the served page can upgrade a WebSocket — declare websockets, self-heal the venv, say when the stream is dark ([#83](https://github.com/willow-memory/willows-grove/issues/83)) ([5e8d54b](https://github.com/willow-memory/willows-grove/commit/5e8d54b85caf64c9d653665b7a52b778620aaea5))

## [0.12.0](https://github.com/willow-memory/willows-grove/compare/v0.11.0...v0.12.0) (2026-09-22)


### Added

* **grove:** serve the seat's per-seat event stream over WebSocket ([0378c47](https://github.com/willow-memory/willows-grove/commit/0378c47a3dd86530112a0154a4b247d0b137cacb))
* **serve:** a per-seat event stream on the served page — the seat subscribes instead of polling ([#81](https://github.com/willow-memory/willows-grove/issues/81)) ([4b81fb2](https://github.com/willow-memory/willows-grove/commit/4b81fb2b22cb676246f471a95f6611e057732254))


### Fixed

* **grove:** events stream survives a Postgres outage and delivers a full backlog ([1e70c98](https://github.com/willow-memory/willows-grove/commit/1e70c98dc4ca6a25fcd80c6f8ae9c9be704b546a))

## [0.11.0](https://github.com/willow-memory/willows-grove/compare/v0.10.0...v0.11.0) (2026-09-20)


### Added

* **deploy:** track the Kart mount policy as a portable template ([481baa6](https://github.com/willow-memory/willows-grove/commit/481baa622434a56edd0393ab5d5f6f8e7631ce39))
* **deploy:** track the Kart mount policy as a portable template ([#34](https://github.com/willow-memory/willows-grove/issues/34)) ([736a588](https://github.com/willow-memory/willows-grove/commit/736a588e45adca2bea2d84a939cacfe4ab4f4a29))
* **envelopes:** relocate live registry into the grove charter repo ([#42](https://github.com/willow-memory/willows-grove/issues/42)) ([54802f4](https://github.com/willow-memory/willows-grove/commit/54802f4899a4c52294a4f5a311f7c44eed1854b0))
* **envelopes:** relocate live registry into the grove charter repo. ([d1bc9bc](https://github.com/willow-memory/willows-grove/commit/d1bc9bcb7fbb0610e70e0404184fb1e3c09993e8))
* **governance:** register ratatosk as a fleet persona ([5a31ce2](https://github.com/willow-memory/willows-grove/commit/5a31ce2779163e7b75826b8f3565e1267ba50aa9))
* **governance:** register ratatosk as a fleet persona ([#56](https://github.com/willow-memory/willows-grove/issues/56)) ([2740fe5](https://github.com/willow-memory/willows-grove/commit/2740fe5d791cda97cfeadddc34e601418baa588c))
* **hooks:** Grove's hook manifest, and §8 check 1 against it ([397cea5](https://github.com/willow-memory/willows-grove/commit/397cea52135ebce402081d2f0782b64b64492d7e))
* **hooks:** Grove's hook manifest, and §8 check 1 against it ([#53](https://github.com/willow-memory/willows-grove/issues/53)) ([fb267d3](https://github.com/willow-memory/willows-grove/commit/fb267d320eda5174ec4839aaa9b610788cf69253))
* **journal:** C11 seam speaks MCP to willow-mcp ([#30](https://github.com/willow-memory/willows-grove/issues/30)) ([38c5331](https://github.com/willow-memory/willows-grove/commit/38c53315286cdb0895fde41228f8155988504e75))
* **journal:** speak MCP to willow-mcp instead of REST /tools/* ([ed5068a](https://github.com/willow-memory/willows-grove/commit/ed5068a5eba98920ea928b48eed83203d4bbdc3a))
* **seat:** land the Jeles intake packets and make federation consents readable ([043b6ee](https://github.com/willow-memory/willows-grove/commit/043b6eec0f7c35767468f3456dbfe6a67731b7b5))
* **seat:** polish Willow desk scripts and steward tooling ([a5d909d](https://github.com/willow-memory/willows-grove/commit/a5d909db9c8cd690004fa0a920d51d741c2db276))
* **seat:** polish Willow desk scripts and steward tooling ([#61](https://github.com/willow-memory/willows-grove/issues/61)) ([0c84a42](https://github.com/willow-memory/willows-grove/commit/0c84a425b5fc871195171382fc521a5d720f03cc))
* **seat:** prefer fleet venv willow-bot for pr-watch ([13de958](https://github.com/willow-memory/willows-grove/commit/13de958eba24bd1f5eec884b3436fdb04b979e65))
* **seat:** prefer willow-bot-steward for pr-watch ([ea8e7aa](https://github.com/willow-memory/willows-grove/commit/ea8e7aa4c4752d1f9454c74f4330eb9f38167866))
* **seat:** the Desk takes the head of the repo ([e199435](https://github.com/willow-memory/willows-grove/commit/e19943522b96b59e94dd4dc395e488a2e500ad54))
* **seat:** Willow desk home and Grove persona partition ([#37](https://github.com/willow-memory/willows-grove/issues/37)) ([77cf265](https://github.com/willow-memory/willows-grove/commit/77cf2654fd64d94c37ced7fa2e1edc24eaaf7df2))
* **seat:** Willow desk home; Jarvis is not a mode switch ([dd5ff4a](https://github.com/willow-memory/willows-grove/commit/dd5ff4a85d322ac1267aac14d7dbd63440d50e5e))
* **seat:** wire the Desk so the seat is chosen by where you open ([2d67189](https://github.com/willow-memory/willows-grove/commit/2d67189441b26d8c2437a6b943fe70441f0570d5))
* **seat:** wire the Desk so the seat is chosen by where you open ([#48](https://github.com/willow-memory/willows-grove/issues/48)) ([889a5d6](https://github.com/willow-memory/willows-grove/commit/889a5d69341c0d11f8065cd89c51e5168019dde7))
* **vault:** consolidate the stranded grove branches onto the operator box ([#46](https://github.com/willow-memory/willows-grove/issues/46)) ([b0b7d26](https://github.com/willow-memory/willows-grove/commit/b0b7d26a00f95c9d8b7fcfbee48e187ce92a8e4c))
* **vault:** follow the operator box for the store, the keyring and the trust root ([a00f5e3](https://github.com/willow-memory/willows-grove/commit/a00f5e31878851fec8fa5e25244dbf6820d5a266))


### Fixed

* **docs:** add PR 43 citation to CHANGELOG [Unreleased] bullet ([753a6a1](https://github.com/willow-memory/willows-grove/commit/753a6a12ce937a36199372635887b889b2cf2d95))
* **governance:** let the coverage report see every clause ([f7f3ae1](https://github.com/willow-memory/willows-grove/commit/f7f3ae116a7f260e167ecdc2ee8de36942e24abe))
* **governance:** let the coverage report see every clause ([#54](https://github.com/willow-memory/willows-grove/issues/54)) ([4e6576f](https://github.com/willow-memory/willows-grove/commit/4e6576f35353b926cc3ebd75842c666d3421bed3))
* **governance:** read the fleet roster instead of copying it ([1b4ecfd](https://github.com/willow-memory/willows-grove/commit/1b4ecfdf541f357ee2a4162fb25e867aa7cf6fc1))
* **governance:** read the fleet roster instead of copying it ([#55](https://github.com/willow-memory/willows-grove/issues/55)) ([b4e321d](https://github.com/willow-memory/willows-grove/commit/b4e321df2c585f37808ffa60faf8d3888a5a375b))
* **governance:** repoint two dangling persona canonical_file entries ([dc1468e](https://github.com/willow-memory/willows-grove/commit/dc1468ee3634f3fc0d92ef5ab9a8923d1e2e65f7))
* **governance:** repoint two dangling persona canonical_file entries ([#24](https://github.com/willow-memory/willows-grove/issues/24)) ([fdc64fe](https://github.com/willow-memory/willows-grove/commit/fdc64fe9035bfd60f45f9394bd2914a57282040a))
* **grove-dispatch-rail:** guarantee 28-char legibility floor on .action ([3019883](https://github.com/willow-memory/willows-grove/commit/3019883b72aeb94e595f8604018a0a687afaafea))
* **mcp:** move Grove MCP to 8767 to end the 8765 collision ([4cc7205](https://github.com/willow-memory/willows-grove/commit/4cc720579490eec9d9822808055456311ba15c87))
* **mcp:** move Grove MCP to 8767 to end the 8765 collision ([#36](https://github.com/willow-memory/willows-grove/issues/36)) ([39876c6](https://github.com/willow-memory/willows-grove/commit/39876c68fc786db9732bc17a325eb45c0523ec51))
* **seat:** bind a Grove sender in the probe instead of asserting on an unbound one ([b8059c5](https://github.com/willow-memory/willows-grove/commit/b8059c533644d2c919ee82af6f3a846ae4f51571))
* **seat:** keep nestor-grove-session and pin its argv to the template ([c354749](https://github.com/willow-memory/willows-grove/commit/c354749c6a1812a4fafd02dfad6dee2d64e24d5e))
* **stack:** the serve toggle installs 8767, and the unit gets a DSN ([983985c](https://github.com/willow-memory/willows-grove/commit/983985c9da07a09747794398b591b1be3e8e2e4b))
* **stack:** the serve toggle installs 8767, and the unit gets a DSN ([#50](https://github.com/willow-memory/willows-grove/issues/50)) ([f0b7615](https://github.com/willow-memory/willows-grove/commit/f0b76150e3c378f27360139c5d9970b11934a04d))
* **tests:** CI wrapper venv python and persona roster env isolation ([#28](https://github.com/willow-memory/willows-grove/issues/28)) ([98befdc](https://github.com/willow-memory/willows-grove/commit/98befdc9cdf20846b7126e0a706ead49ec4fa22c))
* **tests:** resolve venv python in CI wrapper and isolate WILLOW_HOME ([2cbe5a9](https://github.com/willow-memory/willows-grove/commit/2cbe5a9253ab19386a9363de2cb356c138e01b06))

## [Unreleased]

### Added

- **Forge convergence design — tree, experiment protocol, step 0 gate.**
  `docs/design/forge-convergence.md` §1.5 (one tree / one soil; growth vs
  flowering); pre-registered
  `docs/design/forge-convergence-flowering-experiment.md` (hypotheses T0–T6,
  chain-depth secondary, AI-Gamemaster theory bookmark). Step **0** blocks §6
  build PRs until the flowering-threshold test is run and signed. **§8
  pre-run sign-off** filled (T=70%, C=0.3, N=12, R0+R1, P-cloud, tier
  ladder, K=2); fixture home `seat/willow/experiments/flowering-2026-09/`.
  Jeles loopback probe gaps logged on the operator box (`a6d8ae37f8be`,
  `621488f2d6da`).

- **The served page declares a WebSocket library.** (PR 83) Measured
  2026-09-22T06:29Z: `grove-serve.service` reloaded
  onto #81's master and a harness Monitor's WS upgrade against a live
  `/events/{seat}` got `HTTP 404`, then close 1006. Nothing in this repo
  declared `websockets` or `wsproto` — uvicorn ships no WebSocket
  implementation of its own, so it refused every upgrade before
  Starlette's route ever ran; Starlette's `TestClient` serves WebSockets
  in-process and never needed either library, which is why the route's
  own 70-test suite was green while the live socket 404'd.
  `requirements.txt` and `pyproject.toml` now declare `websockets>=13.0,<17`
  (uvicorn's own default pick and floor — its `standard` extra pins
  `websockets>=13.0` — and the narrower choice over `uvicorn[standard]`,
  which would also add httptools/uvloop/watchfiles/python-dotenv/pyyaml).
  `scripts/grove-serve-run` now installs it on start if missing, so a
  re-render or restart self-heals a venv that predates this dependency.
  `grove_serve.py` gains `_ws_library_available()` — uvicorn's OWN
  resolution (`uvicorn.protocols.websockets.auto.AutoWebSocketsProtocol`),
  not a hand-rolled guess — and `/health` gains an `events` field:
  `{"state": "populated"}` or `{"state": "unreachable", "reason": "no
  websocket library"}`, three-state, never a silent 404; `run()` prints a
  matching warning at serve start when the library is missing.
  `tests/test_grove_serve_ws_dependency.py::EventsWsLibraryImportableTests`
  is a test that cannot pass without the fix reaching the interpreter
  under test: it asserts a WS library is actually importable via uvicorn's
  own lookup, so it stays red in any venv — including this Kart sandbox,
  network-isolated with no egress lease held for this dispatch — until
  something actually installs `websockets` or `wsproto` into it.
  Ride-along per Loki 1BA3415E: `scripts/grove-serve-run` no longer
  `exit 1`s when its self-install fails — this is the only place in the
  repo that installs code at runtime from a systemd unit, and under the
  unit's `Restart=on-failure`/`RestartSec=2` an `exit 1` here meant an
  offline box with a stale venv served NOTHING (HTTP included) and
  retried pip every 2 s, worse than the 404 stream it replaced; it now
  attempts the install, prints one line naming the attempt and why it
  failed, and `exec`s the server either way, so `run()`'s startup
  warning and `/health`'s `events` field carry the "page up, stream
  dark" state instead. `hooks/grove_hook.py::orient`'s boot-line probe
  now does a bounded `GET /health` (same 250 ms budget) instead of a
  bare TCP connect, and reads its `events` field: page unreachable still
  says "served page down"; page up but `events.state != "populated"`
  now says "stream dark: `<reason>`; reinject inbox is the path" instead
  of promising a Monitor against a route that will 404 every upgrade.

- **Grove serves a per-seat event stream.** (PR 81) Sealed pair
  `13330d1c` (2026-09-22): `grove_serve.py` gains a read-only Starlette
  `WebSocketRoute` at `/events/{seat}` on the existing loopback
  127.0.0.1:8766 host — no new port. A non-loopback client is refused
  before accept; an inbound frame is drained and ignored, never acted
  on. No identity on the socket: any loopback client can subscribe to
  any seat's stream by naming it in the URL — per-seat isolation was
  not asked for by this pair and is not achievable without one, so it
  is not claimed. The first frame is a three-state frame
  (`{"state": "populated"|"empty"|"unreachable", "reason": ...}`);
  the seat's unread tail (via a new `grove_reader.grove_events_since` —
  the same three sources `grove_inbox` reads: @mentions, bus-addressed,
  and the seat's own `#<seat>` channel, but as one ascending,
  `since_id`-bounded, `limit`-bounded query, re-paged until a page
  comes back short — i.e. caught up — rather than the "newest N"
  merge-and-cap `grove_inbox_bundle` uses for the desk pane) then
  streams as one `{id, channel, sender, content, at}` frame per row,
  oldest first, polled at a 2 s interval (LISTEN/NOTIFY is a follow-on).
  `since_id` resumes past what a re-armed Monitor already saw, and is
  bounded to a non-negative, in-range Postgres bigint — a malformed or
  oversized value is refused with a state frame naming the field, never
  forwarded to SQL. A reader failure mid-stream — including a Postgres
  connect failure, caught the same as a query failure — sends another
  `unreachable` frame with a type-redacted reason (never DSN/psycopg2
  text on the wire) and the socket stays open and re-probes rather than
  closing. `hooks/grove_hook.py::orient` (session_start) gains one boot
  line, only when a 250 ms probe finds the served page's own port
  answering — `arm a Monitor on ws://127.0.0.1:8766/events/<seat>?since_id=<n>
  (30-minute timeout, re-arm on expiry)` — naming `since_id` from the
  seat's existing Grove inbox anchor; when the page is down the line
  says so and names the reinject inbox as the path that still works,
  rather than telling the seat to arm a Monitor against nothing. The
  hook cannot arm a Monitor itself, and the reinject inbox line stays
  the fallback, not superseded. The writer half (the seal watcher
  posting to a seat's channel) is a separate willow-mcp packet.
  Reworked per Loki FA0EFB5F: F1 (a Postgres connect failure bypassed
  the route's `except Unreachable` entirely and closed the socket in
  silence — connection acquisition now happens inside
  `grove_events_since`'s own `try`, and the route also catches any
  non-`Unreachable` reader exception), F2 (the prior `grove_inbox_bundle`
  read kept only the newest 35 rows by id, so 60 unread on connect sent
  rows 26-60 and dropped 1-25 under `state: populated` — the new
  `grove_events_since` pages ascending with no such cap).

- **Reinject surfaces the seat's unread Grove inbox.** (PR 80)
  `hooks/grove_hook.py::reinject` (UserPromptSubmit + PreCompact) gains a
  fourth, conditional section under sealed pair `11ccb0f7`
  (seat-inbound-channel-2026-09-21): one line per unread item on the
  seat's Grove inbox since the session's anchor —
  `[grove #<channel> <sender>] <first 140 chars>`, oldest first, five per
  prompt plus an `… and N more — next prompt, or grove_inbox(since_id=…)`
  tail; the anchor moves only past what was shown, so a backlog pages
  across prompts rather than being consumed — or one
  `[grove unreachable: <reason>]` line when Postgres / willow-mcp cannot
  be reached within a 3 s budget. A quiet inbox emits nothing, so the
  hook stays byte-stable in the common case. Read-only: the hook never
  posts, acks or flags; it advances a local anchor
  (`$WILLOW_HOME/deposits/hook-state/grove-anchor-{session,seat}-*.json`)
  only after the lines are emitted, and leaves it untouched on
  `unreachable`. A new session inherits the seat anchor so a CI red that
  landed between sessions surfaces once; a first-ever run seeds at the
  current high-water mark and replays nothing. The seat's own posts are
  filtered out. `hooks/wiring.json` is untouched: its rows are the sealed
  record `governance/decisions/grove-hook-rows-sealed.json`, and the
  `reinject` row's `answers` text is the operator's to re-seal — this
  change is within that row's stated purpose ("the only mid-session
  surface for … what changed since session_start").

### Fixed

- **`check_changelog_bullet.py` test isolation from ambient
  `GITHUB_EVENT_PATH`.** (PR 79)
  `tests/test_changelog_bullet_check.py::_run_checker` now strips
  `GITHUB_EVENT_PATH` from the child environment (as it already stripped
  `GITHUB_BASE_REF`), so the release-please exemption added in PR 78
  cannot leak into synthetic-repo test cases whose whole point is to
  drive the checker's "no bullet, tracked-code change" refusal path.
  Caught by release-please's own regenerated PR #75 run on head
  `41d5ea4`: the workflow steps all reported `release-please PR exempt`
  correctly, then pytest failed `test_code_change_without_bullet_fails`
  because the checker read the CI's release-please event and returned
  exempt inside the pytest child. Same class of leak the persona test
  file already handled by stripping `GITHUB_BASE_REF`.

### Changed

- **willow-bot usable build brief — third-pass reconciliation.** (PR 78)
  `docs/design/willow-bot-usable-build-brief.md` moves to a 2026-09-20
  snapshot against willow-bot `22e51f8` (main, 0.2.0) and willow-mcp
  `89ae5e5` (master, 2.57.0). Four of the six second-pass "Open gaps"
  land in "Resolved records" (`acfd27ae3259`, `a6c0926d7e83`,
  `158600e03598`, `5ecb87cfdf56`); the two survivors (`4ef96ee6a3b0`,
  `83af08a4deda`) live outside either repo (Jeles/Nestor corpus, the
  operator's box). Build order steps 3–5 flip to BUILT with citations —
  voice head_sha (voice.py + fleet_bridge.py:248, willow-bot #28),
  `X-GitHub-Delivery` dedup (`delivery_dedup.py`, bot.py:74), the
  seat's status verb (`bot_status.py`, server.py:4935), the PR-update
  verb (`pr_update_executor.py`, Row 16), the explicit-ask surface
  (`gate_request.py`). Row 15 `unit.reload` (`unit_reload_executor.py`)
  and its seal-driven live-table sync (`seal_drain.py`, sealed
  `72292afd`) both landed; the gidgethub decision (`0031ab90`) is
  closed. Two non-gap-tracked residuals — `WILLOW_OPERATOR_GITHUB_LOGIN`
  as an operator env act, community-health vendoring as a policy — now
  sit under their own table rather than under Step 3/4.
- **release-please bounded exemption for §11, §12, and §3.** (PR 78)
  `scripts/check_persona_provenance.py`, `scripts/check_ratification.py`
  and `scripts/check_changelog_bullet.py` gain a narrow, two-axis
  exemption for release-please's own release commit and release PR:
  author `willow-ci[bot]` AND
  subject `chore(<branch>): release X.Y.Z` (commit) or `head.ref`
  starting with `release-please--` (PR). Single-axis matches still fail
  closed. INVARIANTS.md §11's `Persona:` rule, §12's `Ratified-by:`
  rule, and §3's `[Unreleased]` bullet rule each grow one bounded
  exemption clause; both scripts carry pinning tests for both
  directions. Motivation: PR 75 (release-please's 0.11.0 cut) has been
  red since 2026-09-15 because release-please cannot by construction
  write the operator's verbatim words into a body it emits itself, nor
  supply a `Persona:` for a commit it authors, nor `- ` bullets under
  `[Unreleased]`; PR 62 flagged the collision and left it "proposed
  rather than pushed, a governance change to an invariant." This PR
  makes the amendment.
- **Nestor ledger is the per-db chain.** (PR 77) `mcp.template.json` and
  `seat/heimdallr/mcp.template.json` pin `NESTOR_LEDGER` to
  `@VAULT_BOX@/nestor.db.ledger.jsonl` instead of the retired
  `@VAULT_BOX@/ledger.jsonl`. Ruling `db84faec` (2026-09-19, "retire
  ledger.jsonl"): the chain for a Nestor store is `<db>.ledger.jsonl`
  beside it, which is where the 8765 UI had been sealing since 2026-09-14
  while both seats ledgered their `nestor_ask` passages into the archive
  (gap 507a71433397). Pinned explicitly rather than dropped — an explicit
  pin beats letting `home_paths.ledger_for` guess, the ambient-resolution
  class the ruling closed. The live, globally-ignored `.mcp.json` files on
  the operator box were rewritten the same way outside this diff. Also
  carries the willow-bot usable build brief (`docs/design/`), reconciled
  twice against source.

### Added

- **`Gap-Id:` / `Idea-Id:` join-key trailers.** (PR 76) INVARIANTS §11 gains two
  optional trailers: `Gap-Id: <12 hex>` names the backlog gap a commit
  lands the fix for; `Idea-Id: <slug>` names a recorded idea. Neither is
  required, but a present value must parse —
  `scripts/check_persona_provenance.py` refuses a `Gap-Id` that is not
  twelve lowercase hex characters, because the willow-bot steward resolves
  the cited gap on the sweep that brings the merge home and a malformed id
  would resolve nothing silently. Shape only; the checker does not consult
  the backlog. Eight new cases in `tests/test_persona_provenance_check.py`.
  Motivated by the 2026-09-12 market survey (Mechanism 1: "trailer + CI
  refusal not yet implemented") read against gap e278ec952b9c (the backlog
  cannot record its own closures) and reconciler slice 0 (no join key, 0.0
  recovery).
- **The operator's verifier stays out of tracked files.** (PR 74)
  `scripts/sync_desk_client_hooks.py` routes `WILLOW_OPERATOR_VERIFIER` —
  the name that opts the session_start hook into the boot pinentry — to the
  gitignored `.claude/settings.local.json` (created if absent, nothing else
  in it touched, idempotent), keeps it out of the rendered tracked block, and
  `--check` refuses a tracked `.claude/settings.json` that carries it.
  `nestor/README.md` gains the 2026-09-14 keyring-partition note (repo
  staging lane, not fleet law) without naming the verifier or the key.
  `tests/test_sync_keeps_the_operator_out_of_tracked_files.py` pins all of
  it, including a planted tracked block the gate must refuse.
- **grove_hook Nestor-first probe + Jarvis close-out.** (PR 72) Two §3
  addenda from the proposal, layered on top of #71's `gate`/`deposit`.
  `_nestor_reach()` probes `127.0.0.1:8765` (PR 69's sealed port row) with a
  250 ms timeout; on refuse it falls back to `shutil.which("nestor")` and
  returns tri-state (`reachable` / `installed_not_answering` /
  `not_installed`). `reinject` now prepends a Nestor-first line ahead of the
  four seat lines: an attributed state (`Nestor: sealed`, etc.) when Nestor
  answers, or the once-per-session boot line for the other two states —
  guarded by `/tmp/willow-nestor-status-<sid>-<state>.flag` so subsequent
  `prompt_submit` events don't repeat it. `orient` emits the same boot line
  on session_start. `deposit` gains a Jarvis close-out: counts draft pairs
  across `willows-grove/nestor/*.json`; if any exist and 8765 is not
  serving, launches `nestor ui --loopback` fire-and-forget; either way,
  prints `"The store is open if you'd like to sign them."` — one sentence,
  no checklist. Zero unsealed pairs → silent. Seven new contract tests in
  `tests/test_grove_hook_actions.py` cover the three probe branches, the
  once-per-session sentinel, the reachable-but-ask-returns-none fallback,
  and the three Jarvis close-out states.

- **grove_hook implements `gate` and `deposit`.** (PR 71) Stop-event `gate`
  refuses a turn whose last assistant message reads "all tests pass" /
  "done" / "complete" without a `tool_use` in the same turn — a
  structured `{"decision": "block", "reason": "..."}` response. Second Stop
  in the same turn (`stop_hook_active`) is advisory: prints to stderr, exits
  zero, does not fight the pinentry flow approval-broker §5c is designing.
  SessionEnd `deposit` walks the transcript's `tool_use` blocks and writes
  a JSON summary to `$WILLOW_HOME/deposits/<session_id>.json` (fallback
  `~/.willow/deposits/<session_id>.json`); cannot block per Nestor's
  SessionEnd finding, so any write failure warns to stderr and exits zero.
  Nestor `kb_journal` writes + draft pair proposals from this action stay
  deferred — MVP semantic per operator direction 2026-09-14. Contract tests
  in `tests/test_grove_hook_actions.py` pin: block-on-done-claim,
  allow-with-tool-call, advisory-on-stop_hook_active, fail-open on missing
  transcript, deposit shape, deposit-cannot-block on unwritable dir,
  missing-transcript still writes total=0.

- **Willow proposes 5 grove-hook action rows as a draft Nestor bundle.**
  (PR 70) `nestor/2026-09-14-grove-action-rows.json` carries 5 draft pairs
  mirroring the entries in `hooks/wiring.source.json` one-for-one:
  `session_start → orient`, `prompt_submit → reinject`,
  `pre_compact → reinject`, `stop → gate`, `session_end → deposit`.
  Bundle 2 of 2 for PR 3 (bundle 1 carried the §0 rule + port owners in
  PR 69, sealed 2026-09-14). Nothing is sealed by merging this PR; the
  operator seals in `nestor ui` against the local grove-session store.
  Once sealed, PR 3 Phase B chunk 2 exports the sealed state to
  `governance/decisions/grove-hook-rows-sealed.json` and retargets
  `scripts/generate_grove_hook_wiring.py` to read from it, deleting
  `hooks/wiring.source.json` as the 1.4 mistake §0 rules out.

- **Willow proposes §0 hooks-and-index rule + §2 port map as a draft Nestor
  bundle.** (PR 69) `nestor/2026-09-13-hooks-index-and-port-map.json`
  carries 7 draft pairs — the governing "an index the fleet depends on is
  derived from the trees, never maintained by hand" rule from the
  2026-09-02 grove-hooks-and-skills proposal, plus port row assignments
  for 8765 / 8766 / 8767 / 8768 / 9000 / 11434 with operator's 2026-09-13
  corrections applied (added willow-bot on 9000; removed the OpenClaw
  gateway row that had lived as a placeholder). Nothing is sealed; the
  operator seals in `nestor ui` against the local grove-session store per
  `nestor/README.md`. Downstream §3 grove-action rows are deliberately
  deferred to a second bundle after §0 is sealed.

- **One Desk hook stack for every IDE/CLI.** (PR 66) `hooks/client-hooks.json` is the
  neutral table (Nestor-shaped); `scripts/sync_desk_client_hooks.py` compiles
  it into `.cursor/hooks.json` (local) and `.claude/settings.json` (tracked,
  portable `$CLAUDE_PROJECT_DIR` / `${WILLOW_HOME}`). `hooks/grove-hook`
  launches the same actions on both dialects and reinjects a
  codebase-memory-mcp session reminder (Cursor's `install` only wires global
  MCP — Claude already got SessionStart hooks). Drift gate:
  `tests/test_desk_client_hooks.py` + `--check` / `--parity` (gap 651b4a1ccfab).

- **Grove hook wiring is generated, not hand-kept.** (PR 64) `hooks/wiring.source.json`
  is the editable input; `scripts/generate_grove_hook_wiring.py` writes
  `hooks/wiring.json`; `tests/test_grove_hook_wiring_generated.py` fails on
  hand drift (KB 20BACCD0 / Grove hooks proposal §6).

- **The fleet CI floor, and release-please.** (PR 62) Fleet plan Wave 4,
  decision 5: C4-tests-yml-grove and C4-grove-release. `tests.yml` now runs
  the suite on a Linux matrix derived from the `pyproject.toml` classifiers
  (3.11, 3.12, 3.13), a Windows leg on the floor and ceiling (3.11, 3.13),
  and a lint leg with ruff pinned to 0.16.7 (`ruff check` on the E4/E7/E9/F
  baseline, `ruff format --check`); the aggregate `test` job needs every leg
  and its verdict is `scripts/ci_gate.py`, which treats skipped and cancelled
  as failures and is planted. `tests/test_ci_floor.py` holds the workflow to
  that shape. The tree is ruff-formatted (128 files) and its 48 baseline
  findings fixed; `.gitattributes` pins LF on every checkout; the executable
  pin reads git's mode rather than the filesystem's. release-please (manifest
  config, hidden types chore/ci/docs/test per the vendored fleet
  conventions, `$comment-hidden-rule` and `$comment-what-cuts-a-release` in
  place, `extra-files` bumping the hatch fallback version and
  `safe-app-manifest.json`) and the pr-title guard with this repo's
  `PACKAGED` set land beside it; `tests/test_fleet_conventions.py`'s
  real-tree tests no longer have a vacuous branch.

- **A numbered idea pile, and the `Idea-Id` trailer gate.** (PR 60) Fleet
  loop plan Wave 3, E3-piles and E3-trailers. `docs/ideas.md` is the repo's
  one numbered pile in the shape willow-reconciler reads: 29 items carried
  over from `docs/KNOWN_GAPS.md` (now the `GAP-00N` → item map), the plan's
  bites for this repo, and the open sections of the design record — never
  invented, tagged shipped only where git history shows the landing.
  `.github/workflows/trailers.yml` runs `reconciler verify` on every PR so an
  `Idea-Id` trailer naming an item the pile does not contain fails loud, and
  `CONTRIBUTING.md` (new) names the test command and the trailer convention.
  `tests/test_fleet_conventions.py` now points `PILE` at the pile, asserts
  the workflow is present, and the CONTRIBUTING rule's xfail is gone.
  CodeQL found the new workflow (and `tests.yml`) declaring no
  `permissions:` block; both now declare `contents: read`, and
  `tests/test_ci_workflows_declare_permissions.py` holds every workflow to
  it, planted.

### Changed

- **`hooks/wiring.json` derives from sealed Nestor rows, not the hand-kept
  source.** (PR 73) `scripts/generate_grove_hook_wiring.py` now reads
  `governance/decisions/grove-hook-rows-sealed.json` — a "sealed record"
  file mirroring the 5 pairs the operator sealed via PR 70's Nestor bundle
  on 2026-09-14. Ambient scaffolding (command, env, ide-stack pointer, the
  `_no_pre_tool_use` note) moved from the source file into module
  constants inside the generator; changing them is a code change, reviewed.
  `hooks/wiring.source.json` is deleted — its row content lives in Nestor
  now, per proposal §6. Chunk B2 of Phase B, delivering "an index the fleet
  depends on is derived from the trees, never maintained by hand" (§0,
  sealed via PR 69). `tests/test_grove_hook_wiring_generated.py` extended
  with a hand-edit plant + input-validation cases.

- **`scripts/sync_desk_client_hooks.py` delegates the tracked-file write to
  `willow_mcp.install_project.apply_hooks`.** (PR 68) The neutral compile
  pipeline through `willow_mcp.project_wiring._compile_hook_manifest` is
  unchanged; only the final write moved. A hand-added third-party PreToolUse
  entry in `.claude/settings.json` now SURVIVES a re-sync (was previously
  overwritten wholesale). `--check` compares against
  `apply_hooks(dry_run=True)` output, so the drift gate still fires on real
  drift but no longer trips on a preserved third-party row.
  `tests/test_sync_delegates_to_install_project.py` pins the invariant.

- **`before_web` covers the full willow_web_* family.** (PR 67) `.claude/settings.json`
  (regenerated via `scripts/sync_desk_client_hooks.py` after the upstream
  willow-mcp `project_wiring._TOOL_MATCHERS["web"]` extension) and
  `seat/heimdallr/.claude/settings.json` (hand-edited — not on the sync
  pipeline) now include `willow_web_search`, `willow_web_fetch`,
  `willow_institutional_search`, and their `mcp__.*__` variants in the
  PreToolUse matcher. A direct call to `willow_web_fetch` or
  `willow_institutional_search` previously skipped the grove hook's
  `before_web` entirely — defense in depth so the corpus-first delegation
  to willow-mcp fires on every web-family verb, not only native
  WebSearch/WebFetch. Also reframes `docs/design/approval-broker.md` §6
  stage table: push is not a Kart-initiated egress act, it is brokered
  via `git_push_execute` with the willows-bot installation token on the
  broker (docs/design/brokered-push.md slice 3); what stage 1 unblocks
  for push is the signed push envelope the broker demands, not the push
  itself.

- **Desk Claude SessionStart opens presence pinentry before auto-sign.** (PR 65)
  Wire `WILLOW_KEYRING` from `$WILLOW_HOME` into `.claude/settings.json`
  SessionStart/End (verifier comes from ambient `WILLOW_OPERATOR_VERIFIER`,
  not a hard-coded handle); document the host presence path as
  approval-broker §5c (companion to willow-mcp SessionStart pinentry gate).

- **Polish Willow desk and steward seat tooling.** (PR 61) Auto-resolve the
  Jeles Python runtime in `seat/willow/scripts/jeles-intake.py` across venvs;
  wire `heartbeat`, `scan`, `steward`, and `intake` subcommands into
  `seat/willow/scripts/willow-seat.sh`; fix bash arithmetic truthiness bug
  and accept CLI PR args in `seat/willow/scripts/kart-watch-prs.sh`; and
  document the desk subcommands in `seat/willow/README.md`.

- **The meta-scan, and the tree held to the fleet's published conventions.**
  (PR 59) Fleet loop plan Wave 2, G2-meta-scans-grove and
  G2-conventions-grove. `tests/test_scans_fire.py` is homestead-ledger's
  meta-scan ported and re-grounded here: every module-level helper in
  `tests/` shaped like a violation-scanner (walks `ast`, runs a pattern,
  reads a file and asks a membership question of it, or walks a word list)
  must be reached by a planted-violation test in the same file, and no test
  body may itself be an unfactored scan. Against this tree it reported
  twenty-one never-fired helpers across fifteen files and three inline
  scans; all twenty-one are now planted and the three are factored into
  helpers with plants of their own. One re-grounding, planted: this suite
  writes its tests as `unittest.TestCase` methods, so a plant method counts.
  `tests/test_fleet_conventions.py` reads its rules from the vendored
  `tests/fleet_conventions.json` (`reconciler conventions --json`,
  willow-reconciler 0.6.0, sha256-pinned with a planted one-byte change)
  and holds the tree to them: no `release-please.yml` here until Wave 4, so
  the pr-title rule is asserted vacuous; no pile, so the trailers rule is
  vacuous; no `CONTRIBUTING.md`, so the test-command rule is a strict
  `xfail` naming the follow-up rather than a bent test.

- **The first coverage verdict is on the record.** (PR 57) `CONST-X-4`, the
  Concurrence Rule, is declared `differently`: `ratatosk.permission` composes
  conjunctively and fails closed exactly as the clause requires, but over two
  in-process tool vocabularies (`PolicyStore`, `CapabilityGate`) rather than the
  six constitutional authorities it names — neither passing nor failing, which is
  what Appendix A's four-verdict scale exists for. `_status` no longer says the
  file is empty on purpose, and records that the remaining 64 undeclared rows are
  a statement about what has been judged, not about what is enforced. `CONST-X`
  stays undeclared; X.1–X.3 are untouched by anything in either tree.

- **ratatosk is on the persona roster.** (PR 56) It was a fleet member by
  every measure except `governance/fleet_personas.json` — a willow-mcp manifest
  (`app_id ratatosk`, `role session_runtime`), a Grove sender identity posting
  under its own name, a released package on the `[tool.willow.fleet]` roster —
  so §11 rejected trailers naming the seat that did the work. Registered at
  `trust: WORKER` alongside jeles, binder, publius and schmidt, following its
  manifest: it denies `envelope_ratify`, `envelope_propose`, `kb_promote`,
  `knowledge_ingest` and `human_attestation_create`, so it carries work and
  mints nothing. `voice_source: inferred`, with `_meta.notes` moved from 17
  entries to 18 and the inferred count from 8 to 9. Inert until PR #55 makes the
  checker read the roster.

- **The Desk seat is wired, not only described.** `CLAUDE.md` (PR 46) named
  `seat/willow/` as where the Willow seat opens while nothing implemented it:
  the repo's only willow-mcp wiring was `.cursor/mcp.json`, and it declared
  `heimdallr`. Opening the grove in Claude Code got you no seat at all. Adds
  `seat/willow/mcp.template.json` and `seat/willow/.claude/settings.json`, and
  documents the arrangement in the seat README. Verified rather than assumed:
  the project root is the launch directory, so a config in a subdirectory is
  what loads — and the PreToolUse hook, which reads
  `$CLAUDE_PROJECT_DIR/.mcp.json`, correctly lifts git routing for this seat
  while still warning on `ls`. The live `.mcp.json` stays untracked by design;
  `**/.mcp.json` is ignored on an operator box because it carries absolute
  paths and a seat identity.

- **heimdallr joins the materialized manifest set, and its README stops naming
  the retired home.** The set is compiled from willow-mcp's `specialists.json`,
  which gained a heimdallr row in willow-mcp#443 — so the tracked copy held
  seven of eight seats. The manifest here is byte-identical to the live
  `$WILLOW_HOME/mcp_apps/heimdallr/manifest.json`, which has carried an operator
  signature since 2026-08-27; copying rather than compiling means installing it
  cannot invalidate that signature. Note the live manifest says
  `role: gatekeeper` where the bundle row says `watchman` — the two are
  reconciled toward the signed file in a companion willow-mcp change, not here.
  Every command in the README pointed at `~/github/willow-memory/.willow` and
  its venv: the pre-migration home, moved to the vault archive this session, so
  a reader following it would have compiled against a tree that no longer holds
  the fleet.

- **The hook manifest path is exercised, and the Grove declares its hooks
  through it.** willow-mcp has carried `hook_manifest` / `project_wiring` — a
  neutral event vocabulary (`session_start`, `prompt_submit`, `pre_compact`,
  `pre_tool_use`, `stop`, `session_end`, `notification`) that compiles to
  client-specific hook config — but no registered project declared one, so the
  compiler had never been run against a real repo. Adds `hooks/wiring.json`
  (five rows, no `pre_tool_use`), `hooks/grove-hook` (an `<client> <action>`
  entrypoint whose `orient` reuses `willow_mcp.blockers` rather than
  re-implementing the checks, and whose `gate`/`deposit` fail open), and
  `hooks/seat.md`, the drift-pinned seat file. `tests/test_hook_manifest.py`
  runs eleven assertions through willow-mcp's own compiler, so the wiring is
  validated by the thing that will consume it rather than by a copy. The audit
  this enables caught PR 49's hand-written tracked hook config mechanically,
  which is the point: the manifest is what makes hook drift detectable instead
  of a thing someone has to notice. `wiring.json` carries a `_provisional` key
  admitting it is hand-authored contrary to §6 until the generator lands.
  PR 53.

### Removed

- **`envelopes/pre-approved.json` is no longer tracked — the live register is
  machine state, not law.** The file records which envelopes are in force on
  *this* box, and willow-mcp rewrites it on every `envelope_propose` /
  `envelope_ratify`. Tracking it had two costs. It drifted: 352 uncommitted
  lines carrying 22 envelope ids had accumulated across several sessions
  because no one owned committing a file the server was writing underneath
  them. And it leaked authority: a fresh clone inherited this box's 48 active
  grants as though root had ratified them there. `grove/envelope_reader.py`
  already handles the file's absence (logs once, returns no envelopes), so an
  untracked clone now fails CLOSED with zero grants. The law it sat beside —
  `syscall-table.json`, `frank_head_anchor.json`, `review_queue.json`,
  `README.md` — stays tracked. Same rule the Nestor session store follows: the
  blueprint travels, the live store does not.
  PR 45.

- **The rest of `envelopes/` follows it out — the vault is the trust root.**
  Supersedes PR 45's "the law it sat beside stays tracked": `syscall-table.json`,
  `frank_head_anchor.json` and `review_queue.json` now live only at
  `$WILLOW_HOME/constitutional/`. `WILLOW_CHARTER_REPO` is retired, so
  `envelopes.registry_path()` falls through to a location that follows
  `WILLOW_HOME` instead of pinning law to a checkout — the third instance of
  gap `006e0144da95`, where which file is law depended on the launching
  process. Measured before the move: `pre-approved.json` was identical in both
  trees (63 grants, same ids); `syscall-table.json` had **diverged**, and the
  vault copy was the newer one (2026-08-11 against 2026-07-06) already carrying
  verb 13's bounds as `${WILLOW_HOME}/constitutional/pre-approved.json` — the
  fix had been authored in August and the charter pointer had been overriding
  it ever since. `frank_head_anchor.json` and `review_queue.json` existed only
  in this tree and would have been orphaned by the repoint.

### Changed

- **The Desk takes the head of the repo; the Watch becomes a seat you open.**
  Supersedes the arrangement added in PR 48: `seat/willow/` held the seat wiring
  while the root held Heimdallr's, so reaching the Desk meant opening two levels
  down — and the root's `.claude/settings.local.json` exported
  `WILLOW_APP_ID=heimdallr` into every session regardless. That env is not scoped
  to the root, and `session_start_hook.py:41` resolves `app_id` from its own
  process environment rather than from `.mcp.json`, so the Desk was seated as the
  Watch: `sessions/willow-793a857c-….json` and `sessions/heimdallr-793a857c-….json`
  written in the same second for one session start (gaps `acceefc0ec77`,
  `3727efb30041`). The root now carries `mcp.template.json` and a tracked
  `.claude/settings.json` whose hooks pin `WILLOW_APP_ID` inline — the hook cannot
  inherit a seat from the launching shell. Heimdallr moves to `seat/heimdallr/`
  with the same shape. `seat/willow/` keeps desk *content* — scripts and
  `jeles-intake/` — and loses its seat config; the root `.mcp.json` is untracked
  like every other, beside its tracked template. The persona partition is
  unchanged: Heimdallr still owns served-page honesty, the resident watcher,
  Gjallarhorn and serve-mode auth. Two operator-ratified Nestor pairs in
  `seat/willow/jeles-intake/` still name the old path and need re-sealing by hand
  — superseding a seal is a human act. `nestor-grove-session` keeps its entry and
  gains an absolute command, replacing the bare `nestor` that raised ENOENT at
  every session start; `tests/test_nestor_bundle_domain.py` now pins that argv
  against `mcp.template.json` rather than the untracked `.mcp.json`, which does
  not exist in a fresh clone or in CI — the assertions are unchanged, only the
  file they read moved, on PR 45's precedent that the blueprint travels and the
  live wiring does not. PR 49.

- **Seat probe binds a Grove sender instead of asserting on an unbound one.**
  `willow-seat.sh probe` called `ratatosk.grove.send()` in a bare process, but
  `crown.py` binds the sender only under `--mcp`, so the check reported
  `grove sender not configured` regardless of how the box was configured — it
  could not trigger what it tested. The probe now separates channel-unset,
  channel-set-but-sender-unbound, and a live receipted send; the live path is
  opt-in behind `SEAT_PROBE_GROVE_SEND=1`, since binding costs a willow-mcp
  stdio process. Verified with `RATATOSK_GROVE_CHANNEL=willow`:
  `grove.send: ok=True detail=posted to willow`.
  PR 44.

- **Willow seat stack documented; probe gains Ratatosk + vault env.**
  Cherry-picks phone-seat production + tier-0 homecoming docs onto master;
  adds `docs/design/seat-stack.md` (Phone → Ratatosk → MCP/Grove → deposit).
  `willow-seat.sh probe` sources `fleet.env` / `WILLOW_VAULT_BOX`, checks
  `RATATOSK_GROVE_CHANNEL`, dry-runs `grove.send()`, and lists serve ports.
  PR 43.

- **Live envelope registry moves to `envelopes/` in the grove charter repo.**
  Article III.2 law (`pre-approved.json`, `syscall-table.json`,
  `frank_head_anchor.json`, `review_queue.json`) no longer lives under
  `$WILLOW_HOME/constitutional/`; `grove/envelope_reader.py` probes
  `WILLOW_CHARTER_REPO/envelopes/` first, with per-node
  `$WILLOW_HOME/constitutional/` overrides on `id` collision. Pairs with
  willow-mcp path resolution for `WILLOW_CHARTER_REPO` / `WILLOW_VAULT_BOX`.
  PR 42.

- **Willow desk home + Jarvis is not a mode switch.** Operator seat scripts and
  jeles-intake live under `seat/willow/`; `docs/design/grove-persona-partition.md`
  splits Willow desk vs Heimdallr watch. Governance / PM / PA stay back-of-house
  triage questions — C12’s operator lens switch is demoted from the first
  viewport (`grove_html.py` no longer mounts `<grove-lens-switch>`). Cursor’s
  Made-with footer is treated as a machine trailer for §12 ratification.
  PR 37.

- **Grove MCP moves 8765 → 8767, ending a real port collision.**
  `grove/mcp_local.py --serve` and `willow-mcp --serve` both defaulted to
  `8765`; only one can bind, so a tunnel pointed at "the MCP port" fronted
  whichever process won the race. The fleet map is now explicit and written in
  the Grove runbook: **8765** willow-mcp MCP (the ratified remote-seat endpoint,
  KB `2026B306`), **8766** the desk page — loopback only, never fronted (D4) —
  and **8767** Grove MCP. `tests/test_port_map.py` asserts the declared defaults
  from source, including that the launcher and the module agree. Found while
  reading a remote-seat design doc that instructed a builder to front
  `willow-mcp --serve` "at 127.0.0.1:8766", which is both the wrong default and
  the one surface doctrine forbids exposing. PR 36.

- **Kart mount policy: `WILLOW_ROOT` is bound read-only and tasks get a work
  root.** It resolves to the product's source (or `site-packages`), and bound
  read-write it let a sandboxed task edit the code deciding what tasks may do —
  measured from inside a task: `gate.py`, `pyproject.toml`, `.git` and
  `.gitignore` writable while `mcp_apps/` and `consent.json` were correctly
  read-only. `deploy/kart-sandbox.template.json` now binds `WILLOW_ROOT` `ro`
  with `{{WILLOW_ROOT}}/worktrees` as the writable lane, and records the three
  rules that cost something: the host must create the lane, `WILLOW_ROOT` must
  never also appear in `bind_try` (read-write wins a collision regardless of
  order), and it must be set explicitly — inferred on an editable install it
  resolves to `<repo>/src`. Implementation in willow-memory/kartikeya#37. PR 35.

- **willow-config tombstoned:** `LOCAL_GITHUB_LAYOUT.md` no longer clones
  `rudi193-cmd/willow-config`; `.willow` is runtime-only. See
  `github/archive/RETIRE-willow-config-2026-09-01.md`. PR 32.

- Drop **willow-2.0** product naming from fleet docs and canon: the archived
  origin monorepo is **legacy fleet monolith**; checkout env is
  `WILLOW_LEGACY_MONOLITH_REPO` (archive paths may still end in `willow-2.0`).
  PR 31.

- C11 journal seam: Grove speaks MCP (`grove/willow_mcp_client.py`) — stdio
  child or `{WILLOW_MCP_URL}/mcp` — instead of invented REST `/tools/*`
  routes. Mock e2e server updated to match. Implements governance proposal
  #25 item 1. PR 30.

- GAP-007 closed: `kb_journal_read` landed upstream in willow-mcp; cleared
  `_PENDING_UPSTREAM` and updated e2e conftest to reflect the C11 read path
  is no longer a protocol-only mock. PR 27.

- The constitution stopped naming the machinery. Draft 0.8 strips every
  implementation reference from `governance/CONSTITUTION.md` — no filenames,
  module names, product names or agent names in the body or the appendices —
  on the rule that references point **up**: artifacts cite clauses by Trace ID
  and the law cites none of them. Every citation the document has ever retired
  was a downward one, and no upward reference has gone stale, because a Trace
  ID does not move when a file does. Article 0 is untouched, asserted by diff
  rather than by intention. Three further moves ride with it. Cases, field
  evidence and name-collision notes move to a new companion volume,
  `governance/CASEBOOK.md` (nine cases, four disambiguations; six had never
  been written down) — a case is *supposed* to name the actor, the date and
  the file, which is why it cannot live in the statute. Article IV's single
  ladder splits into the two axes it had been fusing: **Standing** (who has
  checked this) and **Ground** (what it rests on), orthogonal, with
  Contested/Frontier/Canonical retained as their named conjunctions so no
  Trace ID moves; new IV.5 forbids inferring either axis from the other and
  IV.6 holds that a verifier is an attribution, not a warrant. And Appendix
  A's hand-maintained enforcement table — which named an archived module as
  Article II's enforcement while the gate that actually enforces it went
  unnamed — is replaced by `governance/scripts/const_coverage.py`, a generated
  report on a four-verdict scale (satisfied / **differently** / not applicable
  / failing). "Differently" exists because a clause can hold by a mechanism
  that is not its own, and scoring that either way would be a lie. The script
  refuses to guess verdicts, reading them from
  `governance/compliance/coverage-declarations.json`, which ships empty on
  purpose: Draft 0.8 provides the form, the verdicts are the operator's. It
  also excludes itself from its own scan, because a gate fails closed on its
  subject and open on itself. Still Draft, still ratified by no one. PR 26.

### Fixed

- **The persona checker kept its own copy of the fleet roster.** (PR 55)
  `check_persona_provenance.py` held the closed persona set as a frozenset
  literal, though INVARIANTS §11 names `governance/fleet_personas.json` as the
  source. The two had already drifted: `schmidt` reached the roster and never
  the literal, so a commit naming a real fleet member would have been reported
  as drift. The checker now reads the file, refuses `_meta`, and fails closed
  when the roster is missing, malformed or empty. The synthetic-repo fixture
  stands up its own roster containing `quill` — a name in no fleet literal
  anywhere, so a commit naming it passing proves the file was read.

- **The coverage report could not see most of the constitution.** (PR 54)
  The charter says clauses inherit their article's Trace ID, but only Article 0
  wrote its clause IDs out, and `const_coverage.py` scanned for literal
  `CONST-*` strings — so it reported 21 identifiers for a document that has 65,
  counting the Trace-ID sentence's own examples as definitions while every
  clause of Articles I–XIII stayed invisible. `CONST-X-4` could not be reported
  at all, though ratatosk's permission seam enforces and cites it. Clause IDs
  are now derived from the document's own headings. Adds the unchecked
  direction too — a Trace ID cited in the tree that matches no clause, which
  surfaces `CONST-0-3-II` (a compliance-case ID, not a clause) and
  `CONST-X-N` (a shape placeholder). Verdicts are untouched and remain the
  operator's to record.

- **`scripts/grove-serve` installed a unit bound to 8765 — the port holding the
  operator's origin-bound browser key.** Grove MCP serve mode is 8767; the
  toggle script had kept 8765 as its default while the module and the launcher
  moved on, so running it would have written a systemd unit that either fought
  the Nestor UI for that port or, worse, answered on it.
  `tests/test_port_map.py` grew three assertions that read the toggle script
  itself, because the existing coverage read the module and the launcher —
  every file except the one that drifted. Separately, and on a different unit:
  `deploy/grove-serve.service.template` — the *served page* on 8766, which the
  toggle does not install and which is filled in by hand per its own header —
  gained `Environment=WILLOW_DB_URL=@DB_URL@` and the matching `sed` line in
  that header, so a hand-installed served page starts with a DSN instead of
  finding Postgres missing at first read. The toggle installs
  `grove-mcp-serve.service.template`, and only that one. PR 50.

- `run_test_dir_or_fail.sh` resolved the repo venv python instead of bare
  `python3` (no pytest on fleet boxes). Persona roster tests now clear host
  `WILLOW_HOME` when unset so in-repo fallback cases stay isolated. PR 28.

- Two persona `canonical_file` pointers named files that do not exist.
  `heimdallr` pointed at `safe-app-willow-grove/CLAUDE.md`, a repo archived
  2026-08-27 and tombstoned `rebuilt -> willows-grove`; the registry was
  generated the same day, so it captured the path on its way out and the
  gatekeeper's own voice source has named a missing tree ever since. `nestor`
  pointed at `Nestor/nestor/persona.py`, which never resolved either — every
  other pointer is repo-relative with no org and the checkout is lowercase. All
  nine pointers were checked; these were the only misses. Separately measured
  and left for an operator decision: `$WILLOW_HOME/fleet_personas.json` is the
  copy `PersonaRoster()` actually loads and carries 0/16 voices and 3/16
  visuals, while this repo's copy carries 17/17 of each. PR 24.

- Eleven dead documentation links across three design and runbook docs — the
  sweep in PR 21 reported eight, and undercounted by three. Five pointed at
  `the-house-already-knew.md`, a real and readable document in the public,
  active `rudi193-cmd/safe-app-store`, through relative paths that assumed a
  sibling checkout the 2026-08-10 org-folder move ended; they are absolute URLs
  now. Two pointed at `docs/synthesis/*`, which `docs/INDEX.md` records as
  out-of-tree by design at the **private, archived**
  `rudi193-cmd/safe-app-willow-grove` — named with their location rather than
  linked, since a URL there 404s for nearly every reader. One pointed at
  `docs/generated/`, which is not missing but *generated*: extractor output,
  and the extractor is itself out-of-tree.
  **The three the first sweep missed are the interesting ones.** They climbed
  out of the repository to `../../../willow-mcp/...` and *resolved cleanly*
  during that audit, because a sibling checkout of willow-mcp happened to sit
  beside this repo at the time. On a fresh clone and in CI they were always
  dead. A file-existence check blesses a link whose validity depends on what
  else the reader has cloned, so `tests/test_docs_links_resolve.py` asserts two
  properties, not one: every relative link resolves, **and** no relative link
  escapes the repository root. Resolution asks *is it there* and the answer
  varies by machine; escape asks *could it ever reliably be there* and the
  answer is a property of the link. Only the second is portable, and without it
  the count stays wrong. No allowance list: every link was fixed rather than
  excused. PR 23.

- The C11 read-back suite was green against a willow-mcp tool that was never
  built. `tests/e2e_willow_mcp/mock_willow_mcp.py` serves
  `/tools/kb_journal_read`; the name appears **zero times** in willow-mcp, so
  both of Grove's read paths — `getattr(willow_mcp.server, "kb_journal_read")`
  and the `POST {WILLOW_MCP_URL}/tools/kb_journal_read` fallback — depend on the
  same absent dependency, and the fallback is not a second chance. The write
  half is genuinely wired (`kb_journal` exists; Grove's writer was driven
  through it to a live Postgres row); the read half raises `Unreachable`
  against real willow-mcp while the mock answers happily.
  `tests/test_mock_willow_mcp_surface.py` reads the mock's tool routes off the
  live `build_app()` and compares them to the installed upstream. The obvious
  pin — every mock route must exist upstream — would have been born failing,
  since the divergence is real and outside this repo's control, and a pin that
  cannot pass gets skipped or deleted. So the divergence is **enumerated
  instead of excused** in `_PENDING_UPSTREAM` and fails in both directions: a
  new unmatched route fails as drift, and `kb_journal_read` appearing upstream
  also fails, telling the reader to strike the entry and close the gap. Both
  directions were exercised before landing. `tests/e2e_willow_mcp/conftest.py`
  now states which half of the suite proves a contract and which is a protocol
  test against a pending tool, and `docs/KNOWN_GAPS.md` carries it as GAP-007.
  Issue #16. PR 22.

- `docs/ARCHITECTURE.md` carried three links that went nowhere, and all three
  pointed at the cross-repo material nothing else documents — a reader
  following them to learn how Grove meets the rest of the fleet arrived at a
  404 with no other route. They were two different defects wearing one
  symptom. `../../willow-2.0/docs/db/WILLOW_SCHEMA.md` names a document that
  is real and readable; the path only resolves in a checkout where willow-2.0
  sits beside this repo, and the 2026-08-10 org-folder move ended that layout
  — now an absolute link to the public archive, marked archived.
  `CROSS_REPO_BRIDGE.md` and `extractor/GROVE_DOCS_EXTRACTOR_SPEC.md` were
  linked as local siblings but have never been in this tree or its history:
  `docs/INDEX.md` already recorded them under *"Not in this tree (by design)"*,
  living at `rudi193-cmd/safe-app-willow-grove`. That repository is private and
  archived, so they are now named with their location rather than linked — a
  URL there would 404 for most readers, which is the same dead end dressed up
  as a working reference. The decision had been made and written down
  correctly; ARCHITECTURE.md never learned of it, so two documents in one
  directory disagreed about what this repository contains and the one a
  newcomer reads first was wrong. `tests/test_architecture_links_resolve.py`
  pins every relative link in the canonical reference against disk, and pins
  the two by-design absences as named-not-linked. PR 21.

### Fixed

- Tester onboarding did not survive its own first hour. `pip install -r
  requirements.txt` aborts on Debian and Ubuntu with `Cannot uninstall PyJWT
  2.7.0, RECORD file not found` — PyJWT arrives transitively through `mcp`
  (`pyjwt[crypto]>=2.10.1`), pip resolves it forward, and cannot remove a copy
  `apt` installed because distro packages ship no `RECORD`. The error names
  Debian, so it reads as a broken machine rather than a missing step. Step 2 now
  creates `.venv` before installing — which is also the interpreter both
  `run_mcp.sh` and `scripts/grove-serve-run` already resolve to and that
  onboarding never created. Three more dead references in the same document went
  with it: step 5 ran `python3 app.py`, which has never existed in this
  repository; the u2u chat step ran `grove_standalone.py`, part of the departed
  Textual dashboard, and `u2u/` exposes no entrypoint at all, so that step is
  now marked unavailable rather than described; and a duplicated sanity-check
  section carried curly quotes, so `psql -d “$WILLOW_PG_DB”` failed as written
  in the first of two otherwise identical blocks.
  `tests/test_tester_onboarding_runnable.py` pins all four properties — venv
  before install, every named file on disk, no curly quotes inside a shell
  fence, no duplicated headings — each paired with a self-check, because a
  parser that silently stops matching turns an audit into a green no-op, which
  is the failure class the document was already suffering from. Issue #14.
  PR 20.

### Added


- **The Kart mount policy is tracked, as a portable template.** `deploy/kart-sandbox.template.json` + `deploy/kart-sandbox.md`. The policy deciding what a sandboxed task may open, write and never see lived in one untracked file on one disk — no history, no review, no ratification. The template names no person, home directory or machine, so it imports into an APK, a wheel or another box; an instance adds only its repositories and its sensitive files. Nine rules recorded in `_policy`, including that `bind_try` is READ-write, that secret files need their own read-only overlay (the receipt ledger and secret store were writable by the tasks they record), and that a parent bind silently republishes whatever is added under it later. Two known holes recorded as holes: `WILLOW_ROOT` lets a task edit the gate, and `{{WILLOW_HOME}}` is not a template key. PR 34.
- `docs/design/fleet-wiring.md` — how the fleet is actually wired, seam by seam,
  verified against running code with all seven repositories installed together.
  `docs/ARCHITECTURE.md` is Grove-scoped by declaration and hands cross-repo
  wiring to `willow-2.0` through three links that no longer resolve; the drawio
  set draws which face talks to which, but every one of its arrows is a
  different mechanism — a subprocess speaking line-delimited JSON-RPC, a Python
  import, a Postgres trigger, an HTTP POST — and an arrow cannot say which, nor
  what happens when the far end is absent. Covers the five transports, eight
  seams, the three disciplines that make it a system (three-state, fail-closed
  authorization, confirm-once-then-revalidate), and four things a diagram cannot
  show: an import is a transport, `WILLOW_PG_DB` defaults differently in Grove
  (`willow_20`) than in willow-mcp (`willow`), the Nestor domain lives in three
  places where a disagreement reports success, and the C11 seam exists in the
  write direction only. PR 19.

- `docs/design/fleet-standup.md` — how to stand the whole fleet up in one box,
  and what that turns up. Grove's suite goes 517 passed / 9 skipped to 522 / 4
  and willow-mcp's 2874 / 14 to 2883 / 5 once Postgres, willow-mcp, kartikeya,
  jeles, nestor, willow-gate and the archived willow-2.0 policy are actually
  present rather than skipped past — no container runtime required, and nothing
  mocked to get there. Records the dependency graph (it is circular: nestor
  audits itself against the charter case cards in this repo), a runbook, the
  four skips that are correct as they are, the three hosts and one kernel
  interface that are genuinely unreachable from a cloud seat, and four findings
  — including two in nestor that only appear once its optional extras are
  installed. PR 19.

- `.mcp.json` serves this session's Nestor store to an agent over MCP (stdio,
  `--read-only`, `--engine offline`) — seven verbs including `nestor_ask`,
  `nestor_provenance` and `nestor_ledger_verify`. `nestor/session-decisions.json`
  is the portable bundle it is built from; the live `.db` and its ledger are
  gitignored per LOCAL-ONLY.md's rule that the blueprint travels and the live
  store does not. PR 15.

### Fixed

- The Nestor decision gate answered `clear` without having looked. The shipped
  bundle was keyed `grove→grove` while every reader queries `decision` — the
  CLI's own default for `nestor decision check`, and the value hardcoded in
  `grove/nestor_client.py`. The bare command therefore reported "no decision on
  record" against a store holding that exact question at 0.984 similarity: not
  an error, not the unreachable state §1 can render, a clean and confident
  wrong answer. `.mcp.json` passed the domain explicitly, so the MCP path
  answered correctly throughout and only the human at the keyboard was misled.
  The bundle is re-keyed, `DECISION_DOMAIN` is now a named constant the other
  two surfaces are pinned against by `tests/test_nestor_bundle_domain.py`, and
  `nestor/README.md` no longer certifies the earlier fix as complete — it
  replaced `question→finding` with a second unqueryable domain and the symptom
  never changed. Issue #12. PR 15.
- `<grove-card>` was never loaded on the served page. `grove_html.py` mounted
  eight component scripts and not `grove-card.js`; the only importer in the tree
  was `web/harness.html`, so `customElements.define("grove-card", …)` never ran
  in production and `layout-memory-boot.js` walked `querySelectorAll(
  "grove-card[id]")` against an empty set on every load — layout memory live
  under test, inert on the real page, under a docstring asserting an ordering
  guarantee with nothing behind it. The component is mounted ahead of the boot
  module, and the pin that would have caught this no longer skips itself when
  the tag is absent: a skip cannot enforce an ordering discipline, because the
  state it skips on is the state where the discipline is being violated.
  Issue #13. PR 15.
- `docs/KNOWN_GAPS.md` records three open defects that previously lived only
  in a session transcript: the served page's absent authentication and its
  warn-then-bind (GAP-004), u2u dispatching without destination binding,
  replay defence or a header allowlist (GAP-005), and
  `check_changelog_bullet.py` reporting counts it did not compute (GAP-006).
  `pr14-carryovers.md` marks #3 and #10 closed — both were delivered and never
  marked — retires the migration checklist as history, and records #13
  (character continuity across compactions) as confirmed in the wild. PR 15.

- `docs/design/the-forge-shape.md` — the Forge's shape as talked out with the
  operator: the "what's the first bite" entry, keyword→major with ambiguity as
  a scripted state rather than a guess, an `almanac-tech` rung holding pinned
  official docs beside the awesome lists and their criteria, per-project Nestor
  holding the *connections* rather than the pairs, and contribution as shape
  never content. Also records how the Socratic method actually works — it is
  `friction_score` on the maker's own rationale feeding the FSRS grade, with no
  questioner anywhere, which is why it resisted explanation. PR 17.

- `governance/architecture/willow-v08-toolchain-path.drawio` — a draft of where
  a repo gets its Python, and the first diagram in this directory that is meant
  to keep changing. Measured today: 8 venvs across 7 different paths, 25 repos
  that declare dependencies with no venv at all, a fleet venv at
  `$WILLOW_HOME/venvs/` that exactly one thing uses, and Kart binding `/usr`
  and nothing of `forge-play`. Carries a REVISIONS box; what settles there
  graduates to v0.7. PR 17.

## [0.10.0] — 2026-08-29

The PR-14 batch: the operator guide's launchers restored, the archived
charter repository cut out of every live probe path, four carryovers
closed, and two invariants that were written but unenforced given CI
witnesses.

### Added

- `scripts/check_changelog_bullet.py` now also reads the newest released
  section, not only `[Unreleased]`. A release-cut commit empties
  `[Unreleased]` into a fresh `## [X.Y.Z]`, so its own changes are
  documented in the release they ship in — and the check failed such a
  commit for putting the bullet in the right place. Caught when this
  release tripped over it. PR 14.
- `tests/test_version_changelog_sync.py` — pins `pyproject.toml`'s
  `fallback-version` to CHANGELOG.md's latest released version. Its own
  comment always required the sync and nothing enforced it, so a release
  that bumped one and forgot the other would ship a wheel claiming the
  previous version to any tagless build, silently. PR 14.
- `public.routing_decisions` and `public.human_required_queue` in
  `schema.sql`, so CI exercises the `populated` and `empty` branches of
  INVARIANTS.md §1 rather than only `unreachable` — those readers had no
  table to reach, which is the PR 9 CI symptom. Plus
  `tests/test_schema_completeness.py`, a static guard that every table the
  readers and `/api/*` handlers query exists in `schema.sql`. Closes
  PR 14 carryover #3.
- `scripts/check_changelog_bullet.py`, wired into
  `.github/workflows/tests.yml`: INVARIANTS.md §3's changelog-bullet clause
  is now enforced in CI. Not a numbered carryover — surfaced during the
  PR 14 build, when the gap was caught in this repo's own history. It was unenforced, which is how PR #8 merged 22
  files with no bullet and a green build. Docs-only PRs, changelog-only
  PRs, and pushes with no base to diff against are all exempt by
  construction.
- `docs/design/operator-tier-review.md`: the OPERATOR-tier `not_do` audit,
  PR 14 carryover #9. All five OPERATOR personas, not the three the
  carryover named — Loki's tier was unaccounted for.

### Fixed

- The four launcher and unit files `docs/grove-served-page.md` tells an
  operator to run — `scripts/grove-serve-run`, `scripts/grove-watcher-run`,
  `deploy/grove-serve.service.template`, `deploy/grove-watcher.service.template`
  — did not exist. They were never committed here, lost in the v0.9
  clean-build port, so the product had not started the way its own
  operator guide says since v0.9. Restored, built to the behavior the doc
  already specified. `tests/test_documented_entrypoints_exist.py` now
  parses the guide for `scripts/*` and `deploy/*` references and asserts
  each exists and is executable, so a doc cannot promise a missing file
  for a release again. PR 14.
- `grove/resident_watcher.py` documented `GROVE_WATCHER_OLLAMA` as the
  override for its Ollama endpoint but never read it — `main()` always
  used the hardcoded default, so the documented override was a dead
  letter no matter how it was set. It is now honored. PR 14.

### Changed

- The fleet persona registry and the seed canon now live in this repo —
  `governance/fleet_personas.json` and `governance/seed/canon/`,
  byte-identical to the originals in the archived `willow-memory/willow`.
  `grove/persona_roster.py` and `grove/seed_reader.py` probe
  `$WILLOW_HOME` first, then `~/.willow`, then the in-repo copy; no
  archived-repo path remains in either. `/seed/{1..6}` now render the real
  canon on every host with no mount required, and the registry has a live
  home for the first time since the 2026-08-27 archiving. Absence stays a
  reachable, tested state in both readers (INVARIANTS.md §1). PR 14.
- `grove/envelope_reader.py`'s absence messages named five
  `willow-memory/willow` directories the code has not probed since the
  constitutional-path migration — an operator following them at 3am would
  have searched five wrong places. They now name the two directories it
  actually reads. Probe behavior unchanged. PR 14.
- Live prose pointers repointed at the new in-repo homes across
  `docs/INVARIANTS.md` §9/§11/§12, `docs/OPS_RUNBOOK.md`,
  `docs/design/willow-grove-premise.md` D10/D16,
  `docs/design/operator-tier-review.md`, and `tests/e2e/README.md`.
  Historical records in `governance/`, audit reproducibility anchors, and
  `willow-memory` GitHub-org references were deliberately left as written,
  per the method in `FINDINGS-2026-08-20-charter-docs-drift.md`. PR 14.

- `docs/audits/loki-swarm-measurement.md` now bounds its claim to the
  prompt-injection layer it actually measured, naming Grove MCP dispatch,
  `kb_journal` writes, Nestor seal-and-verify, and `willow.routing_decisions`
  as unexercised. Closes PR 14 carryover #10.

### Release notes

**Ratification (§12) was not in force for PRs 1–11.** §12 requires a
recorded `Ratified-by:` line at PR-open and at merge. It was sealed in
PR 12; the eleven PRs before it were opened and merged without one and
carry no ratification record. This is not backfillable — merged history
is not rewritten — so it is named here instead. Same gap-class as
pre-v0.9 persona provenance (§11). Every PR from 12 forward carries the
record, and `scripts/check_ratification.py` enforces it in CI.

**The `v0.9.0` tag is lightweight, not annotated.** PR-14 carryover #6
asked for the release tag to carry `Ratified-by:` in its annotated
message. `v0.9.0` (`2a15323`) has no message to carry one, and it is
already published to PyPI as `willows-grove 0.9.0` — moving it would
change what that version means for anyone who has fetched it. It stays
as it is, and the gap is recorded here rather than papered over.
`v0.10.0` is annotated and carries the line.

## [0.9.0] — 2026-08-27

**First release of Willow's Grove at its permanent home
(`willow-memory/willows-grove`).** Clean-build port from the working
repo where v0.9 was authored — the tree carries what matters, not the
history of how it got here.

Twelve CI-enforced invariants (`docs/INVARIANTS.md` §1–§12); a
Loki-swarm audit with all findings resolved
(`docs/audits/loki-v0.9-audit.md`); persona provenance and ratification
sealed and demonstrated in every commit and PR body from this point
forward.

The release is ratified by the human trust root, not the fleet — no
fleet persona has unilateral commit / PR / merge / master-push
authority. §12 seals this.

See:

- `docs/OPS_RUNBOOK.md` — how to run, check, recover Grove
- `docs/INVARIANTS.md` — the twelve sealed invariants
- `docs/audits/loki-v0.9-audit.md` — Loki's audit in his voice
- `docs/audits/loki-swarm-measurement.md` — persona-discipline scored
- `docs/design/pr14-carryovers.md` — what's intentionally not in v0.9
