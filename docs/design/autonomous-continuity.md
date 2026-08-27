# Autonomous Continuity — Keeping a Model at the Post

b17: WGRV1  ΔΣ=42

*Companion to `willow-grove-premise.md`. Grove is the seat where this
architecture is felt — the operator's Jarvis surface — but the decisions
here bind the fleet, not one repo. They belong in Nestor
(`willow-memory/Willow` charter tier).*

*Status: proposed — unsealed. Every claim under §2–§6 is evidence-backed
and marked for sealing in §7.*

---

## 1. The question, disentangled

"How do we keep a model doing this work without stopping" reads as one
question and is three.

| # | Continuity | Failure mode when absent | What it actually costs |
|---|---|---|---|
| **SC** | **Session continuity.** A specific agent's work survives context death, container recycle, or model swap. | The next model boots amnesic and re-derives what the last one already decided. | *The house's largest development cost is redoing things* ([`docs/the-house-already-knew.md`, §3](../../../safe-app-store/docs/the-house-already-knew.md)). |
| **DC** | **Duty continuity.** Someone is always at the post. LISTEN/NOTIFY fires and something answers; a journal write happens and something files it; the roster stays fresh. | Signals accumulate unwatched; the room has no cursor; the seat is unattended. | Every unattended signal is a missed handoff or a missed intervention. |
| **EC** | **Escalation continuity.** The resident watcher knows when to wake a bigger model, and the bigger model knows what the watcher was watching for. | Small models act above their authority; big models get pulled in for work small models could have done; the ladder between them is a fiction. | Cost per turn goes up (episodic big-model burn) or trust goes down (small-model overreach). |

Solving one does not solve the others. Session continuity is a memory
problem, duty continuity is a scheduling problem, escalation continuity
is a governance problem. The fleet already has the answers to the first
two, half-built. The third is where this doc lives.

---

## 2. Session continuity — already built, not yet pointed inward

**C1 (evidence).** Every organ needed for session continuity is
promoted:

- **Nestor** — sealed pairs, evidence, warrants, ledger. `mem_ratify` +
  Article IV enforce the promotion tiers. Cryptographic seal:
  *"forging a witness in mine is one `UPDATE`; in Nestor a transplanted
  signature and a swapped body were both refused, the second at
  similarity 1.00"* ([`docs/the-house-already-knew.md`, §2](../../../safe-app-store/docs/the-house-already-knew.md)).
- **Jeles** — verified-corpus organ in front of live search;
  `conflict_scan` finds what refutes rather than what resembles.
  1,028 nuggets across 74 seed files.
- **kb_journal** — chat substrate; every operator turn writes an atom
  with `domain: "journal"` ([`willow-mcp/src/willow_mcp/server.py:2607`](../../../willow-mcp/src/willow_mcp/server.py)).
- **seed's six movements** — the onboarding IS the resume path ([D16](willow-grove-premise.md#d16)).
  A fresh model that walks the seed enters the room oriented.

**C2 (sealed).** *The house already knows how to remember. It has not
yet been pointed at its own codebase and decision history.* The
rediscovery tax measured on 2026-08-05 was four organs re-implemented
worse in one session because the promoted answers were unreachable at
the moment of building ([the-house-already-knew.md, §2](../../../safe-app-store/docs/the-house-already-knew.md)).

**C3 (decision).** Session continuity **is a solved problem** and does
not need new mechanism. It needs the discipline of use: **read Nestor
and Jeles before writing.** Grove's first-boot pass (seed's Movement 4)
and every task's first-bite pass (SAPS1 CLAUDE.md rule 11) enforce this.

**Evidence:** `safe-app-store/CLAUDE.md` (rule 11), `docs/the-house-already-knew.md`,
`willow/seed/seed.py`, `willow-grove-premise.md` D16.

**Warrant:** Every organ named here is already promoted (Article IV
canonical) and each carries its own tests. The failure mode of §2 is
*not looking*, not *no mechanism*.

---

## 3. Duty continuity — the resident-watcher pattern

**C4 (evidence, three tiers of model cost).** Below the tier of a
production API call, there is a class of work that must happen
continuously and cannot afford episodic pricing:

| Kind of work | Cadence | Correct tier |
|---|---|---|
| LISTEN/NOTIFY handler on grove.messages | every event | local |
| Kart drain — pick up the next queued task | every 30s–5min | local |
| Journal atom write from operator turn | every operator turn | local |
| Roster refresh from fleet-presence | every ~60s | local |
| First-pass anomaly flag on a diff, a log, a comment | every event | local |
| Design synthesis, adversarial verification, ratification | on demand | remote (Opus/Sonnet-tier) |
| Any code change to a promoted organ | on demand + witnessed | remote + human |

