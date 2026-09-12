<!-- b17: WGRV1  ΔΣ=42 -->
# Approval broker — how a human act reaches a sandboxed caller

Written 2026-09-09 against the open decision `attest-via-kart-pinentry`
(gap `caf0e4060b18`). Line numbers are from the tree this file lands on.

## 1. The problem, stated as the operator states it

> *"Kart should be able to run those, and the system password prompt pops up."*

Today it cannot. Every operator-only mutation funnels through one function:

```python
def require_operator_terminal() -> None:
    if os.environ.get("WILLOW_IN_KART", "").strip():
        raise PermissionError("mutation refused inside the Kart sandbox")
    if not sys.stdin.isatty():
        raise PermissionError("mutation requires an interactive operator terminal")
    ...
    if owner_uid != os.getuid():
        raise PermissionError(
            "controlling terminal is not owned by the invoking operator"
        )
```

`human_session.py:307-331`, mirrored inline at `server.py:6538`, `:6719`,
`:6764`. Its own docstring names the real property: `isatty()` alone is
forgeable, because an agent can allocate a pty and pass it — so an
**operator-owned controlling tty** stands in for *a human is present*.

That is a proxy, not the property. The property is: **something happened that
the calling process could not have caused.** A passphrase prompt satisfies it.
A tty is one way to get one, not the only way.

## 2. Two shapes, and why only one survives the phone

**(a) Widen the guard.** Let `require_operator_terminal()` accept a local
pinentry challenge as an alternative presence proof. One function changes.

**(b) Broker it.** The sandboxed caller *requests*; a host process outside
bwrap prompts the operator and performs the act where the keys already live.

(a) is host-bound in two ways that matter. It puts the signing inside the
sandbox, which means mounting `config/verifiers.json` — ed25519 **private**
keys — into every task, reopening gap `1937696f6513`. And it assumes the human
is standing at this box.

`phone-surface-context.md` settles it independently. §12: *"The phone carries
ciphertext. **The key stays home.**"* The tier table makes tier 1 (LAN, u2u)
**signals only, not contents** until Gate 6, and tier 2 (remote, Pangolin)
terminate at `:8768`, never at the desk. An approval arriving from a phone is
not a local interactive challenge and never can be. Build (a) and it is rebuilt
as (b) the first time you approve something from your pocket — having put
private keys in the sandbox in the meantime.

**So: (b).** Not because it is safer. Because it is the only one that lands twice.

## 3. Most of the host side is already built

This is the part that shrinks the work. `gates_panel.py` + `gates_actions.py`
are already a host-side, operator-only action surface:

- `gates_panel.collect()` builds one `GateRow` per authorization gate, using
  the same readers `diagnostic_summary` calls. It adds no state.
- `gates_actions.describe(row)` is pure — *what would pressing this do, and
  what input does it need* (`lease_grant` → `needs=("ttl", "reason")`).
- `gates_actions.apply(row, inputs)` does it, calling `lease.grant`,
  `manifest_admin.set_permission`, `identity_binding.confirm_binding`.
- It is already shared by two front ends — the TUI (`gates_tui.py`) and the
  local HTML dashboard (`gates_serve.py`) — precisely so "what does this button
  do" has one implementation.

Its module docstring states the constraint the broker must preserve:

> **This adds no new authority.** Every action here calls the same functions
> the CLI subcommands already call.

The broker is therefore **not a new mechanism**. It is a third front end on
`describe`/`apply`, plus the one thing that surface lacks: a way for an agent
to *ask*.

## 4. What is actually missing

| # | gap | notes |
|---|---|---|
| 1 | **A request channel.** Today the operator must notice a gate is off. Nothing lets a blocked task say "I need lease X, for task Y, because Z." | `human_required_enqueue/_list/_resolve` already exist (`server.py:6302-6329`, backed by `human_loop.py`, `public.human_required_queue`) with `kind: consent \| attestation \| review \| ...`. This is the queue; it needs to surface as a gate row. |
| 2 | **A presence proof that is not a tty.** ~~`sign-session` and `sign-net-task` need a passphrase.~~ **They do not — see §5b.** What they need is proof a human is present, and today the only such proof is an operator-owned controlling tty. | a delegated approval signature (§5b), not a prompt. |
| 3 | **A remote front end.** The phone driving the same `describe`/`apply`. | tier 1 u2u signal, or tier 2 terminating at `:8768` — never `:8766`, which stays loopback by §12. |

