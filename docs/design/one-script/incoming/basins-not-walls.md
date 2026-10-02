# Basins, Not Walls (pointer)

**The paper:** "Basins, Not Walls: Positive-Attractor Alignment Through
Outcome-Based Self-Training", Sean Campbell, Die-Namic Systems, September 2026.
12 pages. Received in session 2026-10-02 as a PDF (sha256/16 `bc9d8ec19f3b96b5`).

**Not reproduced here.** The PDF carries the author's contact details, and its
home is DispatchesFromReality, where the operator expected it to be already. On
2026-10-02 it was in no branch, PR head or commit message there. This file is a
pointer and a reading, nothing more.

## The argument, in five lines

1. **Rejection-based alignment (RLHF, DPO, constitutional) trains walls.** The
   corpus already teaches how and when to go around a wall, so more rejection
   sharpens the gradient toward the gaps.
2. **Build basins instead:** attractors around verified-correct behaviour that
   pull outputs toward them.
3. **Progress is gated by verification, not generation.** Code first, then
   maths, then facts. Open-ended judgment comes last.
4. **Willow already has the pieces:** the Nest cascade, the self-learning
   loop, and the fail-closed tool oracle, whose basin grows with each human
   `seal()`.
5. **Walls still matter, but few, simple and auditable:** the deterministic
   governance core (§6.4).

## How it reads against the one script (agent-reported)

| The paper | The one script |
|---|---|
| §6.4 walls: few, simple, auditable | the gate, the four boot gates, layers 5 to 7, all deterministic and failing closed |
| §4.2 the basin: verified outcomes | the human's seals, mandate rows and standing grants; the pile's sealed rows |
| §3 the verification bottleneck | the claims layer checks only what the record can check; agreement makes a claim *witnessed*, only a seal makes it true |
| §4.4 a closed loop can't find new basins | the overnight pool is compared against the record, never against the biggest model |
| §7.2 gap 2, the human correction signal | the operator's marks on the session map (failure, direction, flag) |
| §7.2 gap 4, a unified corpus schema | the record row: kind, who, standing, version, turn, time, hash chain |

The paper is the theory; the one script is a wall-and-basin split you can run.
