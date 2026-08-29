# The box as measured, 2026-08-28 — read against `willow-v04-full.drawio`

b17: WGRV1  ΔΣ=42

`willow-v04-full` is dated **2026-07-20** and is the last full picture drawn. It
was left in the archived `willow` repo when the charter moved here, classified
with `design/` as *"repo-operating docs for a repository that no longer
exists"*. It is not that. It is the wiring intent for the whole box, and most
of it still describes the box correctly.

This file is the diff: every element of v04, against what is on disk tonight.
Everything below was measured, not recalled. It exists so the diagram can be
refined against reality rather than against memory.

---

## The line that mattered most

v04's `(USER)-data-vault` node reads, verbatim:

> **(USER)-data-vault — target**
> Postgres and SOIL live in here
> **✗ not built** — today the data plane is:
> Postgres (system svc): KB 21,810 · FRANK · tasks · jeles
> SOIL: per-project stores (402 collections)
> `.willow`: config + handoffs (411 dirty ⚠)
> `sean-data-vault` 🔒 operator key, user-granted paths only

**Still `✗ not built`.** Postgres and SOIL are not in the vault. What is in
`~/sean-data-vault` as of tonight is snapshots — 290 MB of Postgres dumps, two
archive tarballs — plus the repo's older archive layers. The live data plane is
still where v04 says it is.

The generic `(USER)` in that node is deliberate and still correct: for this
operator the target is `sean-data-vault`; for another it is wherever their own
user-data-vault lands.

---

## Element by element

| v04 says | measured 2026-08-28 |
|---|---|
| **Postgres (system svc): KB 21,810 · FRANK · tasks · jeles** | `willow_20`, 254 MB — knowledge **21,914**, frank_ledger **1,206**, tasks **827**, attestations **75**. Eight databases became two tonight; the other is `willow_personal` (9 MB, 74 atoms, 10 ratified) — the personal lane, which v04 does not have. |
| **SOIL: per-project stores (402 collections)** | **22 collections** under `$WILLOW_HOME/store`. Either the 402 count was fleet-wide across all project roots, or the tree has been consolidated since. Worth resolving on the next pass. |
| **`.willow`: config + handoffs (411 dirty ⚠)** | `$WILLOW_HOME` = `~/github/willow-memory/.willow`, reached by symlink from `~/.willow`. Holds `vault.db` (0 secrets), `vault.key`, `dispatch_signing.key`, `env`, `fleet.env`, 22 collections, 11 agent manifests + `_federation`. |
| **Gate — Kart egress needs 3 keys: task_net cap + consent.internet + operator lease** | Unchanged and correct. `consent.internet` = **false**, active leases = **0**, so the lane is shut at two of three keys. |
| **User (operator) holds: vault key · net leases · ratification** | Unchanged. All three still operator-only, and #396 made the fourth egress class (`mcp_federation`) grantable for the first time. |
| **FRANK ledger ✓ 927 entries, chain unbroken** | **1,206** entries, latest today. |
| **willow-mcp — the hub** | Live. ~180 verbs. |
| **willow unified server (legacy) — ◐ retire → willow-mcp** | Retirement in progress and now visible in the seal record: three natural-language routes to `willow_web_*` were **rejected** tonight with the reasons *"Jeles carries web search"*, *"Jeles covers this"*, *"willow web fetch can be retired now that Jeles is wired"*. |
| **Web primitives (hub target): web_search · web_fetch · jeles_search — ✗ not on hub yet** | `willow_web_search` / `willow_web_fetch` / `willow_institutional_search` **are** on the hub now — and are the three being retired in favour of Jeles. Note `willow_web_fetch` has **no Jeles equivalent**; there is no `corpus_fetch`. |
| **jeles-remote — fly.dev, stateless institutional lane** | Retired. Jeles is now a **federated MCP server** — `jeles-corpus`, `server_id 8cae3d1dcdf4`, PGP-signed, the first and only entry in the ratification registry. |
| **Kart — bwrap sandbox, fast + batch lanes ✓ live** | Fast lane live (`willow-mcp-worker-fast.service`). The `kart-worker` / `kart-worker-batch` units point at `~/SAFE/.venv`, **which no longer exists** — both inactive and now unfixable in place, since `~/SAFE` was removed tonight. |
| **Ollama — 7 models on T500** | Unverified tonight. |
| **codebase-memory graph ✓** | Live, but **48 of 51 indexed projects have `root_exists: false`** — `search_code` greps the filesystem and returns an *empty success* for a tree that is gone. |
| **Grove bus · Discord bridge ✓** | Not exercised tonight. Grove is gate-denied to the `jeles` seat, so a specialist cannot post its own work there. |
| **Daemons: gitsync 25min · kart workers ✓ · grove ✓ · discord ✓** | **One** unit running: `willow-mcp-worker-fast`. The rest are inactive. |
| **human_required queue — 3 open** | 15 rows in `willow_20.human_required_queue`. |
| **Constitution — Draft 0.7, ΔΣ=42** | Relocated here as `governance/CONSTITUTION.md` (PR #6). v04 shows it living in the `willow` repo, which is archived. |
| **Envelopes — `envelopes/pre-approved.json`** | Stayed in the archive; the live registry is `$WILLOW_HOME/constitutional/`. Four envelopes still name `rudi193-cmd/*` after the org transfer (gap `df81cbd8654e`) — and scalar bounds compare by exact string, so the **true** repo name is refused while the old one is admitted via GitHub's redirect. |

---

## The two the operator flagged as changed

**Connected apps and SAFE.** v04 shows `Ask Jeles (SAFE app)` as *the* federated
search product, `repo: safe-app-store-public/apps/ask-jeles`, reaching
`corpus → local KB → web → institutional`.

Today there are **43 apps** under `safe-app-store-public/apps/`. `ask-jeles`
still exists as a directory but the work moved into the `Jeles` repo, which is
now a federated MCP server rather than a SAFE app. So v04's product layer is
the element furthest from current reality, exactly as flagged, and is the part
that most needs redrawing rather than annotating.

---

## What v04 called unbuilt that now exists

- **The federation lane.** v04 draws Ask Jeles as a product outside the hub.
  The hub now federates: `federation_discover` / `list_servers` / `call`, with
  authorization as the intersection of a caller's manifest grant and an
  operator-ratified server's advertised tools. Unreachable until tonight —
  `mcp_federation` was enforced by `permitted()` and grantable by nobody.
- **A personal lane.** `willow_personal`, its own database, separable by
  `pg_dump`. Not in v04.
- **A route catalog.** 112 natural-language → verb mappings, 109 sealed.

## What is still `✗`

- Postgres and SOIL in the user data vault — the headline above.
- **Kart cannot see the vault**: `sean-data-vault` appears **zero times** in
  `kart-sandbox.json`, and sits outside the `~/github` operator-desk bind. If
  the store moves before that bind exists, every sandboxed task opens a root
  that is not there and reads an **empty store** — passing every gate on the
  way, because scope matches, the manifest permits, and consent is irrelevant.
- Lane enforcement: `lanes.py` is merged, `WILLOW_LANE` is undeclared, and
  nothing calls `refusal()` yet.
