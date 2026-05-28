## Known gaps (documentation index)

This file is intentionally short. It links to canonical writeups (or notes “missing writeup”) so gaps don’t get rediscovered repeatedly.

- **GAP-001 — MCP URL / ngrok is undocumented**: `GROVE_MCP_URL` shows up in `.mcp.json` and `grove/mcp_local.py` supports a `--serve` mode that requires a public base URL, but tester docs historically didn’t explain when it’s needed vs when it’s not.
  - Canonical doc: `docs/TESTER_ONBOARDING.md` (“Optional: MCP (Claude Code / agents) and GROVE_MCP_URL (ngrok)”)
- **GAP-002 — DB bootstrapping duplicated**: `schema.sql` exists, but there’s no single “one true setup” doc for `willow_20` vs `grove_local` naming and `.env` vs `export` usage.
- **GAP-003 — Python version drift**: `README.md`/`TESTER_ONBOARDING.md` say Python 3.11+, but at least one historical implementation plan cites Python 3.13. Standardize on 3.11+ unless/until the code requires newer.

