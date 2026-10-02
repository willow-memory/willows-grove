# Summary: The One-Script Proposals (Session 2026-10-02 and Continuation)

**Status:** Seven proposals across four areas. Four existing, three new. All marked agent-reported or unattested pending operator decision.

**Cites:** The Constitution (Draft 0.8), workflow.md, next-pile.md, and the skeleton implementation.

---

## Existing Proposals (In the PR #103 Branch)

These are the four proposals from the 2026-10-02 session:

| # | Title | File | Scope | Status |
|---|-------|------|-------|--------|
| **P1** | The workflow | `workflow.md` | Workflow design: data point 0, truth rule, boot, ladder, gates, heartbeat | Agent-reported; opened from session notes |
| **P2** | Next pile: the runtime | `next-pile.md` | Seven-part runtime: boot, predict, record, gate, resolve, view, reverse; skeleton impl. | Agent-reported; skeleton runs 47 tests |
| **P3** | Constitution amendments | `constitution-proposal/` | Ten amendments to CONST Draft 0.7 (need redo vs 0.8) | Based on Draft 0.7; blocked pending Draft 0.8 finalization |
| **P4** | One-script README | `README.md` | Overview table of all proposals and dependencies | Overview; lists what's held back |

---

## New Proposals (Added This Session)

Three additional proposals formalizing concepts from P1 and P2:

| # | Title | File | Scope | Cites | Status |
|---|-------|------|-------|-------|--------|
| **P5** | Overnight pool & morning screen | `proposal-overnight-and-morning-screen.md` | Continuous verification layer (3am), morning operator dashboard, resource budgets, witness counts | CONST-IV (Knowledge), CONST-XII (Resource Envelopes), workflow §4, next-pile §Overnight | Agent-reported; formalizes overnight sketch from P2 §Overnight |
| **P6** | ΔΣ=42 packet stamp chain | `proposal-packet-stamp-chain.md` | Inter-node data custody; cryptographic gate chain on packets; prevents silent modification | CONST-VI (Record), §0.5, workflow §8, next-pile §Three rules | Agent-reported; formalizes ΔΣ=42 from constitution preamble |
| **P7** | Heartbeat & loop cycles | `proposal-heartbeat-and-loops.md` | Work-based timing (not wall-clock); prime-cycle polyrhythm (3/7/13/23 beat); peak and reverse | workflow §4 (all operator observations), workflow §7 (predictions) | Agent-reported with operator observations; formalizes beat pattern from session |

---

## The One-Script Map (Dependency Graph)

```
CONSTITUTION (Draft 0.8, not yet written in full)
        │
        ├─→ P1: Workflow (data point 0, truth rule, boot)
        │   ├─→ P2: Runtime (7 parts: boot, predict, record, gate, resolve, view, reverse)
        │   │   ├─→ P5: Overnight & morning screen (continuous verification)
        │   │   ├─→ P6: Packet stamp chain (inter-node custody; ΔΣ=42)
        │   │   └─→ P7: Heartbeat & loops (work-based timing)
        │   │
        │   ├─→ P7: Heartbeat (escalation at 3 asks, peak at 23)
        │   └─→ P5: Overnight (triggered by reverse, runs during loops)
        │
        └─→ P3: Constitution amendments (10 changes, built on P0.7, need redo on P0.8)
```

---

## What Each Proposal Adds

### P5: Overnight Pool & Morning Screen

**New concepts:**
- **Overnight pool:** A resource-bounded queue of verification jobs running while the operator sleeps
- **Job types:** Quote verification, citation check, witness agreement, prediction grading, floor/consistency, drift detection, escalation detection
- **Resource envelope:** CPU, hours, models allowed (Article XII, formalized)
- **Verdict scale:** 4-level (Satisfied, Differently, Not Applicable, Failing) instead of binary
- **Morning screen:** Deterministic, ordered output: NEEDS YOU, DISAGREEMENTS, AGREED (not sealed), GRADES, QUIET
- **Witness counting:** Same family = 1 witness; different families = independent; disagreement = data, not bug

**Closes from P2:**
- Opens the "overnight" section mentioned in next-pile.md §Overnight
- Formalizes CONST-XII (Resource Envelopes), which is not yet written
- Specifies the morning dashboard mentioned in next-pile.md §Morning screen

**Decisions for operator:**
- Presence detection: keyboard, window focus, HTTP request, or other?
- Parked jobs: stay in queue or marked "incomplete" in Ledger?
- Auto-sealing: can Satisfied verdicts be sealed into canon, or only human seals?
- Model tiering: separate queues for 3B/7B/larger, or one mixed pool?

