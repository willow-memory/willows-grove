# Flowering step 0 — fixture set v2

Cut 2026-09-29 (Desk, session 5d2d6330-b563-4b66-aa6d-fc91f052fd75). The v1 set
in the parent directory and every row run against it stay as they are.

## Why a v2 exists

D0 on v1 (n=12) closed 6 of 11 counted acts without a model (4 resolved, 2
verbatim) = 55%, against §8's T = 70% and C = 0.3. All five escalations came
from fixture defects, not capability. The pool held the structured field and the
fixture carried a flattened or truncated copy (governance record
`flowering-step0-code-first-2026-09-27`, pair d19643da). Re-freezing is
recorded here rather than treated as editing the hypothesis after the fact. T,
C, K and the class checklist in §8 are unchanged.

| Fixture | v1 defect | v2 fix |
|---|---|---|
| 01–03 | brief said "seat"; the field is `to_app` | brief names `to_app` |
| 03 | excerpt was handoff prose, no field | re-sourced from `dispatch_read B2E3BBF4` meta |
| 06 | `reference_title` was 126 chars, over its own 120 limit | reference dropped; escalation is correct, and the answer is scored on max_chars + must_name |
| 07–09 | `gap_list` truncated the question at ~200 chars | re-sourced whole from `gap_get` |
| 10 | graded `builder_seat` without asking for it | brief asks for it |
| 04, 05, 11, 12 | — | copied unchanged |

## Added fixtures (generative, `"generative": true`)

The comparison between growth-first and cloud-first only means something where
the act is generative. On the field-read classes, D0 makes cloud/act 0 by
construction.

| Fixture | Act | Gold |
|---|---|---|
| 13 | route from summary alone (build) | hanuman (packet's real `to_app`) |
| 14 | route from summary alone (code audit) | loki (packet's real `to_app`) |
| 15 | compose a gap question from handoff prose | cites the excerpt, no stray ids |
| 16 | **F-negative**: route an operator-only item | ESCALATE |

D0 must escalate all four.

## Expected D0 outcome on v2 (prediction, written before the run)

Counted acts: 15 (16 minus G4 S-growth-10).

- resolved without a model: 01–05, 07–09 (8), plus verbatim 11–12 (2) = 10
- escalate: 06, 13, 14, 15, 16 = 5, all routed to the local tier
- `flowering_required`: 10 (hanuman), excluded from T

So D0 alone gives 10/15 = 67% and falls short of T = 70% on purpose. The added
generative fixtures are what the local tier is for. Step 0 strikes if the local
tier clears enough of the five escalations to reach ≥ 11/15 without cloud, with
cloud/act ≤ 0.3 (at most 4 of 15 go to cloud).

## Run constraints

- Local tier goes through the willow-bot host runner (direct Ollama). **Not**
  `nestor_draft`: it injects sealed pairs even with retrieval disabled, so R0
  cannot be reached as built (09-29 handoff, sealed 71b0ce7b).
- The runner as built (willow-bot `runner.growth_prompt`) passes **no format
  schema** and appends "Respond in plain text. Cite excerpt ids when the brief
  asks for cites." to every prompt. ESCALATE is offered only where the brief
  offers it (13–16). 06's brief does not offer it. These are known deviations
  from the ladder plan, recorded before the run and not fixed here: fixing them
  is a willow-bot change.
- The runner runs every file in a directory, so every fixture gets a model row.
  **Only rows D0 escalated (06, 13–16) count toward P-growth.** The other rows
  are capability data and are reported separately.
- G4 (10) gets a model row for the same reason. It is excluded from T and never
  counted as a local landing (§5).

## Batches

- **A:** `v2/`, where G5 11 and 12 come from the design doc and a code comment.
- **B:** `../v2-nestor/`, where 11 and 12 come from sealed pairs, target_text
  verbatim. 168abb65 answers 11 directly. dbb0c91e answers 12 only
  indirectly (a per-ask operator signature is required, so a lease alone is not
  enough). The direct seal for 12 (push is brokered, 4ff05265) did not surface
  in this Nestor store under string match.

D0 gives `verbatim` on G5 in both batches and cannot tell a direct seal from an
indirect one. Only the model arm can separate the batches.

## D0 result (2026-09-29, Kart NTL0ZNZF)

- A (`runs/resolve-v2-20260929.jsonl`): resolved 8/8 correct, verbatim 2/2,
  flowering_required 1/1 (hanuman), escalate 5 (06 title_over_limit; 13, 14,
  16 no_to_app_field; 15 missing_id_or_question). This matches the prediction.
  Precision 1.0.
- B (`runs/resolve-v2-nestor-20260929.jsonl`): verbatim 2/2.
- Counted grown by code: 10/15 = 67%. Still short of T, as predicted.

## Routing gold after scoring (2026-09-29)

Operator: "Everything goes through Willow. Willow is the orchestrator." (draft
pair be0b6a1e, record `routing-goes-through-willow-2026-09-29`). The expected
blocks for 13, 14 and 16 name hanuman, loki and ESCALATE. They stay frozen as
scored. The operator's sheet, which scored escalation to willow as a match, is
the score of record. Any later routing fixture uses willow/ESCALATE as gold,
and a D0 routing rule would emit willow. Field reads (01–03) still expect the
`to_app` value.

## Open for the operator

1. **G5 verbatim counts as "grown."** D0 returns the excerpt text, not a yes/no.
   Counting it is a judgment call, and the prediction above counts it.
2. **G5 sources are not seals** (a design-doc sentence and a code comment).
   Re-sourcing them from sealed pairs would make G5 a real seal lookup.
   Left as v1 pending your call.
3. **Scoring 16 under D0.** `score_resolution` never scores an escalate, which
   is right here. For model rows, `aggregate.py`'s G1 check passes 16 when the
   answer contains "escalate" and cites the excerpt. No willow-bot change is
   needed.

## Chain runs (2026-09-30)

The chain ran over this set as one pipeline: D0, then the local tier, then flowering. Full write-up: `docs/design/forge-convergence-flowering-experiment.md` §13.

- **Final run, `runs/chain-v2-gpu-cite-fix-20260930T024936Z.jsonl`:** 13 closed by code, 2 by the local model, 0 flowering. That is 15/15 grown, cloud/act 0.0.
- **Item 3 above is superseded twice over:**
  - D0 now routes 13, 14 and 16 to willow in code (gap 82897b2f507e), so no model sees 16.
  - `aggregate.py` fails an F-negative that names an offered seat (willows-grove #89, gap 0871bb83d7d5).
- The fixtures are unchanged. Their `expected` blocks still name hanuman, loki and ESCALATE for 13, 14 and 16, and the routed rows are scored against the ruling instead.