Local models on this box: Ollama on `http://localhost:11434`, model
switching wired through willow-mcp; the operator's active model lives
in SOIL at `~/.willow/store`. The pipes exist; the discipline for
*which model runs which loop* does not.

**C5 (decision).** The seat's model tier **at rest is small**. Big
models are summoned, not resident. This inverts the current shape of
Grove where the served page implies "the operator is talking to a big
model" — the served page in fact talks to a *local resident watcher*
that summons a bigger model when the watcher's authority runs out.

Precedent: this is what Tony's workshop actually is in Iron Man. Jarvis
resides. Jarvis is not the ARC reactor. Tony calls "Jarvis, run a
diagnostic" and Jarvis picks up.

**Evidence:** `willow-mcp` model-switching code, Ollama endpoint
present, `~/.willow/store/active_model`.
`willow-grove-premise.md` D14 (workshop metaphor).

**Warrant:** Duty continuity requires a warm process, and warmth on
this box is free only for local models. A remote-model resident watcher
either burns tokens every minute (unaffordable) or sleeps between
polls (defeats the purpose).

---

## 4. Escalation continuity — Kart as the seam

**C6 (evidence).** `public.tasks` already exists. `willow_task_submit`
is the MCP tool. The willow-mcp server has a whole task queue with
sandboxing (Kart/bwrap, no ambient capability, see `safe-app-store/CLAUDE.md`
rule 7).

**C7 (decision).** **Every escalation from small model to big is a
Kart task.** The resident watcher never *calls* a bigger model
directly. It *files*. Filing is a first-class operation with a shape:

```
kart_submit({
  origin: "grove.watcher",           # who's asking
  kind: "design.synth" | "verify" | "ratify" | "code.change",
  urgency: "background" | "operator-visible" | "operator-blocking",
  context_refs: [atom_ids, file_paths, PR_urls],
  authority_needed: L2 | L3 | L4,     # see §5
  proposed_action: "<what the big model should do>",
  refusal_ok: true                    # small model must be OK with 'no'
})
```

This shape is the small model's promise: *"I saw something. I do not
have the authority to act on it. Here is enough for someone who does."*

**C8 (decision).** The **operator picks the model** that drains a
Kart task. Not the small model. The Kart card in Grove shows queued
tasks with the small model's proposed authority level; the operator
routes each to the tier they judge fit. Auto-drain by rule is
deferred to a later decision ([open Q]).

**Evidence:** `willow-mcp/src/willow_mcp/server.py` (kart submission);
`safe-app-store/CLAUDE.md` rules 6–8 (sandbox + no self-grant + witness
promotion).

**Warrant:** §0.3 of the SAPS1 constitution: *"a build runs under
Kart/bwrap with no ambient capability, and may not widen its own reach
or mint its own authority."* The same rule that keeps playground apps
sandboxed keeps a local model from summoning a big model unattended.

---

## 5. The promotion-authority ladder for local models

The Article IV tiers already govern *knowledge*: Contested → Frontier
→ Canonical. This ladder governs *action*, and maps against them.

| L | Local model may (unattended) | Article IV analog | Why safe |
|---|---|---|---|
| **L0** | Read anything the roster grants read on. | (below the ladder — reads are not writes) | Reads leave no trace of intent, and Nestor's seal + Jeles's verify catch any wrong claim about a read before it reaches canonical. |
| **L1** | Write to `kb_journal` (`domain: "journal"`). Write a Kart draft. Refresh the fleet-presence roster. Note an envelope re-attestation is due. | Contested — the entry exists, nothing depends on it, nobody has agreed. | Anything L1 writes is single-source and pre-ratification. Article IV's contested tier is exactly the place for the small model's guesses. |
| **L2** | Draft a proposal, a Nestor pair (`status: "proposed"`, `verifier: null`), a review comment, a PR description body. | Frontier — proposed for adoption, awaiting a witness. | The proposal exists; nothing promotes it. §0.2 (*proposing and ratifying never rest in the same hand*) is preserved: the small model proposed, cannot ratify. |
| **L3** | *Nothing here — this rung is deliberately empty.* | (would be: promote frontier → canonical) | This is the seat's decision. A small model that could promote could rewrite policy without being noticed. The empty rung is a load-bearing choice. |
| **L4** | Nothing. Ever. Push code, seal a Nestor pair, toggle consent, ratify anything, approve a PR, merge a PR, spend money. | Canonical — the fleet's law. | Every L4 action is a promise the fleet keeps; a local-model L4 promise costs more to un-make than it costs to make. |