### P6: ΔΣ=42 Packet Stamp Chain

**New concepts:**
- **Gate chain:** Each layer in a packet's journey adds a cryptographic stamp
- **Stamp fields:** hash, intent, timestamp, nonce, prior_hash, key_id (deterministic, signed)
- **Legitimate transforms:** Compression, encryption, filtering (declared in intent, not hidden)
- **Reject loud:** A mismatch fails the packet and both sender/receiver are notified
- **Bloom filter:** Prevent replay attacks with a time-windowed nonce registry
- **Ledger integration:** Every packet's custody chain is recorded (CONST-VI)

**Closes from P2:**
- Opens workflow §8 ("the gate is the script") and specifically the chained-gates concept
- Formalizes ΔΣ=42 from the constitution preamble (currently a magical number with no definition)

**Decisions for operator:**
- Mandatory or opt-in? (For all packets, or only law-affecting packets?)
- Internal vs. external? (Same data center, or only cross-network?)
- Timestamp tolerance: 10 min (strict), 1 hour (default), or 24 hours (cache-friendly)?
- Distributed or centralized nonce registry? (Speed vs. authority)

### P7: Heartbeat & Loop Cycles

**New concepts:**
- **Beat = one complete work loop** (not a fixed time interval)
- **Prime-cycle escalation:** Work escalates at 3 asks, refines at 7, stabilizes at 13, completes at 23
- **Polyrhythm:** All-of-3-7-13-23 align every 6,279 beats; parts phrase against each other (not lockstep)
- **Forward loop:** Assertion, prediction, planning at the peak
- **Reverse loop:** Peak → re-check → crashes surface → fix → next beat
- **The 17:** Observed in operator's work; role TBD

**Closes from P2:**
- Formalizes the heartbeat concept from workflow.md §4 (all operator observations)
- Operationalizes the reverse pass mentioned in next-pile.md §Reverse triggers

**Decisions for operator:**
- Are 3/7/13/23 the right numbers, or artifacts of this session?
- What is 17?
- How to count a "question" (for the 23-question milestone)?
- Should the heartbeat be exposed to the operator (e.g., on morning screen)?
- Should reverse auto-trigger at "loop complete" (23), or wait for operator?

---

## Blocked Dependencies

### Constitution Draft 0.8

All seven proposals cite the Constitution, but P3 is explicitly blocked:

