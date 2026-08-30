# nestor/ — this session's findings, as a Nestor store

`session-decisions.json` is a Nestor **bundle** (`nestor_bundle` v4): 15 draft
decisions in the `grove→grove` domain, recorded 2026-08-30. Each carries an
`origin` naming how it was established — `verified:<path>` where the tree was
read, `peer-reported:` where another session is being relayed, and
`operator-statement:` for the human's own words. Nothing in it is sealed.

The `.mcp.json` entry at the repo root serves this store to an agent over MCP
(stdio, `--read-only`). The `nestor` it names is a console script, not an
import — install it first:

```
pip install 'nestor-meaning>=0.16.2,<0.17'      # or: pip install -e '.[nestor]'
```

Then build the store the entry points at. Pin `NESTOR_DB` to the destination
and the import lands there directly, ledger sidecar and all:

```
NESTOR_DB=nestor/grove-session.db \
  nestor import --apply --verifier <you> nestor/session-decisions.json
```

Verified 2026-08-30: 15 draft pairs in `grove→grove`, ledger intact (1 entry),
`nestor serve` answering `tools/list` under the exact `.mcp.json` argv, and
`NestorClient.available()` returning True against it.

The older two-step (`nestor import --apply` then `nestor db --out
nestor/grove-session.db`) works too, but the unpinned import writes to
Nestor's own default first and leaves a scratch `./data/nestor.db` in the repo
cwd.

The `.db` and its ledger are gitignored — the bundle travels, the live store
does not (`LOCAL-ONLY.md`). A bundle is also reviewable in a diff.

## The domain, and why it is `decision`

A decision's domain rides in **both** language tags identically
(`docs/decision-memory.md` N8). A bundle written as `question→finding` imports
without error and is then invisible to `nestor decision check` and `nestor
triage`.

That rule is necessary and it is not sufficient, which this bundle learned
twice. The `question→finding` shape was caught and replaced with `grove→grove`
— two tags that match each other, satisfying N8, and that no reader queries.
The symptom survived the fix untouched: the bare `nestor decision check` still
answered

```
✓ clear — no decision on record for 'How does the phone reach Grove?'
```

against a store where that exact question sat at 0.984. Not an error, not an
unreachable state Grove could render (`docs/INVARIANTS.md` §1) — a clean,
confident *clear*, with nothing for the caller to notice. Meanwhile `.mcp.json`
passed an explicit `--source-lang grove --target-lang grove`, so the MCP path
answered correctly the whole time: an agent saw the record and the human at the
keyboard was told there was none.

Matching each other was never the test. The tags have to match the domain the
**readers** query, and there are three of them:

| Surface | Where |
|---|---|
| Grove's own reader | `grove.nestor_client.DECISION_DOMAIN` |
| The session's MCP entry | `.mcp.json` → `nestor serve --source-lang/--target-lang` |
| This bundle | `domain`, and every row in `pairs` |

`decision` is the value because it is also the CLI's own default for
`nestor decision check`, so an operator typing the bare command with no flags
lands where Grove already is. `tests/test_nestor_bundle_domain.py` pins all
three against the constant, structurally (no `nestor` binary needed, because a
wrong domain imports cleanly and only shows up at query time) plus one
end-to-end check of the bare invocation when the binary is present.
