# Standing the fleet up in one box

**b17: WGRV1 ΔΣ=42** · recorded 2026-08-30

Grove's test suite skips whatever it cannot reach. Nine of its tests named
things that live somewhere else — a database, a model server, a sibling
repository — and every one of them reported the same way a genuinely passing
test does: quietly, in a summary line nobody reads twice.

This document is what happened when those dependencies were actually stood up
rather than skipped past, in a disposable cloud container with no Docker
daemon. It is a runbook so the next session does not rediscover it, a record
of what could not be reached and why, and three findings that only appear once
the real thing is running.

The headline: **Grove's suite went 517 passed / 9 skipped → 522 / 4, and
willow-mcp's went 2874 / 14 → 2883 / 5.** Nothing was mocked to get there.

---

## 1. The dependency graph is circular

The fleet is usually drawn as a tree with Nestor at the root. It is not a tree.

```
willows-grove ──────► willow-mcp ──────► kartikeya
      ▲                    │                (sandbox, cgroups, TaskQueue)
      │                    └──────────────► jeles
      │                    └──────────────► nestor  [nestor extra]
      │                                        │
      │                                        └──► willow-gate  [gate extra]
      │                                        │
      └────────────────────────────────────────┘
         nestor audits itself against the charter, and the charter
         case cards live in willows-grove/governance/compliance/cases/
```

That last edge is the one worth knowing. Nestor's `tests/_fleet_paths.py`
resolves `constitution_cases()` to `<charter>/governance/compliance/cases` —
the `const_*.py` Trace-ID cards in **this repository**. Nestor audits its own
package against Grove's constitution. Six of Nestor's tests are unreachable
until Grove is on disk beside it, and Grove's own seams are unreachable until
Nestor is installed. Neither repo can fully test itself alone.

### Internal (fleet repos) vs external (services and libraries)

| Dependency | Kind | Needed by | Obtained |
|---|---|---|---|
| PostgreSQL 16 | external | Grove `kart_reader`, willow-mcp, the C11 write path | natively installed; `initdb` a cluster |
| `willow-mcp` | internal | Grove `journal_writer` / `journal_reader` | `willow-memory/willow-mcp` |
| `kartikeya` | internal | willow-mcp (`sandbox`, `cgroup_setup`, `TaskQueue`) | `willow-memory/kartikeya` |
| `jeles` | internal | willow-mcp; Nestor's jeles audit wants a *checkout*, not the wheel | `rudi193-cmd/Jeles` (public) |
| `nestor` | internal | Grove's decision seam; willow-mcp `[nestor]` extra | `Die-Namic-Systems/nestor` (public) |
| `willow-gate` | internal | Nestor `[gate]` extra → `nestor.cloud_seal` | `willow-memory/willow-gate` |
| legacy fleet monolith | internal (archived) | fleet Kart sandbox containment policy | archived clone (`WILLOW_LEGACY_MONOLITH_REPO`) |
| charter case cards | internal | Nestor's constitution audit | **this repo**, `governance/compliance/cases/` |
| `numpy` | external | willow-mcp voice stages | pip |
| `hypothesis`, `pytest-xdist` | external | Nestor's property lane | pip |
| `playwright>=1.62` (`nestor[browser]`) | external | Nestor's browser lane | pip — **must match Chromium build, see F4** |
| full git history + tags | external | willow-mcp changelog dedup | `git fetch --unshallow --tags` |

---

## 2. Runbook

Ordered. Later steps assume earlier ones.

### 2.1 Postgres, without a container runtime

CI uses a `pgvector/pgvector:pg15` service. There is no Docker daemon in this
environment — `docker` is on PATH but `/var/run/docker.sock` does not exist —
and none is needed: `postgresql-16` is installed natively, and `schema.sql`
requires only `pg_trgm`, never `vector`. The pgvector image is more than the
schema asks for.

`initdb` refuses to run as root, so the cluster runs as the packaged
`postgres` user:

```bash
PGBIN=/usr/lib/postgresql/16/bin
PGDATA=/var/lib/postgresql/grove-test
install -d -o postgres -g postgres -m 700 "$PGDATA"
install -d -o postgres -g postgres -m 775 /var/run/postgresql
echo postgres > /tmp/pgpw && chown postgres /tmp/pgpw
su postgres -c "$PGBIN/initdb -D $PGDATA -U postgres --auth=md5 --pwfile=/tmp/pgpw"
rm -f /tmp/pgpw
su postgres -c "$PGBIN/pg_ctl -D $PGDATA -l $PGDATA/server.log \
  -o '-p 5432 -k /var/run/postgresql -c listen_addresses=127.0.0.1' -w start"
```

