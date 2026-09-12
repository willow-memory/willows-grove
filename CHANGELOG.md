# Changelog

All notable changes land here per INVARIANTS.md §3. Format follows Keep a Changelog v1.1.0.

## [Unreleased]

### Added

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
