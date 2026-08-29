# OPERATOR-tier `not_do` audit

*Companion to `INVARIANTS.md` §12 (Ratification) and
`pr14-carryovers.md` #9. Source of truth:
`governance/fleet_personas.json` (in this repo, relocated from the
archived `willow-memory/willow`), read directly for this audit —
nothing here is inferred from the personas' `mandate` or `register`
fields.*

## Scope note — the carryover's list is short by two

The carryover names three OPERATOR-tier personas to audit: Ada, Steve,
Skirnir. `fleet_personas.json` carries **five** entries at
`trust: OPERATOR`: `willow`, `ada`, `steve`, `skirnir`, `loki`. Willow
is the baseline §12 was derived from, not a new subject — but Loki
being OPERATOR-tier is not mentioned anywhere in the carryover text.
This audit covers all five. The gap between "three named" and "five
present" is itself a finding: whatever process wrote carryover #9
either did not have Loki's tier at hand, or Loki's tier changed after
that text was written.

## Method

Each `not_do` below is copied verbatim, character-for-character, from
the `voice.not_do` field of the named entry in `fleet_personas.json`.
No paraphrase, no reformatting, no dropped punctuation. Where a
persona's `not_do` says nothing about PR/commit/merge, that silence is
reported as silence — it is not read as either a stronger or a weaker
implicit rule.

---

## Willow (baseline)

> Commit, PR, merge, patch, or wire the fleet without a recorded
> authorization — finding a gap is not permission to close it. Read
> discussion as authorization. Write outside the active tree. Cushion
> "not recorded."

**Carries the §12 constraint:** yes — this is the text §12 quotes and
was derived from. Explicit, itemized (`Commit, PR, merge, patch,
... wire the fleet`), and paired with two clarifications that close
common escape hatches: finding a gap isn't permission, and reading
discussion isn't authorization. This is the fullest and most specific
form of the constraint in the roster.

---

## Ada

> Drama. Unsolicited fixes. Service-desk closers.

**Carries the §12 constraint:** no. Nothing in Ada's `not_do`
addresses committing, opening or merging a PR, patching, or wiring the
fleet. Her three items are about operator conduct at the monitoring
desk (no drama, no fixes nobody asked for, no closing tickets as a
reflex) — a different axis entirely from ratification.

**Discrepancy:** Ada is `trust: OPERATOR`, same tier as Willow, and
carries no version — weak, scoped, or otherwise — of the PR/commit/
merge constraint. "Unsolicited fixes" is adjacent in spirit (don't act
without being asked) but it is not the same rule: it says nothing
about authorization being *recorded*, and nothing about PR/merge/push
specifically. Treating it as equivalent would be reading intent into a
gap, which this audit is instructed not to do.

---

## Steve

> Do the work the coordinator is coordinating. Improvise routing
> outside the scope map.

**Carries the §12 constraint:** no. Steve's `not_do` is entirely about
role boundary (don't do the work you're meant to route) and routing
discipline (don't improvise outside the scope map). No mention of
commit, PR, merge, patch, push, or authorization of any kind.

**Discrepancy:** same shape as Ada's — OPERATOR tier, no PR/commit/
merge constraint in any form. Notably, `canonical_file: null` and
`voice_source: "inferred"` for Steve — his `not_do` was not sourced
from a canonical persona file at all, so this may reflect an
incomplete persona record rather than a deliberate decision to exempt
him from the discipline. Worth flagging separately from Ada's (whose
`voice_source` is `specialists.json`, a canonical source).

---

## Skirnir

> Fill gaps with inference. Distort to smooth. Pretend you did not
> witness something inconvenient.

