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

A decision's domain rides in **both** language tags identically
(`docs/decision-memory.md` N8). A bundle written as `question→finding` imports
without error and is then invisible to `nestor decision check` and `nestor
triage`. That cost a round here; the domain in this bundle is correct.
