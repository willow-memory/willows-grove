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
| **`willow-v11-verification-edge.drawio`** | **containment and the check** — the seven nests on this box, drawn as nests, and which of them can be asked whether their contents still match. Measured 2026-09-01. |

`CURRENT-STATE-2026-08-28.md` reads v04 against what is actually on disk,
element by element, measured rather than recalled.

## v0.11 — why containment, and not a component diagram

v04 through v10 answer *what is wired to what*. v11 answers a different
question and is drawn differently for it: **what contains what, and what checks
inward.**

The box is not a stack of peers. Nestor's pair holds a warrant which holds an
evidence pointer; FRANK's entry holds the hash of the entry before it; the gate
narrows manifest ∩ tier ∩ capability; the vault's blueprint holds the shape of
a snapshot that holds a live box. It nests all the way down — which is what the
main product is named for, and it was worth drawing once as the thing it is.

The diagram's claim is one sentence: **a container asserts what it holds, and
without an inward check the assertion drifts.** Four nests can be asked and
answer honestly (`nestor_ledger_verify`, `frank_verify`, the gate on every
call, and `vault_intake.py` as of 2026-09-01). Three cannot, and all three had
already drifted when they were checked by hand that day — Kart's `bind_try`,
the Nest's classifier, and the code graph's roster. Each failed the same way:
silently, returning a shape indistinguishable from a true negative.

Not a status board. If a check is added or a seam closes, redraw it — the
figures are dated on purpose.

## v0.8 is a draft, and stays one

`willow-v08-toolchain-path.drawio` is different in kind from the rest of this
directory. v0.1–v0.4 are the operator's originals; v0.5–v0.7 are snapshots
taken on 2026-08-29 and are finished as of that date. **v0.8 is live.** It is
being molded as the shape settles, and it carries a REVISIONS box for that
purpose.

The rule: append to REVISIONS as it changes, and **what settles there graduates
to v0.7**, the composition map. A thing is not "in the architecture" because it
is drawn in a draft; it is in the architecture when it has moved to the map that
claims to describe the whole box.

Deliberately plain — no HTML markup in any label, so a box can be double-clicked
and retyped without fighting the file.

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
