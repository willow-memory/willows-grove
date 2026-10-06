# Rules cross table: boxes and branches (2026-10-06)

*Desk session, 2026-10-06. Collected by the agent from the docs and code named
in each row and reported here as found. Nothing here is ratified, and nothing
here changes a rule. Each source still holds its own rule.*

> "This isn't about making everything fit in a box — it's about making a box
> that the user and the system can grow together." (operator, 2026-10-01)

## How to use it

- The grid is 13 × 13: 13 rows (A–M) by 13 columns (1–13), all 169 cells
  filled. The label column and the number row are only there to give every
  cell its address, such as **B3** or **G2**.
- To use a rule, name its address. Each cell is a short label. "Where each
  row comes from" names the source for the whole row, and the index under it
  gives the full rule for the cells first gathered in this session (A1–A11,
  B1–B8, C1–C4, D1–D6, E1–E6, F1–F3, G1–G6, H1–H6).
- Once an address is given out it is never renumbered. When the grid needs
  to grow, the new rules go in a second grid.
- Picking cells is up to whoever is in the seat. This table doesn't choose
  any.

## For agents: how to fill this out

### Is there enough context here?

Enough to find a rule, not yet enough to act on one. What's here:

- Every cell has an address and a short label.
- Every row names its source.
- 50 cells (A1–A11, B1–B8, C1–C4, D1–D6, E1–E6, F1–F3, G1–G6, H1–H6) have
  their full text in the index.

What's missing:

- The other 119 cells are labels only, with no full text.
- No cell cites a line number, so nothing can be checked by hash yet.
- The 57 documents under "Also applicable" were found by title and have not
  been read.
- Row F refers to numbered boxes ("box 2", "box 6") whose list was not found.

"Filling this out" means closing those four gaps. It never means changing a
rule.

### The entry every filled cell gets

One row in the index, in this shape:

| Cell | Rule | Source | Standing |
|---|---|---|---|
| J5 | The rule in one or two sentences, in the source's own words where it has them. | `repo: path` §section, line N | unattested |

- **Source** is one file and one line or section. If a rule has two sources,
  name both, and say which one is canonical.
- **Standing** is `unattested` when an agent wrote it, `witnessed` when a
  second, independent check agreed, and `sealed` only when the operator seals
  it. No agent writes `witnessed` or `sealed` on its own entry.
- If the source can't be found, can't be read, or doesn't say it, write that
  in the Rule column (`not found`, `unreachable`, `source silent`). Never
  leave the cell blank and never fill it with a guess. This is INVARIANTS §1:
  three states, never collapsed.

### Fixed for every agent

1. **Addresses never move.** Don't renumber, reorder, merge or delete a cell.
   A cell that turns out wrong gets a correction in its entry, and the label
   stays until the operator changes it.
2. **Copy, don't compose.** The rule comes from the source. If the source and
   the label disagree, the source wins, and you flag the label. Don't fix the
   label yourself.
3. **One cell, one source line.** If you can't point to the line, the cell
   isn't filled.
4. **Propose, don't seal.** Every change is a commit on a branch with a
   `Persona:` trailer, and the operator decides whether it merges (G2–G5).
5. **No new rules in this grid.** It's full. A new rule goes in a second grid
   (`rules-cross-table-2`), with addresses that start from N1.
6. **Look in the box first** (C1–C3). The source paths are all local. Don't
   go to the web for anything in this table.
7. **The vault is the operator's key.** Row D describes the box rule. Don't
   read, open or write anything under the vault to fill it.

### Small agents (local models, short context, single-step tools)

Work one cell at a time:

1. Take the lowest unfilled address, reading left to right, top to bottom
   (A12, A13, B9 …).
2. Open only that row's source from "Where each row comes from".
3. Search it for the label's key words. Take the first passage that states
   the rule.
4. Write the entry: copy the passage (trim it to one or two sentences), with
   the path and line number, `unattested`.
