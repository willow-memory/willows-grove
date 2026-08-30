# nestor/ — this session's findings, as a Nestor store

`session-decisions.json` is a Nestor **bundle** (`nestor_bundle` v4): 15 draft
decisions in the `grove→grove` domain, recorded 2026-08-30. Each carries an
`origin` naming how it was established — `verified:<path>` where the tree was
read, `peer-reported:` where another session is being relayed, and
`operator-statement:` for the human's own words. Nothing in it is sealed.

The `.mcp.json` entry at the repo root serves this store to an agent over MCP
(stdio, `--read-only`). Build the store the entry points at:

```
nestor import --apply --verifier <you> nestor/session-decisions.json
nestor db --out nestor/grove-session.db
```

The `.db` and its ledger are gitignored — the bundle travels, the live store
does not (`LOCAL-ONLY.md`). A bundle is also reviewable in a diff.

A decision's domain rides in **both** language tags identically
(`docs/decision-memory.md` N8). A bundle written as `question→finding` imports
without error and is then invisible to `nestor decision check` and `nestor
triage`. That cost a round here; the domain in this bundle is correct.
