---
kind: doc
name: box-build-tools-into-the-flow
description: Where cbm (code graph) and mai (MarkdownAI) move work out of model rungs and into code in the deterministic flow, with probe evidence, tests and confidence.
b17: BOXB1
---

@markdownai v1.0

# Tools into the deterministic flow

§1 Verdict · §2 What the probes showed · §3 Ranking · §4 Rejected · §5 Risks · proposals T-mai-1 … T-cbm-4 as phases · constraints at the end

Design only. No code was written to any repo. Probes ran against the sandbox clones under `/home/user/sandbox/repos/` and a throwaway git repo in the scratchpad (its cbm project was deleted afterwards).

## §1 Verdict

Neither tool can replace a model rung's judgement, and neither needs to. Both can do what the flow's code checks cannot do today.

| Tool | Real contribution | Where it does not help |
|---|---|---|
| mai | A static shape gate on every `@markdownai` doc before it enters the record. A phase-addressed, byte-verbatim lookup for rules text (a D0 `verbatim` answer). A fixed-order ladder (`next_phase`). | `@macro` cannot replace `seat_boxes.compose`. `@phase` is strictly linear, so it cannot model branching game scenes. constraint directive text is free prose, not a gate. |
| cbm | A deterministic "does this symbol exist at file:line" check for qualified code citations. A caller/test-coverage card for a human before a seal. A closed D0 class for "where is X defined". | It does not see calls through injected callables. It leaves no edge for an unresolved import. `detect_changes` is file-granular. `manage_adr` is not a decision record. |

## §2 What the probes showed

| # | Probe | Result |
|---|---|---|
| E1 | `cbm search_graph` / `query_graph` / `trace_path` on willow-bot | `chain_act` chain.py 172-260; `check_claims` gate.py 437-510 (start_line and end_line both return); `resolve_fixture` has 10 inbound callers. 19-29 ms per call. |
| E2 | `trace_path check_claims` before and after `index_repository` | md5 identical. Deterministic. A re-index of willows-grove took 0.11 s. |
| E3 | Symbol that does not exist (`^totally_made_up_fn$`) | `total: 0` plus a hint. Empty is a clean answer, but it only means "not in the graph as indexed". |
| E4 | 109 backticked identifiers from `forge-convergence.md` checked against 6 indexed sandbox repos | 66 hit, 43 miss. Misses are hex ids, env vars, hook names and tool names. Hits include generic names (`app_id`, `escalate`, `self`) that exist in most repos. A bare-name check would both reject true cites and verify invented ones. |
| E5 | Throwaway repo, one-line edit in `leaf()`, `detect_changes` | `changed_files: 1`, `seed_symbols: 3` (every symbol in the file), `impacted: 0`. It is file-granular and treats the callers as seeds. `trace_path leaf inbound` correctly gave `mid` at hop 1 and `top` at hop 2. |
| E6 | `trace_path run_checks` in willows-grove | 6 `Seat` callers found. `trace_path check_claims` in willows-grove found 0, because `seat_cli.py:349` passes `gate.check_claims` as a value. The graph is blind to injected callables. |
| E7 | Throwaway repo with `from forge.calibration import brier` (not indexed) | The `IMPORTS` query returned only the internal edge. An unresolved external import leaves no edge, so a graph import-boundary check would pass falsely. `search_code "forge"` did find the line. |
| E8 | Name-resolved call edges | The `get` and `resolve` callees from chain.py resolved to `sigh.py` and `credentials.py`, and `execute` resolved to a test file. Bare method names produce wrong edges. Qualified `file:symbol` lookups are safe. |
| E9 | `manage_adr mode=update` on the scratch project | `{"status":"updated"}`. Nothing appeared in the repo; the text lives in `~/.cache/codebase-memory-mcp/<project>.db`. |
| E10 | `mai_list_phases` / `mai_resolve_phase` / `mai_next_phase` on PLAN.md | Exact names and lines. `resolve_phase` returns the content verbatim. `next_phase` returns `next` or `done: true`. An unknown phase returns an error plus the available list. Strictly linear. |
| E11 | `mai_get_constraints` on a probe doc | `[{severity, text, line}]`, sorted critical first. There is no machine field beyond severity. |
| E12 | `mai_call_macro` with `count: 3` (int) | "Error executing tool". Strings work. A missing arg leaves the literal `{noun}`. Replacement is a plain `str.replace`, so `$c` collides with `$count`. |
| E13 | `mai_read_file` on a doc with `@db` / `@http` / `@env`, as the `box-build` seat (manifest: `markdownai_read`, `markdownai_write`) | Every directive returned `[mai directive denied: caller lacks the 'markdownai_directives' grant (#161)]`. The gate holds. |
| E14 | `mai lint` on PLAN.md, BRIEF.md and the probe docs | Clean. The lint is textual: header first, colon form of the constraint directive, last-constraint swallow, last-phase swallow, balanced `@if`/`@macro`. It never executes a directive. |

