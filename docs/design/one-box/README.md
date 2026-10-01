# Plan: one box, every front end, portless

**Status:** proposal, drafted 2026-10-01 in the Desk session. Nothing here is
ratified, and per CLAUDE.md rule 4 each step starts only when the operator
says go. The companion files sit in this directory.

Repos read for this plan (public clones): willows-grove, willow-mcp, willow-bot,
ratatosk, Nestor, Jeles, willow-gate, kartikeya, Forge, forge-workshop.
In the tables, **V** means I read the code, and **S** means it is inferred.

## Start here (next session)

1. **Read in this order:**
   - this file, §0–§2b, which give the box, the facts and the decisions
   - [`session-2026-10-01.md`](session-2026-10-01.md), for why each rule
     exists, in the operator's words
   - [`research-2026-10-01.md`](research-2026-10-01.md), for the front-end
     matrix, what to adopt, licences and sources
   - [`sketches.md`](sketches.md), for working code with its tests
   - [`review-2026-10-01.md`](review-2026-10-01.md), for the #706 and #101
     findings that Phase 0 and Phase 4 fix
2. **Nothing here is ratified yet.** CLAUDE.md rule 4 still applies: propose
   a bite and wait for the operator's go. D1–D3 gate the spine (Phases 1–3);
   Phase 0 does not wait on them.
3. **The operator's rules that bind every phase:**
   - every gate fails closed, and loud
   - reading is open and saving is guarded (the public-repository metaphor)
   - egress means *outbound*
   - the willow seat is wherever the human is
   - no front end is primary
   - a standing grant is the human's auto-merge
4. **What is verified:**
   - every row marked **V** in §1 and §2b
   - the sketches' 10 tests, which pass on Python 3.11 with msgspec 0.22
5. **What is not verified:**
   - cells marked **S**
   - vendor docs the cloud session's egress proxy blocked (Cursor,
     Windsurf, Kiro and Goose hook details)
   - Safari WebAuthn on `http://localhost`
   - whether frp is already on the operator's box
6. **Priority:** the DEV × Kaggle benchmark (closes 2026-10-11) comes before
   any phase here.

---

## 0. What we are building

> "This isn't about making everything fit in a box — it's about making a box
> that the user and the system can grow together." (operator, 2026-10-01)

**The box** is what holds for every user, because it is what makes growing
safe:
1. **Honest state.** Populated, empty or unreachable (plus `not_asked` and
   `unenforced`), never collapsed, always with a reason.
