# Grove Invariants

Single source of truth for the discipline Grove's readers, endpoints,
and Web Components share. Every code-changing PR that reads a source or
paints a state cites a section here by anchor, not by line number.

Load-bearing constraint (Constraint 1, DESIGN_CONSTRAINTS.md):

> Every surface has at least three states — populated, empty, and unknown.
> "I could not reach the source" must never collapse into "there is
> nothing there."

## §1 — The three-state contract

Every reader returns EITHER a value with a bounded shape (populated OR
empty) OR raises a `grove.errors.Unreachable` sentinel. **A bare `[]` or
`{}` MUST NOT mean "unreachable" anywhere in the tree.**

### Reader shape

| Case         | Return                                        |
|--------------|-----------------------------------------------|
| populated    | the value's real shape, non-empty             |
| empty        | the same shape with no data (`[]`, `{}`, `PersonaRoster` with no rows, `{"schema": "...", "envelopes": []}`) |
| unreachable  | `raise Unreachable(reason)` — never a value   |

### Endpoint shape

Every `/api/*` handler wraps its reader in a `try/except Unreachable` and
answers with one of:

| Status | Body                                                             | When |
|--------|------------------------------------------------------------------|------|
| `200`  | `{"state": "populated", <data-fields>}`                          | source reached, data present |
| `200`  | `{"state": "empty",     <same-shape-with-no-data>}`              | source reached, no data      |
| `503`  | `{"state": "unreachable", "reason": "<why>"}`                    | source could not be reached  |

Every other pre-existing status (400 on bad input, 405 on wrong method,
etc.) is preserved verbatim. `state` is the discipline; the other
non-2xx codes are the pre-existing surface. A successful write endpoint
has no `empty` case — a successful write is always `populated`.