Then CI's own bootstrap, unchanged:

```bash
export PGHOST=127.0.0.1 PGPORT=5432 PGUSER=postgres PGPASSWORD=postgres
psql -c "CREATE DATABASE willow_20_test;"
psql -d willow_20_test -f schema.sql
export WILLOW_DB_URL="postgresql://postgres:postgres@127.0.0.1:5432/willow_20_test"
```

`grove/nestor_client.py` and willow-mcp's `get_pg()` connect over the **Unix
socket** using `WILLOW_PG_DB` / `WILLOW_PG_USER`, not `WILLOW_DB_URL` — hence
the `-k /var/run/postgresql`. Both paths must work.

### 2.2 The fleet repos

```bash
git clone https://github.com/willow-memory/willow-mcp   ~/willow-mcp
git clone https://github.com/willow-memory/kartikeya    ~/kartikeya
git clone https://github.com/willow-memory/willow-gate  ~/willow-gate
git clone https://github.com/Die-Namic-Systems/nestor   ~/nestor-repo
git clone https://github.com/rudi193-cmd/Jeles          ~/Jeles

pip install -e ~/willow-mcp"[test,web,nestor]"   # pulls kartikeya + jeles
pip install -e ~/kartikeya
pip install -e ~/willow-gate
pip install -e ~/nestor-repo"[dev,keys,gate,browser]"   # browser → playwright>=1.62
pip install "pytest-xdist[psutil]" pytest-cov hypothesis shtab numpy
```

**Do not shallow-clone willow-mcp.** Four of its tests read tag history
(`test_changelog_dedup.py` needs `v2.18.0` to resolve). `git clone --depth 1`
causes four skips that look like missing features and are actually a missing
clone depth. `git fetch --unshallow --tags origin` fixes them.

Install Nestor's dev dependencies but **run its suite from the checkout** —
installing the repo over the PyPI `nestor-meaning` would swap the `nestor`
binary that `.mcp.json` resolves.

### 2.3 The willow-mcp gate manifest

`willow_mcp.server.kb_journal` is `@_guarded`. It denies any app with no
manifest, fail-closed — including Grove:

```
gate: no manifest for 'willow-grove' (tool='schema_confirm_mapping') — denied
```

Grove's app id is `willow-grove` (`grove/journal_writer.py:42`). Least
privilege — the two tools that path actually calls, no groups, no
`full_access`:

```bash
export WILLOW_HOME=~/.willow-standup
mkdir -p "$WILLOW_HOME/mcp_apps/willow-grove"
cat > "$WILLOW_HOME/mcp_apps/willow-grove/manifest.json" <<'JSON'
{
  "app_id": "willow-grove",
  "name": "Willow's Grove",
  "permissions": ["kb_journal", "schema_confirm_mapping"]
}
JSON
```

Then the knowledge table and its mapping — writes stay locked until confirmed:

```bash
psql -d willow_20_test -f ~/willow-mcp/docs/schema/knowledge.postgres.sql
export WILLOW_PG_DB=willow_20_test WILLOW_PG_USER=postgres PGPASSWORD=postgres
python3 -c "from willow_mcp import server as s; \
  print(s.schema_confirm_mapping(app_id='willow-grove', table='knowledge'))"
```

### 2.4 The fleet containment policy

Three willow-mcp tests audit the real Kart sandbox policy — no vault binds, no
`~/github` blanket bind, `kartikeya` present in `bind_try`. They read a fixed
path and skip when it is absent, because an absent policy means a different
machine, not a containment failure:

```bash
mkdir -p /root/github/.willow
cp "$WILLOW_LEGACY_MONOLITH_REPO/willow/fylgja/config/kart-sandbox.json" \
   /root/github/.willow/kart-sandbox.json
```

> **Caveat, load-bearing.** That copy is from the **archived** legacy monolith tree,
> not a live fleet host. The three assertions pass against it, which says the
> archived policy is clean — it does not say the current fleet host's policy is.
> Do not read a green here as an audit of production.

### 2.5 Nestor's fleet paths

Source the fleet env before any test run (sets `WILLOW_HOME`, Postgres,
Nestor paths, `umask 077`, and a `TMPDIR` **outside** `$WILLOW_HOME` — pytest
dirs under `.willow/` break git-scoped nestor tests because `.willow` is itself
a checkout):