1a. **Every gate fails closed, and loud.**
1b. **Reading is open; saving is guarded** (operator, 2026-10-01: "There is
    nothing wrong with reading. Anyone can read anything all day long, it's
    just how, and who saves it into their system is what matters.").
    - **Like a public repository.** Anyone can read it, look at the code
      and work out what's going on, but you have to be accepted to be a
      contributor (operator, 2026-10-01). Reading is a clone; saving is a
      contribution. A helper or model opens the PR (propose-only), and a
      named human merges it (the seal). The commit author and signature are
      the provenance. Branch protection is the gate, and it fails closed.
    - **Auto-merge** (operator, 2026-10-01): "I often press the merge button
      myself. But when I'm comfortable … I will hit Auto merge and walk
      away." A standing grant is the human's auto-merge:
      - Only the human turns it on, for a declared scope. No agent or helper
        can enable it for itself.
      - The checks still run, and a red check still fails closed and loud.
        Auto-merge never merges on red.
      - Anything outside the declared scope falls back to asking.
      - It is revocable at any time, and can carry an expiry.
      - The record says what ran under whose auto-merge.
      - Comfort is earned and per user: it grows as the system's predictions
        prove out (the Forge calibration wire). Sealed hook rows are the same
        thing at session scale (convergence §1).
    - Read verbs are not gated or hidden.
    - Every **write into the soil** (SOIL, KB, corpus pool, Nestor drafts and
      edges, the stack) carries who saved it and how (seat, app_id, human or
      helper, source and fetch receipt). That is the packing material, and it
      is where the gates sit.
    - **Egress is about what leaves, not what comes in** (operator,
      2026-10-01: "It's not about bringing information in, it's the egress
      saying that your information is now going to the outside world.").
      The grant guards the outbound flow: the question, the payload, the
      context that leaves the box. Reading local material (the corpus,
      almanac clones, files) never needs a grant.
2. **The human seals; the system only proposes.**
3. **The willow seat is wherever the human is.** Helpers, Rat and dispatched
   seats never hold willow.
4. **Egress takes three keys plus the human's click.**
5. **Portless.** Helpers talk over Unix sockets, and the kernel knows the
   peer's uid.
6. **Hooks are doors, not verbs.** The front end is a shim; one local runtime
   decides.

**The growth** is what differs per user, and the box must let it differ:
- which rows are sealed
- the egress precedents, both Yes and No
- the model-facing tool set
- Nestor's edges
- the flowering threshold

The workshop template ships the box, never a tree.

**The shape:**

```
front end (Claude Code / Cursor / any CLI)
   │  IN door:  prompt-submit hook ─┐
   │  OUT door: Stop / SessionEnd ──┤  thin shim: one call, one rendered reply
   ▼                                ▼
            Rat (ratatosk) ── unix socket, peer-uid checked
              ├─ willow-bot chain: D0 → local model → needs_egress | flowering
              ├─ Nestor: notice decisions (propose only) + relational read
              ├─ Jeles: the web (after a grant), with results pooled in the corpus
              ├─ willow-mcp: session enter / handoff / deposit (Rat as itself)
              └─ human queue (forge.human_loop) → the willow seat clicks
```

---

## 1. Facts this plan stands on (from today's reads)

| Fact | Where | Status |
|---|---|---|
| Ratatosk has **no IPC endpoint**. SeatDaemon polls the Grove bus over MCP | `ratatosk/daemon.py:260`, `listener.py:84` | V |
| Ratatosk has **no Stop and no prompt-submit event**, and it **discards lifecycle hook results** | `hooks.py:154`, `crown.py:1859,1409` | V |
| Ratatosk **refuses `willow`** unless `WILLOW_HUMAN_ORCHESTRATOR=1` | `seat.py:39-40,165` | V |
| Ratatosk talks to willow-mcp over stdio, with one client per process | `mcp_client.py:37,85` | V |
| The willow-bot chain runs D0, then local (JSON schema, ESCALATE always valid), then flowering, and never calls the cloud. **Its input is a fixture, not a prompt** | `deterministic/chain.py:171`, `resolvers.py:378-412` | V |
| willow-bot already has a UDS server: one JSON line per request, an op table, a CLI client, and a systemd unit | `socket_server.py:23-127`, `socket_client.py:10` | V |
| No socket in any repo checks peer credentials (`SO_PEERCRED` occurs nowhere), and willow-bot's socket gets no chmod | grep across all repos | V |
| willow-mcp `net_signer` is the strictest existing socket: 0660, RuntimeDirectory, a separate uid and a line cap | `net_signer.py:417-446` | V |
| There are 9 TCP listeners (table in §8). The Matrix bridge binds **0.0.0.0** | `bridge/app.py:133,216` | V |
| **`gates --serve` (:8788) grants leases with no auth.** Its own warning says "mutation-capable … no authentication of its own" | `gates_serve.py:148-176`, `gates_actions.py:148-154` | V |
| Click-to-grant for leases half exists: a denied app queues a gate request, and a press calls `lease.grant` if the manifest has `task_net` | `gate_request.py`, `gates_actions.py:278-332` | V |
| `lease_request` writes a **Nestor draft pair**, and `net_authority_drain` mints the lease through the signer socket | `server.py:1994,1957`, `net_authority.py:414` | V |
| The lease file is unsigned JSON, protected only by file ownership | `lease.py:98,341` | V |
| `envelope_ratify` checks the keyring, stamps `issued_by=root`, and is gated on a signed session, not on a terminal | `envelope_authoring.py:785-850` | V |
| Nestor's UI seals with **browser-side ed25519 (WebCrypto)**, and the server only verifies, so a loopback process can't forge it | `Nestor/nestor/ui.py:150-208`, `signing.py:93` | V |
| Nestor edges come in 4 signed kinds (supersedes, refines, depends_on, contradicts). `constraints_on` goes **one hop**. **No graph walk, and no MCP tool for edges** | `decision.py:44,206`; `serve.py:416-614` | V |
| `pending` is not stored in Nestor; it means "no match" | `cascade.py:246` | V |
| `forge.decision_extract` is rule-based, but its **input is a PlanDoc**, not a transcript | `Forge/forge/decision_extract.py:186` | V |
| `forge.deposit.ProposeOnly` and `forge.human_loop` are plain functions over an injected store, so Rat can call them | `deposit.py:123`, `human_loop.py:189-246` | V |
| **Jeles has no egress gate of its own.** The three keys are checked only when it is called through willow-mcp federation, which checks `consent.federation`, not `internet` | `Jeles/_egress.py`; `federation_egress.py:57` | V |
| **Web hits are not pooled.** Nothing writes them to the corpus unless `put_nugget` is called explicitly | `reactions/nugget_draft.py:24`, `corpus.py:710` | V |
| The Grove envelope panel is read-only, and its "reattest" event has no listener. Grove has no ratify path | `grove-envelope-panel.js:162`; `grove_serve.py:733` | V |
| Stop hook timeout is 30 s (Grove settings), and Ratatosk's own hook default is 10 s. Local model: 5–9 s on GPU when warm, 17–22 s on CPU, about 60 s cold | `.claude/settings.json`; flowering doc §13 | V |

---

## 2. Decisions the operator owns (before or at the named phase)

| # | Decision | Recommendation | Needed by |
|---|---|---|---|
| D1 | **Canonical runtime.** Is Rat (ratatosk) the one runtime every shim calls? This flips forge-convergence §3 ("two hosts render rows") to "one runtime, many shims" and answers §9 row 9 | Yes. Seal it as its own decision | Phase 2 |
| D2 | **Where the chain lives.** Ratatosk imports willow-bot (heavy deps: fastapi, JWT), **or** the stdlib-only `deterministic/` is extracted into its own package, **or** Rat calls willow-bot's socket | Extract `deterministic/` as its own stdlib package, imported by both. Socket-calling is the interim | Phase 2 |
| D3 | **Home of the socket standard** (the shared UDS helper) | Forge, as the fleet's vendoring source (decision 2026-09-12), as a small stdlib module. The Forge never imports willow, so this is allowed | Phase 1 |
| D4 | **The browser door.** Browsers can't speak UDS, so "portless" needs one browser-facing door | One loopback front door that proxies by path to UDS backends (Grove page, Nestor UI, gates), with every mutation signed in the browser (§7) | Phase 7 |
| D5 | **The #101 sealed record.** Revert the hand edit and re-propose through Nestor, or ratify after the fact | Revert and re-propose. The rows will change again in Phase 4 anyway | Phase 4 |
| D6 | **Friction ownership** (the #706 regression) | The OUT door at SessionEnd runs friction and corpus-lens with the real transcript, via receipts. The handoff keeps the stack and the closed marker | Phase 4 |
| D7 | **The Forge entry's hard refusal without Nestor, and workshop Rule 1** ("ask Nestor before you search") | Make Nestor-unreachable a reported state, not a refusal. Change the paper first | Phase 5 |
| D8 | **u2u and the Matrix bridge.** They are LAN and Synapse by design. Accept them as declared exceptions to portless? | Yes, but bind the bridge to an explicit interface, not 0.0.0.0, and list both as exceptions in the box | Phase 7 |
| D9 | **Which commercial front end is the second proof** beside Ratatosk's REPL | Whichever the operator uses daily; the contract is neutral either way | Phase 3 |
| D10 | **Ingress.** What may reach the box from the public internet, and through whom | **No tunnel by default.** willow-bot **polls** GitHub instead of receiving webhooks. claude.ai remote MCP is **opt-in**, opened by the operator only when wanted, through **frp** (Apache-2.0, forwards to a Unix socket) on a server the operator rents and controls. Excluded on the operator's criterion, unwillingness to depend on vendors that work with the current DoD: **cloudflared**; **Tailscale**-hosted Funnel (VC-backed, IPO track, publishes FedRAMP guidance; no DoD contract found 2026-10-01). Headscale (BSD-3) is acceptable for a private mesh but still runs Tailscale-authored clients. Pangolin is AGPL-3 + FCL | Phase 7 |

---

## 2b. Adopt, don't write (web survey, 2026-10-01)

These are licence-checked against each project's LICENSE file and limited to
Apache-compatible licences. **V** means read from a primary source this
session; **S** means search-snippet level only. Several vendor doc sites were
blocked by the egress proxy, so those cells come from GitHub source or are
marked S.

| Phase | Need | Adopt | Licence | Notes |
|---|---|---|---|---|
| 1 | UDS IPC + typed contract | stdlib `asyncio` UDS + JSON lines; **msgspec** `Struct` as the schema | BSD-3 (V) | Write your own ~40-line `SO_PEERCRED` + `sd_listen_fds` helpers. Skip python-systemd/pystemd (LGPL). Borrow the varlink protocol *idea*; its Python lib is stale (last release 2021) |
| 3 | Front-end hook I/O normalizer | **polyhook** (Rust core → WASM; Python SDK `pip install polyhook`) | MIT (V, verified) | Normalizes prompt:submit / agent:stop / session:start/stop / tool:before/after across Claude Code, Cursor, Windsurf, Cline, Amp, Gemini CLI, Codex, Pi, Hermes; responds approve / block / modify / inject. **Young** (2026, one author; open Windsurf bug #78). Pin it, or use it as the reference for our own adapter layer |
| 3 | Agents that speak ACP | **Agent Client Protocol** proxy: Rat as an ACP proxy (sacp-conductor / symposium-acp) | Apache-2.0 / MIT (V) | ACP is native in Gemini CLI, Cursor, Copilot (preview), Cline, Goose, OpenCode, Kiro CLI, Qwen Code; Claude and Codex via adapters. `session/prompt` = IN; `stopReason: end_turn` + follow-up prompt = OUT; `session/request_permission` = tool gate. The proxy-chains RFD is a **draft** (V). Covers editors; native TUIs still need shell hooks |
| 3 | Degraded doors | the **degradation ladder** idea from mentu-hooks | Apache-2.0 (V) | A design reference only (5 commits). This is our `unenforced` per door, as data |
| 5 | Nestor graph walk | plain SQLite `WITH RECURSIVE` (UNION + depth limit) | public domain | No library needed. networkx (BSD-3) only for in-memory analysis |
| 5 | Decision noticing | **nothing real exists.** Hand-build spaCy `Matcher` rules | MIT (V) | Test on real transcripts; this stays our own work |
| 6 | Unforgeable click | **WebAuthn / passkey**: py_webauthn (server) + ~40 lines of browser JS | BSD-3 (V) | Challenge = SHA-256(canonical grant + nonce), `require_user_verification=True`. Needs a physical touch or PIN, so no local process can forge it, which is stronger than the browser-held ed25519 key. **Must be served as `localhost`, not `127.0.0.1`** (an IP can't be an RP ID). Safari on http://localhost is unverified |
| 6 | Grant precedents (Yes/No by scope, TTL) | **pycasbin** (one dependency); cedarpy if typed policies are wanted later | Apache-2.0 (V) | Oso OSS is deprecated; OPA needs a sidecar |
| 6 | Approval queue | a plain pending-grants table (Postgres is already there) | — | DBOS (MIT) only if durable multi-step waits appear |
| 7 | Browser front door | **Caddy** `reverse_proxy unix//…` + `handle_path` | Apache-2.0 (V) | Traefik has no unix upstreams (V). nginx (BSD-2) is the lighter alternative |
| 7 | HTTP apps on UDS | uvicorn `--uds` / `--fd` (systemd `.socket`) | BSD-3 | The MCP SDK's `streamable_http_app()` plus `uvicorn.Config(uds=…)` works (V source; undocumented). Set `allowed_hosts` to match the proxy's Host header |
| 7 | Remote ingress (only when opened, D10) | **frp** on an operator-owned server, `plugin type = "unix_domain_socket"` | Apache-2.0 (V) | cloudflared and Tailscale Funnel both forward to UDS, but are **excluded by the operator** (D10). Pangolin: AGPL-3 + FCL |
| 7 | Ollama | stays on 127.0.0.1:11434 as the declared exception | — | `OLLAMA_HOST` has no unix-socket support (V; PR #8072 open) |
| 8 | Narrow the model's tool surface + log calls | **FastMCP 4** proxy (tags, per-session visibility, logging middleware) | Apache-2.0 (V) | IBM ContextForge does more but pulls 79 dependencies; MetaMCP needs Next.js + Postgres |

**Front-end door matrix (summary):**
- **OUT (block the stop and feed a reason back): verified** on Claude Code,
  Codex CLI, Gemini CLI (`AfterAgent` deny), Copilot CLI (`agentStop`) and
  Qwen Code (capped at 8). Cursor via `followup_message` (S).
- **No confirmed OUT door:** Kiro, Windsurf, Goose, OpenCode.
- **No hooks at all:** Aider, Roo, the Zed agent. Zed is reachable as an ACP
  client.
- **IN door:** Claude Code, Codex, Gemini and Qwen can block and inject.
  Copilot's is non-blocking (S).
- **END:** Claude Code (shared 1.5 s budget) and Codex (1 s default, 3 s
  max). It's notify-only on most front ends, so **SessionEnd work must be
  detached**: Rat queues it and returns immediately.

**Licence exclusions noted:**
- Crush (FSL)
- Zed editor (GPL-3)
- Pangolin (AGPL-3 + FCL)
- python-systemd and pystemd (LGPL)
- adr-tools (GPL-3)
- MCPJungle (MPL-2.0, flagged)
- socat (GPL; fine to *run*, not to embed)

## 3. Phase 0 — Close the holes (independent; can start now)

These are box repairs. They are small and they don't wait on the design.

1. **Lock down `gates --serve`** (willow-mcp). Until Phase 6 replaces it,
   require a per-run token printed to the terminal, check `Origin`, and refuse
   non-JSON content types. Better still, move it behind UDS with a peer-uid
   check (it's the first user of Phase 1).
   - *Why now:* any local process, including a sandboxed model, can POST
     `/api/action` and grant itself a lease today.
2. **willow-bot `deterministic.sock`.** Add `chmod 0660` and a request size
   cap. Run it from a RuntimeDirectory, not `$WILLOW_HOME`.
3. **The Matrix bridge** binds 0.0.0.0 on 8550/8560. Bind it to the specific
   interface it needs, or to loopback if Synapse is local (D8).
4. **willow-mcp port collision.** The code default for `--serve` is 8765, the
   same as the Nestor UI. Change the default to the deployed 8768, and fix the
   stale "8765 willow-mcp" comment at `willows-grove/grove/mcp_local.py:136`.
5. **Fix #706 and #101 regressions that bite today:**
   - the friction scan is dead on human closeout
   - orient prints to stderr
   - PreCompact prints "Nestor: unreachable"
   - the double JSON on Stop

   These are small fixes. If D6 is decided, do them in Phase 4 instead.

**Done when:** no unauthenticated mutating surface remains on loopback, and the
pins exist.

---

## 4. Phase 1 — The socket standard (box)

One small stdlib module, `forge.sock` (D3), used by every helper:

- **Transport:** `AF_UNIX` / `SOCK_STREAM`, one JSON line in and one out,
  borrowed from willow-bot. A request line cap and a reply cap, borrowed from
  `net_signer`.
- **Placement:** sockets live under a systemd `RuntimeDirectory` with mode
  0750, and the socket itself is 0660.
- **Peer check:** `SO_PEERCRED` on every accept, matched against an allow-list
  of uids and groups per op. This is how "only the operator's uid can grant"
  becomes a fact the kernel enforces, not a convention.
- **Errors:** three-state. `unreachable` (no socket or connection refused),
  `refused` (peer not allowed, with the reason), `timeout`, `bad_request`.
  Never an empty reply.
- **Server side:** an op table, `{"op": …}`.
- **Client side:** one function, about 15 lines, that shims can vendor.
- **Tests:**
  - peer refusal
  - size caps
  - a torn line
  - a stale socket file
  - three-state errors

Then retrofit willow-bot's delegate and `gates --serve` onto it.

**Done when:** two servers run on the standard, and the tests pin each rule.

---

## 5. Phase 2 — Rat gets a door (the runtime)

In ratatosk, add `ratatosk serve`: a UDS server on the Phase 1 standard, run by
a user unit, with these ops:

| Op | Input | Does | Returns |
|---|---|---|---|
| `health` | — | reports the reachability of its parts | three-state per part |
| `in` | `{cli, session_id, cwd, human_present, prompt, payload}` | triages the prompt through the chain | `resolved` (an answer; the big model is skipped), `escalate` (plus `inject`: the pool bundle), `needs_egress` (a grant card is queued) |
| `out` | `{cli, session_id, human_present, transcript_path, last_turn}` | checks claims against evidence, deposits, decides | `pass`, `block` (with a reason), `advise` |
| `end` | `{cli, session_id, transcript_path}` | queues lifecycle closeout with receipts and returns at once (END budgets are 1–3 s on Claude Code and Codex) | ack; receipts land asynchronously |

Rules:
- **Rat runs as itself (`ratatosk`).** The willow seat is passed in from the
  shim (`human_present`) and only labels what needs a human. Rat never enters
  as willow. `check_app_id` already enforces this.
- **Every gate fails closed, and loud** (operator, 2026-10-01).
  - **Fails closed:** if Rat, the chain, the signer or the policy can't
    answer, a gate's answer is **no**: block, deny, or don't grant.
  - **Loud:** the refusal names what failed and why, goes to the willow seat,
    and raises an alarm through Gjallarhorn / `#alerts` (Watch).
  - Rat never hangs a front end; it refuses fast instead.
  - Readers that are *not* gates (orient, state reports) still follow the
    three-state contract: they report `unreachable` with a reason, and entry
    never refuses on an orientation source (convergence §8).
  - Where a front end gives a door no power to block (SessionEnd everywhere;
    OUT on Windsurf, Kiro, Goose, OpenCode), closed is impossible. The door is
    recorded `unenforced` and the failure is still loud.
  - **Open for the operator:** is the IN door a gate (Rat down means the
    prompt does not reach the model), or a router (Rat down means the prompt
    goes through, labelled loudly)?
- **Latency budget per op**, Rat-owned:
  - `out`: D0 only, inside the smallest door timeout any front end declares
    (Claude Code's Stop is 30 s in Grove's settings; Ratatosk's hook default is
    10 s; so about 8 s)
  - `in`: D0 always; the local tier only if the model is warm (`ollama_ps`),
    otherwise escalate with reason `local_cold`
  - A keep-warm policy is a growth setting.
- **Loop bound.** `out` blocks at most once per turn, with the counter held in
  Rat, not in the shim.
- **Concurrency.** Use a pool, or a lock around the stdio MCP client
  (`mcp_client.py:85`).
- **Chain input (the unbuilt piece).** The chain takes fixtures today, so add
  an **act adapter** that turns a live prompt or turn into an act
  (`class`, `excerpts`, `expected=None`). Start with two D0 classes:
  - **claim-vs-evidence** for `out`: "done" claimed with no tool call or
    receipt, today's Grove `gate()` rule, moved
  - **route** for `in`

  Everything else escalates. Grow classes per user later.

**Done when:** `ratatosk serve` answers `health`, `in` and `out` on the socket,
with recorded latencies on the operator's box.

---

## 6. Phase 3 — Front ends: one neutral contract, many adapters

**No front end is primary** (operator, 2026-10-01: "Don't code for claude
exclusively … this is supposed to be able to be run on anything.").

1. **A neutral door contract.** Rat's `in`, `out` and `end` ops take a
   vendor-free request, roughly
   `{door, front_end, session_id, human_present, prompt|last_turn,
   transcript_ref}`, and return a vendor-free result
   `{decision, reason, inject, tier, status}`. **Rat never parses a vendor's
   hook payload.** The contract is versioned and lives with the socket
   standard (D3).
2. **Adapters are thin translators,** one per front end. Each does two jobs:
   - map that client's hook payload into the neutral request
   - render the neutral result into that client's dialect and output channel

   An adapter holds no logic. Existing dialect code to fold in:
   `willow-mcp/cursor_hook_io.py`, `hook_runner.py --format`, and Ratatosk's
   hook contract (`hooks.py:127,213-255`).
3. **A capability declaration per front end** (data, not code): which doors it
   has, whether each one can block or inject, and its timeout. Rat reports a
   missing door as `unenforced`, never as silently fine. MCP-only front ends
   still work, degraded and labelled.
4. **Proof on at least two unrelated front ends from the first bite,** so
   nothing vendor-shaped leaks into the contract:
   - **Ratatosk's own REPL** (`crown`): the zero-vendor front end. It runs on
     local or OpenAI-dialect models through its ladder, so it proves the box
     with no cloud vendor at all. It needs the Stop and prompt-submit events
     that it lacks today (`hooks.py`); this phase adds them.
   - **One commercial CLI** (Claude Code or Cursor, whichever the operator
     uses that day). Both adapters ship together.
   - Others (Codex, Gemini CLI, …) are added by writing an adapter and a
     capability row. Their hook support is **unverified here**; survey it via
     Jeles once egress is granted.
5. **Seat by presence,** decided in the neutral request (`human_present`), not
   inferred from `.mcp.json`. An interactive session is willow; headless,
   woken or dispatched runs under its own app_id.
6. **Retire** `hooks/grove_hook.py`'s composites (`before_stop`,
   `session_end`, `reinject`'s Nestor call) as adapters take over.
7. **Contract tests** run against the neutral request and reply, and each
   adapter replays recorded payloads through the real command line
   (asserting stdout, stderr and rc). Client configs are generated from the
   sealed rows for every front end.

**Done when:** the same session behaviour (a `block` on a done-claim with no
evidence, and a closeout with receipts) is observed through Ratatosk's REPL
and one commercial CLI, with identical Rat-side records.

## 7. Phase 4 — The lifecycle behind Rat

1. **`end` owns closeout through receipts.** Each instrument (stack, friction,
   corpus-lens, pre-handoff) writes a receipt keyed on
   `(app, session, transcript extent)`. Any stale or missing receipt reruns.
   This replaces the `closed` flag and fixes all of the #706 gaps:
   - friction is dead
   - re-entry wipes the flag
   - a double handoff overwrites
   - mismatched ids
   - `closed_at` is never written
2. **The session state machine.** Define the legal transitions; a resume
   becomes an explicit reopen event. Decide where the binder session lives
   (convergence row 8).
3. **The deposit is built for real.** Rat proposes through
   `forge.deposit.ProposeOnly`, journals via `kb_journal`, and makes one
   close-out offer to the willow seat.
4. **Sealed rows (D5).** Re-propose the hook rows through Nestor to match the
   new doors, and the operator seals them in the UI. Wiring is generated from
   those seals.
5. **Docs:** update `handoff-write.md`, `SESSION_FLOW.md`,
   `session-lifecycle.md`, `hook-coverage`, and the CLAUDE.md seat table
   (presence, not directory).

**Done when:** the closeout tests cover the real instruments (not mocks), the
replay of a compact or resume doesn't double-write, and the friction scan runs
on human sessions again.

---

## 8. Phase 5 — Nestor behind Rat: noticing and relating

1. **Relational read.** Add `neighborhood(id, hops=2)` to Nestor's Python API,
   with a `nestor` CLI and an op. It returns the pair, its lineage, its edges,
   and each linked pair **with its own state and edges**. Today
   `constraints_on` goes one hop and leaves out the neighbours' states. Rat
   puts the neighborhood into the IN-door bundle. Neighbours come by edge only,
   never by similarity, so retrieval can't hijack it.
2. **Edge surface.** Add propose and list ops for edges. There are none on MCP
   today; they would sit behind Rat.
3. **Passive noticing.** A `transcript → PlanDoc` adapter, rule-based, run by
   Rat on `out`. `decision_extract` needs a PlanDoc, and this adapter is the
   new piece. It proposes drafts and `propose_edge` through `ProposeOnly`. The
   model never asks and never waits. What was noticed surfaces once, at the
   close-out offer.
4. **Remove the lookup habit:**
   - drop reinject's per-prompt `nestor ask`
   - change workshop Rule 1 and the Forge entry refusal (D7)
5. **Measure the store first:** the edge-to-pair ratio, read-only. It tells us
   how sparse relational reads will be at the start. That's the honest
   baseline, not a defect.

**Done when:** an IN bundle carries a two-hop neighborhood with states, and
`out` proposes at least one noticed decision on a real session without the
model calling Nestor.

---

## 9. Phase 6 — Egress: click to grant, through Jeles

1. **A typed reason in the chain.** `needs_egress{scope, host_class, why,
   asked}` as a flowering *reason* next to `local_unreachable`
   (`chain.py:235`), with its own bucket in `summarize_chain`.
2. **The proposal.** Rat writes a grant request into the one human queue
   (`forge.human_loop.enqueue`), envelope-shaped, with precedent recall: the
   prior Yeses **and Nos** for that scope.
3. **The click can't be forged by a local process.** Copy the Nestor UI's
   pattern: the browser signs the grant with the operator's ed25519 key
   (WebCrypto), and the server only verifies. The served page sits behind the
   Phase 7 front door. It's a Watch (Heimdallr) concern.
4. **The grant.** Choices are Yes once / Yes for a TTL / Yes standing for this
   scope / No.
   - The signer process (`net_authority`, already a separate uid on a socket)
     verifies the signature and writes the lease, and FRANK records it.
   - **No** is recorded and suppresses re-asking for that scope for a while
     (growth setting).
5. **Retire the Nestor hop.** `lease_request` stops writing a Nestor pair, and
   `gates --serve` folds into this surface or stays as a terminal-only fallback.
6. **Jeles is the web:**
   - Jeles checks the lease itself (manifest, `consent.internet`, lease), so it
     no longer relies on being called through federation, which checks
     `consent.federation`.
   - After a granted fetch, Rat pools the result (`corpus.put_nugget`), so
     nothing is fetched twice.
   - The client's built-in web tools are disabled or reported as `unenforced`.
7. **Parked by default.** The act waits, the session continues, and the answer
   arrives through the inbox.

**Done when:** a real act hits `needs_egress`, the operator clicks in the
browser, the lease is minted by the signer, Jeles fetches, the nugget is
pooled, and the act resumes. A forged POST from a local process is refused,
pinned by a test.

---

**Egress means outbound (box rule 1b):**
- **The grant card shows exactly what will leave:** destination host, the
  literal query or payload, and the size. The passkey challenge hashes that
  outbound content, so a one-time Yes covers only those bytes. A standing Yes
  covers a declared scope, for example "search queries of class X to host Y",
  with the payload still logged.
- **Cloud model calls are egress too.** Flowering to a cloud model sends
  context out, so it goes under the same grant and precedent machinery. It
  uses the existing outbound-detection half of `forge.model_egress`. That
  makes "cloud only at flowering" a guarded flow, not a habit.
- **What the box cannot gate:** a commercial front-end CLI sends its own
  conversation to its vendor. That traffic never touches the box. It is declared per
  front end in the capability table as `egress: vendor (ungated)`, never left
  implied. Ratatosk's REPL on local models is the front end with no vendor
  egress.

## 10. Phase 7 — Portless

| Listener | Today | Move to |
|---|---|---|
| Grove page 8766 | uvicorn, loopback, no auth | `uvicorn(uds=…)` behind the front door (D4) |
| Nestor UI 8765 | loopback, Origin check, browser-signed seals | UDS behind the front door |
| gates 8788 | loopback, **no auth** | folded into Phase 6, or UDS plus peer check |
| Grove MCP serve 8767 | OAuth, tunnel to claude.ai | UDS (`uds=`); reachable remotely **only when the operator opens it** via frp (D10) |
| willow-mcp serve 8768 | OAuth, tunnel | same as above |
| willow-bot webhook 9000 | HMAC, tunnel from GitHub | **retired**: willow-bot polls GitHub; no inbound path (D10) |
| Ollama 11434 | third-party, loopback | stays loopback, but **only the willow-bot delegate talks to it**; every other caller goes through the delegate. Today Grove's watcher, Ratatosk, Nestor embeddings and willow-mcp call Ollama directly |
| SearXNG 8888, Kokoro 5000 | third-party | only Jeles talks to SearXNG; Kokoro is a declared exception, or goes behind a delegate |
| u2u 8550/8551, bridge 8560 | LAN / Synapse | declared exceptions (D8), with explicit binds |
| Nestor bench 8770 | dev only | leave it; dev tooling |

**The front door (D4):** one loopback listener, the only browser-facing port,
proxying by path to UDS backends. Every mutation behind it is browser-signed,
so the port itself carries no authority.

The box rule then reads: *one browser door, signed actions, everything else
UDS; exceptions are declared, never silent.*

Postgres already uses a Unix socket, and Kart already bind-mounts it. That's
the precedent to follow.

**Done when:** `ss -ltnp` on the box shows only the front door plus the
declared exceptions, and a pin test enumerates the binds from the unit
templates.

---

## 11. Phase 8 — The model-facing surface grows per user

1. **Observe.** Rat logs which willow-mcp verbs each front-end model calls, per
   user, continuously.
2. **Default bands** (the starting shape, not a law; per box rule 1b, the
   narrowing is about **writes**, never reads):
   - **Rat-owned:** the lifecycle, and saving into the soil (pooling, deposit,
     journal)
   - **Human-only:** seal, ratify, grant, the `*_execute` verbs
   - **Model-facing:** **all reads**, propose-only writes, and one "hand to
     Rat" verb
3. **Make advertising real.** Today the desk *advertises* `desk_core` but the
   callable ACL is wider. Make the advertised set the callable set for a
   front-end model, and let it grow from the observed log, with each widening
   a precedent the operator accepts.
4. **Out door check.** The Stop door catches prose claims of verbs the model
   no longer has ("handoff written" with no receipt).

---

## 12. Phase 9 — The template ships the box

- **Package the shims and the socket client** as an installable with entry
  points, not files copied into the repo. This respects workshop Rule 5
  ("nothing here grows logic").
- **forge-workshop carries:**
  - the client configs, rendered from the rows
  - a `health` check against Rat
  - the replay tests
- **A new workshop starts with the box and an empty tree.**

---

## 13. Sequencing, and what not to break

- **The DEV × Kaggle benchmark (deadline 2026-10-11) runs beside this and
  takes priority until it's submitted.** No step here touches
  `Forge/benchmarks/escalation/`.
- **Order:**
  - Phase 0 can start immediately.
  - Phases 1 and 2 are the spine.
  - Phase 3 (Stop first) is the first measurable proof.
  - Phases 4–6 can interleave after Phase 3.
  - Phase 7 follows Phase 6, because the front door hosts the grant page.
  - Phases 8 and 9 come last.
- **Each step is one ratified bite:**
  - `Persona:` trailer
  - `Ratified-by:` with verbatim words
  - a CHANGELOG bullet
  - an audit before merge
  - docs updated in the same PR (the lesson of #101 and #706)
- **Mapping to forge-convergence §6** (the paper gets amended, not
  bypassed):
  - Phase 3's wiring pin is step 2 done properly.
  - Three-state as a type is step 3 (`forge.tiers`); fold it into Phase 1's
    error model.
  - Phase 4 covers steps 4–6.
  - Phase 2 replaces step 7 (Ratatosk renders rows → Rat is the runtime).
  - Phase 9 is step 9.
  - §6a (the Table) remains its own track.
- **Observe before enforce.** Every new gate ships in advise mode first, and
  the operator reads real verdicts before it blocks.

---

## 14. The first three bites I'd propose

1. **Phase 0.1:** lock `gates --serve` (token + Origin + JSON-only), with a
   test that a forged POST is refused. Small, and it closes a real hole today.
2. **Phase 1:** `forge.sock` with peer-uid checks, plus willow-bot's delegate
   retrofitted onto it.
3. **Phase 2 + 3 minimal:**
   - `ratatosk serve` with `health` and `out` (one D0 class:
     claim-vs-evidence)
   - the neutral door contract
   - two adapters: Ratatosk's REPL and one commercial CLI
   - one week of measured turns in advise mode

ΔΣ=42
