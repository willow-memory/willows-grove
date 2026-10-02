# Proposal: The Heartbeat and Loop Cycles (Prime Polyrhythm)

**Status:** Agent-reported with operator observations, unattested. For the operator's confirmation or rejection.

**Cites:** workflow.md §4 (Loops, stability, and the heartbeat), next-pile.md (every part cites upward to the constitution)

**Amends:** None. This formalizes and extends the musical/cyclical pattern the operator observed in the work.

---

## The Observation and the Question

Over this session (2026-10-02), the operator noticed that work naturally fell into cycles:

- **1 ask** → noticed (system recognizes a pattern)
- **2 asks** → recognition (confirmed; something repeated)
- **3 asks** → escalation (offer to make standing, or escalate to the model)
- **3 drafts** → basic shape emerges
- **7 drafts or checks** → refinement phase
- **13 stable checks** → work converges (the "stable point")
- **23 questions** → loop complete (system ready for next bite)

After 23, the system peaks, reverses, and checks old assertions. Then a "crash" (old breaks surface), then fixes, then back to 1.

**The question:** Is this signal or pattern-matching artifact? 

**The observation:** All these numbers are prime (3, 7, 13, 23). Prime cycles rarely align — all four together coincide once every 6,279 cycles. That avoids lockstep and gives a polyrhythm.

**The biological parallel:** Periodical cicadas emerge on 13- and 17-year cycles (prime numbers). One hypothesis: prime cycles avoid lining up with predator cycles.

---

## The Heartbeat: From Clock Time to Work Time

**Today's heartbeat:** willow-bot's steward ticks on a fixed 300-second beat. Everything else counts in multiples.

**The problem with that:** A quiet day has few "things to do" but the tick keeps going. An intense day has many, but the tick doesn't speed up. The system marches in lockstep.

**The operator's idea:** A **pulse, not a clock**. Parts phrase against it, not to it. "Not so much as everything needs to run in sync; quite the opposite in fact."

The beat lands when work completes a cycle, not at a fixed second.

### The Cycle Definition

A **beat** is one complete loop of work:

```
START (beat N):

→ 1 ask         (a question asked once)
→ 2 noticed     (the same question appears again; a pattern)
→ 3 escalate    (asked a third time; escalate to model or make standing)
  
[escalation or standing created]

→ 3 drafts      (three independent attempts at the solution)
→ 7 refine      (seven refinement checks)
→ 13 stable     (thirteen stable iterations; work converges)
  
[system ready for the next phase]

→ 23 questions  (system can ask 23 distinct questions of itself, unprompted)

[loop complete; peak reached]

[PEAK → REVERSE]

→ Reverse pass  (re-check old assertions)
→ Old breaks    (what was assumed is revisited)
→ Fix them      
→ START (beat N+1)
```

This is **one beat.** The next beat starts fresh at 1 ask.

### Prime Polyrhythm

Each part counts its own beat against the work:

