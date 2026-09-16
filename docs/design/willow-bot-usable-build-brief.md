# willow-bot usable build brief

**Snapshot:** 2026-09-15; reconciled against source 2026-09-16  
**Target repository:** `/home/sean-campbell/github/workshop/willow-bot`  
**Broker repository:** `/home/sean-campbell/github/willow-memory/willow-mcp`

**2026-09-16 reconciliation.** Read via codebase-memory after re-indexing
both repos (willow-mcp at `0551ee9`, willow-bot at `e249cf4`; the seat cannot
run git, so whether either checkout is merged upstream is unverified). Step 1
and the template half of step 4 are built in willow-mcp source; gaps
`bc9945dd47da`, `3f24d2d4a243`, `378c2e57c3d0` resolved with source citations.
Steps 2, 3, 5 and 6 are not started. Gap `67282a6f6578` was closed 2026-09-15 as
a misdiagnosis (a SIGTERM timeout in `test_seal_daemon`, not Postgres auth).

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
   **Still open** (`1f6b033ffca7`).
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

## Open gaps: eight records (as of 2026-09-16)

| Gap | Scope | Build consequence |
|---|---|---|
| `acfd27ae3259` | willow-bot | Umbrella inventory: no PR voice/check/labels, reviewer path dark, weak delivery dedup and catch-up, incomplete event coverage, no self-deploy, cleanup, or sufficient observability. |
| `a6c0926d7e83` | willow-bot | Prior-art freeze only partly landed: CI outcomes lack a hash chain, catch-up remains outside the tick, and the gidgethub decision is unresolved. |
| `1d737ffa2595` | willow-bot | `check_run` events are deposited into the webhook inbox but `steward/inbox.ingest` skips non-`pull_request` items (verified at `inbox.py:80`, 2026-09-16). |
| `1f6b033ffca7` | bot/runtime | Merged releases do not reliably update local checkouts and editable installs. `merge.sync_checkout` fires only when a PR leaves the open set; nothing calls willow-mcp `gitsync_sweep` on a tick. |
| `158600e03598` | bot/operations | The Willow seat cannot read the bot unit's active state, running commit, or recent journal through a read-only tool. No such surface in willow-mcp `src/` (2026-09-16). |
| `5ecb87cfdf56` | willow-mcp broker | Brokered push mostly landed, but the explicit-ask surface and orphan `gate_request` declaration remain unreconciled. |
| `07651e0c46ba` | repository scaffolding | Organization-level PR/community templates are invisible to local agents when a repo has no local copy. `pr_template.preflight` resolves the in-repo template only. |
| `4ef96ee6a3b0` | knowledge | willow-bot, the PR-time deposit, and fleet-bridge design are missing from the corpus agents are instructed to query first. |

`1d737ffa2595` is a specific child of the `acfd27ae3259` umbrella, not a
duplicate to delete.

## Resolved records that must not be rebuilt

| Gap | Resolution |
|---|---|
| `f5bd3cc19bec` | `pr_open_execute` now opens PRs with the App token; PR #530 returned HTTP 201. |
| `1f7d1d62207b` | `whoami` now uses the enforcement predicate and lists `git_push_execute`, including its explicit orphan classification. |
| `bc9945dd47da` | Remote-base ancestry preflight: `remote_base.preflight_local_ancestry` (push) and `preflight_via_compare` (PR-open), both before citation. Resolved 2026-09-16 from source. |
| `3f24d2d4a243` | Workflow-path preflight: `push_executor._preflight_workflow_paths` refuses `EWORKFLOW` before the envelope is cited. Granting the App `workflows: write` is still an operator act. Resolved 2026-09-16 from source. |
| `378c2e57c3d0` | In-repo template enforced: `pr_template.preflight` refuses `EBODY` before citation. Org-template fallback and title/body update remain open under `07651e0c46ba` and step 4. Resolved 2026-09-16 from source. |
| `67282a6f6578` | Misdiagnosis: the red leg was a SIGTERM timeout in `test_seal_daemon`, not Postgres auth. Closed 2026-09-15. |
| `8d1bcb2b7c02` | Red CI reaching no seat — resolution note cites willow-bot `5cb6b25` (merged). The `e249cf4` checkout indexed 2026-09-16 shows no `run_ci` step in `tick.run_once`; either the clone is behind or the note is wrong. Verify before building step 3. |

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