```bash
. ~/github/willow-memory/.willow/fleet.env
```

All env-overridable, so nothing needs to be moved into a hardcoded location:

```bash
export WILLOW_CHARTER_REPO=~/willows-grove      # -> governance/compliance/cases
export JELES_REPO=~/Jeles
export WILLOW_LEGACY_MONOLITH_REPO=~/github-archive-greenfield-2026-08-10/archive/legacy-flat-2026-08-10/willow-2.0
export NESTOR_EXTERNAL_TEST=1
export NESTOR_BROWSER_TEST=1
```

### 2.6 The two that need a different identity

`tests/test_lease.py` skips one case with `root bypasses mode bits` — it
chmods a lease root to `0o500` and asserts reads still work, which is
meaningless as uid 0. Run as anyone else:

```bash
useradd -m grovetest
# One-time: copy tree + venv into grovetest's home (their home is 700).
sudo rsync -a --exclude '.venv' --exclude '.git' ~/github/willow-memory/willow-mcp/ /home/grovetest/willow-mcp/
sudo chown -R grovetest:grovetest /home/grovetest/willow-mcp
sudo -u grovetest bash -lc 'cd ~/willow-mcp && python3 -m venv .venv && .venv/bin/pip install -q -e ".[test]"'
# Run (use sudo -u, not su — grovetest has no login password):
sudo -u grovetest bash -lc 'cd ~/willow-mcp && HOME=/home/grovetest .venv/bin/python -m pytest tests/test_lease.py'
# 60 passed
```

Playwright must match the Chromium already on the box — see **F4** in §6.

---

## 3. Results

| Repo | Before | After | Recovered |
|---|---|---|---|
| **willows-grove** | 517 passed / 9 skipped | **546 / 1** | kart_reader DB, persona roster env |
| **willow-mcp** | 2874 / 14 | **2880 / 10** | egress import, home_init modes, conftest isolation |
| **kartikeya** | — | **143 / 3** | (3 remaining are spent guards, §4) |
| **nestor** | 2264 / 25 / 1 failed | **2310 / 17** | F3 cloud_seal pollution, TMPDIR outside `.willow` |

### The C11 write path, end to end, no mock

Grove's `journal_writer` → real `willow_mcp.server.kb_journal` → real Postgres:

```
write_operator_turn -> {'ok': True, 'id': 'EFF2DD7F', 'ts': '2026-08-30T12:25:52Z'}
```

```
id      | EFF2DD7F      domain | journal      source | heimdallr
content | Willow Airlines: stood up from the seat — postgres native, willow-mcp real, no mock.
tags    | ["ts:2026-08-30T12:25:52Z", "domain:standup", "sender:heimdallr", "journal"]
```

The **read** path could not follow it. See finding F1 and issue #16.

---

## 4. Skips that are correct as they are

Not every skip is a gap. Four kinds here are working exactly as designed, and
"fixing" them would be the error:

- **Inverse guards.** `test_tool_oracle.py:46` — *"nestor installed — the
  unavailable path is not exercised here."* It skips *because* the dependency
  is present. Standing more up makes it skip harder.
- **Spent guards.** All three of kartikeya's: *"a changelog exists now — this
  guards the no-changelog state"*, *"release-please has written a section —
  this guard is spent"*. They guarded a transition that has completed.
- **Sentinels.** Grove's `JournalRoundTripUnittest` exists so a stray
  `python -m unittest` gives a legible message; the real tests in that file are
  pytest functions and they run.
- **Honest capability probes.** Nestor's `_semantic_model_loadable()` returns
  False when the ONNX model cannot be fetched. That is the right answer, and it
  is the shape every one of these should have.

---

## 5. What could not be stood up, and why

Recorded exactly, because "we tried" is not a finding and a host name is.

| Blocked | Cause | Cost |
|---|---|---|
| **Ollama** | `ollama.com:443` — proxy `403` to CONNECT, policy denial. GitHub release API unreachable for asset discovery. PyPI's `ollama` is the client library, not the server. | 3 Grove tests, 4 nestor `test_ollama_matcher` |
| **`[semantic]` lane** | `huggingface.co:443` — proxy `403` to CONNECT. `fastembed` installs; `TextEmbedding()` then dies fetching ONNX. | 8 nestor tests |
| **cgroup delegation** | Container runs cgroup **v1**; `/sys/fs/cgroup` is tmpfs. A fresh `cgroup2` mount succeeds but offers only `hugetlb` — no `memory`, no `pids`, which is precisely what the tests assert. | 2 willow-mcp `test_pg_task_queue_caps` |
| **`test_signing_e2e`** | SDK 2.x removed `create_connected_server_and_client_session`; the in-memory client/server pair needs hand-wiring. Code work, not a dependency. | 1 willow-mcp |
| **`data/corpus`** | Local extracted corpus, not in any checkout. | 1 nestor |