5. If nothing matches, write `source silent` and the path you searched. Move
   on, and don't widen the search.
6. Stop after each cell. Your output is one index row and nothing else.

Don't read the "Also applicable" documents, don't touch other cells, and
don't decide whether a rule is right.

### Large agents (frontier models, long context, many tools)

Work one row at a time:

1. Read the row's source in full, plus the row's "Also applicable" documents.
2. Fill every unfilled cell in the row with an entry in the shape above.
3. Check the first 50 entries in the row as well. Add the line numbers
   they're missing, and flag any that no longer match the source.
4. For each "Also applicable" document, say which cells it bears on, or that
   it bears on none. Move a document that doesn't fit the row to the row it
   does fit, and say why.
5. Where two sources disagree, record both and name the conflict. Don't pick
   a winner, because that's the operator's call.
6. Record anything that belongs in a second grid as a proposal at the end of
   the row. Don't put it in this grid.
7. Row F: look for the numbered box list. If you find it, cite it. If not,
   record where you looked.

A large agent's output is one commit per row, with a summary: cells filled,
cells `source silent`, conflicts found, and documents moved.

## The grid

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** Box rules | Honest state | Gates fail closed, loud | Presence is a label; authority is a passkey | Reading open, saving guarded | Human seals, system proposes | Willow seat is where the human is | Egress: three keys + click | Portless | Hooks are doors | Auto-merge is a standing grant | Template ships the box | Exceptions declared, never silent | No front end is primary |
| **B** Security core | Model sees only its scope | Code fills, human seals | One hook: Read allow, Write ask | Cite outside the pool is `link_fail` | Mosaic rule | Unguessable ids | Seal binds to one hash | Serving code is the attack surface | Injected text: the model has no hands | Human reads the points, not just the sentence | Only the seal ledger is shared | Model gets only `{excerpts, joins[]}` | Uncitable excerpt → flowering first |
| **C** Look in the box first | Ask Nestor first | Then look in the box | Only then go remote | Silent corpus ≠ absence | Name which tier answered | Record that the box was checked | A skipped step fails loud | Greenfield archive is in the box | `superseded/` is in the box | Retired repos are a shelf | Refused ≠ retired | Rule 1: coverage is all of `~/github` | Rule 2: the PR is the extraction event |
| **D** willow-bot box rule | `WILLOW_HOME`, else `WILLOW_VAULT_BOX` | Blank is unset; `~` expands | Absolute path only | Must already exist | Made only by `provision.sh` | Resolve, never create | Steward state lives in the box | Script key path is in the box | Counters live in the box, not `~/.willow` | Carried-over counter keeps its mode | Carry-over lock held for the whole copy | Unconfigured reads as "not configured" | Every resolver uses the one rule |
| **E** willow-bot box workspace | Persistence | Isolation | Egress by request only | Auditability | Reach unchanged | No runs from GitHub triggers | No long-lived shells | No ambient current venv | No new MCP package or tools | No webhook surface changes | No bot-held tokens (broker only) | Doesn't replace Kart for seats | Model weights stay out (for now) |
| **F** One-script rules | The stamp | Every proposal cites | Reverse re-checks | `view` draws the heading from the stamp | The law = constitution + the user's half | Code checks the cite's form; a witness checks it's true | Unknown law is refused | Amends waits for the seal | Egress without a grant writes a card | Any internal error fails closed | Agent proposals can't ratify themselves | Same box → same bytes | No clock but the enter key |
| **G** Git branches | willow-mcp ruleset | Feature branch + PR | No persona merges alone | Standing grant in first commit | Trailers: `Persona:`, `Ratified-by:` | Session branch name | All commits on the feature branch | Reviewed shell work goes through Kart | Read-only git is fine | `hotfix/`: same rule, faster name | Merge commits are exempt | Release-please exempt on two conditions | Code PRs add a CHANGELOG bullet |
| **H** The tree | One tree, one soil | Grafts splice on | Sapwood → heartwood on seal | Growth before flowering | Model at a leaf | Gate only narrows | Session and bite: one machine, two scales | Entry never refuses on orientation | The Forge imports no fleet code | The flowchart is derived | Cloud is pollination, not metabolism | Pools collect; they aren't oracles | One nutrient policy at the soil |
| **I** The stack | Everything is a hash | New cites older hashes | Pointers, not prose | Code first, model last | Only a human makes it true | Three states, never collapsed | Pile it up; what stacks matters | The model's job is connections | Picture and compare | A pre-AI foundation | The database builds itself | The 3 / 7 / 13 / 23 rollup | Once / session / permanent |
| **J** Invariants | §1 Three-state contract | §2 Supersedes D7 | §3 Doc discipline | §4 Reader/endpoint coverage | §5 Trust order | §6 Manifests describe code | §7 Consent is real, not automatic | §8 Panels read live endpoints | §9 Seed reads real canon | §10 CI proves the invariants | §11 Persona provenance | §12 Ratification | §12 Grandfather (PRs 1–11) |
| **K** Operator decisions | D1 Canonical runtime | D2 Where the chain lives | D3 Home of the socket standard | D4 The browser door | D5 The #101 sealed record | D6 Friction ownership | D7 Forge refusal without Nestor | D8 u2u and the bridge | D9 Second front end | D10 Ingress: no tunnel by default | D11 Grants away from the box | D12 Helper commit persona | Kaggle benchmark comes first |
| **L** One-box phases | 0 Close the holes | 1 The socket standard | 2 Rat gets a door | 3 Front ends: one contract | 4 The lifecycle behind Rat | 5 Nestor behind Rat | 6 Egress: click to grant | 7 Portless | 8 The surface grows per user | 9 The template ships the box | Sequencing: what not to break | Gap pass | The first three bites |
| **M** The ladder and the seven | Rung 1: hash | Rung 2: code | Rung 3: embedder | Rung 4: small model | Rung 5: cloud | Rung 6: the human | boot | predict | record | gate | resolve | view | reverse |

