# the desk over the piles

One box over the folder that holds the piles the desk works from (Willow,
the Provider, Die-Namic, this Grove). Every step reads the box, or a pile by
name, and writes nothing into any of them. `@PILES@` is filled by
`box-desk.sh` with the folder that holds them.

## what each pile tells an agent before its first change
- instruction-files -- --from @PILES@/Willow
- instruction-files -- --from @PILES@/Model-Context-Provider
- instruction-files -- --from @PILES@/rudi193-cmd/die-namic-games --at ai-game-master
- instruction-files -- --from @PILES@/willow-memory/willows-grove
- agents-md-check -- --from @PILES@/Model-Context-Provider
- agents-md-check -- --from @PILES@/rudi193-cmd/die-namic-games
- agents-md-check -- --from @PILES@/willow-memory/willows-grove

## what the code still owes
- todo -- --box {box}
- risky-code -- --box {box}
- unpinned -- --box {box}
- install-scripts -- --box {box}
- ref-check -- --box {box}

## what shouldn't be sitting in plain files
- secrets-audit -- --box {box}
- pii-audit -- --box {box}

## one question, each pile answering in turn
- fair-merge -- --box {box} "who may approve"
- fair-merge -- --box {box} "what never leaves the machine"
- fair-merge -- --box {box} "what is the key for"
- fair-merge -- --box {box} "what happens when the key is lost"
- fair-merge -- --box {box} "what does the agent never do"

## what the box needs from the person
- digest -- --box {box}
- box-health -- --box {box}