Note the asymmetry, because it decides sequencing: **the egress lease needs no
passphrase at all.** `_lease_grant` takes `ttl`, `reason`, `issuer` and calls
`lease.grant`. The only reason a lease cannot be issued in response to a
blocked task today is that nothing carries the request to a surface the
operator is looking at. That is gap 1 alone.

## 5. Design

```
  sandboxed task            host (outside bwrap)              operator
  ─────────────             ────────────────────              ────────
  blocked on a gate
      │
      ├─ enqueue request ──▶ human_required_queue
      │                          │
      │                      gates_panel.collect()
      │                        emits a request row
      │                          │
      │                      gates_actions.describe()
      │                        "needs: ttl, reason"
      │                          │
      │                          ├──────── TUI / HTML / phone ──▶ prompt
      │                          │                                  │
      │                          │◀───────── approve + (passphrase) ┘
      │                      gates_actions.apply()
      │                        lease.grant / sign / bind
      │                          │
      ◀── polls; gate now on ────┘
```

**Invariants this preserves.**

1. No key enters the sandbox. Signing happens in the host process, where
   `vault.key` and the keyring already live. Gap `1937696f6513` stays closed.
2. No new authority. The broker calls `gates_actions.apply()`, which calls the
   same functions the operator-only CLIs call. Nothing gains a capability.
3. `require_operator_terminal()` is **not weakened**. The host process that
   runs `apply()` has a real operator-owned tty (TUI) or is the operator's own
   session (HTML/phone-authenticated). The agent still fails the guard, because
   the agent still never calls the mutation.
4. One trust root. Desktop pinentry today and phone approval later drive the
   same `describe`/`apply` pair, so there is no second path to audit.

**Replay is the live risk.** u2u is Ed25519-signed but plaintext until Gate 6,
so an approval is legible in transit. Its contents are not secret — "yes, task
X" — but a captured "yes" must not authorize a second thing. The discipline
already exists in the network envelope: bind the approval to a **task id, a
nonce, and an expiry**, and make the signed task id the queue primary key, the
way `task_submit`'s `network_authorization` already does.

## 5b. Stage 2 is not a prompt — corrected 2026-09-09

This section replaces the "host-side pinentry" framing above. That framing was
wrong, and the correction changes what stage 2 costs to build.

**There is no passphrase in the signing path.** `keyring.py:123` generates with
`NoEncryption()`; `:179` stores the ed25519 private half as raw hex.
`cmd_sign_session` (`sign_session_cli.py:97-126`) gates on exactly four things:

1. `WILLOW_KEYRING` is set,
2. `require_operator_terminal()` passes,
3. a live session record exists,
4. the named verifier holds a private half.

A pinentry would unlock nothing. It would be a dialog whose only function is to
assert that a human is present.

**So what is actually guarding the operator's signature?** Both keyring files
are mode `0600`, which excludes other users — and this box has one user. The
owned-tty check in `require_operator_terminal()` is therefore the *sole* barrier
between any process running as the operator and the operator's signature. Kart
is additionally blind to the keyring only because `config/verifiers.json` is not
in the sandbox mount map (gap `4e1825878677`) — an accident of configuration,
not a lock.

Stage 2 is therefore not "add a prompt". It is **replace the only lock on the
door**, which is why it warrants a review rather than an envelope and an
afternoon.

### The delegated approval signature

The phone cannot produce a tty. It can produce something an agent cannot: a
signature under a key the box does not hold.

| piece | where it lives |
|---|---|
| approver key, **public half only** | the box's keyring — a shape `keyring.py:135` already documents and supports |
| approver key, private half | the phone, and nowhere else |
| operator signing key | the box, and nowhere else |

An **approval** is a token signed by the approver key binding
`{request_id, task_id, nonce, expires_at}` — so it authorizes *one act*, not
presence in general. `require_operator_terminal()` gains exactly one
alternative: a valid, unexpired, unreplayed approval from an enrolled approver
satisfies presence **for that act only**. The signing itself still happens on
the box under the operator key, which never travels — the rule gap
`1937696f6513` exists to protect. No approval, no signature: it fails closed.

