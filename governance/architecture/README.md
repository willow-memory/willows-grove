# Architecture — the diagrams, recovered 2026-08-28

b17: WGRV1  ΔΣ=42

The operator's own drawings of how the box should be wired. They predate the
split into organizations, were never finished, and were **not** brought over
when the charter moved here.

## Why they were missed

`governance/README.md` records the relocation and lists what deliberately
stayed in the archive:

> `design/` (2.8 MB), `tools/`, `notes/`, `soil/`, `CLAUDE.md`, `AGENTS.md`,
> `ORIENT.md` — *left in the archive — repo-operating docs for a repository
> that no longer exists, and the grove has its own*

That call was right for most of `design/` and wrong for this subdirectory.
`design/architecture/` is not repo-operating documentation; it is the wiring
intent for the whole fleet, and it is the only place several decisions were
ever written down. It sat unreachable for a day, and in that time a session
reconstructed much of it from code — reaching the same conclusions the
diagrams already held.

The lesson is narrower than "check the archive": a directory named for the repo
it lived in can hold material about everything *except* that repo. `design/`
was classified by its parent rather than its contents.

## What is here

| file | what it is |
|---|---|
| `willow-v01.drawio` | first pass, 2026-07-20 (recovered from `~/Documents`, not the repo) |
| `willow-v02.drawio` | second pass |
| `willow-v03-full.drawio` | first full picture |
| **`willow-v04-full.drawio`** | **the last and most complete** — v0.3 + the ask-jeles product layer + the search split. `willow-v04-full.png` renders it. |
| `willow-new-user.drawio` · `-draft` · `-draftv,02.png` | the greenfield flow — what a new user's box looks like |
| `willow-session-start.drawio` | session entry |
| `github-corpus-map.drawio` | repos → corpus |

`CURRENT-STATE-2026-08-28.md` reads v04 against what is actually on disk,
element by element, measured rather than recalled.

## Status

**Unfinished, and still the reference.** v04 is dated 2026-07-20 and marks its
own gaps with `✗` and `◐`. Several have since closed and one — the big one —
has not:

> **(USER)-data-vault — target · Postgres and SOIL live in here · ✗ not built**

That node is the plan for where the data plane goes. It is still unbuilt, and
the generic `(USER)` is deliberate: for this operator the target is
`sean-data-vault`; for another it is wherever their own user-data-vault lands.

The element furthest from reality is the product layer — connected apps and
SAFE. v04 draws `Ask Jeles` as a SAFE app; Jeles is now a federated MCP server,
and there are 43 apps where v04 shows a handful. That part wants redrawing
rather than annotating.
