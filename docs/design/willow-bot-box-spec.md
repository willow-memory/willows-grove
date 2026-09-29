# willow-bot Box Spec

**Status:** draft (operator shape, 2026-09-28)  
**Implements in:** `willow-memory/willow-bot` (all runtime code)  
**Fleet context:** `willows-grove` (Kart mounts, flowering experiments, design cross-links)  
**Indexed for this draft:** codebase-memory-mcp — `willow-bot@ace4ff85` (main), `willow-mcp@75c27189`, `kartikeya@0338096d`, `willows-grove@2a33639e` (branch `docs/forge-convergence`)

*Positronic brain expansion — everything stays inside willow-bot. Reach unchanged; capability grows behind the surfaces Willow already uses.*

ΔΣ=42

---

## 1. Intent

willow-bot already sits behind existing MCP tools that Willow calls (`bot_status`, brokered git verbs invoked from the steward when `WILLOW_BOT_MCP=1`, and the deterministic runner reached indirectly via Kart). This work expands **what the bot can do**, not how it is reached.

The bot gains a persistent, self-contained **box**: a durable workspace under its existing state root that owns named virtual environments, controlled execution, gated network egress (request-only), and (later) local model assets. Small deterministic models continue to wire “x → y” edges; structured results feed the same pools (fixture JSONL, friction deposits, growth experiments). The box gives those models a reliable place to run real code without inventing a second sandbox or a new MCP server.

This spec formalizes the horizon already captured in:

- `willows-grove/docs/design/forge-convergence-flowering-experiment.md` §12 (willow-bot in the deterministic chain)
- `willow-bot/INSTALL.md` §Deterministic runner (flowering T1 MVP)
- `willows-grove/deploy/kart-sandbox.md` §Loopback model runs

---

## 2. What exists today (verified in tree)

### 2.1 Bot state root (not the checkout)

`willow_bot.paths` defines the box anchor:

| Helper | Path | Role |
|--------|------|------|
| `willow_home()` | `$WILLOW_HOME` or `$WILLOW_VAULT_BOX` (absolute, must exist) | Operator data-vault box; **no default path** (`BoxNotConfigured` if unset) |
| `bot_dir()` | `$WILLOW_HOME/willow-bot/` | Bot journal: deposits, persona, delivery dedup, deterministic policy, runs |
| `deposits_dir()` | `…/willow-bot/deposits/` | CI outcomes, offsets |
| `webhook_inbox_dir()` | `$WILLOW_HOME/upstream_steward/webhook_inbox/` | Fleet bridge inbox |

The **git checkout** (`~/github/willow-memory/willow-bot`) is separate: systemd units use `WorkingDirectory` there while **ExecStart** uses `$WILLOW_HOME/venvs/willow-bot/bin/…` (`INSTALL.md`).

### 2.2 Dogfood venv (console scripts, not “box venvs”)

- Preferred install: `$WILLOW_HOME/venvs/willow-bot` — holds `willow-bot`, `willow-bot-steward`, `willow-bot-deterministic` entrypoints (`pyproject.toml` console script `willow-bot-deterministic`).
- Keep separate from `$WILLOW_HOME/venvs/willow-mcp`.

This venv runs the bot processes. It is **not** the same thing as named task venvs inside the box (§5); the box may call into the dogfood venv for its own tooling but must not conflate the two in API or on-disk layout.

### 2.3 Deterministic runner (loopback, socket, policy)

Already shipped in `willow_bot/deterministic/`:

- **Policy:** `load_policy()` reads `$WILLOW_HOME/willow-bot/deterministic-policy.json`, with defaults from `_default_policy()`:
  - `socket_path` → `$WILLOW_HOME/willow-bot/deterministic.sock`
  - `runs_dir` → `$WILLOW_HOME/willow-bot/runs`
  - `ollama_base` → `OLLAMA_HOST` or `http://127.0.0.1:11434`
  - `chain_tiers`, `ollama_chat_timeout_s` (template in `deploy/deterministic-policy.template.json`)
- **Serve:** `willow-bot-deterministic serve` — `socket_server.serve_forever`, `_dispatch` handles ops: `run_growth`, `health`, `ollama_tags`, `ollama_ps`, `probe_model`, `runs_summary`, `status` (writes `runs/flowering-kart-overlay.json` when asked).
- **Client:** Kart tasks call `willow-bot-deterministic client` over the Unix socket (`kart-sandbox.md`); **`allow_localhost` is retired** — Kart does not talk to Ollama directly.

Unit: `willow-bot-deterministic.service` (`INSTALL.md`).

### 2.4 Desk visibility

