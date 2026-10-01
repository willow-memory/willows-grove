# Slice B seal lineup (2026-10-01)

Corpus index: 1064 nuggets. Scoring = exact question match to intake `source_text`.

Doctrine: **other/asserted ≠ “no human checked.”** These rows need a seal ceremony (or confirm they were never human-reviewed).

## Already human (done — do not re-seal unless signatures fail)

| Packet | human / pairs |
|--------|---------------|
| grove-persona-partition-seals.json | 3/3 |
| paperclip-genealogy.json | 26/26 |
| sovereign-ai.json | 16/16 |
| sovereign-ai-research.json | 1/1 |
| willow-local.json (partial) | 3/15 |

## Backlog (knock-down order)

| Priority | Packet | human | other | missing | Why next |
|----------|--------|------:|------:|--------:|----------|
| 1 | researched-gaps.json | 0 | 16 | 0 | Ladder/docs Q&A; operator-facing |
| 2 | willow-local.json remainder | 3 | 12 | 0 | Desk routing; 3 already sealed |
| 3 | right-to-fix.json | 0 | 7 | 0 | Novel research track |
| 4 | childrens-software-interruption.json | 0 | 9 | 0 | Novel research track |
| 5 | tabletop-mechanical-engines.json | 0 | 5 | 0 | Novel research track |
| 6 | kids-tabletop-r2r-research.json | 0 | 2 | 0 | Small; after tabletop |

## Ceremony (same as Slice A)

1. Review pair text against sources in the intake JSON.
2. Seal in Nestor (`nestor ui` / `sign_seal`) as `sean campbell`.
3. Bridge to Jeles human rung with `nestor-seal-v1` evidence.
4. Prove: `corpus_ask` → `found:true` / `verification_kind:human`; `nestor ask` → sealed.

Do **not** set `JELES_CORPUS_TRUST_TOOL_WRITES=1` in an agent session.

## Out of scope

- Seed 968 asserted-by-design (machine adversarial rounds).
- Auto-promoting asserted → human.
