# The Table — session record (stays in this scratchpad; never committed)

GM: Jane · machine proposes, the human seals · session 1 (session 0 archived at archive/record-session-0.md)

## Table rules carried from session 0
- Output follows willows-grove's rules (CLAUDE.md 7, 15, 16, 17; the box stream)
- The character exists before any scene
- The human chooses the ruleset; nothing is rolled before it (chosen: session 1, line 3)
- A die is rolled only when something uncertain hangs on it; its prediction is recorded first and graded after
- Proposals and predictions are tracked in ledger.json, not shown in the chat (session 1, line 2)

## Ruleset (the human, line 3: use the box's built rule sets)
- character sheet: SRD 5.1 ability scores; pools derived as nestor_clocks.py does (score -> Nd6, +1 die proficiency, +1 expertise)
- action: Forged-in-the-Dark pool, humans.py roll_pool (Nd6 take highest; 0 dice = 2d6 take lowest; 6 success, 4-5 partial, 1-3 failure, two 6s critical); position/effect -> ticks (TICKS) and burnout (BURNOUT_TABLE)
- hazards and knowing things: SRD 5.1 ability_check with degrees (compound.py: CRITICAL / FULL / PARTIAL / FAIL / BOTCH); saves, HP, death saves, exhaustion (resolution.py)
- life: progress and danger clocks, life events before each push (humans.py Life, LIFE_EVENTS, roll_life_event)
- people: NPCs on SRD 5.1 blocks, resolved before the protagonist leans on them (npcs.py)
- evidence and heat: document ladder, HEAT_ABORT (compound.py)
- the decision: StorySession propose -> seal; only a named human seals (the-table)
- predictions: one-script predict.declare/grade + wagers (willow-bot); scored for calibration (Forge calibration ledger: Brier)
- the record: hash-chained ledger (ai-game-master); the rolls live there when play starts

## Human lines (verbatim)
- 1: "Man, whoooo eee here. The \"friend\" told me this here machine can predict the future. \nI traveled all the way from Buckhorn to see this, and as you know, thats no easy FEET for us."
- 2: "Output change. I would like you to keep a track of the proposals and predictions, and move them out of the context window."
- 3: "We already have some very complicated rule sets in the box. We don't have to start simple with things we know already work."
- 4: "We're in the world of middle earth"

## Rolls

## Sealed
- s1: the visitor traveled from Buckhorn to see the machine — line 1
- s3: the world is Middle-earth — line 4
- s2: a "friend" (the human's quotes) told the visitor the machine can predict the future — line 1

## Proposals and predictions
- kept in ledger.json beside this file, out of the chat (the human, turn 2)
