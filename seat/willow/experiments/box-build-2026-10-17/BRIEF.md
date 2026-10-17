---
kind: doc
name: box-build-brief
description: What every builder, auditor and idea-side agent on the box build reads first.
b17: BOXB1
---

@markdownai v1.0

# Box build — agent brief

§1 Tools · §2 Sandbox · §3 Tests and baselines · §4 Recorded guesses · §5 Output

## §1 Tools, in this order

| Need | Use | Example |
|---|---|---|
| Find code, callers, structure | `/home/user/tools/bin/cbm` (codebase-memory-mcp) | `cbm search_graph '{"project":"home-user-sandbox-repos-willow-bot","name_pattern":"wager"}'` · `cbm trace_path '{"project":"…","function_name":"reconcile_wagers","direction":"inbound"}'` · `cbm search_code '{"project":"…","pattern":"random.seed"}'` · `cbm get_code_snippet '{"project":"…","qualified_name":"…"}'` |
| Read/write/check docs | `/home/user/tools/bin/mai` (MarkdownAI) | `mai mai_list_phases '{"file":"/home/user/sandbox/box-build/PLAN.md"}'` · `mai mai_resolve_phase '{"file":"…","phase":"J1-wagers-brier"}'` · `mai mai_get_constraints '{"file":"…"}'` · `mai lint <paths>` |
| Anything else | grep / read | only after the two above |

Projects in cbm: sandbox clones are `home-user-sandbox-repos-<repo>` (index them again with `cbm index_repository '{"repo_path":"/home/user/sandbox/repos/<repo>"}'` after you change code); the untouched originals are `home-user-<repo>`.

## §2 Sandbox

- Work ONLY in `/home/user/sandbox/repos/<repo>` on branch `box-build`. Never touch `/home/user/<repo>` (the originals). Pushes are disabled.
- Commit locally on `box-build` with a clear message and a `Persona: willow` trailer. Never push, never open a PR.
- Python: `/home/user/tools/venv/bin/python` (has pytest, ruff 0.16.7, cryptography, hypothesis, dice, willow-mcp).
- The plan is `/home/user/sandbox/box-build/PLAN.md` (phases J1–J9, constraints). The spec, once written, is `/home/user/sandbox/box-build/SPEC.md`.

## §3 Tests and baselines (before any change)

| Suite | Command (from the repo dir) | Baseline |
|---|---|---|
| onescript | `cd willow-bot/one-script && python -m pytest -q onescript/tests` | 502 passed, 1 skipped |
| willow-bot | `cd willow-bot && python -m pytest -q tests` | 1099 passed, 2 skipped, 3 failed + 7 errors pre-existing in this container (do not count them against a change; do not add to them) |
| the-table | `cd safe-app-store/apps/the-table && python -m pytest -q` | 152 passed, 2 skipped |
| ai-game-master | `cd safe-app-store/apps/ai-game-master && python -m pytest -q` | 7 passed |
| Forge | `cd Forge && python -m pytest -q tests` | 836 passed, 144 skipped |
| lint | `ruff check` on files you touch (willow-bot pins 0.16.7) | clean |

A change ends with every suite you touched at or above baseline.

## §4 Recorded guesses (the human has not ruled; each is a guess, not a decision)

| Question | Guess | Confidence |
|---|---|---|
| Brier math in onescript: import Forge or vendor? | Vendor the small pure functions (`brier`, `log_score`) into onescript with a provenance comment naming `forge/calibration.py`, the way Forge itself keeps a "diffable" copy; onescript stays dependency-light | 70% |
| `apps/game/engine_v1_7.py` is "stalled": edit it? | One backward-compatible change only: `roll(..., rng=None)` falling back to the module `random`; everything else stays in the-table's adapters | 65% |
| Where the exact-odds predictor lives | `safe-app-store/apps/the-table/the_table/peaks.py`, emitting a distribution onescript can take as a wager | 70% |

## §5 Output

End with a README-style report: numbered `##` sections, a table of what changed (file:line), test counts before → after, what you could not do and why. No questions at the end except in a final "Questions" section.