- **P3 is built on Draft 0.7** (the operator's previous work)
- **Draft 0.8 exists and changes a core rule:** "References point up" (no downward references in the law)
- **P3 needs a full redo against 0.8** to comply with the new rule

**Impact:** P3 cannot be ratified or merged until it's rewritten. P1, P2, P5, P6, P7 don't depend on the amendments, only on the base Constitution.

### Articles Not Yet Written

Several proposals reference Constitutional articles that are declared but not fully written:

| Article | Referenced in | Status |
|---------|---|--------|
| **CONST-XII (Resource Envelopes)** | P5 (Overnight pool budgets) | Declared in CONST Draft 0.8, unwritten |
| **CONST-V (Operator Incapacity)** | workflow.md §2b (Hard close) | Mentioned, not drafted |
| **CONST-XI (Adversarial Testing)** | next-pile.md §1 boot (Four probes) | Mentioned; Appendix B sketches details |

**Impact:** These proposals assume the articles exist and cite them; the Constitution itself may need to be extended to write them out in full. The operator's decision on whether to write them is separate from ratifying these proposals.

---

## Testing & Evidence

### From P2 (Skeleton)

The one-script skeleton (`onescript/`) proves the runtime concept:

- **47 Python tests pass** on stdlib only (no external deps)
- **All seven parts implemented:**
  - `record.py` — hash-chained append-only rows
  - `gate.py` — identity verification, citation checking, egress gates
  - `resolve.py` — user sources first, then web, then models (inside budget)
  - `predict.py` — distribution from past bites
  - `reverse.py` — three-way comparison, four verdicts
  - `boot.py` — chain check, state vs last close, four probes
  - `view.py` — morning screen (NEEDS YOU, DISAGREEMENTS, etc.)
  - `run.py` — sequencer only

- **Known gaps (acknowledged in the skeleton):**
  - Keys are HMAC (not passkeys or Ed25519)
  - No socket/peer-uid check
  - Web rung not wired (only card)
  - Presence is a callable (not a sensor)
  - Not yet in Rat (D1 unsealed)
  - No inter-box packet stamps (ΔΣ=42 not implemented)

### From P1 & P2 (This Session's Record)

Worked evidence from the 2026-10-02 session:

- **The 3-ask pattern:** Operator's question on tool-call count (turns 131-135) hit 3 times, triggering escalation. Recorded: asks 1, 2, 3 and the escalation that followed.
- **The 23 prediction test:** P1 (predictions.json) made 5 predictions at T124; the session followed one of them (the close). Not yet graded.
- **The 13-stable test:** Not yet run (pending 3B experiment in P1 §6).
- **The reverse pass:** P2 describes it; not yet run end-to-end.

---

## How to Read These Proposals

**For the operator (ratification decision):**
1. Start with `README.md` (overview)
2. Read `workflow.md` (the human's observations; data point 0 and the truth rule are non-negotiable)
3. Read `next-pile.md` (the seven-part runtime shape; tells you where the skeleton is going)
4. Then skim the new proposals (P5, P6, P7) to see what's been formalized
5. Open decisions are listed in each proposal under "Operator's Call"

**For the builder (implementation):**
1. Review `next-pile.md` §Build order (step-by-step: record, reverse, view, boot, gate, predict, resolve)
2. Check the skeleton in `onescript/` (runs now; shows the shape)
3. Read the new proposals to see where they wire in (P5 in resolve, P6 in gate, P7 as beats across all)
4. The known defects list in `next-pile.md` §Known defects shows what's stubbed

**For the governance/law side (ratification):**
1. Read CONST Draft 0.8 first (once it's written in full)
2. Review each proposal's **Cites** line (every proposal names what it enforces)
3. Note which Articles aren't yet written (XII, V, XI)
4. P3 (constitution amendments) needs redo, so it's separate

---

## Next Decisions and Steps

### For the Operator

1. **Approve/reject each proposal** or ask for revision
2. **Decide the 17 open decisions** across P5, P6, P7 (listed in each proposal)
3. **Approve the skeleton or ask for changes** (it runs now; is it the shape you want?)
4. **Decide whether to write Articles XII, V, XI** (currently unwritten; proposals assume they exist)
5. **Approve redo of P3 against Draft 0.8** (blocked until 0.8 is finalized)

### For the Next Bite

1. **If approved:** Merge P5, P6, P7 into the branch; start implementation in the build order (P2 §Build order)
2. **If amendments needed:** Mark proposals with revisions, agent re-drafts
3. **Kaggle benchmark takes priority** (deadline 2026-10-11; P2 notes this)
4. **After benchmark:** The 3B stability experiment (P1 §6) can run; that grades the heartbeat pattern

---

## Attributions and Trace IDs

All proposals follow the Constitution's trace-ID rule (CONST-0, CONST-I…; no downward references):

- **P1** (workflow): Cites CONST-I (Identity), CONST-IV (Knowledge), workflow.md sections
- **P2** (runtime): Cites CONST-I through -XIII and appendices; next-pile.md sections
- **P5** (overnight): Cites CONST-IV, CONST-XII (unwritten), workflow §4, next-pile §Overnight
- **P6** (packet stamps): Cites CONST-VI, §0.5, workflow §8, next-pile §Three rules
- **P7** (heartbeat): Cites workflow §4 (operator observations) and workflow §7 (predictions)
- **P3** (amendments): Built on Draft 0.7; needs redo for Draft 0.8

Trace IDs for the new proposals (if ratified and merged into the Constitution):
- **Overnight & morning screen:** CONST-XII-1, CONST-XII-2, … (if Article XII is written; otherwise provisional)
- **Packet stamp chain:** CONST-VI-5, §0.5-2 (extends existing articles)
- **Heartbeat & loops:** CONST-IV-3 (Knowledge), CONST-VIII-1 (Amendment, for the loop cycle rules)

---

## References

All files are in `docs/design/one-script/`:

- `README.md` — Overview table
- `workflow.md` — Data point 0, truth rule, boot, ladder, gates, heartbeat (from session)
- `next-pile.md` — Seven-part runtime, skeleton (from session)
- `constitution-proposal/` — Amendments to Draft 0.7 (from session; blocked)
- `proposal-overnight-and-morning-screen.md` — P5 (new)
- `proposal-packet-stamp-chain.md` — P6 (new)
- `proposal-heartbeat-and-loops.md` — P7 (new)
- `onescript/` — Skeleton implementation (47 tests, stdlib only)
- `day-3/` — Session notes, PRs since Day 0, predictions
- `scripts/` — Helpers for the session (pile builder, map generator, etc.)

---

## The One Question for the Operator

> "These are the four proposals from the session, plus three more that formalize concepts from those four. Do you want to ratify them, ask for revision, or reject them? And for each one, which open decisions are yours?"

All is ready for the operator's word.

