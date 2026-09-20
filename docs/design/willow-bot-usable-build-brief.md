# willow-bot usable build brief

**Snapshot:** 2026-09-15; reconciled 2026-09-16 (2nd pass); reconciled
2026-09-20 (3rd pass) against `willow-bot@22e51f8` (main, 0.2.0) and
`willow-mcp@89ae5e5` (master, 2.57.0).  
**Target repository:** `/home/sean-campbell/github/workshop/willow-bot`  
**Broker repository:** `/home/sean-campbell/github/willow-memory/willow-mcp`

**2026-09-20 reconciliation, third pass.** Every gap the second pass left
open has since landed in code and shipped in a release; four of the six
gaps in the table below move to Resolved records, and the two that stay
carry residuals that live outside either repo (the operator's box, the
Jeles/Nestor corpus). The three decisions sealed 2026-09-16 (Row 15
`unit.reload`, Row 16 `pr.update`, gidgethub retired) are all built and
in the syscall table. Landed via willow-bot #28 (voice head_sha,
`X-GitHub-Delivery` dedup), #31 (seal-drain-on-tick under sealed
`72292afd`), #32 (0.2.0 cut); willow-mcp #572–#575 (seal-watch ledger
resolution, Nest escalation, and the release trains carrying
`bot_status.py`, `unit_reload_executor.py`, `pr_update_executor.py`,
`gate_request.py`). See "Landed since the second pass" below for the
per-item citations.

**2026-09-16 reconciliation, second pass.** The first pass read a willow-bot
clone that was 66 commits stale (`e249cf4`, last fetch 2026-09-14) and
concluded steps 2, 3, 5, 6 were unstarted. That was the clone, not the repo:
the desk had no advertised pull verb (gap `83af08a4deda`, fixed by willow-mcp
#551), and once `git_pull_execute` brought the clone to `553ab06` (PR #26
`feat/catch-up-in-tick`), codebase-memory showed most of the build order
already landed. willow-mcp master `0551ee9` = `origin/master` (2.49.0). Each
step below carries its verified state. Resolved from source that day:
`bc9945dd47da`, `3f24d2d4a243`, `378c2e57c3d0`, `1d737ffa2595`,
`07651e0c46ba`, `1f6b033ffca7`. `67282a6f6578` closed 2026-09-15 as a
misdiagnosis (SIGTERM timeout in `test_seal_daemon`, not Postgres auth).

Lesson for the next reader: a stale clone reads exactly like unbuilt work.
Pull before reconciling. And: read the tree at head before writing that
a residual is still open — the brief's own residuals had all landed by
the third pass, four days after the second.

## Goal

Make willow-bot a dependable PR steward: it keeps local default branches
current, opens and maintains reviewable PRs, reports its work on GitHub,
recovers missed webhook deliveries, and exposes enough runtime state for the
Willow seat to tell populated / empty / unreachable apart.

The bot must not merge PRs. Merge remains an operator-ratified act under
Willow's Grove `INVARIANTS.md` §12.

## Verify before building

The gaps below are evidence, not a substitute for reading the current trees.
Several older gap descriptions contain state that has since changed.

Before editing:

0. pip install codebase-memory-mcp and index willow-bot
1. Query codebase-memory for the bot, broker, PR-open, push, and
   steward decisions.
2. Read willow-bot `router.py`, `integrations/fleet_bridge.py`, and
   `willow_bot/steward/`.
3. Read willow-mcp `push_executor.py`, `pr_executor.py`, `repo_sweep.py`, and
   the corresponding tests.
4. Inspect the live GitHub App permissions and webhook subscriptions. Report
   unavailable configuration as unreachable, not absent.
5. Reconcile every gap against current source before claiming it is still
   open.

## What already works

- `git_push_execute` performs ordinary non-force pushes with a short-lived
  willows-bot installation token inside a ratified envelope.
- `pr_open_execute` opens PRs as willows-bot. PR #530 demonstrated the path
  live.
- The steward has a `sync_checkout()` implementation that fetches and
  fast-forwards a local default branch after a watched PR leaves the open set.
