# Envelopes — live Article III.2 registry

The fleet's standing authority grants live here in the grove charter repo.
`willow-mcp` enforces `pre-approved.json` and `syscall-table.json` from this
directory when `WILLOW_CHARTER_REPO` points at `willows-grove`.

| File | Role |
|------|------|
| `pre-approved.json` | Active and proposed envelope grants |
| `syscall-table.json` | Verb definitions the checker matches against |
| `frank_head_anchor.json` | FRANK governance chain head (outside Postgres) |
| `review_queue.json` | Article XI proposal queue |

Per-node overrides may still exist at `$WILLOW_HOME/constitutional/`; Grove's
`envelope_reader` treats those as higher priority on `id` collision.

Relocated from `$WILLOW_HOME/constitutional/` on 2026-09-07.
