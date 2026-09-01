# How the fleet is wired

**b17: WGRV1 ΔΣ=42** · recorded 2026-08-30

`docs/ARCHITECTURE.md` is the canonical reference for **Grove**, and says so:
its scope line stops at Grove's own boundary, and it hands cross-repo pipelines
off to `willow-2.0/core/pg_bridge.py` — an archived repository — through a
sibling path that does not resolve. Three of its outbound links are dead today:

```
DEAD  ../willow-2.0/docs/db/WILLOW_SCHEMA.md
DEAD  docs/CROSS_REPO_BRIDGE.md
DEAD  docs/extractor/GROVE_DOCS_EXTRACTOR_SPEC.md
```

All three point at exactly the cross-repo wiring this document covers.

The drawio set in `governance/architecture/` draws the fleet as boxes and
arrows — which face talks to which. That is the right picture for placement and
the wrong one for wiring, because every arrow in it is a different mechanism.
One is a subprocess speaking line-delimited JSON-RPC. One is a Python import.
One is a Postgres trigger. One is an HTTP POST. An arrow cannot tell you that,
and it cannot tell you what happens when the thing on the other end is missing.

This document is the arrows, opened up. Every claim below was verified against
running code with all seven repositories installed in one container — see
`fleet-standup.md` for how that box was built.

---

## 1. Five transports, not one

| # | Between | Mechanism | Carried by |
|---|---|---|---|
| **T1** | Grove ↔ Postgres | connection pool + `LISTEN/NOTIFY` | `grove_db.py` |
| **T2** | Grove → Nestor | child process, line-delimited JSON-RPC on stdio | `grove/nestor_client.py` |
| **T3** | Grove → willow-mcp | **in-process Python import**, else HTTP POST | `grove/journal_writer.py` |
| **T4** | willow-mcp → Postgres | connection over the **Unix socket** | `willow_mcp/db.py` |
| **T5** | agent → Grove | MCP: stdio, or HTTP+OAuth on `:8765` | `grove/mcp_local.py` |

Plus two that carry no bytes between processes at all and are still load-bearing
wiring: **willow-mcp → kartikeya** and **nestor → willow-gate** are ordinary
Python imports, and **nestor → the charter** is a filesystem path resolved from
environment variables.

---

## 2. The seams

### S1 · Grove ↔ Postgres

**Mechanism.** A psycopg2 pool for queries, plus a *separate* dedicated
autocommit connection for `LISTEN` — deliberately not from the pool, because a
pooled connection can be handed to another caller mid-listen.

Live updates are a database trigger, not polling: every `INSERT` on
`grove.messages` fires

```sql
PERFORM pg_notify('grove_channel', NEW.channel_id::text);
```

so the payload is a channel id and the listener re-reads. The UI never learns
message content from the notification itself.

**Contract.** `WILLOW_DB_URL` wins if set. Otherwise Grove composes
`dbname=$WILLOW_PG_DB user=$WILLOW_PG_USER`, defaulting to `willow_20` and
`$USER`.

> **Gotcha.** willow-mcp reads the *same two variables* with a **different
> default database**: `willow`, not `willow_20` (`willow_mcp/db.py:89`). Set
> `WILLOW_PG_DB` explicitly whenever both are in play, or Grove and willow-mcp
> will quietly address two different databases and both will look healthy.

**Failure mode.** Missing DSN, missing table, or absent psycopg2 → `Unreachable`
(§4). Never an empty list.

---

### S2 · Grove → Nestor

**Mechanism.** `NestorClient` spawns a long-lived child:

```python
subprocess.Popen([self._exe, "serve"], stdin=PIPE, stdout=PIPE, text=True, bufsize=1)
```

and speaks one JSON object per line — write `{"jsonrpc":"2.0","method":…,"id":n}`,
`flush()`, then a single `readline()`. Requests are matched by incrementing id.
This is the minimal MCP-lines subset, not the full SDK.

The child is pinned to a store by environment, not by argument:
`_apply_nestor_store_env` sets `NESTOR_HOME` for a directory or `NESTOR_DB` for a
file, and adds `NESTOR_KEYRING` + `NESTOR_REQUIRE_SEAL_KEY=1` **only when a
keyring file exists beside the store**. That last conditional means Nestor fails
closed on seal verification only when a keyring happens to be present; with none,
it fails open. There are 0 sealed pairs today, so nothing is exposed — the moment
anything is sealed, that conditional is the thing to revisit.

