# Continuous refresh — Grove docs extractor

**b17:** GDCNT · ΔΣ=42  

## Local / cron

Use `scripts/grove_docs_refresh.sh` from repo root. It runs `python3 scripts/grove_docs_extract.py all` with defaults and writes under `docs/generated/`.

Example **weekly** cron (adjust paths):

```cron
0 6 * * 1 cd /home/you/github/safe-app-willow-grove && WILLOW_DB_URL=postgresql:///willow_19 ./scripts/grove_docs_refresh.sh >> /tmp/grove-docs.log 2>&1
```

## Makefile

`make grove-docs` — thin wrapper; safe to no-op with message if `python3` or DB unavailable in CI.

## CI / PR automation

`.github/workflows/grove-docs-refresh.yml` provides **`workflow_dispatch`** and optional **`schedule`**. Set repository secret **`WILLOW_DB_URL`** if a runner can reach Postgres; otherwise skip regeneration in CI and run locally.

## Review practice

1. Regenerate artifacts on a protected branch.
2. Diff `docs/generated/*.md` — should be small if message volume is stable.
3. Promote **candidates** to `docs/adrs/` or runbooks manually until ratification workflow exists.
