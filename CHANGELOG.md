# Changelog

All notable changes land here per INVARIANTS.md §3. Format follows Keep a Changelog v1.1.0.

## [Unreleased]

### Added

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
  write direction only. PR 17.

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
  installed. PR 17.

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