## Where each row comes from

| Row | What it holds | Source |
|---|---|---|
| A | Box rules | `README.md` §0, §9, §10, §15; `session-2026-10-01.md`; CHANGELOG (PR 102) |
| B | Security core | `../one-script/README.md`, the security core |
| C | Look in the box first | `../the-forge-shape.md` §3, §12 |
| D | willow-bot box rule | willow-bot `willow_bot/paths.py`, `tests/test_box_rule.py` |
| E | willow-bot box workspace | `../willow-bot-box-spec.md` §3, §9, §11 |
| F | One-script rules | `../one-script/next-pile.md`, rules and `gate.py` |
| G | Git branches | willow-mcp `CONTRIBUTING.md`, `skills/worktree.md`; `INVARIANTS.md` §3, §11, §12; `CLAUDE.md` 5–6 |
| H | The tree | `../forge-convergence.md` §1, §1.5, §8 |
| I | The stack | `../one-script/README.md`, the stack (rows 1–13) |
| J | Invariants | `../../INVARIANTS.md` §1–§12 |
| K | Operator decisions | `README.md` §2 and §15 (D1–D12); `../one-script/next-pile.md`, constraints |
| L | One-box phases | `README.md` §3–§15 |
| M | The ladder and the seven | `../one-script/README.md` (resolve ladder); `../one-script/next-pile.md` (the seven) |

## Also applicable (shallow pass)

*Found by title and opening lines across willows-grove, willow-mcp and willow-bot (the Willow repo has no commits yet). Not read in full and not folded into the cells: each is a place to look next for that row.*