- Completed check-run webhooks are deposited into the upstream-steward inbox.
- Red CI can enter the human-required path.
- The bot has deterministic tick and heartbeat machinery.
- `whoami` now exposes `git_push_execute`, `git_pull_execute`,
  `gitsync_sweep`, and `pr_open_execute`, while identifying their name-gated
  status.

## Current incident proving the missing seams

willow-mcp PR #530 was built from stale local `master` and pushed without a
remote-base freshness check. GitHub required the operator to click **Update
branch**. That changed only the remote feature branch, so a later local CI fix
had to be reconciled in a worktree before it could be pushed non-force.

The reconciled commit then touched `.github/workflows/tests.yml`.
`git_push_execute` consumed its one-use envelope before GitHub rejected the
push because the App lacks workflow-write permission. The operator had to push
the commit manually.

These are separate failures:

1. The steward did not demonstrably keep the local default branch current.
   **Fixed in source:** `tick.run_loop` runs `run_sweep` → `run_catchup` →
   `run_install_receipts` each tick (willow-bot #25, #26).
2. Push and PR-open perform no remote-base ancestry preflight.
   **Fixed in source:** `remote_base.preflight_local_ancestry` /
   `preflight_via_compare`, called before citation in both executors.
3. The broker does not preflight whether the App may update workflow files.
   **Fixed in source:** `push_executor._preflight_workflow_paths` refuses
   `EWORKFLOW` before citation.
4. A failed remote permission check consumes the one-use push envelope.
   **Fixed in source** by 2 and 3 running before `authorize_and_cite`; a
   remote rejection after action still lands as `EPUSH`, distinct in the
   receipt.

## Open gaps: two records survive the third pass (2026-09-20)

Every gap the second pass left open at the code level has landed. The two
records that remain sit outside either repo — neither is a git-visible
gap.

| Gap | Scope | What is actually left |
|---|---|---|
| `4ef96ee6a3b0` | knowledge | willow-bot, the PR-time deposit, and fleet-bridge design are still missing from the Jeles/Nestor corpus agents are instructed to query first. Not visible from a git checkout; verify against the corpus itself. |
| `83af08a4deda` | desk | Pull/sweep advertised since willow-mcp #551 (2nd-pass close). Residual on the operator's box, not this repo: the willow-bot clone's `origin` remote still names the retired fork, and the pull left a local `main` beside the old `master`. |

`1d737ffa2595` is a specific child of the `acfd27ae3259` umbrella, not a
duplicate to delete — closed by the second pass, kept here for reference.

## Residuals that are not gap-tracked

Two things stay open that never had a gap number: they are an operator
env act and a governance question, respectively.

| Residual | Shape | What is actually left |
|---|---|---|
| `WILLOW_OPERATOR_GITHUB_LOGIN` | operator env | Set the variable on the box so bot-opened PRs are assigned. `pr_executor.operator_login` reads it; #551's receipt reported `assigned: false — none configured`. One line in the unit's EnvironmentFile. |
| Community-health vendoring | governance | Whether the fleet's `.github/PULL_REQUEST_TEMPLATE.md` and friends should be vendored into every fleet repo, or resolved via the org-template fallback that `pr_template.preflight` already does. Live decision (`07651e0c46ba` resolves org fallback); the vendor-or-not question is separate and ratifiable, not a bug. |

## Resolved records that must not be rebuilt

| Gap | Resolution |
|---|---|
| `f5bd3cc19bec` | `pr_open_execute` now opens PRs with the App token; PR #530 returned HTTP 201. |
| `1f7d1d62207b` | `whoami` now uses the enforcement predicate and lists `git_push_execute`, including its explicit orphan classification. |
| `bc9945dd47da` | Remote-base ancestry preflight: `remote_base.preflight_local_ancestry` (push) and `preflight_via_compare` (PR-open), both before citation. Resolved 2026-09-16 from source. |
| `3f24d2d4a243` | Workflow-path preflight: `push_executor._preflight_workflow_paths` refuses `EWORKFLOW` before the envelope is cited. Granting the App `workflows: write` is still an operator act. Resolved 2026-09-16 from source. |
| `378c2e57c3d0` | In-repo template enforced: `pr_template.preflight` refuses `EBODY` before citation. Org-template fallback and title/body update remain open under `07651e0c46ba` and step 4. Resolved 2026-09-16 from source. |
| `67282a6f6578` | Misdiagnosis: the red leg was a SIGTERM timeout in `test_seal_daemon`, not Postgres auth. Closed 2026-09-15. |
| `8d1bcb2b7c02` | Red CI reaches the seat: `tick.run_ci` reads the deposits file from its own offset and files `human_required` items for red conclusions, idempotent on `(head_sha, check_run_id)`. Confirmed at `553ab06`; the earlier doubt was a stale clone. |
| `1d737ffa2595` | `inbox.ingest` consumes `check_run` items with every terminal conclusion kept distinct. Resolved 2026-09-16 from source. |
| `1f6b033ffca7` | Sweep, catch-up and install receipts run in the tick (willow-bot #25, #26); broker pull/sweep verbs advertised (willow-mcp #551). Resolved 2026-09-16. |
| `07651e0c46ba` | Org template fallback is live: `pr_open_execute` on #551 resolved `org:willow-memory/.github:pull_request_template.md` and refused `EBODY` until the body matched. Resolved 2026-09-16. |

### Landed since the second pass (resolved 2026-09-20 from source)

| Gap | Resolution |
|---|---|
| `acfd27ae3259` | Both code residuals landed. (a) Status comment / bot-check per head SHA: `willow_bot/steward/voice.py` implements `_latest_head_sha_by_pr`, `_status_comment_body`, `_check_conclusion`; `integrations/fleet_bridge.py:248,313` writes `head_sha` onto `pull_request` and `check_run` inbox items — willow-bot #28 `feat/voice-check-run-and-residues`, pinned in `tests/test_pr_voice.py`. (b) `X-GitHub-Delivery` dedup at the boundary: `bot.py:74` reads the header, `willow_bot/delivery_dedup.py::mark_seen` short-circuits a redelivery before dispatch, pinned in `tests/test_delivery_dedup.py`. The one non-code residual (`WILLOW_OPERATOR_GITHUB_LOGIN`) moves to the residuals table above. |
| `a6c0926d7e83` | Closed by sealed decision `0031ab90` (2026-09-16): gidgethub is not required; the prior-art commitment is retired. Verified: no `gidgethub`/`gidget` references remain in willow-bot at `22e51f8`. |
| `158600e03598` | Seat's half of the read-only status surface landed. `src/willow_mcp/bot_status.py::read_status()` runs `willow-bot-steward status` (bounded, ≤5s), and translates every failure mode into the §1 three-state contract — `binary_missing` / `nonzero_exit` / `timeout` / `unparseable` distinct on the unreachable side; passes through to the bot's own populated/empty otherwise. Exposed as MCP verb `bot_status(app_id)` at `src/willow_mcp/server.py:4935`, pinned in `tests/test_bot_status.py`. |
| `5ecb87cfdf56` | Explicit-ask surface built: `src/willow_mcp/gate_request.py` writes the request row at the DENIAL site (not from the agent), closing the gap the module's own docstring names verbatim ("the seam was built from the operator's end inward and stopped one step short of the agent"). The orphan `gate_request` declaration is the module that got that name. |

## Build order

### 1. Make push and PR-open safe before making them broader — BUILT

Verified in willow-mcp source 2026-09-16 (`push_executor.py`,
`pr_executor.py`, `remote_base.py`):

- Remote base is fetched/queried before `git_push_execute`
  (`preflight_local_ancestry`) and `pr_open_execute` (`preflight_via_compare`).
- Behind or diverged heads refuse `ESTALE`; a failed fetch refuses `EFETCH`;
  a repo whose remote HEAD is not advertised reports `state="skipped"`
  rather than a pass.
- Outgoing ranges touching `.github/workflows/**` are detected; App
  capability is checked via an idempotent token mint; missing scope refuses
  `EWORKFLOW`.
- All of the above run before `authorize_and_cite`, so no refusal consumes
  the one-use grant. A remote rejection after action is `EPUSH`, distinct.
- Tests name `ESTALE`, `EWORKFLOW` in `tests/test_push_executor.py`,
  `tests/test_pr_executor.py`, `tests/test_pull_executor.py`.

Not covered by this step, still true: workflow mutation is not a separately
visible authority class (the App simply either has `workflows: write` or
not), and the operator has not granted that permission. Force-push remains
`--force-with-lease` only on the host path; the App path takes `force` as a
bound.

### 2. Make steward synchronization convergent — BUILT

Verified at willow-bot `553ab06` (#25 `feat/sweep-install-receipt`, #26
`feat/catch-up-in-tick`): `tick.run_loop` runs `run_sweep` → `run_resolve`
→ `run_install_receipts` → `run_mirror` → `run_ci` → `run_catchup` →
`run_audit` → `run_voice` per tick, each step wrapped so one failure does
not kill the rest. The acceptance list below has not been walked item by
item against the tests; treat it as the checklist for that pass.

Original spec:

- Keep webhook-first behavior, but run a periodic App-authenticated catch-up
  reconciliation inside the steward tick.
- Reconcile all tracked repositories, not only PRs observed leaving one
  in-memory/open-set snapshot.
- Fetch and fast-forward clean local default branches.
- Report dirty, ahead, diverged, missing-checkout, and install-failed as
  distinct states.
- After a successful default-branch update, refresh the intended editable
  runtime and record the installed source commit.
- Do not switch a checkout away from an active feature branch behind an
  agent's back. Use a dedicated default-branch worktree or another
  concurrency-safe layout.

Acceptance:

- A missed merge webhook is repaired by the next catch-up tick.
- Repeating the same tick is idempotent.
- A dirty or diverged checkout is reported and left untouched.
- Heartbeat/receipt names bot commit, checkout commit, installed commit, and
  last successful reconciliation.

### 3. Give the bot a visible, idempotent PR voice — BUILT

Verified at willow-bot `22e51f8` (main, 0.2.0) and willow-mcp `89ae5e5`
(master, 2.57.0):

- **Built:** labels — `steward/voice.run_voice` converges the `willow-bot/*`
  owned set (`audit-dispatched`, `ci-red`) per tick and never touches
  labels outside that prefix.
- **Built:** `check_run` consumption — `inbox.ingest` keeps every terminal
  conclusion distinct; `tick.run_ci` files reds as `human_required`
  items, idempotent on `(head_sha, check_run_id)`.
- **Built (third pass):** one status comment / one bot check per head SHA.
  `willow_bot/steward/voice.py` at `22e51f8` implements
  `_latest_head_sha_by_pr` (`webhook_signals` → `{repo#pr: head_sha}`),
  `_status_comment_body(key, head_sha, state, at)`, and
  `_check_conclusion(key, head_sha, state)`; `integrations/fleet_bridge.py:248`
  writes `head_sha` onto `pull_request` inbox items and `:313` onto
  `check_run` items. Landed via willow-bot #28
  `feat/voice-check-run-and-residues`; pinned in `tests/test_pr_voice.py`.
- **Built (third pass):** `X-GitHub-Delivery` keying. `bot.py:74` reads the
  header; `willow_bot/delivery_dedup.py::mark_seen(delivery_id)` is a
  boundary guard whose LRU (`$WILLOW_HOME/willow-bot/delivery-seen.json`)
  survives restart; a redelivery short-circuits to
  `{"ok": True, "dedup": "delivery_seen"}` before `router.route` runs.
  Pinned in `tests/test_delivery_dedup.py`.
- **Not configured (unchanged):** `WILLOW_OPERATOR_GITHUB_LOGIN` — the
  broker reads it (`pr_executor.operator_login`) and #551's receipt
  reported `assigned: false — none configured`. Operator's env, one line;
  now tracked in the residuals table above rather than under this step.

Acceptance:

- Webhook redelivery changes no durable count or duplicate comment.
- Every terminal GitHub check conclusion has an honest stored state.
- One current status comment and one current bot check are visible for each
  head SHA.
- The operator is assigned or the receipt says exactly why assignment was
  unreachable.

### 4. Enforce review shape — BUILT

Built in willow-mcp (`pr_template.py`): the repo template, or the
organization template when the repo has none, is resolved via the API and a
body missing required sections refuses `EBODY` before citation;
`enforce_template=True` is the default on `execute_pr_open`. Measured live
2026-09-16 on #551: `template_source = org:willow-memory/.github`, first
attempt refused, second accepted.

**Built (third pass):** governed PR title/body/labels update support.
`src/willow_mcp/pr_update_executor.py` implements Row 16 `pr.update`,
sealed `783bab4e` (2026-09-16). Deliberately narrow: title/body/labels
only, never merge/approve/close; labels are refused unless every requested
label sits under the `willow-bot/` prefix (`ELABEL`); the call goes
through `EnvelopeAuthority.authorize_and_cite` with a field-diff
near-miss reported as `EAMBIG`; a miss files an operator ask ("X wants
to update PR Y").

Remaining, unchanged from the second pass:

- Decide whether community-health files should be vendored into every fleet
  repo; do not silently copy them until that policy is ratified. Now
  tracked in the residuals table above.

Acceptance:

- API-created PRs satisfy the same template as web-created PRs.
- A malformed body fails before GitHub mutation.
- Updating title/body is auditable and cannot merge or approve.

### 5. Expose operations without granting mutation — BUILT

`willow_bot/status.report` (verified at `22e51f8`) reads running commit and
version, last heartbeat and tick receipts, a bounded journal excerpt, inbox
depth by kind, catch-up cursors and last successful sync, exposed as
`willow-bot-steward status`.

**Built (third pass):** the seat's half. `src/willow_mcp/bot_status.py`
resolves the steward binary (env override
`WILLOW_BOT_STEWARD_BIN`, else the venv entrypoint under `$WILLOW_HOME`),
runs it under a bounded timeout (default 5 s), and translates every
failure mode into the §1 three-state contract without collapsing them:
`binary_missing`, `nonzero_exit`, `timeout`, and `unparseable` are all
distinct causes on the unreachable side; a reachable outcome falls
through to the bot's own report (populated if any field is populated,
else empty). Exposed as MCP verb `bot_status(app_id)` at
`src/willow_mcp/server.py:4935`; pinned in `tests/test_bot_status.py`.
No writes, no envelope, no FRANK citation — a read, gated like one.

Original spec — a read-only status surface:

- Bot webhook/steward unit active state.
- Running bot commit/version.
- Last heartbeat and tick result.
- Recent bounded journal excerpt or equivalent structured receipt.
- Webhook inbox depth by event kind.
- Catch-up cursor and last successful local/runtime sync.

The surface must preserve populated / empty / unreachable. It must not map an
unreadable journal or missing DBus session to "unit absent."

### 6. Finish integrity and knowledge follow-ons

- ~~Hash-chain `ci_outcomes.jsonl`~~ Built: `deposits.compute_row_hash`,
  `_read_tip`/`_write_tip`, `verify_chain` (verified at `553ab06`).
- ~~Decide and record whether gidgethub remains required; implement it or
  remove the stale commitment.~~ Closed by sealed Nestor pair `0031ab90`
  (2026-09-16, "gidgethub retired"); no `gidgethub` references remain in
  willow-bot at `22e51f8`.
- Ingest current willow-bot and PR-time-deposit design into the intended
  Jeles/Nestor corpus with provenance. **Still open** — tracked as gap
  `4ef96ee6a3b0` in the surviving table above. Not verifiable from a git
  checkout.
- ~~Resolve the orphan `gate_request` declaration against the actual
  human-required request path.~~ Built: `src/willow_mcp/gate_request.py`
  produces the ask at the denial site; the "orphan declaration" is the
  module that got the name.
- ~~Fix the independent Postgres CI authentication flake.~~ Closed
  2026-09-15 as a misdiagnosis (`67282a6f6578`).

## Required tests

- Unit tests for remote-base ancestry: current, behind, ahead, and diverged.
- Push tests proving preflight happens before envelope citation/consumption.
- Workflow-path tests for permitted, denied, and unknown App capability.
- Steward catch-up tests with a deliberately missed webhook.
- Dirty and active-feature-checkout synchronization tests.
- `X-GitHub-Delivery` redelivery tests.
- Check-run conclusion coverage tests for all GitHub terminal states.
- PR comment/check idempotency tests keyed by head SHA.
- Template resolution tests for repo, organization fallback, and missing
  template.
- Three-state operational-status tests.
- End-to-end fixture: merge event -> catch-up -> local default fast-forward ->
  editable install receipt.

## Delivery constraints

- Use small PRs in the build order above; do not submit one omnibus bot rewrite.
- Every tracked-code commit needs the repository's required lowercase
  `Persona:` trailer.
- Every PR body must end with:
  `Ratified-by: <id> — "<operator's verbatim words>"`.
- Do not merge, grant GitHub App permissions, edit live systemd units, or
  deploy without a separately recorded operator act. "Recorded operator
  act" means a sealed Nestor decision and an envelope — the seal is the
  operator key (syscall-table verb 12: "operator key, FRANK-recorded, git
  history"). It does not mean a keyboard. Operator rule 2026-09-16: an act
  that cannot run through Kart or a broker verb when the product is bundled
  into the APK is a gap, not a note to the operator.
- Audit changes to credentials, webhook verification, envelope accounting,
  workflow mutation, or merge-adjacent behavior before push.
- Lint is `ruff check` in both repos. Neither CI nor pre-commit runs
  `ruff format --check`, and willow-mcp master does not pass it; a packet
  that says otherwise costs a builder a revert (Hanuman, 1DDD6672). Do not
  run `ruff format` on touched files until a deliberate repo-wide format PR
  lands.
- PR bodies go through `pr_open_execute`, which refuses `EBODY` before
  citation unless the body carries the org template's sections: Bite /
  What was done / Evidence / Out of scope / Next bite.

## Decisions sealed or proposed 2026-09-16

| Nestor pair | Decision | State (third pass 2026-09-20) |
|---|---|---|
| `06075e99` | Syscall-table row 15 `unit.reload`: a service restart after a pulled merge is a brokered act. Build: `unit_reload_execute` + seal-driven live-table sync (packet AA115574). | **BUILT.** `src/willow_mcp/unit_reload_executor.py` (docstring cites `06075e99` directly); syscall-table verb 15 present in `src/willow_mcp/bundle/constitutional/syscall-table.json`. Seal-driven live-table sync landed via `src/willow_mcp/seal_drain.py` + willow-bot #31 `feat/seal-drain-tick` under a later Nestor pair `72292afd` (2026-09-18): the seal watcher runs on the steward tick rather than as its own unit. |
| `0031ab90` | gidgethub is not required; the prior-art commitment is retired. Closes `a6c0926d7e83`. | **CLOSED.** No `gidgethub` references remain in willow-bot at `22e51f8`. |
| `783bab4e` | Row 16 `pr.update`: title/body/labels on a bot-opened PR under an envelope; never merge/approve/close. Builds after row 15 lands. | **BUILT.** `src/willow_mcp/pr_update_executor.py` (docstring cites `783bab4e` directly); syscall-table verb 16 present. |
| — | Seal-driven grants for the remaining terminal-only acts: egress lease (`ab65a9a1fdb3`), seat permission changes (Jeles' `f5d00bf2`/`21eaf829`), gap closure and the `DESK_CORE` cap (`b33e2e1720ab`), registry-row env (`e8b50531aab3`). | gaps, not yet proposed |

## Definition of usable

The bot is usable when an operator can leave a clean local checkout and an
authorized branch with it, and the system can:

1. prove the branch is based on current remote state;
2. push and open a correctly shaped PR;
3. put the operator and bot status visibly on that PR;
4. track every CI terminal state without duplicate delivery effects;
5. recover a missed webhook without a host `gh` command;
6. bring an operator-approved merge home and report the installed commit;
7. explain any refusal before consuming one-use authority;
8. never merge without a separate human-ratified act; and
9. restart the unit onto the pulled code under an envelope, so the merge
   loop closes from a phone (row 15, `unit_reload_execute`).