- **MCP:** `willow_mcp.bot_status.read_status()` runs `willow-bot-steward status` (≤5s), maps to populated / empty / unreachable (`tests/test_bot_status.py`). No new MCP verb is required for v1; optional later: expose box summary via steward `status` JSON only.
- **Steward:** tick / heartbeat / sweep when `WILLOW_BOT_MCP=1` — brokered pulls, not raw tokens in the bot (`INSTALL.md`, ruling: Kart never holds credentials).

### 2.5 Isolation elsewhere in the fleet

| Component | Role |
|-----------|------|
| **kartikeya** | `sandbox.run_shell` / `run_shell_result_for_task` — bubblewrap (+ Landlock on supported paths), driven by `$WILLOW_HOME/kart-sandbox.json` instance (`kart-sandbox.md`) |
| **willow-mcp `task_submit`** | Queues Kart work; `allow_net` requires **three keys**: `task_net` in manifest, operator `consent.internet`, unexpired lease — plus per-task envelope when policy demands it |
| **forge-play** | `forge.instrument_execution._kartikeya_runner` — default isolated runner delegates to `kartikeya.sandbox.run_shell` |

The box spec **does not** replace Kart for seat-submitted tasks. It gives willow-bot a first-class way to run **bot-owned** commands in named venvs using the **same** isolation primitives.

---

## 3. Core guarantees

1. **Persistence** — Box contents survive bot process restarts; they live under `bot_dir()` (§5), not the git checkout.
2. **Isolation** — Every execution uses existing Kart / forge-play / kartikeya bubblewrap paths (§6). No parallel “trust the bot uid” runner for untrusted code.
3. **Egress** — Any network use (including `pip install`) is **request-only**. The bot never self-grants: same three-key / consent / lease / envelope stack as `task_submit` (`willow-mcp` tests: `test_task_submit_allow_net_*`). Lane A (§6.1) has **no net**; lane B must pass the gate.
4. **Auditability** — Each `run_in_venv` produces a stable `Result` (§4) suitable for logs, JSONL pools, and replay; side effects are listed in `artifacts` or gated installs.
5. **Reach unchanged** — No new top-level MCP server, no new Willow discovery path. New capability appears only when existing tools (steward heartbeat, deterministic socket ops, future internal hooks) invoke the box API.

---

## 4. Primary primitive

```text
run_in_venv(
    venv: str,                          # required, e.g. "default", "data-science"
    command: str | list[str],           # argv or shell string per lane policy
    cwd: str | None = None,             # default: box work dir for this run_id
    env: dict[str, str] | None = None,  # merged over venv activate env
    timeout: float | None = None,
    capture: bool = True,
    allow_net: bool = False,            # request only; gate decides
    run_id: str | None = None,          # correlates work/ + artifacts/
    lane: Literal["sync", "kart"] | None = None,  # None = policy default (§6.1)
) → Result
```

### 4.1 `Result` (stable JSON shape)

```json
{
  "ok": true,
  "exit_code": 0,
  "stdout": "",
  "stderr": "",
  "duration_ms": 42,
  "artifacts": ["artifacts/<run_id>/out.json"],
  "venv": "default",
  "command": ["python", "-c", "print(1)"],
  "run_id": "20260928T201500Z-abc12",
  "lane": "sync",
  "gate": { "allow_net_requested": false, "verdict": "not_applicable" }
}
```

| Field | Notes |
|-------|--------|
| `ok` | `exit_code == 0` and no runner-level failure |
| `artifacts` | Paths **relative to `box/`** (§5) that callers may promote to pools |
| `gate` | Present when `allow_net`; records denial reason verbatim from broker/Kart |

**Failure modes (fail closed):**

| Condition | `ok` | `exit_code` | Notes |
|-----------|------|-------------|--------|
| Unknown `venv` | false | null | Do not auto-create in v1 except `default` bootstrap |
| Timeout | false | null | `stderr` includes timeout marker |
| Gate denied net | false | null | No partial install |
| Sandbox refused | false | null | Propagate kartikeya refusal text |
| Missing `WILLOW_HOME` | false | null | `BoxNotConfigured` — same as rest of bot |

---

## 5. Layout (on disk)

All paths under existing `bot_dir()` — **do not introduce `WILLOW_BOT_HOME`** as a second env; document alias only.

```text
$WILLOW_HOME/willow-bot/
    deterministic-policy.json    # existing
    deterministic.sock           # existing
    runs/                        # existing (growth JSONL, overlays)
    deposits/                    # existing
    …
    box/                         # NEW — positronic workspace
        state.json               # index: venv names, python version, created_at (cache)
        venvs/
            default/
            data-science/
        work/
            <run_id>/            # ephemeral cwd per run
        artifacts/
            <run_id>/            # durable outputs referenced in Result
```