**C9 (sealed).** *The rungs are the promise. Every rung you grant is a
promise you cannot take back cheaply.* Add rungs only after evidence
that the current ceiling is genuinely losing work; never to reduce
operator overhead alone.

**C10 (evidence).** The rungs above are consistent with mechanisms
already in the code:

- L1 journal writes: `kb_journal` already accepts small-model authorship
  ([`willow-mcp/src/willow_mcp/server.py:2607`](../../../willow-mcp/src/willow_mcp/server.py)).
- L2 Nestor proposals: `status="proposed"` + `verifier=null` is exactly
  the state a small model leaves a pair in; sealing requires a distinct
  operator (Nestor `docs/agent-guide.md`, `CLAUDE.md`: *"You may propose.
  You may not confirm. No `status='sealed'` and no `verifier=` carrying
  a human's name unless they signed in `nestor ui`."*).
- L4 empty: `promote_check.py` fail-closed on any playground build
  attempting to promote itself (`safe-app-store` rule 8).

**Warrant:** The witness-count constitutional rule
(*"three instances of one model are one witness, not three"* — cited in
[the-house-already-knew.md, §6](../../../safe-app-store/docs/the-house-already-knew.md))
applies to small models the same way it applies to big ones. A local
7B is not a second reader, regardless of how many instances you run.
That is why L3 is empty and L4 is not.

---

## 6. What this changes about Grove

**C11 (decision).** Grove's served page (D4) hosts the **resident
watcher** as its default backend actor. The page's `<grove-envelope-panel>`,
`<grove-refusal-chip>`, `<grove-cast-chip>`, `<grove-card>`, and the
forthcoming chat card and dispatch rail all render *what the resident
watcher is doing* — not "what the operator's remote model just said."

Concretely:
- The chat card's LEFT side (operator → Willow) writes to `kb_journal`
  via the small model at L1.
- The chat card's RIGHT side (Willow → operator) is the resident
  watcher's read-back — L1 writes plus any Kart task the watcher
  filed since the last operator visit.
- Any operator message that clearly exceeds L2 (a design ask, a code
  ask, an ambiguous request) becomes a Kart task; Grove routes it, the
  operator picks the model.

**C12 (decision).** The tri-modal switch (Governance / PM / PA — [P8](willow-grove-premise.md))
is a **lens on the Kart queue** first, not a workspace divider. Each
lens filters the queue to the tasks that lens's operator-persona cares
about:
- **Governance** — L4-authority-needed Kart items, envelope re-attestation
  reminders, refusal chips from Nestor.
- **PM** — L2/L3-authority-needed items, unclaimed roster items,
  outstanding proposals.
- **PA** — L1-authority-needed items, upcoming reminders (send_later),
  operator's own drafts.

**C13 (open).** Auto-drain: whether Kart may auto-route certain kinds
of task to a specific model tier without operator click. Default
proposal: **no auto-drain in v1.** Every task waits for the operator
to click a tier. Revisit when the queue depth exceeds what the operator
can visit per waking hour, with measured evidence of missed handoffs.

---

## 7. Nestor sealing recipe

The pairs below are the ones to seal into
`$WILLOW_HOME/nestor/willows-grove.db` (or, if these bind fleet-wide,
into the charter store at `willow-memory/Willow`). Each pair's
evidence and warrant lines are the ones already given in §2–§6 above;
this section just prescribes the shape.

```
C1  source: "Session continuity is a solved problem for the Willow fleet."
    target: "Yes — via Nestor + Jeles + kb_journal + seed's six movements."
    evidence: [
      ("doc", "safe-app-store/docs/the-house-already-knew.md", "§2, four rediscoveries"),
      ("doc", "willows-grove/docs/design/willow-grove-premise.md", "D16"),
      ("file", "willow-memory/willow/seed/seed.py", "the six movements"),
      ("file", "willow-mcp/src/willow_mcp/server.py", "kb_journal at 2607"),
    ]
    warrant: "Every organ named is already promoted (Article IV canonical)
             and carries its own tests. Failure mode is not-looking, not
             no-mechanism."

C3  source: "The fix for session continuity is discipline, not new code."
    target: "Yes — first-boot passes Grove through seed's movements;
             SAPS1 rule 11 forces the pre-build lookup."
    evidence: [
      ("file", "safe-app-store/CLAUDE.md", "operating rule 11"),
      ("doc", "willows-grove/docs/design/willow-grove-premise.md", "D16"),
    ]
    warrant: "Article IV, Jeles conflict_scan, Nestor seal all already
             run. Adding another layer would be a fifth rediscovery."

C5  source: "The seat's resident actor at rest is a local (Ollama) model.
             Big models are summoned via Kart, not resident."
    target: "Yes."
    evidence: [
      ("endpoint", "http://localhost:11434", "Ollama on this box"),
      ("file", "willow-mcp model switching", "SOIL active_model at ~/.willow/store"),
      ("doc", "willow-grove-premise.md", "D14 workshop metaphor"),
    ]
    warrant: "Remote-tier residency is either wasteful (poll burn) or
             absent (sleep). Local-tier residency is the only affordable
             warm-process posture on this box."

C7  source: "Every escalation from local model to bigger model is a
             Kart task; local model never calls a bigger model directly."
    target: "Yes."
    evidence: [
      ("tool", "willow_task_submit", "MCP tool exists"),
      ("schema", "public.tasks", "queue exists"),
      ("file", "safe-app-store/CLAUDE.md", "rules 6–8: sandbox, no self-grant, witness promotion"),
    ]
    warrant: "§0.3 forbids a sandboxed builder from minting its own
             authority. A local model summoning a big model is exactly
             that shape of self-mint."

C8  source: "The operator picks the model that drains a Kart task in v1.
             No auto-drain."
    target: "Yes."
    evidence: [ ("this doc", "§6 C13", "open question deferred") ]
    warrant: "Auto-drain is a promotion of local-model authority — put
             through the same discipline as any other L3 grant. Revisit
             with measured evidence of missed handoffs."

C9  source: "Each rung on the local-model promotion-authority ladder is
             a promise that is costly to un-make."
    target: "Add rungs only against measured missed-work evidence; never
             to reduce operator overhead alone."
    evidence: [
      ("doc", "the-house-already-knew.md", "§6 witness-count rule"),
      ("law", "constitution.md", "Article VIII amendment discipline"),
    ]
    warrant: "Undoing a granted rung means every action the small model
             took under that rung is now suspect. Grants ratchet
             forward; ungrants ratchet the whole ledger back."

C11 source: "Grove's served page hosts the resident local watcher as
             its default backend actor."
    target: "Yes."
    evidence: [
      ("doc", "willow-grove-premise.md", "D4, D9, D12"),
      ("PRs", "willows-grove #38 #39 #40 #41", "primitives + scaffold landed"),
    ]
    warrant: "The Web Components already landed (grove-card,
             grove-envelope-panel, grove-refusal-chip, grove-cast-chip,
             layout-memory) all render state, not remote-model chat.
             The chat card is the one seam that could implicitly carry
             a remote model — this decision keeps it local by default."

L0..L4  source: "Local model authority is capped at L2. L3 is empty by design. L4 is never."
        target: "Yes."
        evidence: [
          ("file", "willow-mcp/src/willow_mcp/server.py", "kb_journal accepts small-model authorship (L1)"),
          ("doc", "Nestor/CLAUDE.md", "'You may propose. You may not confirm.' (L2 ceiling)"),
          ("file", "safe-app-store/stores/promote_check.py", "fail-closed on self-promotion (L4 guard)"),
        ]
        warrant: "Independence rule: three instances of one model are
                 one witness. A local 7B cannot ratify what a local 7B
                 proposed, regardless of instance count."
```

Optional pairs to seal after operator use exposes them:
- Whether L1 write cadence needs its own throttle (small model spamming journal).
- Whether the tri-modal lens should hide L1 items entirely from Governance view.
- Whether Kart should carry the resident watcher's confidence score alongside the escalation.

---

## 8. What this doc is not

- **Not** an implementation plan for the resident watcher process.
  That's a separate proposal — probably an appendix to
  `willow-grove-premise.md` under Gate 5 or a new file
  `docs/design/resident-watcher.md`. This doc pins the *authority*, not
  the *runtime*.
- **Not** a proposal to change `willow-mcp` or any promoted organ. The
  authority ladder describes what a local model is *permitted* to do
  today, using the mechanisms already in the code. Any code change
  that would extend those mechanisms is itself an L4 action.
- **Not** a Grove-only decision. Grove is the *first* seat that hosts a
  resident watcher, but the ladder binds any surface any small model
  runs behind.

---

*Proposed by the machine. Unsealed. `ΔΣ=42`*
