# Governance — the charter, relocated here 2026-08-28

The constitution and its supporting documents were the whole content of the
`willow` repository (`willow-memory/Willow`, on disk at
`~/github/willow-memory/willow`). That repository was archived 2026-08-27 to
`~/github-archive-willow-2026-08-27/willow`, and its charter had **no live home
on this box** between then and this move — readable only from the archive and
from 134 extracted claims pinned at `willow@ba332ae` in the household corpus.

The grove is the charter's home now because the grove is the watchman's seat
(`willows-grove` carries the Heimdallr identity, `role: "Watchman, gatekeeper"`).

## What moved, and what deliberately did not

| | where it is |
|---|---|
| `CONSTITUTION.md`, `PROTECTED_AGENTS.md`, `PROTECTED_PERSONS.md`, `AGENT_SERVICES.md` | **here** — they had no live home before this |
| the `governance/` tree (proposals, decisions, flags, compliance, materialized-mcp-apps, layout and migration docs) | **here** |
| `FINDINGS-2026-08-20-charter-docs-drift.md` | **here** — the audit that governs how the paths below were handled |
| `fleet.json` | `$WILLOW_HOME/fleet.json` — relocated earlier, not duplicated here |
| `mem_ratify/` | `willow-mcp/src/willow_mcp/mem_ratify` |
| `seed/` | `$WILLOW_HOME/seed` and `willow-mcp/seed` |
| `envelopes/` | **stayed in the archive.** Its own `MOVED.md` records that its default-path role went to `$WILLOW_HOME/constitutional/`; the archived `pre-approved.json` / `syscall-table.json` are the operator's real grants as of 2026-07-22 / 2026-07-06, kept as historical record. They differ from the live files because the live ones are current. Moving them here would have put a superseded copy beside a live one. |
| `design/` (2.8 MB), `tools/`, `notes/`, `soil/`, `CLAUDE.md`, `AGENTS.md`, `ORIENT.md` | left in the archive — repo-operating docs for a repository that no longer exists, and the grove has its own |

## About the paths in these documents

`FINDINGS-2026-08-20-charter-docs-drift.md` sets the method these documents are
maintained under, and its central rule applies to this move: *"The 42 dead paths
are not one defect. They separate into four classes, and treating them as one
would have made three of the four worse."*

So the relocation rewrote **only the sites stating where the charter lives** —
five of them, in `LOCAL_GITHUB_LAYOUT.md`, `materialized-mcp-apps/README.md`,
and `FLEET_PLACEMENT_DRAFT.md`. Everything else naming `willow-memory/willow`
was left exactly as written, and is not drift:

- **`FLEET_PLACEMENT_DRAFT.md` §40, §51** name the *agent identity* `willow`
  (`app_id`, `WILLOW_AGENT_NAME`) — a seat, not a directory. Unchanged by this
  move.
- **§313, §314, §434, §490, §613, the `2026-08-21-registry-path-repoint`
  tables, and `FINDINGS` §45** are records of what was true when they were
  written — the 2026-08-10 layout move and the 2026-08-21 transfer. A record of
  a past move is not a stale path, and rewriting one would destroy the history
  it exists to hold.

Two things in that second group are worth a reader's eye rather than an edit:
`FLEET_PLACEMENT_DRAFT.md` §490 states in the present tense that the charter is
"on disk at willow-memory/willow", and §613 lists ratifying the transfer as
outstanding. Both are now overtaken — by this relocation, and by both remotes
(`rudi193-cmd/Willow` and `willow-memory/Willow`) being archived. They are left
for the operator to amend, because deciding what a draft's open items now say is
a ratification, not a path repair.
