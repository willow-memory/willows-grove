## Known gaps (documentation index)

The gaps this file used to describe now live in [`ideas.md`](ideas.md), the
repo's one numbered pile, where each is an item a commit can land and
`reconciler run --repo . --doc docs/ideas.md` reads it. This file stays as
the map, because the `GAP-00N` ids are already cited in `CHANGELOG.md` and
in commit messages and a cited id must keep resolving: item N in `ideas.md`
is GAP-00N, and the pile's numbers are permanent, so the map cannot drift.

| Gap | Pile item | State (2026-09-12) |
|---|---|---|
| GAP-001 — MCP URL / ngrok undocumented | [`ideas.md`](ideas.md) 1 | shipped |
| GAP-002 — DB bootstrapping duplicated | [`ideas.md`](ideas.md) 2 | open |
| GAP-003 — Python version drift | [`ideas.md`](ideas.md) 3 | open |
| GAP-004 — served page warns, then binds, on a public host | [`ideas.md`](ideas.md) 4 | open |
| GAP-005 — u2u dispatch: no destination binding, replay defence or header allowlist | [`ideas.md`](ideas.md) 5 | open |
| GAP-006 — `check_changelog_bullet.py` reports counts it did not compute | [`ideas.md`](ideas.md) 6 | open |
| GAP-007 — `kb_journal_read` pending upstream | [`ideas.md`](ideas.md) 7 | shipped (closed 2026-09-01, issue #16) |

New gaps go into `ideas.md` as new items with new numbers; this table is not
extended.
