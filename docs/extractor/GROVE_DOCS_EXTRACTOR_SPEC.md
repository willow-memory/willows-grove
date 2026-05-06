# Grove → enterprise docs — extraction specification

**b17:** GDESP · ΔΣ=42  

## Purpose

Define a **deterministic**, **repeatable** pipeline from Postgres `grove.messages` (plus `grove.channels`) to markdown artifacts: digests, ADR **candidates**, and incident/runbook **candidates**. Enterprise rule: **refs-not-blobs** — output cites message **ids** and optional **git** SHAs; it does not paste full conversations.

## Inputs

| Input | Filter |
|-------|--------|
| `grove.messages` | `is_deleted = 0` unless `--include-deleted` |
| `grove.channels` | Join for human-readable `channel name` |
| Time window | `--since`, `--until` (ISO dates) optional |
| Channel filter | `--channels name1,name2` or `--channel-glob '*arch*'` |

**DSN:** Same as runtime: `WILLOW_DB_URL` or `WILLOW_PG_DB` + `WILLOW_PG_USER` (see `.env.example`).

## Tag vocabulary (lightweight)

Authors MAY prefix lines with:

| Tag | Meaning |
|-----|---------|
| `[DECISION]` | Decision recorded; promote to ADR |
| `[ADR]` | Explicit ADR seed |
| `[INCIDENT]` | Operational incident worth a runbook entry |
| `[RUNBOOK]` | Runbook addition/change |
| `[SCHEMA]` | Schema-related note (link to `docs/db/*`) |
| `[GAP]` | Documented gap — cross-link `KNOWN_GAPS` where applicable |

Tags are **convention** in `content` text; no DB migration required for v1.

## Heuristic triggers (when tags absent)

**ADR / decision candidates** — message matches **any** of:

- case-insensitive regex: `ratified`, `needs decision`, `alternatives considered`, `decision:`, `ADR`
- tag `[DECISION]` or `[ADR]`

**Incident / runbook candidates** — match **any** of:

- `[INCIDENT]` or `[RUNBOOK]`
- keywords: `pool exhaustion`, `deadlock`, `postgres`, `locks`, `down`, `auth failure`, `oauth`

Tune keywords in `scripts/grove_docs_extract.py` as the fleet learns false positives.

## Outputs

| Artifact | Description |
|----------|-------------|
| `digest-{YYYYMMDD}.md` | Tabular digest: `id`, `created_at`, `channel`, `sender`, excerpt |
| `adr-candidates.md` | Ranked list with **message id** + **one-line excerpt** + link hint |
| `incident-candidates.md` | Same for incidents |

Optional: `adr-stubs/` directory with `ADR-YYYYMMDD-msg{id}.md` **templates** (placeholders for human completion).

## Required fields in promoted docs (quality gate)

When a candidate becomes a real ADR or runbook section:

1. **Decision** (one sentence) or **Symptom → cause → fix** for incidents.
2. **Context**
3. **Alternatives** (ADRs) or **verification commands** (runbooks).
4. **Consequences**
5. **Receipts** — at least one of:
   - `grove.messages.id = <bigint>`
   - `git: <40-char sha>` or short `git: <7-char>` with full SHA in footnote

## Refs-not-blobs rule

- **Do:** `Receipt: grove.messages.id = 90421`
- **Don’t:** paste 50 lines of thread into `docs/adrs/`.

Digests may include **≤240 chars** excerpt for orientation — that is summary, not archival.

## CLI surface

Implemented by `scripts/grove_docs_extract.py`:

- `digest` — write digest markdown
- `candidates` — write adr + incident candidate files
- `all` — both
- Flags: `--limit` (default 10000), `--out DIR`, `--channels`, `--since`, `--until`

## Continuous refresh

See [`CONTINUOUS.md`](CONTINUOUS.md) for shell wrapper, cron, and optional CI.

## Verification queries

```sql
SET search_path = grove, public;
SELECT COUNT(*) FROM messages;
SELECT m.id, c.name, left(m.content, 80)
FROM messages m
JOIN channels c ON c.id = m.channel_id
ORDER BY m.id DESC LIMIT 5;
```
