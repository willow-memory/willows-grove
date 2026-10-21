@markdownai v1.0
<!-- b17: WGRV1  ΔΣ=42 -->

# The deterministic loop — forward and reverse, permeable, never falsely closed

**Status:** agent-drafted, **operator-ratified** at PR willows-grove#163
(session `session_01HcW1c3UnM36KckW1hpsy1r`, 2026-10-20). This is a second pass: the
first draft was built from the operator's spoken framing and missed the written
closed-loop canon. It is now grounded in that canon — G76/G77 (Gerald atoms),
`one-box/three-answers-2026-10-06.md` §HM, `one-script/workflow.md`
(forward/reverse), and the seed canon — cited inline. The *framework* (§1–§3) is
the operator's own; the *groundings* (§4–§8) were **reverse-checked against
source this session** — 10 bites, every checkable assertion traced-true (the
descriptive spine, and all four §8 egress gaps). They were then **ratified by
the operator** at PR #163 — the human seal the reverse-check itself could not
supply (ratification is a human act, not a code-check). One meta-finding from the
reverse pass: the box consistently **under-claims** — every correction below
made the written claim *stronger*, never weaker, which is the safe direction
(canon: don't overclaim) but means the note had been underselling the system.

---

## 1. All of it is a closed loop — but closure is permeable, not absolute

The operator: **"All are closed loop system"** (three-answers §HM). The one
script is *"a unified runtime for closed-loop systems with
infinitesimal-perturbation boundaries"* (G76).

Closure here is a precise, *limited* idea, not "sealed off" (G77, Sean's
closed-loop framework):

- A closed system is closed **under some operations and not others** — like the
  multiplicative identity `1`, closed under **multiplication and
  exponentiation** but **not under addition and subtraction**.
- **Closed systems have permeable boundaries, not absolute closure**, and
  **boundary conditions can be reached through infinitesimal perturbations.**
- **Closed loops can be constrained, but not locked.** Real ones are *closed
  enough*, not perfectly (ergodicity is assumed, not proven).

So when a piece "closes into one self-contained loop," read it through G77: it
closes *enough* — constrained, permeable, reachable by a small perturbation —
not hermetically. *(Agent's reconciliation of the operator's spoken "a class
that can't do one self-contained loop is a problem" with G77; correct if the
intent is stricter for a single class than for the system.)*

## 2. Multiplication stays, addition leaves

This is the mechanism for what grows and what *escapes* (three-answers §HM,
G77):

- **Multiplication stays.** Scaling a grid finer — doing more of the same kind —
  stays inside the loop. Reuse stays. Dedup stays. A finer partition of what is
  already there is multiplication.
- **Addition leaves.** **N+1 — adding a new *kind* of thing — is the step that
  leaves.** It crosses the permeable boundary.

That is the real axis under "residue." When a shed piece lands in a pool, a
connection, a section, or something already in the system, that is
**multiplication — it stayed, it was absorbed, nothing new is owed.** When a
shed piece lands nowhere existing, that is **addition — an N+1, a new kind, the
step that left the loop.** The pieces that *leave* are the interesting ones,
because a leaving piece is where a **different idea** was thought. Determinist-
ally, a piece that leaves the loop **escalates**.

## 3. The loop runs both ways: forward asserts, reverse checks

The forward pass is only half. The operator: **"the reverse loop. The check on
the assertion"** (workflow.md).

```
bites -> 13 stable -> 23 loop complete -> PEAK: plan from the highest point
                                            |
                        REVERSE: the completed system re-checks the old work
                                            |
                        "crash": old assertions that never held surface
                                            |
                        fix them -> next bite -> back to 1
```

- **The forward loop asserts** — predictions, declarations, claims, stories.
- **The reverse loop checks each assertion against what happened** — grading,
  reconciliation, adversarial tests, the backward map, the human's marks.
- **Plan at the peak**, before the reverse pass — that is when the system sees
  furthest; once old breaks surface the view fills with repairs.
- **The disruption is the reverse pass working, not bad luck** — a better system
  finding what older work got wrong. It can be expected, scheduled, recorded.

## 4. The cardinal sin is a *false* closed loop

A closed loop is not a thing to be proud of reaching. The seed canon:

- **"An open loop, honestly labeled, beats a closed loop falsely."**
  (`seed/canon/02-the-discipline.md`)
- The failure mode is **"reaching for the mapping that pleased it and presenting
  the closed loop"** (`seed/canon/04-the-language.md`) — a model fabricating
  tidy closure to please.
- **"Collapse (training on model output) is the closed loop with no origin."**
  (next-pile) — a loop fed only by itself degenerates.
- **"A closed loop can't find new basins"** (basins-not-walls §4.4) — compared
  against the record, never against the biggest model.

So the whole machine's honesty apparatus exists to stop a loop from **lying
about being closed**: the reverse pass (§3), the out-of-band anchor no writer
can reach, the human's seal, the three-state that refuses to call *unreachable*
*empty*. Those are not bureaucracy on top of the loop — they **are** the loop's
guard against false closure, and its origin from outside itself.

## 5. It is fractal

The same forward-assert / reverse-check loop, with permeable closure and the
multiplication-stays/addition-leaves boundary, governs a class, a served pile,
an idea, and the growth of the whole system. You cannot tell the scale from the
shape of the loop. This is why "the deterministic system itself" answers almost
every "how does X work" — X is one more turn of it.

## 6. The box already runs it (reverse-checked this session)

- **Pools** are **piles** — who/what/when/where collapsed into one coherent group
  (`serve.py`, `pile.py`). **Connections** are **lineage edges** (direction
  queried, stored once). **Sections** are **domains/collections**.
- **Multiplication that stays** is **dedup/reuse**: gaps bump `asked_count`
  instead of duplicating; lineage stores direction once; a finer grid.
- **Addition that leaves** is a **gap** and, when it will not collapse
  deterministically, an **ESCALATE** — the different idea routed to where a new
  thought can be had.
- **The reverse loop** is not merely named in code — it is **part 7 of the one
  script**: `reverse.py`, whose one line is *"re-check old assertions against what
  is true now,"* and `reconcile` (`api.py:2636`) **defines check-out itself**
  (`api.py:256`: a run is `checked_out` only once a `reconcile` row exists after
  its check-in). You cannot check out until the reverse pass has run. It scores
  the forward loop's assertions (wagers/forecasts) by chain-order under the
  sealed tip, never by clock.
- **The loop eats its own residue.** An escalation — the N+1 that *left* — is
  recorded by hash (`escalate.py`), so the same piece next time hits the `hash`
  rung and is reused (`_find_prior`): today's addition becomes tomorrow's
  multiplication. The residue is absorbed over time, by design.

## 7. picture / cite / seal, and the invariant backbone, fall out of the loop

- **picture** — serve the pools (mature on the box). **cite** — the connections /
  provenance that say where a piece came from; Lineage's `record()` fails closed
  on three gates in order — `id`, a non-empty `rationale` ("a question an agent
  will actually ask"), and at least one `evidence` item — so "an atom that can't
  cite is a story, not memory" (`willow-mcp` `lineage.py:88-100`; reverse-checked
  2026-10-20). (mature) **seal** — the human closing the loop with one yes over an
  exact set of hashes. Seal is the one script's distinctive contribution (CORE:
  `scope_seal` + `nestor_seal`; `onescript_deposit` already bridges).
