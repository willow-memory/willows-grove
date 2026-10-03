# One-box parts partition — four live surfaces

Companion to [`README.md`](README.md). Distinguishes what exists on the box
today from what is still paper. Cite orgpass SOIL
`orgpass-2026-10-02-wave1` / `wave2` / folds; **do not invent seals** for D1–D12.

---

## The four surfaces

| Surface | What it is today | What it is not |
|---------|------------------|----------------|
| **willow-bot UDS** | Live `deterministic.sock` — JSON lines, op table, CLI, systemd unit | Not peercred-checked; not chmod'd 0660 (net_signer is the strict reference) |
| **willow-gate** | A **library** (`willow_gate` package): binding, tier ceiling, session reconcile | **No daemon.** `gates --serve` (:8788) is a separate, authless lease UI — not "the Gate process" |
| **kartikeya** | Sandboxed task runner (bwrap); brokered net via willow-mcp | Not the front door; not the grant UI |
| **willow-mcp leases** | `lease_request` → Nestor draft → `net_authority_drain` → signer socket → unsigned JSON lease file | Not a UDS grant for every verb; not WebAuthn yet |

**Rat-as-door** = design (D1 / Phase 2). Ratatosk today has no IPC endpoint;
it polls the Grove bus over MCP and talks to willow-mcp over stdio.

---

## Gate is a library (orgpass)

Do not write as if willow-gate is a long-running process that owns the
socket. Identity binding and tier ceiling live in code imported by willow-mcp.
The authless `gates --serve` listener is a known hazard (§1 V-fact), not the
Gate itself.

---

## Operator questions this partition carries

| Id | Question | Why it sits here |
|----|----------|------------------|
| **Q1** | Does the operator seal D1 (Rat = canonical runtime)? | Without D1, Rat-as-door stays sketch |
| **Q2** | D2: extract `deterministic/` vs socket-call willow-bot? | Chooses which surface owns the chain |
| **Q11** | Is `gates --serve` retired, firewalled, or given auth before Phase 7? | Library vs hazard listener |
| **Q13** | D11 / IN-door: does every front end's prompt-submit go through Rat, or only selected ones? | Partition of IN across shims |

All four remain **operator-owned**. No seal invented this session.

---

## D10 pin (from outside F8)

[outside-2026-10-02.md](outside-2026-10-02.md) F8 / OW9:

- Pin **frp ≥ 0.68.1** (CVE-2026-40910 / GHSA-pq96-pwvg-vrr9).
- Root = `routeByHTTPUser` auth bypass; unix plugin amplifies Docker-socket
  impact — never treat HTTP-User routing as access control on a unix path.
- D10 itself (no tunnel by default; poll GitHub; frp opt-in) is unchanged;
  this is a floor on the chosen tool, not a new ingress decision.

---

## Related open questions (partition-adjacent)

| Id | Question |
|----|----------|
| Q12 | D12: SessionEnd detach budget — Rat queue vs host timer? |
| Q15 | Soft: does any listener still bind 0.0.0.0 beyond the Matrix bridge? |
| Q16 | Soft: is net_signer still the only 0660 UDS in the fleet? |

Q15–Q16 are verify-pass material, not seals.
