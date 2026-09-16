# willow-bot usable build brief

**Snapshot:** 2026-09-15  
**Target repository:** `/home/sean-campbell/github/workshop/willow-bot`  
**Broker repository:** `/home/sean-campbell/github/willow-memory/willow-mcp`

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
2. Push and PR-open perform no remote-base ancestry preflight.
3. The broker does not preflight whether the App may update workflow files.
4. A failed remote permission check consumes the one-use push envelope.

## Open gaps: twelve unique records

| Gap | Scope | Build consequence |
|---|---|---|
| `acfd27ae3259` | willow-bot | Umbrella inventory: no PR voice/check/labels, reviewer path dark, weak delivery dedup and catch-up, incomplete event coverage, no self-deploy, cleanup, or sufficient observability. |
| `a6c0926d7e83` | willow-bot | Prior-art freeze only partly landed: CI outcomes lack a hash chain, catch-up remains outside the tick, and the gidgethub decision is unresolved. |
| `1d737ffa2595` | willow-bot | `check_run` events are deposited into the webhook inbox but the steward inbox skips non-`pull_request` items. |
| `1f6b033ffca7` | bot/runtime | Merged releases do not reliably update local checkouts and editable installs. |
| `bc9945dd47da` | bot/broker | No fetch-and-ancestry check before push or PR open; active feature branches can be stale. |
| `3f24d2d4a243` | bot/broker/config | The GitHub App cannot update workflow files, and the broker discovers that only after attempting the push and consuming its envelope. |
| `378c2e57c3d0` | bot/broker | PR-open does not enforce the repository or organization PR template and offers no governed title/body update path. |
| `158600e03598` | bot/operations | The Willow seat cannot read the bot unit's active state, running commit, or recent journal through a read-only tool. |
| `67282a6f6578` | CI | The willow-mcp matrix has an intermittent Postgres runner-authentication failure that muddies merge readiness. |
| `5ecb87cfdf56` | willow-mcp broker | Brokered push mostly landed, but the explicit-ask surface and orphan `gate_request` declaration remain unreconciled. |
| `07651e0c46ba` | repository scaffolding | Organization-level PR/community templates are invisible to local agents when a repo has no local copy. |
| `4ef96ee6a3b0` | knowledge | willow-bot, the PR-time deposit, and fleet-bridge design are missing from the corpus agents are instructed to query first. |

`1d737ffa2595` is a specific child of the `acfd27ae3259` umbrella, not a
duplicate to delete.

## Resolved records that must not be rebuilt

| Gap | Resolution |
|---|---|
| `f5bd3cc19bec` | `pr_open_execute` now opens PRs with the App token; PR #530 returned HTTP 201. |
| `1f7d1d62207b` | `whoami` now uses the enforcement predicate and lists `git_push_execute`, including its explicit orphan classification. |

## Build order

### 1. Make push and PR-open safe before making them broader

Implement in willow-mcp:

- Fetch or query the remote base before `git_push_execute` and
  `pr_open_execute`.
- Compare the proposed head against the current remote base.
- Refuse with a structured stale-base result when the head is behind or
  diverged. Never silently force-push.
- Detect whether the outgoing commit range modifies
  `.github/workflows/**`.
- Preflight App capability for that path before citing or consuming a
  one-use push envelope.
- Keep workflow mutation as an explicitly visible higher-authority class if
  the App receives that permission.
- Distinguish refusal before action from remote rejection after action in the
  receipt and human-required item.

Acceptance:

- A current ordinary-code branch pushes and opens normally.
- A stale branch is refused before PR creation.
- A workflow-changing branch either succeeds under an explicit workflow
  capability or is refused before envelope consumption.
- No path converts a non-force envelope into a force push.

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

### 4. Enforce review shape

Implement across willow-mcp and willow-bot:

- Resolve an in-repo PR template first, then the organization template.
- Refuse PR-open with a structured body-shape error when required sections
  are absent.
- Add governed PR title/body update support.
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
- Fix the independent Postgres CI authentication flake.

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