**Rules:**

- **Venvs** — Real `python -m venv` trees under `box/venvs/<name>/`. Creation is explicit (`create_venv`); not implicit on first `run_in_venv` except bootstrap of `default` in slice 1.
- **Work** — Scratch; safe to delete after `artifacts` copied when retention policy says so.
- **Artifacts** — Bounded retention (v1 default: 7 days or 512 MiB per run_id, whichever stricter — tunable in `state.json`); overflow refuses new runs with clear error until operator clears.
- **`state.json`** — **Cache**, not SOIL. Authoritative truth is directory structure + optional steward deposit later. Regenerate with `list_venvs()` if missing.

**Relation to `$WILLOW_HOME/venvs/willow-bot`:** dogfood venv only. Box venvs are children of `box/venvs/` and are what `run_in_venv` activates.

---

## 6. Execution path

```mermaid
sequenceDiagram
    participant Caller as Existing surface<br/>(steward / deterministic / internal)
    participant Box as willow_bot.box
    participant Runner as Lane A or B
    participant Gate as willow-mcp / Kart gate
    participant Pools as runs / JSONL / friction

    Caller->>Box: run_in_venv(...)
    Box->>Box: resolve venv, work/, env
    alt allow_net true
        Box->>Gate: request (annotated)
        Gate-->>Box: allow / deny
    end
    Box->>Runner: concrete argv + cwd
    Runner-->>Box: exit, streams, paths
    Box->>Box: normalize Result, collect artifacts
    Box-->>Caller: Result
    opt deposit
        Caller->>Pools: append structured row
    end
```

### 6.1 Execution lanes (required design choice)

| Lane | Name | When | Runner | Sync? | Net |
|------|------|------|--------|-------|-----|
| **A** | `sync` | Bot-owned, small, policy-allowlisted commands; deterministic internal use; default for slice 1 | `kartikeya.sandbox.run_shell` (same as forge-play default) with cwd under `box/work/` and mounts from a **bot-specific** kart-sandbox fragment or embedded minimal policy | Yes | Off only |
| **B** | `kart` | Heavy/untrusted shell, long runtime, or parity with seat tasks | `willow-mcp` `task_submit` + poll `task_status` to completion | Async with bounded wait | `allow_net` → full gate |

**Why two lanes:** `willow-bot-deterministic serve` already serves **synchronous** socket ops on the host while Kart is often the **client** (`client` subcommand). Seat code path is the opposite (Willow → Kart queue). `run_in_venv` must not block the steward tick on batch-lane queue depth unless lane B is explicitly selected.

**Default:** lane A for `run_in_venv` when `lane` omitted and `allow_net` is false. Lane B when command matches steward “delegate to Kart” policy (future table) or caller sets `lane="kart"`.

**forge-play:** Prefer importing the same `run_shell` entrypoint forge uses (`forge.instrument_execution._kartikeya_runner`) rather than re-specifying bwrap flags in willow-bot.

### 6.2 Kart mount note (desk instance)

`willows-grove/deploy/kart-sandbox.md` documents flowering mounts: willow-bot checkout (read-only), `$WILLOW_HOME/willow-bot`, `$WILLOW_HOME/venvs/willow-bot`. When lane B runs box commands, instance config must include:

- `box/` read-write under `$WILLOW_HOME/willow-bot/box/` (or whole `willow-bot` state dir if policy already allows RW there for bot jobs)
- No grant to `$WILLOW_HOME/secrets/` or operator vault paths beyond existing template denylists

Restart Kart workers after `kart-sandbox.json` changes (`kart-sandbox.md`).

---

## 7. Supporting operations (in-bot API)

Thin helpers; same isolation and egress rules as §4.

| Operation | Purpose |
|-----------|---------|
| `list_venvs() → list[VenvInfo]` | Names, python version, path, created_at |
| `venv_info(name) → VenvInfo` | Single venv metadata |
| `create_venv(name, python="3.12", packages=None)` | Host `python -m venv` under `box/venvs/`; `packages` installs only via gated path |
| `install_package(venv, package, …)` | Always lane B + `allow_net` + gate |
| `python_exec(venv, code)` (later) | Sugar for short snippets → `run_in_venv` |

`VenvInfo` minimal: `{ "name", "path", "python", "created_at" }`.

---

## 8. Determinism and pools