| Row | Documents |
|---|---|
| A | willows-grove: `docs/design/approval-broker.md` · willows-grove: `docs/design/u2u-security-limits.md` · willow-mcp: `docs/design/egress-request-seam.md` · willow-mcp: `docs/design/consent-toggles.md` · willow-mcp: `skills/consent.md` · willows-grove: `docs/design/one-box/research-2026-10-06.md` · willows-grove: `docs/design/one-box/instruction-files-2026-10-06.md` |
| B | willow-mcp: `docs/design/trust-architecture.md` · willow-mcp: `docs/design/willow-gate-seam.md` · willow-mcp: `docs/design/security-hardening-review-2026-07-08.md` · willow-mcp: `docs/design/deny-tools-completeness-review.md` · willow-bot: `SECURITY_AUDIT.md` |
| C | willow-mcp: `skills/external-guard.md` · willow-mcp: `docs/design/nestor-tool-route.md` · willow-bot: `docs/PRIOR-ART.md` · willows-grove: `governance/LOCAL_GITHUB_LAYOUT.md` |
| D | willow-bot: `INSTALL.md` · willow-bot: `docs/MOVE-STAY-BORROW.md` · willows-grove: `docs/design/vault-home-store.md` |
| E | willow-mcp: `skills/kart-tasks.md` · willow-mcp: `docs/design/kart-lift-spec.md` · willow-mcp: `docs/design/kart-productionization.md` · willows-grove: `deploy/kart-sandbox.md` |
| F | willows-grove: `docs/design/one-script/workflow.md` · willows-grove: `docs/design/one-script/constitution-proposal/README.md` · willow-mcp: `docs/design/bound-receipt-schema.md` · willow-mcp: `docs/design/build-loop-receipts.md` |
| G | willows-grove: `CONTRIBUTING.md` · willow-mcp: `ARCHITECT.md` · willow-mcp: `skills/review.md` · willow-mcp: `skills/tdd.md` · willow-mcp: `docs/design/brokered-push.md` · willow-mcp: `docs/design/fleet-versioning.md` |
| H | willows-grove: `docs/design/the-forge-shape.md` · willows-grove: `governance/proposals/2026-09-02-grove-hooks-and-skills.md` · willow-mcp: `docs/design/hooks-and-skills.md` · willow-mcp: `docs/design/session-lifecycle.md` · willow-mcp: `docs/design/stateless-session-state.md` |
| I | willows-grove: `docs/design/one-script/hashing-session-handoff-2026-10-05.md` · willows-grove: `docs/design/one-script/prompt-arms-2026-10-03.md` |
| J | willows-grove: `governance/CONSTITUTION.md` · willows-grove: `governance/CASEBOOK.md` · willow-mcp: `docs/design/permissions-matrix.md` · willow-mcp: `docs/design/pgp-and-persona.md` |
| K | willows-grove: `docs/design/one-box/review-2026-10-01.md` · willows-grove: `docs/design/forge-convergence.md` · willow-mcp: `docs/design/operator-tier-not-do-review.md` · willow-mcp: `docs/design/human-orchestrator.md` |
| L | willows-grove: `docs/design/one-box/parts-partition.md` · willows-grove: `docs/design/one-box/four-pieces-join.md` · willows-grove: `docs/design/one-box/one-script-join.md` · willows-grove: `docs/design/one-box/sketches.md` · willows-grove: `docs/design/one-box/verify-2026-10-02.md` |
| M | willow-mcp: `skills/orchestrator-routing.md` · willow-mcp: `docs/design/specialist-registry.md` · willows-grove: `governance/proposals/2026-09-02-local-inference-seam.md` · willow-bot: `loki/SPEC.md` |

## Index

### A — Box rules
Source: [`README.md`](README.md) §0, §9, §10, §15; [`session-2026-10-01.md`](session-2026-10-01.md), "Box rules added late in the session". The plan's own numbers are in brackets.