**None of these were faked.** A fake Ollama answering `/api/tags`, `/api/pull`
and `/api/generate` is a small amount of code and would have turned three skips
green. It would also have been precisely the defect this repo has now filed
three times — a check that reports success without performing the check. A skip
reading *"Ollama not reachable"* is true. A green test against a fake Ollama is
a lie that looks better.

---

## 6. Findings

### F1 — the willow-mcp mock implements a tool that does not exist upstream

Filed as **#16**. `mock_willow_mcp.py` serves `kb_journal_read`; the string
appears **zero times** in willow-mcp. The C11 read-back suite is green against
a tool that was never built. Grove's own docstring says Gate 5 will land it —
so the dependency is *known* pending, and nothing reports it is *still*
pending, because the mock always answers.

### F2 — a stale property test in Nestor

`tests/test_property.py::TestStringMatcherNormalize::test_output_is_lowercase_alnum_and_spaces`
fails on `text='¦'`.

`¦` is Unicode category **So** — the exact category **decision 0202**
deliberately preserves, so that emoji key distinctly instead of every
pure-emoji row colliding on the empty string. `😀` falsifies it identically;
hypothesis just reached the lower codepoint first. `€` (Sc), `×` (Sm) and `$`
(Sc) still strip, exactly as the implementation comment claims.

**The implementation is right; the test encodes the pre-0202 contract.** It
only runs under the `[dev]` extra, so a normal `pip install nestor-meaning`
never sees it.

### F3 — test-order pollution in Nestor, visible only with `[gate]` installed

`tests/test_no_network_by_default.py:279` asserts `nestor.cloud_seal` is not in
`sys.modules` after importing the default read path — guarding that a
`[gate]`-less deployment can still load Nestor.

Proven by isolation:

```
tests/test_no_network_by_default.py            -> 14 passed
tests/test_cloud_seal.py + the same file       -> 1 failed
```

`test_cloud_seal.py` legitimately imports `nestor.cloud_seal`, leaving it in
`sys.modules` for the rest of the process. The assertion is on process-global
state with no isolation, so its verdict depends on what ran before it.

**Invisible without `[gate]`**: with `willow_gate` absent the sibling skips,
nothing pollutes, and the test passes. Installing the extra is what exposes it.
The intent is right and worth keeping; the mechanism needs a subprocess or a
`sys.modules` snapshot.

F2 and F3 are in `Die-Namic-Systems/nestor`, outside this session's GitHub
scope — readable over the public git proxy, not filable from here.

### F4 — Playwright must match the Chromium build on the box

Playwright Python version is coupled to a **browser build id**, not semver alone.
A mismatch reads as *"PLAYWRIGHT_BROWSERS_PATH not populated"* when the real
problem is the wrong build directory.

| Host | Chromium | Playwright | Notes |
|---|---|---|---|
| Fleet CI image | `1194` at `/opt/pw-browsers/chromium-1194/chrome-linux/` | `playwright==1.56.0` | Preinstalled; never `playwright install` |
| Desktop (this box) | `1234` at `~/.cache/ms-playwright/chromium-1234/chrome-linux64/` | `playwright>=1.62` via `pip install -e nestor"[browser]"` | **6 browser tests pass** |
| Ubuntu 26.04+ | — | `>=1.62` only | `playwright install chromium` fails: *does not support ubuntu26.04-x64* |

Verify before running `NESTOR_BROWSER_TEST=1`:

```bash
python -c "from playwright.sync_api import sync_playwright as s
with s() as p: print(p.chromium.executable_path)"
bash scripts/ci-test.sh browser   # nestor checkout
```

---

## 7. What this cost, and what it is worth

Nine Grove skips became four. Fourteen willow-mcp skips became five. Twenty-five
Nestor skips became thirteen. Two of the four findings above are defects that no
amount of reading the code would have surfaced — they only appear when the real
dependency is running, because both are about what happens *when the thing is
present*.

The general lesson is the one Grove has now hit four times in one day: **a skip
and a pass are indistinguishable in a summary line**, and a mock is a skip that
prints a dot. Anything that reports success without having performed the check
will keep its secret until someone stands the real thing up beside it.