Existing response fields (e.g. journal-writer's `ok`) may coexist with
`state` for backward compatibility — the `state` field is the one every
Web Component reads.

### Web Component shape

Every Web Component that consumes an `/api/*` endpoint renders a
distinct visual for `unreachable`. It is NEVER the same pixels as
`empty`. The empty state and the unreachable state look different to
the operator — text, color, or affordance MUST differ. The three-state
JSDoc header on every consuming component names this section.

Unreachable rendering guidance (not mandate):
- amber / muted-red banner or border for unreachable
- neutral / plant sigil (❦) for quiet-but-reached (empty)
- source-fetch failure fires a component `<name>-unreachable` event so
  a page-level listener can act; log-once to `console.info`, never
  `console.error`

### Where the sentinel lives

`grove.errors.Unreachable` — one class, one `reason` string. See
`grove/errors.py`. Every reader in `grove/*.py` and every endpoint in
`grove_serve.py` uses this vocabulary.

### Pinning tests

Pytest layer: `tests/test_panel_wiring.py` +
`tests/test_refusal_summon_shape.py` pin the reader / endpoint /
wiring wire shape.

Visual layer (Grove v0.9 PR 9): `tests/e2e/grove-served-page.spec.js`
pins the three-state pass through every panel;
`tests/e2e/three-state-affordances.spec.js` pins unreachable ≠ empty
at the render layer (the data-element `<grove-persona-registry>`
exposes its distinction via the `registry-unreachable` event and
`.state`, not visible markup — see PR 14 carryovers);
`tests/e2e/seed-canon.spec.js` pins that the `/seed/` route survives
canon absence (six chapter links, per-page title + body).

Round-trip layer (Grove v0.9 PR 10): §1 is pinned end-to-end by the
willow-mcp suite under `tests/e2e_willow_mcp/`. A minimal Starlette
mock at `tests/e2e_willow_mcp/mock_willow_mcp.py` speaks the
`/tools/kb_journal` + `/tools/kb_journal_read` protocol; the tests
drive `grove/journal_writer.py` and `grove/journal_reader.py` against
it and verify:

- populated: a write → read round-trip returns the same bytes;
- empty: fresh store → the reader returns `[]` (bounded shape, never
  collapsed into `Unreachable`);
- unreachable: the mock's `POST /kill` toggle → both the writer and
  the reader raise `Unreachable`, distinct from empty;
- recovery: `POST /restore` → subsequent writes and reads succeed
  with no latched state.

The full watcher → writer → mock → reader loop is pinned by
`tests/e2e_willow_mcp/test_watcher_chat_readback_flow.py` (the C11
LEFT-write → RIGHT-read chat card seam).

## §2 — Supersedes D7 (premise doc)

`docs/design/willow-grove-premise.md` D7 sealed the phrase *"absence is
a state, not a failure"*. That phrase was widely misread as
"empty-on-failure is fine" — the readers collapsed
"could-not-reach-the-source" into `[]` / `{}` / `None`, and the Web
Components rendered nothing (which reads to the operator as "there is
nothing there"), which IS the fleet's disease named in Constraint 1.

D7 remains sealed. Its correct reading is now three-state per §1 above:
the state (unreached) exists AND rendering it distinctly is required.
The premise-doc D7 section (`docs/design/willow-grove-premise.md`
around line 316) carries a supersede line pointing here.

Pinning tests (§2): the D7-supersede is pinned by `tests/test_panel_wiring.py`
(every reader raises `Unreachable` on missing source; no reader
collapses to empty on a real failure).

## §3 — Doc discipline

- Every design-doc reference in code comments cites `INVARIANTS.md
  §<anchor>`, not line numbers in `DESIGN_CONSTRAINTS.md` (line numbers
  rot; anchors don't).
- Every code-changing PR appends a bullet to `CHANGELOG.md`'s
  `[Unreleased]` section under `### Changed`, `### Added`, `### Fixed`,
  or `### Removed`, per Keep a Changelog v1.1.0.
- New readers state their §1 posture in the module docstring.
- New endpoints state their §1 response shape in the handler docstring.
- New Web Components state their §1 rendering states in the JSDoc
  header.

Pinning tests (§3): `scripts/check_docs_drift.py` (called from
`.github/workflows/tests.yml`) enforces that every `INVARIANTS.md §N`
citation resolves, that every `[Unreleased]` CHANGELOG bullet cites
its PR, and that every INVARIANTS section names at least one CI
witness that exists on disk. Drift on any of these fails the build.

## §4 — Reader/endpoint coverage (v0.9 PR 1 baseline)

Every reader listed below returns bounded-shape-or-`Unreachable`; every
endpoint answers 200/populated, 200/empty, or 503/unreachable.

| Reader                     | Endpoint                       |
|----------------------------|--------------------------------|
| `grove/persona_roster.py`  | `GET  /api/personas`           |
| `grove/envelope_reader.py` | `GET  /api/envelopes`          |
| `grove/kart_reader.py`     | `GET  /api/dispatch`           |
| `grove/journal_reader.py`  | `GET  /api/journal/recent`     |
| `grove/journal_writer.py`  | `POST /api/journal`            |
| `grove/nestor_client.py`   | `POST /api/nestor/decide`      |

Any future reader/endpoint added to Grove joins this table in the same PR.

Pinning tests (§4): `tests/test_panel_wiring.py` pins the endpoint /
reader / Web Component wire shape for every row above; the round-trip
suite under `tests/e2e_willow_mcp/test_journal_roundtrip.py` extends
that to the writer + reader loop for `POST /api/journal` and
`GET /api/journal/recent`.

## §5 — Trust order

Every u2u packet has its signature verified before consent is consulted;
consent decisions never render on unverified data. The order is
**signature → consent → dispatch**, in exactly that sequence.

Concretely, in `u2u/listener.py._process`:

1. Parse and shape-check the header.
2. Verify the Ed25519 signature against the *correct* verification key —
   the stored key for a known contact, or the KNOCK's own payload key for
   an unknown peer's KNOCK (the only self-verifying admission).
3. **Only then** consult `ConsentGate.check` with the (now-authenticated)
   sender address, packet type, and thread_id.
4. Dispatch on ALLOW; refuse-with-signal on DENY; refuse-with-approval-hook
   on PENDING.

Anything derived from an unauthenticated header — including a `_denied`
notification, a `_pending` operator prompt, or a bridge admission — is a
dispatch, and MUST NOT happen before step 2 succeeds.

Two related contact-store rules protect the state that decision depends on:

- `ContactStore.add()` is the ONLY path to create a new contact and refuses
  an address it already knows. Reconstructing the dataclass silently reset
  `blocked` and every `consent_*` flag — that was the "silent trust reset"
  half of the P0.
- `ContactStore.update_key()` is the ONLY path to rotate an existing
  contact's key. It mutates the pubkey and preserves `blocked`, every
  `consent_*` flag, `name`, `added` and `resources`. It defaults closed —
  the caller must explicitly pass `require_confirmation=False` to attest
  that a human authorised the rotation.

Anchor witnesses: `tests/test_u2u_consent_order.py` (this invariant by
name) and `tests/test_u2u_trust.py` (the wider matrix). Every code comment
on the modified lines cites this section by anchor, not by line number.

## §6 — Manifests describe code, not aspirations

Every capability described in `safe-app-manifest.json` reflects a property the
code demonstrably has. Aspirational descriptions belong in design docs, not in
a manifest that claims trust from consumers. Tests enforce this.

The origin case: `dm_conversations` was previously described as *"End-to-end
encrypted, local-only"* while `u2u/packets.py:74-75` writes plaintext JSON
onto a bare TCP socket (the `cryptography` dependency is imported only for
Ed25519 signing). See `CODE_REVIEW.md` P0 — *"the manifest claims u2u is
encrypted; it is not"*. The correction is in the manifest; the aspiration
(Gate 6 confidentiality) lives in `docs/design/u2u-security-limits.md`.

### Enforcement

- `tests/test_readme_honesty.py` pins the README's u2u row — the withdrawn
  phrasings `Encrypted LAN transport` and `encrypted transport` may not
  reappear, and the corrected substrings must be present.
- New capability rows added to `safe-app-manifest.json` MUST be describable
  in code-demonstrable terms. If the description names a property that a
  reader can't verify by reading the tree, the row is wrong.

## §7 — Consent flows are real, not automatic

OAuth authorization never auto-issues a code. The operator approves via a
loopback-only page. Access tokens have a bounded TTL suitable for the
operator seat, not 30 days. DNS-rebinding protection is on regardless of
scheme; a public tunnel deployment requires an explicit operator
acknowledgement flag.

Concretely, for `grove.mcp_local --serve` (see `grove/mcp_auth.py`,
`grove/mcp_local.py`):

- **`/authorize` never issues a code.** It parks the request under a
  256-bit one-shot key and redirects the browser to
  `/grove-approve?pending=<key>`. The pre-PR-6 `GROVE_MCP_AUTO_APPROVE`
  env-var escape hatch is gone — there is no auto-approve path.
- **The approval page runs on the box.** Rendering (GET) is available to
  any peer that has the one-shot key, so an operator can inspect it over
  a tunnel; the POST that completes the grant is refused unless the peer
  is on 127.0.0.1 / ::1 / localhost. The operator has to be on the box
  (SSH port-forward, local browser) to complete the click.
- **Pending approvals expire in 5 minutes.** The one-shot key becomes
  unusable and no code can be issued against it.
- **Access tokens live for 24 hours.** Refresh tokens keep their longer
  reconnect horizon; the access token itself is what gets replayed on
  every call, so it is what has to expire.
- **Dynamic client registration is off by default.** An operator opts in
  explicitly via `GROVE_MCP_ALLOW_DYNAMIC_REGISTRATION=1`. Otherwise
  only pre-enrolled clients can authorize — the pre-PR-6 open dispenser
  is closed.
- **DNS-rebinding protection is on in every configuration.** The prior
  `_transport_security()` carve-out that disabled it "behind ngrok" for
  `https://` base URLs is removed. Loopback plus the operator-configured
  tunnel host stay allowlisted; nothing widens to `*`.
- **A non-loopback base URL logs a WARNING** unless the operator sets
  `WILLOW_MCP_TUNNEL_ACKNOWLEDGED=1`. The listener refuses no request on
  the strength of that flag alone (the transport allowlist is what
  gates access); the flag is the operator saying out loud that the
  tunnel is intended. There is no `--allow-tunnel` CLI flag — the
  warning IS the security note.

Every code change to `grove/mcp_auth.py` or the OAuth surface of
`grove/mcp_local.py` cites `INVARIANTS.md §7` in the docstring or
comment that motivates it. Pinning tests: `tests/test_mcp_auth.py`,
`tests/test_mcp_serve_oauth_flow.py`, `tests/test_serve_mode_identity.py`,
`tests/test_grove_approval_page.py`, `tests/test_transport_security.py`.

## §8 — Panels consume live endpoints by default

Every Web Component consumes its live `/api/*` endpoint by default.
Fixture-based rendering is opt-in (harness use only). The served page
renders live state, not curated data.

Concretely:

- Every Web Component's `data-source` (or equivalent) default resolves
  to the matching endpoint from the §4 coverage table — never a JSON
  fixture path.
- The harness page `web/harness.html` MAY carry an explicit
  `data-source="./fixtures/..."` override so a design pass can inspect
  the populated shape without a running server. That is the only
  legitimate use of an explicit fixture path.
- The served page (`grove_html.py`) MUST NOT carry an explicit
  fixture-path `data-source` on any component. Every panel there
  renders whatever the reader currently returns — populated, empty, or
  unreachable per §1.
- New Web Components state their live-endpoint default (and the
  harness carve-out) in the JSDoc header, alongside their §1 three-state
  posture.

Pinning tests: `tests/test_panel_wiring.py` (endpoint side of the
default source; three-state shape end-to-end),
`tests/test_refusal_summon_shape.py` (the refusal-summon boot module's
POST target and event contract),
`tests/e2e/grove-served-page.spec.js` (visual-layer live-endpoint
consumption, Grove v0.9 PR 9), and
`tests/e2e/three-state-affordances.spec.js` (visual-layer three-state
distinct-render pin, Grove v0.9 PR 9).

## §9 — Seed reads real canon

The `/seed/` route renders content from `willow-memory/willow/seed/canon/`
when the fleet-charter probe path resolves. On absence the stub is
served (C3 discipline). No content is invented at render time; the
reader either quotes canon verbatim (HTML-escaped) or serves the stub.

Concretely, for `grove/seed_reader.py` + `grove/seed_html.py` behind
the `grove_serve.py` routes `/seed/` and `/seed/{n}`:

- **The reader probes three paths, in order** (`_candidate_dirs()`):
  `$WILLOW_HOME/willow-memory/willow/seed/`, then
  `~/willow-memory/willow/seed/`, then `~/.willow/seed/`. The first
  that exists on disk is the seed dir; if the seed dir contains a
  `canon/` subdirectory with six `NN-*.md` files, those files ARE the
  six movements. The reader does not fabricate the sixth chapter from
  five — an incomplete canon degrades to the stub.
- **The renderer escapes every body.** `<`, `>`, `&`, `"`, `'` land as
  `&lt;`, `&gt;`, `&amp;`, `&#x27;`, `&quot;` even though the seed
  source is local files. The discipline holds whether the reader is
  ever repointed at a non-local source or not — the render path is the
  escape point.
- **The absence path is proof of life, not fiction.** When no probe
  rung resolves, `load_movements()` returns the six-movement D16 stub
  (one-sentence bodies from the outline) and logs the absence once per
  process. `/seed/` still renders — C3 sealed session continuity via
  seed's six movements, so the route must survive absence — but the
  stub's body is short and marked in text; it is never mistaken for
  the canon.

Pinning tests: `tests/test_seed_reader.py`, `tests/test_seed_html.py`,
`tests/test_grove_serve_seed.py`,
`tests/test_seed_reader_probe_expansion.py`,
`tests/test_seed_canon_content.py`.

## §10 — CI proves the invariants

Every INVARIANTS section is enforced by at least one CI step. Ollama,
Playwright, docs-drift, and security-grep are CI-first (never
operator-only). Tests that require services declare them in
`.github/workflows/tests.yml`.

Concretely, `.github/workflows/tests.yml` in Grove v0.9 PR 4 carries:

- a `postgres` service (already present) and a new **`ollama` service**
  container. The Ollama-backed watcher e2e (`tests/e2e_ollama/`, filled
  by PR 8) runs against it. Until PR 8 the service idles alongside the
  job and no tests fire — the step is guarded by
  `hashFiles('tests/e2e_ollama/test_*.py', …)`.
- a **Playwright browser install step**
  (`npx --yes playwright install --with-deps chromium`) guarded by
  `hashFiles('playwright.config.js', …)`. The suite itself
  (`tests/e2e/`) is filled by PR 9; the run step is guarded by
  `hashFiles('tests/e2e/*.spec.*', …)` so an empty directory is a
  no-op.
- a **docs-drift step** (`python3 scripts/check_docs_drift.py`) — the
  script is a stub in PR 4 (exits 0 with a note) and is filled by
  PR 11 to enforce §3 (every `INVARIANTS.md §N` citation resolves, every
  CHANGELOG bullet cites its PR, every §N has a CI witness).
- a **security-grep step** (`bash scripts/ci-security-grep.sh`) — sweeps
  the tracked `*.py` / `*.sh` tree for `os.system(`,
  `subprocess.*(shell=True`, bare `eval(` / `exec(`, `pickle.loads`,
  bare `yaml.load(`, etc. False positives live in
  `scripts/ci-security-grep.allowlist` and require a preceding comment
  explaining why they are safe. Non-zero exit on any un-allowlisted hit.

Downstream PRs (8, 9, 10) fill the empty placeholder directories
(`tests/e2e/`, `tests/e2e_ollama/`, `tests/e2e_willow_mcp/`); PR 11
fills the docs-drift enforcement. Each of those PRs cites this section
in its docstrings and CHANGELOG bullet.

A new INVARIANTS section that ships without a CI witness is a §10
violation and is fixed in the same PR — either the enforcement lands,
or a step that fails loudly ("`§N` has no CI witness yet") does.

Pinning tests (populated as each downstream PR lands):

- `tests/e2e_ollama/test_watcher_ollama_readiness.py` — canary for
  the Ollama-backed e2e suite. Verifies the CI Ollama service is
  reachable at `$OLLAMA_HOST` and that the smallest candidate model
  pulls + generates. A skip here signals an environment gap; a fail
  here means the whole suite is not being exercised. (Grove v0.9 PR 8.)
- `tests/e2e_ollama/test_watcher_ollama_e2e.py` — pins the C11
  LEFT-side write path end-to-end: real Postgres LISTEN/NOTIFY on
  `grove.messages` → real Ollama classification → journal write
  carrying `sender="resident-watcher"`, a `domain:*` tag in the
  closed `DOMAINS` set, and the operator's text verbatim (Gate 5 Q2,
  Q3, and V5 discipline). (Grove v0.9 PR 8.)

## §11 — Persona provenance

Every commit that changes tracked code carries a `Persona:` trailer
naming the fleet persona active for the work. Accountability without
persona-provenance is aesthetic; accountability with it is measurable.

- The trailer's value is a key from
  `willow-memory/willow/fleet_personas.json` (verbatim, lowercase) —
  `heimdallr`, `hanuman`, `loki`, `nestor`, `shiva`, `ganesha`, and the
  rest of the fleet. The `_meta` key is not a persona and is refused.
- Multi-persona commits (Loki authors an audit line, Heimdallr commits
  the record) carry two `Persona:` trailers, one per line. Every trailer
  must resolve.
- The trailer lives in the commit-message trailer block, next to the
  existing `Co-Authored-By` line, so `git interpret-trailers --parse`
  reads it cleanly.
- A commit that changes tracked code (`.py`, `.js`, `.sh`, `.md`, `.yml`,
  `.yaml`, `.sql`, `.json`, `.html`) and carries no `Persona:` trailer is
  drift. Merge commits are exempt (they carry no work, only structure);
  commits that only touch untracked files (worktree scaffolding, etc.)
  are exempt by nature.

Grandfather note: every commit landed before v0.9 (before this section
sealed) carries no persona provenance. The build corpus is therefore
not diffable against a hypothetical persona-loaded rerun — a real cost
of shipping this discipline late. §11 is hard from the commit that seals
it forward; no grace period.

Pinning tests (§11):

- `scripts/check_persona_provenance.py` — CI-called from
  `.github/workflows/tests.yml`. Enumerates
  `git log $GITHUB_BASE_REF..HEAD` (or `master..HEAD` locally), reads
  each commit's message trailer block, and fails if any code-changing
  non-merge commit has no `Persona:` trailer or names a persona outside
  the closed fleet set.
- `tests/test_persona_provenance_check.py` — pins the checker
  property-by-property against synthetic commits (clean; missing trailer
  → fail; unknown-persona value → fail; merge commit exempt; docs-only
  commit still requires the trailer since `.md` is tracked code under §3).

## §12 — Ratification

Persona provenance (§11) tracks who did the work. §12 tracks who
authorized it to leave the branch. No fleet persona has unilateral
authority to open a pull request, merge a pull request, or push to
master — not Heimdallr, not Hanuman, not Loki, not even Willow.

Willow's own persona (`willow-memory/willow/fleet_personas.json`)
seals this: *"Commit, PR, merge, patch, or wire the fleet without a
recorded authorization — [do not do]."* Willow is `trust: OPERATOR`,
which is the operator seat where the human trust-root's authorization
is recorded. She holds the seat; she does not sit above it.

### The discipline

- **Opening a PR** requires a `Ratified-by:` line as the last
  non-blank line of the PR body, naming the human authorizer and
  quoting verbatim the message that authorized the open. Format:
  `Ratified-by: <identifier> — "<verbatim quote>"`. It goes at the
  bottom — beneath the description and beneath the marks the agents
  left on the work (§11 `Persona:` trailers, attribution footers) —
  because it is the human's signature on what sits above it, and a
  signature goes last. Position is load-bearing either way: pinning it
  to one line means a `Ratified-by:` mentioned in passing mid-body
  cannot pass for a sign-off. One exception: tooling that appends its
  own attribution footer to a PR body server-side leaves the author no
  way to write below it, so a trailing machine footer of that exact
  shape (a horizontal rule, a "Generated by/with Claude Code" line, a
  bare session URL) is skipped when locating the sign-off. It is an
  allowlist of those lines, not a general "ignore trailing content"
  rule — any other text below the ratification line still fails.
- **Merging a PR** requires the same discipline at the merge action.
  When merged via API, the merge commit message must carry a
  `Ratified-by:` trailer citing the human quote that authorized the
  merge (separately from the PR-open authorization).
- **Pushing to master directly** is refused. All work reaches master
  through a ratified PR.
- **Standing authorizations** may cover a defined scope of work (e.g.
  "run it, keep the reorder" covering the 13-PR v0.9 plan's in-branch
  commits). A standing authorization must be recorded once in the
  branch's first substantive commit under its scope, with a
  `Ratified-by:` trailer citing the verbatim standing quote; every
  subsequent in-branch commit under that scope inherits it.

### Grandfather

PRs 1 through 11 in the Grove v0.9 stand-up were opened and merged
without recorded `Ratified-by:` metadata. Same gap-class as pre-v0.9
persona provenance: real, logged, not backfillable. See
`docs/design/pr14-carryovers.md`. §12 is hard from the commit that
seals it forward.

### Pinning tests (§12)

- `scripts/check_ratification.py` — CI-called on `pull_request` events.
  Reads the PR body from the GitHub event context, asserts the last
  non-blank line matches
  `Ratified-by: <identifier> — "<verbatim quote>"`. Fails the check
  otherwise. On merge, checks the merge commit message the same way.
- `tests/test_ratification_check.py` — pins the checker
  property-by-property against synthetic PR bodies (clean, including
  the real shape with `Persona:` and attribution above it, and the
  shape GitHub actually stores once its own footer is appended below
  it; missing line → fail; wrong format → fail; empty body → fail;
  ratification at the top → fail; ratification buried mid-body → fail;
  real prose below the line → fail; a footer with no ratification line
  at all → fail).
- `tests/test_ci_ratification_edited_trigger.py` — pins
  `.github/workflows/tests.yml` firing on `edited` pull_request events.
  The checker reads the body from the event payload, and a re-run
  replays the *original* payload, so without `edited` a PR that adds
  its `Ratified-by:` line by body edit stays red forever — reachable
  only by an empty commit or a close/reopen, i.e. forging a code event
  to satisfy a governance gate. The pin also holds
  `opened`/`synchronize`/`reopened` in the list, since naming `types:`
  replaces the default set rather than extending it.
