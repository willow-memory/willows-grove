# Changelog

All notable changes land here per INVARIANTS.md §3. Format follows Keep a Changelog v1.1.0.

## [Unreleased]

### Changed

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