**The domain rides in two different places, and both must agree.** This is the
seam that has now failed twice (see #12):

| Caller | Where the domain goes |
|---|---|
| `grove/nestor_client.py` | the **tool arguments** — `source_lang`/`target_lang` on `nestor_ask`, from `DECISION_DOMAIN` |
| `.mcp.json` | the **argv** — `nestor serve --source-lang … --target-lang …` |
| the bundle | `domain` plus every row in `pairs` |

Grove's client spawns bare `nestor serve` with no domain flags and passes the
domain per-call; the `.mcp.json` entry does the opposite. Same value, two
mechanisms, and nothing structural connected them until
`tests/test_nestor_bundle_domain.py`. A mismatch does not error — it answers
`✓ clear — no decision on record`, which is why the pin is structural and
stdlib-only: a wrong domain imports cleanly and only shows at query time.

**Failure mode.** Binary absent → `Unreachable("nestor binary not on PATH")`.
Reachable with no match → `None`. Those two are never collapsed.

---

### S3 · Grove → willow-mcp (the C11 seam)

**Mechanism — MCP ``tools/call`` via ``grove/willow_mcp_client.py``:**

```
(a) streamable HTTP:  {WILLOW_MCP_URL}/mcp  → tools/call kb_journal / kb_journal_read
(b) stdio child:      willow-mcp (no --serve) on the same seat
(c) neither          → Unreachable
```

Grove no longer posts to invented REST routes under ``/tools/*`` — willow-mcp
``--serve`` exposes MCP at ``/mcp``, not per-tool paths. See governance
proposal #25.

**Identity.** Grove's app id is `willow-grove` (`grove/journal_writer.py:42`) —
not `grove`. It is passed on **every** tool call; there is no session.

**The gate.** `kb_journal` is `@_guarded`. willow-mcp resolves
`$WILLOW_HOME/mcp_apps/<app_id>/manifest.json` and reads its `permissions` list,
which may name **permission groups or literal tool names** — `kb_journal` lives
in the `knowledge_write` group, while `schema_confirm_mapping` is gated
separately on purpose, because confirming a mapping is more consequential than
one write. Fail-closed: missing app id, missing manifest, or empty permissions
all deny, and a denial is deliberately indistinguishable from a missing file so
a probe cannot enumerate app ids. PGP signature checking activates only when
`WILLOW_PGP_FINGERPRINT` is set; otherwise the manifest is filesystem-trusted.

A denial reads:

```
gate: no manifest for 'willow-grove' (tool='schema_confirm_mapping') — denied
```

**Asymmetry — the write path exists and the read path does not.** `kb_journal`
is real. `kb_journal_read`, which `grove/journal_reader.py:188` looks up by
`getattr`, appears **zero times** in willow-mcp. Both of Grove's read paths
depend on it, so the HTTP fallback is not a second chance. The e2e mock
implements it, so the read-back suite is green against a tool that was never
built. Filed as **#16**.

---

### S4 · willow-mcp → Postgres

**Mechanism.** `get_pg()` connects over the **Unix socket** — no host, no port —
using `WILLOW_PG_DB` / `WILLOW_PG_USER`, autocommit, with a single cached
connection revalidated by `SELECT 1` and a `postgres_lifecycle` recovery attempt
on failure. A TCP-only Postgres is unreachable to willow-mcp even when `psql -h
127.0.0.1` works fine.

**willow-mcp does not own its schema — it adapts to yours.** This is the single
biggest difference from Grove and the easiest thing to get wrong.

Grove's rule 2 is *`grove_db.py` owns the schema*. willow-mcp's posture is the
opposite: `schema_profile.resolve(conn, app_id, table, canonical_fields)`
introspects whatever `knowledge` table already exists, proposes a mapping from
canonical field names (`id`, `content`, `domain`, `source`, `tags`) onto the real
column names via an alias ring, and **omits anything it cannot map**. A host
table that calls `source` something else is fine.

Writes stay **locked until a human confirms the mapping once**:

```python
schema_confirm_mapping(app_id="willow-grove", table="knowledge")
# -> {'confirmed': True, 'manifest_sha256': …, 'database': <fingerprint>, …}
```

The mapping is keyed by `db_fingerprint(conn)` + app id + table, so confirming
on one database says nothing about another.

**Drift is handled, and this is the good part.** A confirmed mapping is
re-validated against a fresh introspection *on every call*. If any confirmed
field's column has disappeared, `confirmed` is downgraded to `false` and
`schema_drift: true` is set — rather than building SQL against columns that may
no longer mean what the human confirmed they meant. Confirmation is not
permanent; it is a claim about a schema that is re-checked continuously.

---

### S5 · willow-mcp → kartikeya

An import, not a protocol. willow-mcp takes four things:

| Surface | Used for |
|---|---|
| `kartikeya.queue` — `TaskQueue`, `TaskRow`, `QueueStats` | `PgTaskQueue` **subclasses** `TaskQueue`; `WillowMcpTaskQueue is PgTaskQueue` |
| `kartikeya.sandbox` — `resolve_sandbox_config`, `is_vendored_default` | the worker's execution sandbox |
| `kartikeya.cgroup_setup` — `resolve_cgroup_parent` | places each task in a `kart.slice/kart-*` cgroup leaf with memory and pid caps |
| `kartikeya.check_kart_task` | task validation |

Containment degrades rather than failing: with a delegated `kart.slice` parent,
`run_shell` reports `resource_limit == "cgroup"`; without one it falls back to
`rlimit`. Both are tested. The fleet's containment policy itself is a JSON file
audited by three willow-mcp tests — no vault binds, no `~/github` blanket bind,
`kartikeya` present in `bind_try`.

---

### S6 · nestor → willow-gate

`nestor/cloud_seal.py` imports `willow_gate` **at module top** and raises at
import time when it is absent. That makes the `[gate]` extra load-bearing in a
specific way: nothing in Nestor's default read path may import `cloud_seal`, or a
`[gate]`-less deployment fails to import Nestor at all.

Nestor pins that with a test asserting `nestor.cloud_seal` is not in
`sys.modules` after the read path loads. The intent is right; the mechanism is
process-global and order-dependent — it passes 14/14 alone and fails when
`test_cloud_seal.py` runs first in the same process, which only happens once
`[gate]` is installed. See `fleet-standup.md` F3.

---

### S7 · nestor → the charter (the edge that closes the loop)

Not a protocol — a path, resolved from the environment by
`nestor/tests/_fleet_paths.py`:

| Function | Env override | Falls back to |
|---|---|---|
| `constitution_cases()` | `WILLOW_CONSTITUTION_CASES`, else `WILLOW_CHARTER_REPO` + `governance/compliance/cases` | several `~/github/...` layouts |
| `jeles_checkout()` | `JELES_REPO` | `/workspace/jeles`, `~/github/…/Jeles` |
| `willow20_checkout()` | `WILLOW_20_REPO` | archived willow-2.0 layouts |

`constitution_cases()` resolves to the `const_*.py` Trace-ID cards in **this
repository**, at `governance/compliance/cases/`. Nestor audits its own package
against Grove's constitution.

So the graph is not a tree: Grove needs Nestor installed to exercise its decision
seam, and Nestor needs Grove on disk to exercise its constitution audit. Neither
repository can fully test itself alone, and no diagram in
`governance/architecture/` draws that edge.

---

### S8 · Grove's own two surfaces

Distinct ports, distinct purposes, frequently conflated:

- **`127.0.0.1:8766`** — the served page (Starlette + uvicorn). Loopback. Rule 1
  is *no web ports for the dashboard*, and `GAP-004` records that the loopback
  bind is currently a **default rather than a gate**: `GROVE_SERVE_HOST=0.0.0.0`
  is warned about and then honoured, with no credential anywhere in the path.
- **`:8765`** — `grove/mcp_local.py --serve`, MCP over HTTP with a full OAuth
  2.0/PKCE authorization server (`grove/mcp_auth.py`). This is the remote-client
  surface, and the only one that authenticates.

Both are Grove *serving*; T2–T4 are Grove *consuming*. A diagram with one Grove
box hides that it is both.

---

## 3. Three disciplines hold it together

Everything above is heterogeneous. What makes it a system rather than a pile is
that three rules are honoured at every seam.

**The three-state contract (INVARIANTS §1).** Every reader returns populated, or
empty, or raises `Unreachable` — never collapsing the third into the second. The
endpoint layer translates a raised `Unreachable` into `503 {"state":
"unreachable", "reason": …}` without guessing. `reason` is operator evidence:
which path was probed, which variable was unset. This is why `None` from
`decision_check` means *reached, no sealed match* and never *could not reach*.

**Fail-closed authorization.** The gate denies on missing app id, missing
manifest, or empty permissions, and makes a denial indistinguishable from an
absent app.

**Confirm-once-then-revalidate.** A schema mapping is a human claim, re-checked
on every call, downgraded on drift.

Each is a different answer to the same question — *what do we do when the other
end is not what we expected?* — and the answer is never "pretend it is fine".

---

## 4. What a diagram cannot show, and this must

Four things that are invisible as arrows and expensive as surprises:

1. **An import is a transport.** S3(a), S5 and S6 move no bytes between
   processes. Installing a package rewires behaviour with no config change.
2. **The same env var means different things to different repos.**
   `WILLOW_PG_DB` defaults to `willow_20` in Grove and `willow` in willow-mcp.
3. **The domain lives in three places** (S2) and a disagreement reports success.
4. **Direction is not symmetry.** The C11 arrow between Grove and willow-mcp
   exists in the write direction and does not exist in the read direction, and
   the mock hides that.

---

## 5. Doc debt this leaves open

- `docs/ARCHITECTURE.md`'s three dead links should either be repointed or
  removed; two name paths in an archived repository.
- `docs/contracts/` holds exactly one contract (`MESSAGE_ENVELOPE.md`). S2's
  JSON-RPC framing, S3's `kb_journal` payload and S4's canonical field set are
  all contracts in practice and are documented only in the code that implements
  them.
- The drawio set has no edge for S7, which is the edge that makes the graph
  circular.