| Cell | Rule |
|---|---|
| A1 | **Honest state** [1]. Populated, empty or unreachable (plus `not_asked` and `unenforced`), never collapsed, always with a reason. |
| A2 | **Every gate fails closed, and loud** [1a]. This withdraws the earlier "shim fails open." |
| A3 | **Presence is a label; authority is a passkey** [1c]. The model runs as the operator's uid, so a uid alone never unlocks a human-only act. |
| A4 | **Reading is open; saving is guarded** [1b]. It works like a public repository: reading is a clone and saving is a contribution. A helper opens the PR and a named human merges it. Every write into the soil records who saved it and how. Narrowing the tool surface applies to writes, not reads. Still open: does the egress grant stay on the outbound read, or move to the save? |
| A5 | **The human seals; the system only proposes** [2]. |
| A6 | **The willow seat is wherever the human is** [3]. Helpers, Rat and dispatched seats never hold willow. |
| A7 | **Egress takes three keys plus the human's click** [4]. Egress means outbound. The grant card shows the destination, the literal payload and its size, and a one-time Yes covers only those bytes. Cloud model calls count as egress. A vendor CLI's own traffic is declared `egress: vendor (ungated)`. |
| A8 | **Portless** [5]. Helpers talk over Unix sockets, and the kernel checks the peer's uid. "One browser door, signed actions, everything else UDS; exceptions are declared, never silent." |
| A9 | **Hooks are doors, not verbs** [6]. The front end is a shim, and one local runtime decides. |
| A10 | **Auto-merge is the human's standing grant.** Only the human turns it on, for a declared scope. The checks still run, and it never merges on red. Anything out of scope asks. It can be revoked at any time and can expire. It is recorded. Comfort is earned per user. |
| A11 | **The workshop template ships the box, never a tree.** What grows per user: sealed rows, egress precedents, the model-facing tool set, Nestor's edges and the flowering threshold. |

### B — The security core
Source: [`../one-script/README.md`](../one-script/README.md), "The security core: the model never sees the box" (2026-10-05).

| Cell | Rule |
|---|---|
| B1 | The model is served only the points in its scope, named by hashes it can't guess, and returns only proposed rows. |
| B2 | Code fills out every box, and the human seals. The model never sees a box, so it has nothing to fill out wrong. |
| B3 | The one hook is `{"Read": "allow", "Write": "ask"}`. Everything else is no, including tools that don't exist yet. |
| B4 | A cite outside the served pool is `link_fail`. Code catches it and sends it to flowering; it is never accepted as an answer. |
| B5 | **The mosaic rule:** judge scope on the combination of points, not box by box. |
| B6 | Served ids are keyed (HMAC) or random, never a plain content hash. `h16` was too short; `h256` as of 2026-10-06. |
| B7 | A seal binds to one hash, never to an attempt or a session (the Janus case). |
| B8 | The serving code is the real attack surface. Keep it tiny, readable and sealed. |

### C — Look in the box before you look outside it
Source: [`../the-forge-shape.md`](../the-forge-shape.md) (operator, 2026-08-30). Steps C1–C3 are strictly in order.

| Cell | Rule |
|---|---|
| C1 | Ask Nestor. If the corpus answers, stop. |
| C2 | Look in the box, including archives, greenfield, `superseded/` and anything retired. "Retired is not gone; it is a different shelf." |
| C3 | Only then go remote, and say why the first two did not answer. |
| C4 | "A silent corpus is not proof of absence, it is proof nobody extracted." |

### D — The willow-bot box rule
Source: willow-bot `willow_bot/paths.py` (`env_box`, `willow_home`); `tests/test_box_rule.py`. The vault is the operator's key. This table describes the rule and touches nothing in the vault.

| Cell | Rule |
|---|---|
| D1 | The box is `WILLOW_HOME`, or failing that `WILLOW_VAULT_BOX`. There is no default box. |
| D2 | A blank or whitespace-only value counts as unset, and `~` is expanded. |
| D3 | It must be an absolute path. A relative one moves with the working directory. |
| D4 | It must already exist. A missing box is refused, because otherwise reads would say "empty" when the truth is "no box." |
| D5 | Only willow-data-vault's `bootstrap/provision.sh` creates it, never willow-bot. |
| D6 | The resolver works out a path and never creates one. |