An agent cannot mint one, because the private half it would need is not on the
box at all. That is the whole property, and it is stronger than the tty check it
replaces rather than weaker — a tty can be allocated by a process on this
machine; a signature cannot be forged without a key that is not on this machine.

### What this costs, stated plainly

- **`require_operator_terminal()` is the single chokepoint for every
  operator-only mutation** — consent writes, roster sync, frank-anchor writes,
  and signing alike (`server.py:6538`, `:6719`, `:6764` all mirror it). Widening
  it wrong compromises all of them at once, not just egress.
- **It reopens the keyring question.** An approver key must live in a ring the
  box trusts. Today there are two rings with zero overlap, both holding private
  halves (gap `6a36cfdceb5d`), and the operator ruled on 2026-09-09 to leave
  them alone. Stage 2 cannot be built around that ruling; it needs it revisited.
- **Replay is the failure to design against**, not eavesdropping. u2u is
  Ed25519-signed and plaintext until Gate 6, so an approval is legible in
  transit but not forgeable. A captured "yes" must not authorize a second thing,
  which is what the nonce and the bound `task_id` are for.

## 6. Sequencing

Three stages, each useful alone. Only the first is needed for Kart to stop
being blocked on egress.

| stage | what | unblocks |
|---|---|---|
| **1 — request rows** | blocked task enqueues; `gates_panel` renders request rows; TUI/HTML can approve | `git push` from Kart, with the operator pressing one row instead of typing a command. No passphrase needed — `lease.grant` has none. |
| **2 — delegated approval signature** (§5b) | an approval signed by an enrolled approver key satisfies presence for one bound act; signing still happens on the box | session attestation and per-task net envelopes without a terminal — **and this is the stage `git push` from Kart actually depends on**, because a task carrying `allow_net` needs the signed per-task envelope on top of the lease (`server.py:2395`), while a federated jeles call needs only the lease |
| **3 — remote front end** | the phone drives the same `describe`/`apply` over tier 1 or tier 2 | approval when the operator is not at the box |

Stage 1 touches no guard and no key. Stage 2 is where the security review
belongs. Stage 3 is the mobile app's dependency, and it needs stages 1 and 2
under it — which is the answer to *"which one needs to land for the mobile app
to function."* All three, in that order, and none of them is (a).

**The operator's requirement, stated 2026-09-09:** *"I won't have access to a
terminal when this moves to an apk."* That is not a preference about ergonomics;
it is the condition the design has to satisfy. On the phone there is no tty at
all, so `require_operator_terminal()` fails by construction and every
operator-only act becomes unreachable — not inconvenient, unreachable. Stage 2
is the load-bearing one, and stage 1's egress row alone does not get there: a
lease unblocks federated jeles, while a Kart task carrying `allow_net` still
needs the per-task signature.

Worth stating because it is the thing that makes this buildable at all: **Kart
never runs these commands.** The sudo invariant (FRANK `90e52ab7`) refuses that
and should. What the broker delivers is the *outcome* — the act happens with no
terminal in the room — by splitting it in two. Kart asks; the box acts on a
signed approval; the operator key never moves. "Let the agent do it" is
unbuildable. "Let the act happen without a terminal" is what is being built.

## 7. Open, for the operator

- **Does a request row auto-expire?** A stale "I need egress" that sits for a
  week and is then pressed grants a lease for a task that is long gone. Suggest
  the request carries the same TTL discipline as the lease it asks for.
- **Who may enqueue?** Any app with `human_required_enqueue`, or only apps
  whose manifest already holds the capability they are blocked on? The second
  is narrower and probably right — a request to grant `task_net` from an app
  that does not have `task_net` is not a request, it is an escalation.
- ~~**Stage 3 transport.**~~ **Settled 2026-09-09**, operator: *"serve is on
  8768, update the map."* Tier 2 terminates at **`:8768`** — this box's operator
  bind for `willow-mcp --serve`, not the `8765` code default, which the Nestor
  UI holds because the browser verifier key is origin-bound there. Starlink is
  CGNAT, so tier 2 remains Pangolin-or-nothing. `:8766` is not a candidate in
  either case. Build stage 3 against an interface regardless: tier 1 (u2u,
  signals-only, already built, needs nothing from Gate 6) lands first, tier 2
  follows.

---

ΔΣ=42
