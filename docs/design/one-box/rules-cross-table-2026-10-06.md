# Rules cross table: boxes and branches (2026-10-06)

*Desk session, 2026-10-06. Collected by the agent from the docs and code named
in each row and reported here as found. Nothing here is ratified, and nothing
here changes a rule. Each source still holds its own rule.*

> "This isn't about making everything fit in a box — it's about making a box
> that the user and the system can grow together." (operator, 2026-10-01)

## How to use it

- The grid is 13 × 13. Rows are A–M and columns are 1–13, so every rule has
  an address such as **B3** or **G2**.
- To use a rule, name its address. The index under the grid gives the full
  rule and where it comes from.
- 50 of the 169 cells are filled. Rows I–M and the empty columns are room to
  grow. A new rule takes the next free cell in its row, or a new row. Once an
  address is given out it is never renumbered.
- Picking cells is up to whoever is in the seat. This table doesn't choose
  any.

## The grid

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** Box rules | Honest state | Gates fail closed, loud | Presence is a label; authority is a passkey | Reading open, saving guarded | Human seals, system proposes | Willow seat is where the human is | Egress: three keys + click | Portless | Hooks are doors | Auto-merge is a standing grant | Template ships the box | | |
| **B** Security core | Model sees only its scope | Code fills, human seals | One hook: Read allow, Write ask | Cite outside the pool is `link_fail` | Mosaic rule | Unguessable ids | Seal binds to one hash | Serving code is the attack surface | | | | | |
| **C** Look in the box first | Ask Nestor first | Then look in the box | Only then go remote | Silent corpus ≠ absence | | | | | | | | | |
| **D** willow-bot box rule | `WILLOW_HOME`, else `WILLOW_VAULT_BOX` | Blank is unset; `~` expands | Absolute path only | Must already exist | Made only by `provision.sh` | Resolve, never create | | | | | | | |
| **E** willow-bot box workspace | Persistence | Isolation | Egress by request only | Auditability | Reach unchanged | No runs from GitHub triggers | | | | | | | |
| **F** One-script rules | The stamp | Every proposal cites | Reverse re-checks | | | | | | | | | | |
| **G** Git branches | willow-mcp ruleset | Feature branch + PR | No persona merges alone | Standing grant in first commit | Trailers: `Persona:`, `Ratified-by:` | Session branch name | | | | | | | |
| **H** The tree | One tree, one soil | Grafts splice on | Sapwood → heartwood on seal | Growth before flowering | Model at a leaf | Gate only narrows | | | | | | | |
| **I** | | | | | | | | | | | | | |
| **J** | | | | | | | | | | | | | |
| **K** | | | | | | | | | | | | | |
| **L** | | | | | | | | | | | | | |
| **M** | | | | | | | | | | | | | |

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