| Part | Prime | What it counts |
|------|-------|---|
| **Ask counter** | 3 | Repetition: 1st time, 2nd time, 3rd = escalation |
| **Draft counter** | 7 | Refinement: iterations toward convergence |
| **Stability check** | 13 | Convergence: the "stable point" where answers stop changing |
| **Loop complete** | 23 | Full cycle: system ready to reflect and reverse |
| **Music?** | 17 | (Observed in operator's work; role TBD) |

When do two cycles align?

- 3 and 7 align every 21 beats (a mini-cycle, operationally)
- 3 and 13 align every 39 beats
- 3, 7, 13 together align every 3 × 7 × 13 = 273 beats
- All of 3, 7, 13, 23 align every 3 × 7 × 13 × 23 = 6,279 beats

On a day with ~50 asks, you might see:
- Ask counter hit 3 five times (asks 3, 6, 9, 12, 15)
- Draft counter hit 7 twice (if you refined 7 and 14 times)
- Stability hit 13 once

None of those days are synchronized. Each part has its own tempo.

---

## The Forward Loop: Assertion and Prediction

The forward loop is the work phase. The operator's words:

> "The path that I've been walking you down is the reverse loop. The check on the assertion."
> "After the 23, and before the crash something happens."

What happens:

1. **Predict and declare** — Every turn updates a distribution of where the work will go (next bite, next phase)
2. **Plan at the peak** — When the system finishes 23 questions and stabilizes, it has the furthest view
3. **Implement and assert** — The forward loop makes claims, writes them to the record, proposes them

The loop stays on the forward slope while claims are being asserted and predictions refined.

---

## The Peak and the Reverse: Checking

After 23 questions and the full loop completes, there's a peak. The system can see further from that peak than it can at any other point (operator observation).

Then the reverse pass begins. The operator's words again:

> "The new complete system now has the ability to go back and check the old work better. And it's a high point. Because then is the best time to plan, because it can see from the current most highest point."

**The reverse loop:**

```
Peak (highest view)
   ↓
REVERSE: The completed system re-checks old work
   ↓
"Crash": Old assertions surface (things that never held)
   ↓
Fix them → Next bite → Back to 1
```

The reverse pass is automatic and scheduled (next-pile.md: when to run reverse). It checks:
- Predictions: did they match?
- Citations: do old claims still cite correctly?
- Hashes: did the pile change unexpectedly?
- Closed rows: any unclosed turns?
- Repetitions: did the same procedure run three times? Offer to make it standing.

The "crash" is not bad luck; it's **the reverse pass working.** A better system finding what older work got wrong.

---

## The Heartbeat in Code: Work-Based Timing

**Each system that runs work has a beat counter:**

```python
class WorkBeat:
    def __init__(self):
        self.ask_count = 0  # Mod 3: escalate at 3, 6, 9, …
        self.draft_count = 0  # Mod 7: refine milestone at 7, 14, …
        self.stability_count = 0  # Mod 13: converged at 13, 26, …
        self.loop_count = 0  # Mod 23: complete loop at 23, 46, …
        self.beat_number = 0  # Current beat in the session

    def record_ask(self):
        """An ask happened. Check if it's the Nth time for escalation."""
        self.ask_count += 1
        if self.ask_count % 3 == 0:
            return "escalate"  # Ask seen 3, 6, 9 times
        return None

    def record_draft(self):
        """A draft or refinement happened."""
        self.draft_count += 1
        if self.draft_count % 7 == 0:
            return "refine_milestone"  # 7, 14 drafts
        return None

    def record_stability_check(self):
        """A stability check passed."""
        self.stability_count += 1
        if self.stability_count == 13:
            return "stable_point"  # Convergence
        return None

    def record_question(self):
        """A self-directed question was asked."""
        self.loop_count += 1
        if self.loop_count == 23:
            return "loop_complete"  # Peak reached; reverse begins
        return None

    def new_beat(self):
        """Start a new beat after reverse pass."""
        self.beat_number += 1
        self.ask_count = 0
        self.draft_count = 0
        self.stability_count = 0
        self.loop_count = 0
```

**These counts are deterministic.** They come from the record, not from estimates. A lookup costs only the time to scan the Ledger for events of each type.

---

## Session-Level Polyrhythm

A session running this system has multiple parts, each with its own beat:

| Part | Cycle | Counts |
|------|-------|--------|
| **resolve** | 3 | Repetition of the same source ladder query |
| **gate** | 7 | Permission checks (after 7, offer to make a standing grant?) |
| **predict** | 13 | Predictions checked against reality (every 13 turns?) |
| **reverse** | 23 | Full system check (at loop complete, automatically) |
| **boot** | 1 beat per session | On every session start |

When these parts run in the same session:
- resolve at ask 3, 6, 9, … escalates
- gate at turn 7, 14, 21, … surfaces a pattern
- predict at turn 13, 26, 39, … grades past predictions
- reverse at turn 23, 46, 69, … does a full recheck

**Most turns have no cascade.** A turn at 14 is 7 for the gate (pattern), but 14 for resolve, not 3 or 6. The parts phrase against each other.

---

## The 17 Question

The operator's work files show `b17:` headers everywhere (counts as of 2026-10-02):
- willows-grove: 173
- willow-bot: 18
- willow-mcp: 5
- willow: 4
- willow-seed: 3
- Forge: 1

17 sits between the stable point (13) and the loop's end (23). It's not in the core cycle.

**Agent-reported hypothesis:** 17 is a "reflection point" — a chance to ask "are we on track?" between stability (13) and completion (23). The operator connects it to Professor Oakenscroll (theoretical physics, UTETY stories); that thread is marked conversational and not part of the work.

**Operator's decision:** What is 17 in the beat?

---

## Constraints and Known Limits

1. **These counts are aggregate, not real-time.** A beat doesn't land at turn 3; it lands when the third ask actually happens (which could be turn 5 or turn 50, depending on the work).

2. **Part orchestration is loose.** The Heartbeat doesn't force parts to sync. If resolve hasn't seen a repeated ask by turn 3, escalation doesn't happen until it does.

3. **Human marks can override.** The operator's "direction" or "failure" mark on a turn overrides the cycle count. A marked turn is a boundary, not part of the normal count.

4. **Prime cycles are not magic.** They avoid *accidental* sync, but a system that deliberately tries to hit multiple milestones at once still can. This is a heuristic, not a law.

---

## Why This Matters

From the operator (2026-10-02):

> "When a system can ask 13 honest questions of itself, then the system is at a stable point."
> "When it can ask 23, unprompted, then it has completed a loop, and is ready for the next bite."
> "Usually, right after, the system and the models fall into a disruptive period. Things start breaking that I thought were fixed…"
> "I feel the end of the next loop coming up very soon."

The heartbeat is how the system recognizes its own readiness. Not "we've been working for 2 hours" but "we've asked ourselves 13 distinct questions and gotten the same answers." That's evidence of convergence.

---

## Open Decisions (Operator's Call)

1. **Are 3/7/13/23 the right numbers?** Or are they artifacts of this particular work?

2. **What about 17?** Is it part of the beat, or incidental?

3. **How do you measure "question" (for the 23 count)?** Is it unique by content hash? By intent? By who asks?

4. **Should the heartbeat be exposed to the operator?** (E.g., "you're at ask 2/3 on this pattern" on the morning screen?) Or is it internal, driving behavior that the operator observes indirectly?

5. **Enforcement:** If the system hits "loop complete" (23), should reverse automatically trigger, or does the operator decide?

---

## References

- workflow.md §4 (Loops, stability, and the heartbeat; all quotes from the operator are there)
- workflow.md §7 (Open predictions)
- next-pile.md (references to the full loop in the reverse pass description)
- CONST-IV (Knowledge; predictions are candidates until witnessed)