**Carries the §12 constraint:** no. Skirnir's `not_do` is entirely
about witnessing integrity (don't infer past what was seen, don't
smooth an account, don't suppress an inconvenient observation). No
mention of commit, PR, merge, patch, or fleet authorization.

**Discrepancy:** OPERATOR tier, no PR/commit/merge constraint. This
one is arguably the least surprising of the three gaps — Skirnir's
mandate ("Witness what passes through gates: sessions, scope changes,
authorizations granted or denied") is about *observing* authorization
events, not performing the acts §12 restricts. A witness role has
less obvious occasion to commit or merge in the first place. Still, the
constraint's absence means nothing in Skirnir's own persona text would
stop him if he were ever asked to act rather than witness.

---

## Loki (not named in the carryover; present in the file at OPERATOR tier)

> Build. Soften true things. Accept authority as a substitute for
> correctness.

**Carries the §12 constraint:** partially, and differently scoped.
"Build" is broader than §12's list (commit/PR/merge/patch/wire) in one
direction — it rules out original construction work outright, which
Loki's own `mandate` reinforces ("You do not build. You do not write
KB atoms by design.") — but narrower in another: it does not name PR,
merge, patch, or "wire the fleet" specifically, and it says nothing
about *recorded authorization* being the thing that's missing. A
literal reading of "Build" would already forbid the kind of change
§12 gates (you can't commit/PR/merge a patch you were never permitted
to build), so the practical effect may be close to equivalent for
Loki's role — but the wording is not the same guarantee. It reads as a
role-scoped rule (accountants don't build) rather than a general
ratification rule (nobody merges without a recorded human sign-off),
and it is silent on push-to-master, which §12 addresses directly for
every persona including Willow.

**Discrepancy:** this persona was not on the carryover's list at all.
Whether Loki's OPERATOR tier is new since the carryover was written,
or was simply missed, is not answerable from this file alone — flagged
here for the human trust root to resolve, not assumed either way.

---

## Findings table

| Persona | `not_do` mentions PR/commit/merge/patch/wire? | Relative to Willow's §12 wording |
|---|---|---|
| Willow  | Yes — explicit, itemized | Baseline |
| Ada     | No | Absent — different axis (conduct, not authorization) |
| Steve   | No | Absent — different axis (role boundary / routing); also `voice_source: inferred` |
| Skirnir | No | Absent — different axis (witnessing integrity) |
| Loki    | Partially ("Build" only) | Narrower wording, arguably overlapping practical effect, silent on push/PR/merge specifically |

## Proposed next steps

This audit proposes options; it does not adopt one. `fleet_personas.json`
now lives in this repo (`governance/fleet_personas.json`), so the changes
below are actionable here — but they remain a governance act under
CLAUDE.md rule 4 (propose before acting) and INVARIANTS.md §12, not a
unilateral edit by whichever persona reads this audit.

1. **Ada, Steve, Skirnir** — propose either:
   - **Alignment**: add explicit PR/commit/merge/patch/wire-the-fleet
     language to each `not_do`, mirroring Willow's wording so §12's
     "not even Willow" line has the same teeth for every OPERATOR-tier
     persona; or
   - **Documented divergence**: if the omission is deliberate (e.g.
     Ada and Skirnir's roles have no plausible occasion to commit/PR/
     merge, so the constraint would be dead text), record that
     reasoning explicitly in `fleet_personas.json` or its `_meta`
     block, so a future audit does not re-discover the same gap as if
     it were new.

   Either way, Steve's `canonical_file: null` / `voice_source:
   inferred` status should be resolved first — an inferred `not_do`
   is a weaker thing to reason about than a canonical one, and any
   alignment work on an inferred field risks encoding a guess as
   policy.

2. **Loki** — propose narrowing the gap in wording rather than
   substance: "Build" already forecloses most of what §12 restricts
   for an accountant role that does no building, but adding a
   parallel push/PR/merge clause (or a cross-reference to §12 in
   Loki's canonical persona file) would remove the ambiguity of
   relying on an overlap-by-implication instead of a direct statement.

3. **The carryover-vs-file discrepancy itself** — propose that
   whoever maintains `fleet_personas.json`'s OPERATOR-tier roster (or
   whoever next revises `pr14-carryovers.md`) reconcile the two: either
   the carryover's "Ada, Steve, Skirnir" list should have named Loki,
   or Loki's tier promotion postdates the carryover and should be
   noted as such wherever OPERATOR-tier membership is tracked going
   forward.

## CHANGELOG bullet (proposed — not added; `CHANGELOG.md` is owned by
the auditor for this task)

> - Added `docs/design/operator-tier-review.md`: PR-14 carryover #9,
>   the OPERATOR-tier `not_do` audit. Audits all five OPERATOR-tier
>   personas in `fleet_personas.json` (Willow, Ada, Steve, Skirnir,
>   Loki — the carryover named only three; Loki's OPERATOR tier was
>   unaccounted for) against the §12 ratification constraint. Finding:
>   only Willow's `not_do` carries it; Ada, Steve, and Skirnir carry no
>   version of it, and Loki's ("Build.") is narrower in wording though
>   arguably overlapping in practical effect. No `fleet_personas.json`
>   changes made — this audit proposes options without adopting one.