- **Inputs** — Fully specified: `venv`, `command`, `cwd`, `env`, flags.
- **Outputs** — `Result` JSON; growth fixtures already write JSONL under `runs/` (`run_growth_fixtures`, socket `run_growth` op).
- **Models** — Emit `run_in_venv` as a boring edge; resolvers stay in `willow_bot/deterministic/resolvers.py` (fixture scoring unchanged).

**Deposit targets (existing, no new pool types in v1):**

| Pool | Mechanism |
|------|-----------|
| Flowering / growth | `runs/<run_id>.jsonl`, overlay file |
| CI / steward | `deposits/ci_outcomes.jsonl` (unchanged) |
| Friction / session end | Host hooks when steward runs under desk (unchanged) |

---

## 9. Non-goals (this cut)

- Long-lived interactive shells / PTYs
- Ambient “current venv” session state across calls
- New MCP package or new `willow-mcp` tools (optional: enrich steward `status` JSON only)
- Changes to GitHub App webhook surface or #69 “troll” behavior
- Bot-held GitHub tokens or SSH credentials (broker only)
- Replacing Kart for **seat** `task_submit` workloads
- Moving Ollama weights into `box/` (horizon noted in `INSTALL.md`; separate slice)

---

## 10. Implementation plan

### 10.1 Code layout (willow-bot)

```
willow_bot/box/
    __init__.py
    paths.py          # box root, venvs/, work/, artifacts/
    state.py          # state.json cache
    venvs.py          # create, list, resolve python
    runner.py           # lane A / lane B dispatch
    result.py           # Result dataclass + JSON
    run.py              # run_in_venv implementation
```

Wire first callers:

1. **Internal tests** — mutation-proof: missing venv, gate deny does not write artifacts, timeout.
2. **`willow_bot/deterministic`** — optional socket op `run_in_venv` for Kart-delegated growth steps (parallel to existing ops).
3. **Steward** — only after slice 1 stable; never from unauthenticated webhook path in v1.

### 10.2 Vertical slice 1 (ship first)

1. Create `box/` layout + bootstrap `default` venv (stdlib only).
2. Implement `list_venvs`, `run_in_venv` lane A, no `allow_net`, no `install_package`.
3. One fixture or growth hook that runs `python -c` in `default` and appends a `Result` row to a JSONL under `runs/`.
4. Document operator bootstrap beside deterministic policy in `INSTALL.md` (follow-up PR in willow-bot).

**Does not require:** syscall rows 18/25, `package.upgrade` on broker Kart, kartikeya 0.4.x — unless lane B or `install_package` is in scope.

### 10.3 Deferred (wait for fleet pieces)

| Piece | Blocks |
|-------|--------|
| Lane B `task_submit` integration | Kart 0.4.x on broker, stable network verdict semantics |
| `install_package` | Same + egress envelope habit |
| Landlock parity | kartikeya #89+ live on worker venv |
| SOIL-authoritative venv registry | Nestor/seal story (optional) |

### 10.4 Process

- Land commits with `Idea-Id:` trailers pointing at this doc entry in `willows-grove/docs/ideas.md` when the pile is updated — avoids reconciler “0 landed by evidence” on the next session.
- Builder brief: forbid Bash on specialists; name codebase-memory-mcp + `willow-bot` paths for reads.
- Loki audit before merge if lane B or net touches steward tick.

---

## 11. Open questions

1. **Lane A sandbox policy** — Minimal embedded `kart-sandbox.json` fragment vs reuse full instance with `box/` RW bind only?
2. **Steward `status`** — Should `box` summary (venv count, last run) appear in the JSON `bot_status` already reads?
3. **Socket API** — Add `run_in_venv` op to `_dispatch` in v1 or keep socket Ollama-only until slice 2?
4. **#69** — Confirm no box execution from GitHub-triggered paths until contributor policy is sealed.

---

## 12. Related documents

| Document | Repo |
|----------|------|
| `docs/design/willow-bot-usable-build-brief.md` | willows-grove |
| `docs/design/forge-convergence-flowering-experiment.md` §12 | willows-grove |
| `deploy/kart-sandbox.md` | willows-grove |
| `INSTALL.md` §Deterministic runner | willow-bot |
| `willow_bot/paths.py`, `willow_bot/deterministic/` | willow-bot |
| `src/willow_mcp/bot_status.py` | willow-mcp |
| `src/kartikeya/sandbox.py` (`run_shell`) | kartikeya |
| `forge/instrument_execution.py` | forge-play/Forge |

---

## Provenance

- Operator draft 2026-09-28 (desk conversation, positronic brain expansion).
- Desk synthesis 2026-09-29: execution lanes, path alignment with `bot_dir()`, codebase-memory index citations above.
- Supersedes informal notes only; does not ratify implementation or syscall/envelope grants.