### E — The willow-bot box workspace
Source: [`../willow-bot-box-spec.md`](../willow-bot-box-spec.md) §3 and §11 (spec, not built).

| Cell | Rule |
|---|---|
| E1 | **Persistence.** Box contents live under the bot's state root, not the checkout, and survive restarts. |
| E2 | **Isolation.** Every run goes through the existing Kart / forge-play / bubblewrap paths. There is no runner that trusts the bot's uid. |
| E3 | **Egress is by request only.** The bot never grants itself access. Lane A has no network, and lane B must pass the gate. |
| E4 | **Auditability.** Every run returns a stable `Result`, with its side effects listed. |
| E5 | **Reach unchanged.** No new top-level MCP server and no new discovery path. |
| E6 | Nothing runs in the box from a GitHub-triggered path until contributor policy is sealed. |

### F — The one-script rules
Source: [`../one-script/next-pile.md`](../one-script/next-pile.md), "Three rules from tonight".

| Cell | Rule |
|---|---|
| F1 | **The stamp.** `record` stamps every output at the OUT door: who, standing (unattested / witnessed / sealed), turn and time. The model doesn't write the stamp. |
| F2 | **Every proposal cites what it touches:** Cites, Amends, or None-because. Any change to the box counts as a proposal. A change that cites nothing stops at "box 6." |
| F3 | **Reverse re-checks** at checkout, on the heartbeat, when the law changes, and when the script's own version changes. Nothing is rewritten silently. |

Open: F refers to numbered boxes ("box 2" is identity by signature, "box 6" is "changed with no cause"). The full numbered list was not found in these repos.

### G — Git branches
Sources: willow-mcp `CONTRIBUTING.md` and `skills/worktree.md`; [`../../INVARIANTS.md`](../../INVARIANTS.md) §11–§12; [`../../../CLAUDE.md`](../../../CLAUDE.md) rules 5–6.

| Cell | Rule |
|---|---|
| G1 | willow-mcp `master` has a no-bypass ruleset: changes land only by PR with a green `test` check. Branch off the latest `master`, put the tests in the same PR, and merge with `--merge`, not squash. |
| G2 | Every change goes through a feature branch and a PR, and nothing is committed straight to `master`/`main`, not even quick fixes. Branches are named `fix/`, `feat/`, `chore/` or `hotfix/<slug>`, logged with `fork_log`, and deleted after merge. |
| G3 | No fleet persona can open a PR, merge, or push to master on its own authority, not even Willow (§12). |
| G4 | A standing authorization is recorded once, in the branch's first substantive commit under its scope, with `Ratified-by:`. Later commits in that scope inherit it (§12). |
| G5 | Every commit carries `Persona: <key>`, and every PR body ends with `Ratified-by:` and the operator's verbatim words. Merge commits and the bounded release-please pair are exempt (§11–§12). |
| G6 | A cloud session's branch is assigned by the harness (for example `ccr-…`) and doesn't follow G2's naming. Which one wins is open. |

### H — The tree
Source: [`../forge-convergence.md`](../forge-convergence.md) §1.5 and §8.

| Cell | Rule |
|---|---|
| H1 | **One tree, one soil.** Willow (human plus orchestrator seat) is the trunk: one `app_id`, one filing namespace, and the first to register with the gate. |
| H2 | **Grafts** (other repos, orgs and fleet apps) splice on with their own manifests. They don't get a second soil unless federation or promotion says so, and they follow the trunk's policy when they touch the operator's soil. |
| H3 | **Sapwood → heartwood.** Session drafts move into SOIL or KB only on the human's seal. Nothing crosses that line unsigned. |
| H4 | **Growth before flowering.** Pools and local x→y joins handle routine work. Cloud and fleet dispatch are for buds the pools can't close. |
| H5 | **The model sits at a leaf, never at a branch.** |
| H6 | **The gate only narrows.** Observe before enforcing. A session deposits drafts, and no session verb seals. |

---

ΔΣ=42
