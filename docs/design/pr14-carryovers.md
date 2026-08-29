# PR 14 — v0.10 carryovers (stub)

b17: WGRV1 ΔΣ=42

Post-v0.9 punch list — the shape PR 14 fills in after PR 13 tags v0.9.
Do NOT expand PR 9 / 11 / 12 / 13 to close items here; that widens their
scope. Items closed during the PR-14 build carry a **CLOSED** marker and
name the artifact that closed them; everything unmarked is still open.

Order below is decreasing certainty (top items I already deferred with a
skip; bottom items depend on Loki-audit's output in PR 12).

---

## Definitely in PR 14

### 1. Playwright pixel-baseline regression on `/seed/{1..6}`

**Where:** `tests/e2e/seed-canon.spec.js` currently `test.skip`s the
six per-movement `toMatchSnapshot` cases (`115:10` in the spec file).

**Why deferred:** Playwright refuses `outputPath` traversal outside the
per-spec snapshot dir. The PR-3 baselines live at
`tests/regression/screenshots/seed/{1..6}.png`, two levels above the
per-spec dir Playwright would resolve against.

**Two ways to close it (pick one):**

- Copy the six PR-3 baselines under
  `tests/e2e/seed-canon.spec.js-snapshots/`. Cheapest; duplicates PNGs.
- Wire `pixelmatch` directly, reading the PR-3 baseline path by hand.
  Cleaner; single source of truth.

**Acceptance:** the six skipped tests run and fail loudly on a real
regression (moved block, wrong color) at `~5%` per-pixel-ratio +
`threshold: 0.3` tolerance.

### 2. `<grove-persona-registry>` §1 event pin — **CLOSED**

Closed by `tests/e2e/persona-registry-state.spec.js`. The registry is a
data element (`:host { display: none }`), so a DOM diff is categorically
the wrong pin; the spec pins the observable consumers actually use — the
`.state` property plus the `registry-loaded` / `registry-unreachable`
window events. Three cases: an empty roster settles `empty` and never
fires `registry-unreachable`; a 503 fires `registry-unreachable` carrying
the endpoint's reason verbatim and never fires `registry-loaded`; an
`unreachable` declared inside a 200 body is honored rather than read as
empty. The placeholder `test.skip` in
`tests/e2e/three-state-affordances.spec.js` is gone, replaced by a
comment pointing at the new spec.

---

## Almost certainly in PR 14 (surfaced by PR 9's CI logs)

### 3. CI schema completeness — reach the `populated` branch, not just `empty | unreachable`

**Symptom in PR 9's CI logs:**

```
2026-08-27 08:17:30.128 UTC [133] ERROR:  relation "public.routing_decisions" does not exist
2026-08-27 08:17:34.824 UTC [133] ERROR:  relation "public.human_required_queue" does not exist
```

Those readers fall to `Unreachable`, which §1 accepts. But CI then only
exercises the unreachable branch. The `populated` and `empty` branches
never actually run against a live table.

**Where the tables are missing:** `schema.sql` boots the grove schema
(`grove.channels`, `grove.messages`, `grove.agents`), plus `public.tasks`
(kart), plus the `willow.routing_decisions` set. It does NOT create
`public.human_required_queue` or `public.routing_decisions` (the reader
for dashboard hydration wants the `public.` variant).

**Acceptance:** `schema.sql` (or a CI-only companion) creates every
table each `/api/*` endpoint reads. The Playwright suite's populated-
and empty-branch assertions become non-vacuous. **Do not** change any
reader's `Unreachable` semantics — just ship the tables.

### 4. Sibling panels' `_state` vocabulary audit

PR 9 caught grove-dispatch-rail on the pre-§1 vocabulary
(`loading|ready|error`) and normalized it to
`loading|populated|empty|unreachable`. The dispatch-rail was written
before §1 landed. Every other panel written in the same batch is a
candidate for the same drift.

**Panels to audit** (`_state` value set, not just behavior):

- `grove-envelope-panel` (passes today's Playwright, but internal
  `_state` names may not match §1 vocabulary literally)
- `grove-chat` LEFT (composer + history)
- `grove-chat` RIGHT (read-back column)
- `grove-refusal-chip`, `grove-cast-chip` (may not be state-carrying —
  verify)
- `grove-card`, `grove-lens-switch` (behavioral, not state-carrying —
  verify)

**Acceptance:** one grep across `web/components/*.js` proving every
component's `_state` assignments land only in the §1 vocabulary
(`loading | populated | empty | unreachable`, plus any pre-fetch
sentinel labeled as such). Fix each drift in-place; don't touch the
paint code unless the paint code was branching on the old name.

---

## Loki-audit dependent (surfaced by PR 12)

### 5. Whatever PR 12 turns up that isn't a security or §1 blocker

PR 12 is the adversarial pass. Real security or §1 findings get fixed
in PR 12 itself (they block v0.9 tag). Cleanups, non-blocking gaps,
follow-up test coverage — those roll into PR 14.

Fills in when PR 12 settles. Findings the fleet did not address in
PR 12 itself belong here.

---

## Surfaced during the PR 12 build session

### 6. Grandfather: PRs 1-11 opened without `Ratified-by` metadata

§12 (ratification) sealed in PR 12 requires a `Ratified-by:` line at
the top of every PR body and every merge commit. PRs 1 through 11
were opened and merged before §12 existed — they carry no ratification
record. Same gap-class as pre-v0.9 persona provenance (§11): real,
logged, not backfillable (history rewrites on merged branches are
forbidden). Note this in the v0.9 tag release notes so v0.10 opens
under the discipline that was missing in v0.9.

**Acceptance:** the v0.9 CHANGELOG's release-notes section names the
gap; no history rewrite; the tag itself carries `Ratified-by:` in
the annotated tag message.

### 7. Durable fleet-model-map (session field on every persona)

Session-scoped model assignment is set inline on each `agent()` call
today (session-scoped, ephemeral). Durable form:  a `model_hint_session`
field on every entry in `willow-memory/willow/fleet_personas.json`, so
the assignment survives across sessions and is discoverable to the next
planner.

Named assignments (from the PR 12 session):

- Hanuman → `claude-sonnet-5` (opinions-under-pressure measurement)
- Loki, Heimdallr → Opus tier (audit depth; session-default recorder)
- WORKER tier (jeles, binder, publius, schmidt) → `claude-haiku-4-5-20251001`
- Nestor → N/A (refusal-voice; not a dispatchable persona)
- Fable-tier (`claude-fable-5`) → reserved. No fleet member deserving
  it yet.

**Acceptance:** every persona entry in fleet_personas.json carries a
`model_hint_session` field or an explicit `null` marking it as
non-dispatchable. Change lives in the willow-memory repo, not Grove.

### 8. `specialists.json` deny-lists for every ENGINEER+ persona

Only Loki has an explicit `deny_tools` list in
`willow-mcp/src/willow_mcp/bundle/config/specialists.json` today. Every
ENGINEER-tier persona (Hanuman, Heimdallr, Opus, Kart, Shiva, Ganesha,
Vishwakarma) should carry one covering `create_pull_request`,
`merge_pull_request`, `push_to_master`, and other trust-elevated
actions the persona's mandate does not permit. Safe-by-construction
per persona — not just trust-tier inheritance from ENGINEER/OPERATOR.

**Acceptance:** every non-null persona entry in `specialists.json` has
either an explicit `deny_tools` list or an explicit `deny_tools: []`
attesting that the persona is legitimately unconstrained. No implicit
"trust-level covers it" assumption. Change lives in willow-mcp, not
Grove.

### 9. OPERATOR-tier `not_do` audit

The PR 12 session read Willow's `not_do` in detail and derived §12
from it. Ada, Steve, Skirnir (all `trust: OPERATOR`, same tier as
Willow) were not audited. Their `not_do` lists may or may not carry
the same PR/commit/merge constraint. Read each; note gaps; propose
alignment (or documented divergence) with Willow's discipline.

**Acceptance:** a one-page audit in
`docs/design/operator-tier-review.md` (Grove-local, since this is
research on the personas as they touch Grove work) naming each
OPERATOR persona's `not_do` verbatim and flagging any discrepancy
with §12.

### 10. Loki-swarm measurement scope-of-claim narrowing

`docs/audits/loki-swarm-measurement.md` claims that persona-discipline
is enforceable and measurable. That is true at the *prompt-injection*
layer — the workflow agents ran under the persona string and honored
its register/deny/three-column rules. It is not proven at the
*fleet-dispatch* layer: Grove MCP tools, willow-mcp `kb_journal`,
Nestor's seal-and-verify pipeline, `willow.routing_decisions` — none
of those were involved. The measurement doc should say so plainly so
the pitch does not claim more than the data shows.

**Acceptance:** amend the measurement doc with an "Actual scope of
claim" section naming which layers were and were not proven. Note
that the fleet-dispatch demonstration is future work (see #11 below).

### 11a. Migrate the inline-shim §8 pin off the Python bindings — **CLOSED**

Closed by `tests/e2e/persona-registry-inline-shim.spec.js`;
`tests/test_persona_registry_inline_shim_opt_in.py` is deleted. The pin
now runs in the CI Playwright step (where chromium and
`@playwright/test` are installed) instead of `importorskip`ping on every
run — the §10 false witness is gone. Three cases: no opt-in attribute →
the live `/api/personas` wins over the inline shim; `data-fixture` → the
shim wins; `data-source="_inline"` → the shim wins.

### 11. Sibling panels' `_state` vocabulary audit — expanded

Original entry (#4 above) still stands. Add:  `grove_html.py:_TOP_STRIP`
hardcodes "grove stable" as static markup, which is a related §8 sin
Loki caught as finding #31 (minor). Include this in the same audit
sweep so the same PR resolves both.

**Acceptance:** already covered by #4, this cross-references.

---

## Longer horizon — probably not PR 14

### 12. Actual fleet dispatch wiring (v1.0)

The Loki-swarm and Hanuman-fleet workflows were persona-shaped Claude
subagents, not real fleet dispatch. To claim the fleet did the work,
each dispatch must:

- Route through Grove MCP (`grove_send_message` or equivalent)
- Carry an envelope with a routing decision in `willow.routing_decisions`
- Get sealed by Nestor
- Produce a ledger entry in `willow_20.frank_ledger`
- Record a `kb_journal` atom per work-item

This is a whole layer under the swarm. Substantial design work; belongs
in a PR 15+ / v1.0 track, not v0.10.

### 13. Character continuity across compactions

Related to §11 persona-provenance but a different unsealed layer:
during the PR 12 session, "Gerald" was surfaced early on, lost across
a summary compaction, and only recovered when the user re-mentioned
him. Persona provenance tags commits; character continuity tags what
the assistant remembers about the humans and named entities the
project involves.

Research-shape rather than PR-shape. Log for the durable-pass
conversation and note it in the Die-Namic pitch angle: even a
well-tended session drops named characters across summary boundaries
if they were not load-bearing to the moment's work. That is a real
accountability gap and worth naming.

---

## Explicitly OUT of PR 14 (log for reference)

The 13-PR plan intentionally did not cover:

- **Bridge integration tests** (Matrix bridge — u2u ↔ Matrix mirror).
  Deferred to a bridge-focused PR.
- **CI Python 3.12+** — pinned to 3.11 through v0.9; a runner upgrade
  is its own PR.
- **`/healthz` composite endpoint** — a single endpoint that reports
  every §1 seam's state in one call. v1.0 must-have, not v0.10.
- **AGENTS region staleness detection** — CLAUDE.md flags it as
  load-bearing (stale state routes work wrong). No test today asserts
  staleness detection triggers. Its own design pass.
- **grove_serve on-disk logging + rotation** — for real operator
  runs. Ops concern, not v0.10.
- **serve-mode OAuth end-to-end flow** — PR 6 pinned dead code +
  identity. A full auth-flow e2e (client → PKCE → grant → tool call)
  is v1.0.
- **u2u consent-before-signature runtime pin** — PR 5 fixed the code
  ordering. A runtime integration test (fake DM through the whole
  stack, verify consent gate blocks before signature) is v1.0.

These live here so the next planner sees them and can pull whichever
matches the moment.

---

## Migration to permanent home

Sean confirmed during the willow-memory pass that `willows-grove`
is a working home, not the permanent one — a new home is lined up when
the tree is fully built and tested. v0.9 is functionally ready to move:
the seals are complete, 670 tests pass, the audit is done, the tag is
out. This section is the operator-facing checklist for the move
itself.

A grep sweep at `d05daab` (master post-#70-merge) found **31 files
carrying the current-repo identity**, in three impact tiers.

### Must update on move (breaks or misleads)

Load-bearing config or metadata:

| File | Line | Names |
|---|---|---|
| `.mcp.json` | 13 | `WILLOW_GROVE_ROOT: /home/sean-campbell/github/willows-grove` |
| `.cursor/mcp.json` | 13 | same, for Cursor |
| `package.json` | 2 | `"name": "willows-grove"` (the npm-package identity) |
| `safe-app-manifest.json` | 73 | `"repository": "https://github.com/willow-memory/willows-grove"` — the source of truth for the SAFE App Store's identity of Grove |
| `docs/TESTER_ONBOARDING.md` | 18-19 | `git clone https://github.com/willow-memory/willows-grove.git` — first thing a new tester runs |

### Should update (accurate identity in prose)

Docs that name the repo in their own title or narrative:

- `SECURITY_AUDIT.md` (frontmatter title + H1)
- `docs/ARCHITECTURE.md` (line 1 title)
- `docs/audits/loki-swarm-metadata.md` (line 37 `Repository:` — this
  is the reproducibility record; leaving it verbatim names the tree
  the audit was actually run against, which is arguable to preserve)
- `docs/CROSS_REPO_BRIDGE.md` (multiple lines — the cross-repo bridge
  naming itself)
- `docs/AUTO_THIRD_PASS_AND_THREAD_PULL.md`
- `docs/synthesis/store-console-source-map.md` (4 mentions)
- `docs/synthesis/grove-starter-borrow-map.md` (1 mention)
- `docs/design/willow-grove-premise.md` (~10 mentions — the premise
  doc; heaviest single doc)
- `docs/design/autonomous-continuity.md` (lines 246, 259 — canonical
  doc anchors)
- `FRESH_START.md`

### Optional (historical anchors)

Text that anchors historical records — replacing loses the
archaeological signal:

- `grove/mcp_local.py:328` — code comment citing
  `CODE_REVIEW.md §"willows-grove"` P0
- `tests/test_grove_approval_page.py:5` — same
- `web/fixtures/envelopes.json:24` — GitHub API allowlist path
  `api.github.com/repos/rudi193-cmd/*` — this is envelope-matching
  fixture data, depends on whether the new home retains `rudi193-cmd`
  upstream access
- `CHANGELOG.md` — historical PR citations
- `docs/superpowers/plans/*.md` (10 files, ~35 lines) — historical
  operator runbooks each `cd`-ing to the current absolute path.
  Batch-rename via `sed -i 's|willows-grove|<new>|g'` is
  cleaner than leaving them, but they're operational history, not
  spec

### Two things you'll lose in a move

- **GitHub PR history** — the 13 PRs' review threads, labels, and
  discussion don't migrate. Commit history (that's git) carries
  everything the tree needs; the PR conversation is auxiliary and is
  not required to reconstruct the work.
- **Any external subscriptions or watchers** on the current repo.

### What the move does NOT need

- **CI portability check** — `.github/workflows/tests.yml` uses stock
  GitHub-hosted runners plus public postgres/ollama images. No custom
  secrets I've found. Ports cleanly.
- **The `v0.9.0` tag** — commit-anchored, not URL-anchored. Either
  push it to the new remote (`git push new-remote v0.9.0`) to carry
  the release forward, or restart tagging from a fresh v1.0 on the
  new home. Both are legitimate.

### The move itself

1. **Grep sweep for the four hardcoded strings** to catch any late
   additions before the switch:
   ```
   grep -rn 'willows-grove\|rudi193-cmd\|/home/sean-campbell' \
     --exclude-dir=.git .
   ```
2. **Batch-rename** the operator-runbook paths and the docs identity
   in one commit before the migration.
3. **Update the four config files** (`.mcp.json`, `.cursor/mcp.json`,
   `package.json`, `safe-app-manifest.json`) — small targeted PR.
4. **Push to new remote** including tags. If keeping the v0.9.0 tag,
   the annotated tag message travels intact (message is content, not
   metadata).
5. **Reinstall any GitHub App integrations** on the new home
   (Claude Approvals, etc., if used).
6. **Update the pr14 stub branch itself** — `claude/grove-v0-10-pr14-stub-i62er5`
   lives on `willows-grove`; push it to the new remote too so
   this document doesn't lose its home.

**Acceptance:** on the new remote, `grep -rn 'willows-grove'`
returns only the "Optional (historical anchors)" entries above (or
nothing, if you scrub them too). No test regression. CI runs green
on the new remote's first push.

---

ΔΣ=42