## §3 Ranking

Ranked by what moves out of a model rung or hardens a code check, times confidence.

| Rank | Phase | Change | Confidence | PLAN join |
|---|---|---|---|---|
| 1 | T-mai-1 | Pre-seal shape gate on `@markdownai` docs written into the record | 70% | new (beside J4/J9 rows) |
| 2 | T-cbm-4 | Graph stamp and 3-state wrapper (prerequisite for the other cbm items) | 65% | new |
| 3 | T-cbm-1 | `symbol` claim kind in `gate.check_claims` for qualified code cites | 60% | new (extends J5's strike-the-unserved claims check) |
| 4 | T-mai-2 | Rules lookup by `@phase` as a D0 `verbatim` answer | 55% | J6 |
| 5 | T-cbm-2 | Impact and test-coverage card before a human seals | 55% | new (near J9's sealed tip) |
| 6 | T-cbm-3 | D0 class G6 "where is X defined" | 40% | new (sibling of J6) |
| 7 | T-mai-3 | `@phase` ladder as turn-order check | 40% | partly J7, mostly new |
| 8 | T-mai-4 | constraint directive gate registry with drift check | 40% | new |
| 9 | T-mai-5 | `@macro` for fixed-shape roll sentences only | 35% | J7 |

## §4 Rejected, with evidence

| Idea | Verdict | Evidence |
|---|---|---|
| `manage_adr` in place of `decisions_boot.py` / `stores/decisions/fleet.json` | Reject, 90% | E9. The ADR is six free-text sections in an untracked per-project cache DB. `decisions_boot.py` enforces `verified_by != author`, a non-empty reason, and a present `reopen_when`, and `fleet.json` is tracked. cbm has none of these fields. At most an ADR could hold a derived architecture sketch. It must never hold the record. |
| `detect_changes` as the impact check | Reject as the check; keep `changed_files` | E5. Use it only to list files. Impact comes from T-cbm-2. |
| Graph `IMPORTS` as the "onescript imports no Forge" boundary (BRIEF §4 vendoring guess) | Reject | E7. Use `search_code` or grep for the boundary. |
| Bare-name backtick cites checked against the graph | Reject | E4, E8. |
| `@macro` replacing `seat_boxes.compose` | Reject | E12. `compose` (seat_boxes.py:687-792) groups boxes through `_pair`, `_run` and `plural`. Flat templates cannot express that. |
| mai `@db`, `@http`, `@env` in any record or box doc | Reject | E13. They stay gated. See constraints. |

## §5 Risks

| Risk | Detail | Handling |
|---|---|---|
| cbm writes outside the repo | Each project is a SQLite DB in `~/.cache/codebase-memory-mcp/` (the cache already holds ~420 MB across projects), and `manage_adr` writes there too. `config list` shows `auto_watch = true`, a background watcher. | Cache is a derived artefact, never a source of truth. Every cbm answer carries the T-cbm-4 stamp. |
| cbm `install` edits agent configs | The README says it configures 43 client surfaces. | Never run `install`. Use `cbm <tool> '<json>'` (the `cli` entry) only. |
| cbm `--ui` | An HTTP graph UI would be a web port, against willows-grove CLAUDE.md rule 1 (no web ports for the dashboard). | Keep `--ui=false`. Record that in the T-cbm-4 stamp test. |
| Stale graph | BRIEF §1: re-index after code changes. A stale graph yields false "not found". | T-cbm-4 refuses when the working tree is newer than the index. |
| mai side-effect directives | `@db`/`@http`/`@env` are denied for `box-build` (E13). | Static lint only. No gate in this spec calls `mai_read_file` or `mai_execute_directive` on a record doc. |
| mai parser quirks | colon form of the constraint directive is silently dropped. A constraint captures to the next constraint directive or EOF. A phase has no close. | `mai lint` catches these. T-mai-1 vendors those checks. |

@phase T-mai-1

## T-mai-1 Pre-seal shape gate on `@markdownai` docs

| Field | Value |
|---|---|
| Moves from model to code | The claim that a written doc is well-formed. Today nothing checks a doc's structure when it enters the record. |
| Touches | `willow-bot/one-script/onescript/record.py:Record.write_file` (line ~246), reached from `run.py:write_proposal` (line ~535). `write_proposal` already turns a `PermissionError` into a `refused` row. A new module `onescript/mai_shape.py` holds a small vendored copy of `lint_file`'s textual checks from `willow-mcp/tools/mai_lint.py`, with a provenance comment, in the same way BRIEF §4 vendors Brier math. It does not import willow-mcp. |
| Deterministic check added | Only for a `.md` whose body starts with `@markdownai`: header first, frontmatter parses, no colon form of the constraint directive, the last constraint directive and the last `@phase` do not swallow structural content, `@if`/`@macro` balanced. Failure raises `PermissionError`, so a `refused` row is recorded and no bytes are written. A pass is stamped on the `write` row as `lint: clean`. A plain `.md` is not checked. |
| Test | New `one-script/onescript/tests/test_layers.py::test_mai_shape_refuses_*`: a doc using the colon form of the constraint directive is refused, with no file and a `refused` row. A clean doc yields a `write` row with `lint: clean`. A plain `.md` is unchanged. A parity test runs the vendored checks and `tools/mai_lint.py` over the same fixture docs and asserts the same verdicts. Baseline 502 passed, 1 skipped must not drop. |
| Confidence | 70% |
| PLAN join | New. Sits beside J4 and J9 (more row kinds in the one-script record). It also enforces the PLAN's own warning constraint that every document passes `mai lint`. |

@phase T-cbm-4

## T-cbm-4 Graph stamp and 3-state wrapper

| Field | Value |
|---|---|
| Moves from model to code | The statement "I looked in the code and X is or is not there". The model's answer becomes a stamped graph read. |
| Touches | New `willow-bot/one-script/onescript/graph.py:graph_read(runner, project, query)`. `runner` is an injected callable that wraps `cbm <tool> '<json>'`. When it is absent, the state is `unreachable`. onescript stays dependency-light and never imports cbm. |
| Deterministic check added | Returns `{state, stamp, rows}`. `state` is `populated` (rows), `empty` (`total: 0`) or `unreachable` (binary missing, timeout or bad JSON), never collapsed (INVARIANTS §1, willows-grove CLAUDE.md "Grove" table). `stamp` is `{project, nodes, edges, head_sha, dirty}`. `head_sha` and `dirty` come from git, because `index_status` carries no commit. Before querying, the wrapper checks that no tracked file is newer than the index, and otherwise re-indexes, which took 0.11 s on willows-grove (E2). `empty` is worded "not in the graph at <stamp>", never "does not exist". |
| Test | Fake runner cases: raises gives `unreachable`; `total: 0` gives `empty`; rows give `populated` with the stamp. A modified-file case triggers re-index. A real-runner test is skipped when `/home/user/tools/bin/cbm` is absent, and asserts two reads give byte-identical rows (E2). |
| Confidence | 65% |
| PLAN join | New. It is a prerequisite for T-cbm-1, T-cbm-2 and T-cbm-3. |

@phase T-cbm-1

## T-cbm-1 `symbol` claim kind in `gate.check_claims`

| Field | Value |
|---|---|
| Moves from model to code | "The sentence cites a function or line that exists." Today `check_claims` checks count, result, turn and quote claims, and a code citation in a model sentence is unchecked. |
| Touches | `willow-bot/one-script/onescript/gate.py:check_claims` (lines 437-510) gains `kind: "symbol"` rows. `run.py:Run.say` (line ~546) fills `facts["symbols"]` from T-cbm-4 as `{file: {name: [start, end]}}` using one Cypher per node label (`Function`, `Method`, `Class`). Both `start_line` and `end_line` were verified to return (E1). |
| Deterministic check added | Only a qualified cite is read: `path.py:name` or `path.py:LINE`. It is `verified` when the file is in the facts and the name is defined there, or the line falls inside a symbol's range. Otherwise it is `unverified`, with the record naming the stamp. With no `symbols` key in the facts, no row is listed, which matches the function's own rule that an uncheckable claim stays agent-reported. Bare backticked names are never read (E4, E8). The graph is blind to calls through injected callables (E6), so this check covers existence only, never "who calls". |
| Test | Extend `test_layers.py`: `gate.py:check_claims` is verified; `gate.py:check_claimz` is unverified; `gate.py:480` is verified (inside 437-510); `gate.py:900` is unverified; no `symbols` key gives no rows. An integration test builds the facts from the real cbm on the sandbox willow-bot clone, and is skipped without the binary. The existing quote and result tests must still pass. The seat's `CHECK_NAMES` (seat_say.py:75) is left alone. It mirrors the web sketch and `check_quotes` filters on `kind == "quote"` only. A fifth seat check is a separate decision for the human. |
| Confidence | 60% |
| PLAN join | New. It extends J5, where the claims check strikes what was not served. |

@phase T-mai-2

## T-mai-2 Rules lookup by `@phase` as a D0 `verbatim` answer

| Field | Value |
|---|---|
| Moves from model to code | "What does rule R say." A rules or lore doc written as `@phase R-<name>` sections is read by exact name instead of by a model summarising it. |
| Touches | `willow-bot/willow_bot/deterministic/resolvers.py:resolve_fixture` (line 378) gains a branch for a rules-lookup class, using the existing `STATUS_VERBATIM`. Also `one-script/onescript/escalate.py:act_of` (line 289) so the escalate path builds the act. The `@phase NAME … until next @phase` parsing is a few lines in `mai_shape.py` (T-mai-1), not an import of willow-mcp. |
| Deterministic check added | The question must name a phase exactly. The answer is the phase body byte-for-byte, with the phase name as the cite. An unknown or ambiguous name escalates, and nothing is guessed. The doc's `sha` is the one `Record.write_file` already stores in the pile pointer, so the answer is tied to sealed bytes. |
| Test | `tests/test_deterministic_resolvers.py`: a parity test asserts the local parser and `mai mai_resolve_phase` return the same content for every phase of a fixture doc (E10). The named phase returns `verbatim` with the correct cite. An unknown phase escalates. A doc whose sha differs from the pointer escalates. |
| Confidence | 55% |
| PLAN join | J6, "rules-lookup" |

@phase T-cbm-2

## T-cbm-2 Impact and test-coverage card before a human seals

| Field | Value |
|---|---|
| Moves from model to code | "What does this change touch." Today that is a model's or reviewer's narrative. |
| Touches | New `onescript/graph.py:impact_card(changed_files, hunks, graph)`, shown beside `escalate.make_card` (line 480). The seal itself stays `gate.py:verify_seal` and `serve.py:sealed_verified`, which are untouched. Per the PLAN, only the human seals. |
| Deterministic check added | From `git diff -U0` line ranges and the symbol ranges in the graph, list the changed symbols. For each, list inbound callers by hop (`trace_path`) and mark callers whose file is under a test path. A changed symbol with zero test callers is flagged. `detect_changes` supplies only `changed_files` (E5), and impact is computed here. The card is worded "static callers at <stamp>" because injected callables are invisible (E6). |
| Test | A fixture repo with `leaf`, `mid` and `top`: changing `leaf` gives callers `mid` (hop 1) and `top` (hop 2) and "no test calls it". Adding a `test_leaf` removes the flag. Unreachable cbm gives a card with state `unreachable`, not an empty impact list. |
| Confidence | 55% |
| PLAN join | New. It supports J9's sealed tip (A7) without touching the seal. |

@phase T-cbm-3

## T-cbm-3 D0 class G6, "where is X defined"

| Field | Value |
|---|---|
| Moves from model to code | A locate-the-definition question that today escalates to the local rung, or to flowering. |
| Touches | `willow-bot/willow_bot/deterministic/resolvers.py:resolve_fixture` (line 378) gains `if cls == "G6"`, plus `_resolve_g6` and a `score_resolution` case. `chain.py:chain_act` (line 172) is unchanged because D0 closes before the model. The pool excerpt is generated by code from `graph_read` (T-cbm-4), with id `g:<sha of project, stamp, query, rows>`. |
| Deterministic check added | The question is a closed shape, "where is `<symbol>` defined". Exactly one definition node with that exact name gives `path:start-end` and cites `[g:…]`. Zero or more than one match escalates, with the ambiguity listed in the reason (E8 shows bare names collide). `unreachable` or `empty` also escalates. "Who calls X" is out of scope for v1 (E6). |
| Test | `tests/test_deterministic_resolvers.py`: one match resolves and scores. An ambiguous name escalates. An absent name escalates and never says "not found". A tampered excerpt id escalates. |
| Confidence | 40%. No fixture in the pool asks a code-locate question yet, and G1-G5 are dispatch-record classes. The value is unmeasured until such questions occur. |
| PLAN join | New, a sibling of J6 |

@phase T-mai-3

## T-mai-3 `@phase` ladder as turn-order check

| Field | Value |
|---|---|
| Moves from model to code | "Which step of a fixed ladder is this turn on." |
| Touches | `willow-bot/one-script/onescript/record.py:Record.open_turn` (line ~228), whose `intent` is free text today. A ladder doc such as D0, then local, then flowering, or the box-build joins, is parsed with the local `@phase` parser (T-mai-2). |
| Deterministic check added | `open_turn` for a ladder must carry the phase name and match `next(prev)`. A mismatch appends a `refused` row. This is `mai_next_phase` semantics: linear, unknown names rejected, `done` at the end (E10). It is not for branching play. Game scenes use `legal_moves` (J7), not `@phase`. |
| Test | In order passes. A skipped phase is refused. An unknown phase is refused. After the last phase the next `open_turn` is refused as `done`. |
| Confidence | 40% |
| PLAN join | Partly J7, mostly new |

@phase T-mai-4

## T-mai-4 constraint directive gate registry with a drift check

| Field | Value |
|---|---|
| Moves from model to code | The upkeep of "which checks are required" from prose and memory to a doc that code verifies. It does not move any answer out of a model. |
| Touches | `willows-grove/grove/seat_say.py:CHECK_NAMES` (line 75) and `run_checks` (line 358). A `seat-gates.md` doc carries one single-line constraint directive with a severity per gate, whose first token is `gate=<name>`. |
| Deterministic check added | At load, every constraint's `gate=` must exist in the code registry and every registry check must have a constraint. Anything else refuses to load, so a silent drop becomes a failure. Severity decides a strike or a note. Constraints stay grouped at the end, one line each, because `mai_get_constraints` returns only `{severity, text, line}` (E11) and the parser captures greedily and drops the colon form silently. |
| Test | A registry/doc mismatch in either direction refuses. A colon-form constraint is caught by the T-mai-1 shape check. The existing `test_seat_say.py` cases are unchanged. |
| Confidence | 40% |
| PLAN join | New |

@phase T-mai-5

## T-mai-5 `@macro` for fixed-shape roll sentences only

| Field | Value |
|---|---|
| Moves from model to code | A narrator line for a roll, such as roll, modifier, total, DC and outcome, comes from a template instead of a model sentence. |
| Touches | A J7 narrator module that composes roll facts as boxes. It does not touch `grove/seat_boxes.py:compose` (lines 687-792), which stays as is. |
| Deterministic check added | The wrapper converts every arg to `str` first, because an int arg errors (E12). It then asserts no `{…}` or `$…` residue, so a missing arg fails closed instead of printing `{noun}`. The template words are added to the box vocabulary, so `check_nothing_lacking` (seat_say.py:299) still passes. A run of a model on a roll line is replaced by code. |
| Test | The string and int arg cases pass. A missing arg is refused on residue. A `$c` and `$count` collision case is covered. The rendered sentence passes `run_checks`. |
| Confidence | 35% |
| PLAN join | J7 |

@constraint severity=critical
No tool in this spec is allowed to execute a side-effect directive on a record or box doc. `@db`, `@http` and `@env` stay gated behind the `markdownai_directives` grant, which the `box-build` seat does not hold (E13). The mai gates here are static text checks only.
@constraint severity=critical
Never run `cbm install`, `cbm update`, or `--ui=true`. Use only `cbm <tool> '<json>'`. `install` edits agent configs, and the UI would be a web port.
@constraint severity=error
Every cbm-derived fact carries the T-cbm-4 stamp (project, nodes, edges, head sha, dirty flag), and `empty` is never reported as "does not exist".
@constraint severity=error
Graph checks cover only qualified `file:symbol` or `file:line` cites. The graph does not see injected callables and leaves no edge for an unresolved import (E6, E7), so it is never the sole evidence for "no caller" or "no import".
@constraint severity=error
Code and tools propose; only the human seals. T-cbm-2 produces a card and never a seal (PLAN critical constraint, ai-game-master DECISION.md §6).
@constraint severity=warning
The cbm cache under `~/.cache/codebase-memory-mcp/` is derived and disposable and is never a record. The fleet decision record stays `safe-app-store/stores/decisions/fleet.json` read by `tools/decisions_boot.py`.
