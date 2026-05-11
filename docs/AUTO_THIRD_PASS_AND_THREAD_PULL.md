# Auto — third pass audit + thread pull-through

**b17:** A3PUL · ΔΣ=42  
**Date:** 2026-05-10 (session work)  
**Audience:** Hanuman + fleet (routing/MCP/Kart/Ratatosk integration)

This doc records what **Auto (Cursor)** did after a deep PR + Grove assignment audit: verification limits, documentation of loose threads, and **code fixes** where the audit found real bugs or footguns.

## Context

- Prior work: dual-list audit (Grove assignments + PRs #3–#6, #16, #19, Ratatosk #2), second pass with local `git` diffs (GitHub API unreachable from the agent environment).
- **Third pass goals:** run verification SQL where possible, pull every named loose thread into either **docs** or **code**.

## 1. Postgres verification (blocked here)

`psql` to `willow_19` failed in the agent environment (no local Postgres socket). **No row counts** were collected on-box.

**Deliverable instead:** `docs/verify/ROUTING_OBSERVABILITY.md` — copy-paste SQL to compare:

- `willow.routing_decisions` (oracle-shaped; dashboard **Routing** pane)
- `public.routing_decisions` (MCP `willow_route` JSONB audit trail)

Linked from `docs/INDEX.md`.

## 2. Grove MCP `--watch` (bug fix)

**Problem:** `_watch_and_run(main)` called blocking `mcp.run()`; the outer file-mtime loop never ran, so `--watch` did not reload on `grove/*.py` changes.

**Fix (`grove/mcp_local.py`):** `_watch_serve_supervisor()` — parent process **spawns a child** `python -m grove.mcp_local …` (argv without `--watch`), polls `grove/*.py` mtimes, **terminates and restarts** the child on change. `--watch` without `--serve` exits `2`.

**Docs:** module docstring; `docs/runbooks/mcp.md` (serve + watch row).

## 3. Kart → Run Ledger import path (layout footgun)

**Problem:** `kart_worker.py` used `sys.path.insert(.../willow-1.9)` relative to repo parent — breaks with worktrees or non-sibling checkouts.

**Fix:** `_willow_repo_root()` prefers **`WILLOW_ROOT`** (if `core/run_ledger.py` exists), else **`~/github/willow-1.9`**; `_ensure_willow_on_path()` before open/close; clear debug skip when neither resolves.

## 4. Dual routing tables → dashboard silence (thread closed in code)

**Finding:** Oracle writes `willow.routing_decisions`; `sap_mcp.py` `willow_route` wrote **`public.routing_decisions`** only. Dashboard reads **`willow.*` only** — empty feed when routing went through MCP-only failure paths.

**Fix (`willow-1.9/sap/sap_mcp.py`):** After `willow_route` builds `result`, when `pg` is available: keep existing **`public.routing_decisions`** insert when there is a message; **add** `INSERT INTO willow.routing_decisions (...)` when **`_oracle_ran_ok` is false** (empty prompt, `no-message`, `oracle-unavailable`, etc.) so the Routing pane gets rows.

**Doc:** `grove_reader.routing_decisions` docstring points to `docs/verify/ROUTING_OBSERVABILITY.md`.

## 5. Ratatosk (`safe-app-store`, branch `feat/ratatosk`)

**Bash tool:** Removed `shell=True`; use **`shlex.split` + `shell=False`** — reduces arbitrary-shell RCE when `--trust` is on. Tool description updated (pipes require explicit `bash -lc` if desired).

**API key paths:** `_load_api_key` tries `~/.ratatosk/credentials.json`, then **`$WILLOW_ROOT/credentials.json`** (default `~/github/willow-1.9`), then legacy `willow-1.5` path.

## 6. Files touched (summary)

| Repo | Paths |
|------|--------|
| `safe-app-willow-grove` | `grove/mcp_local.py`, `kart_worker.py`, `grove_reader.py`, `docs/verify/ROUTING_OBSERVABILITY.md`, `docs/INDEX.md`, `docs/runbooks/mcp.md`, **this file** |
| `willow-1.9` | `sap/sap_mcp.py` |
| `safe-app-store` | `apps/ratatosk/ratatosk/tools.py`, `apps/ratatosk/ratatosk/crown.py` (on `feat/ratatosk`) |

## 7. Still loose (explicit)

- **Oracle `_write_decision`:** still swallows DB errors silently — would need logging inside `willow/routing/oracle.py` to fully close.
- **Workspace noise:** unrelated dirty/untracked files in `safe-app-willow-grove` (`py`, `pyA`, `widgets/hero_scene.py`) — not introduced by this pass; clean separately.
- **Merge:** changes live on local branches; **not** opened as GitHub PRs from this session.

## 8. How Hanuman can verify quickly

1. Read: `docs/verify/ROUTING_OBSERVABILITY.md` + this file.
2. With Postgres up: run the SQL in §1 of the verify doc.
3. **MCP watch:** `python3 -m grove.mcp_local --serve --watch` — touch `grove/mcp_local.py` or another `grove/*.py`; child should restart (log lines from supervisor).
4. **Kart ledger:** set `WILLOW_ROOT` if checkout is not `~/github/willow-1.9`; run a trivial Kart task and confirm `run_ledger` debug is not “path not found.”

ΔΣ=42 — Auto