- **Machine proposes, human seals, and the two never cross.** The seal is the
  origin from outside the loop (§4) — the thing that keeps closure honest.
- **Invariant backbone** (willow-bot / willow-mcp / nestor): append-only
  tamper-evident chains, each closed by an **out-of-band anchor the writer can't
  reach** — and that out-of-band-ness is **code-enforced**, not convention:
  `record.py:82-83` *raises* `PermissionError("the anchor can't live inside the
  box")`. Plus propose/seal and **three-state** everywhere (`serve.py` refuses to
  call a `unreachable` scope `empty`). The one script is a faithful local
  instance.

## 8. The gates are instances; egress is the capstone

"Served-or-not by what the user allowed" is one **discipline** at every surface —
`store_scope` confinement, operator-hold, `deny_tools`, three-state honesty —
all fail-closed to the human. **Homestead** is the worked example: the Binder,
confined to `projects_homestead_*`, denied the KB-mutating tools, holding its
records to `filed | not-filed | unreachable`, with `homestead-law`/`health`
**held** (2026-09-09) until the per-subject disclosure gate is wired.

**Egress is the capstone, built last — structurally.** In the §2 terms, egress is
the piece that keeps **adding new kinds** (cloud, Grove, dispatch) — it is the
least multiplicatively-closed piece, the one whose N+1s keep leaving, so it
cannot settle into a closed-enough loop until the rest exists for its bits to
land in. Today **the human seals *scope* and *proposals* through the one script —
not *egress*.** The unfinished work is the disclosure-shaping join; the
operator's vision for it is large and deliberately deferred. The residue still
leaving — **all four traced to source this session, not just asserted**:

1. **`escalate.py`** stops escalation at a **human-routed review card** (`route:
   willow`); it never calls cloud, mints a lease, or applies an exposure slice.
   The gap is a deliberate fail-closed terminus, not a broken wire.
2. **`exposure.json` and the one script's `view`** are not reconciled — `serve.py`
   imports nothing from willow-mcp's exposure; two parallel disclosure-minimizers.
3. **Grove send** (`grove_tools.py`) imports no exposure module and sends straight
   through — *"slice 1 (surface-only)"*; the `grove → voice_only` default is not
   enforced at send.
4. **`subject_consent`** is built and AND-composed into `gate.permitted` as a
   per-call `subject_id` allow/deny check — but it is **not a field-slicer** and
   is **not bound to any collection**, so the held `homestead-law`/`health`
   domains reach it through nothing; their hold is still a blunt `store_scope`
   omission.

## 9. How to work it

Not "build layer A first." Pick **one little piece**, run its loop **forward**
(assert), **plan at the peak**, run it **reverse** (check the assertions against
what happened), and **follow the residue**: what stayed (multiplication) is done;
what left (N+1, a new kind) is the next real thought. Keep closure honest — an
open loop labeled beats a closed one faked — and let egress close last, on its
own, when nothing of it is still leaving.

---

## What this doc does not do

- It does not ratify anything, and its author cannot (§0.2).
- It does not change `governance/CONSTITUTION.md`, any `AGENTS.md`/`CLAUDE.md`,
  or settings.
- It does not touch the vault. The vault is Sean's key.
- §4–§8 were reverse-checked against source this session (10 bites, all
  traced-true) and then **operator-ratified** at PR #163 — the code-check located
  the claims, the human seal made them hold. §1 is reconciled from the operator's
  spoken and written words — see the note in §1.