### 2. Make steward synchronization convergent

Implement in willow-bot:

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

### 3. Give the bot a visible, idempotent PR voice

Implement in willow-bot:

- Post or update one bot-owned status comment per head SHA.
- Publish a bot check or commit status for stewardship state.
- Apply labels for states such as CI red, needs ratification, audit
  dispatched, and bot opened.
- Configure `WILLOW_OPERATOR_GITHUB_LOGIN` so bot-opened PRs reach the
  operator's assignment/review queue.
- Key webhook idempotency on `X-GitHub-Delivery` plus semantic event identity;
  do not append duplicate outcomes for redelivery.
- Consume `check_run` inbox rows and preserve success, failure, timed-out,
  cancelled, skipped, stale, neutral, and action-required distinctly.

Acceptance:

- Webhook redelivery changes no durable count or duplicate comment.
- Every terminal GitHub check conclusion has an honest stored state.
- One current status comment and one current bot check are visible for each
  head SHA.
- The operator is assigned or the receipt says exactly why assignment was
  unreachable.

### 4. Enforce review shape — HALF BUILT

Built in willow-mcp (`pr_template.py`, verified 2026-09-16): the in-repo
`pull_request_template.md` is resolved via the API and a body missing
required sections refuses `EBODY` before citation; `enforce_template=True`
is the default on `execute_pr_open`.

Remaining, across willow-mcp and willow-bot:

- Fall back to the organization template when the repo has no local copy
  (`07651e0c46ba`).
- Add governed PR title/body update support — no such verb exists in
  willow-mcp `src/`.
- Decide whether community-health files should be vendored into every fleet
  repo; do not silently copy them until that policy is ratified.

Acceptance:

- API-created PRs satisfy the same template as web-created PRs.
- A malformed body fails before GitHub mutation.
- Updating title/body is auditable and cannot merge or approve.

### 5. Expose operations without granting mutation

Implement a read-only status surface:

- Bot webhook/steward unit active state.
- Running bot commit/version.
- Last heartbeat and tick result.
- Recent bounded journal excerpt or equivalent structured receipt.
- Webhook inbox depth by event kind.
- Catch-up cursor and last successful local/runtime sync.

The surface must preserve populated / empty / unreachable. It must not map an
unreadable journal or missing DBus session to "unit absent."

### 6. Finish integrity and knowledge follow-ons

- Hash-chain `ci_outcomes.jsonl` or replace it with an existing fleet ledger
  primitive.
- Decide and record whether gidgethub remains required; implement it or remove
  the stale commitment.
- Ingest current willow-bot and PR-time-deposit design into the intended
  Jeles/Nestor corpus with provenance.
- Resolve the orphan `gate_request` declaration against the actual
  human-required request path.
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
  deploy without a separately recorded operator act.
- Audit changes to credentials, webhook verification, envelope accounting,
  workflow mutation, or merge-adjacent behavior before push.

## Definition of usable

The bot is usable when an operator can leave a clean local checkout and an
authorized branch with it, and the system can:

1. prove the branch is based on current remote state;
2. push and open a correctly shaped PR;
3. put the operator and bot status visibly on that PR;
4. track every CI terminal state without duplicate delivery effects;
5. recover a missed webhook without a host `gh` command;
6. bring an operator-approved merge home and report the installed commit;
7. explain any refusal before consuming one-use authority; and
8. never merge without a separate human-ratified act.
