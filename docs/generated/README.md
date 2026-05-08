# Generated documentation artifacts

**b17:** GENDC · ΔΣ=42  

This directory holds **machine-regenerated** markdown (digests, ADR/incident **candidates**). It is safe to delete and rebuild from Postgres.

## Regenerate

```bash
cd /path/to/safe-app-willow-grove
./scripts/grove_docs_refresh.sh
# or: python3 scripts/grove_docs_extract.py all --limit 10000
```

Requires `WILLOW_DB_URL` or `WILLOW_PG_*` env (see `.env.example`).

## Files (typical)

| File | Producer |
|------|----------|
| `digest-*.md` | Latest message digest |
| `adr-candidates.md` | Messages matching decision/ratified patterns |
| `incident-candidates.md` | `[INCIDENT]` / keyword matches |

**Rule:** These files store **message ids and pointers**, not full thread dumps (refs-not-blobs).
