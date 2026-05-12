# Gemini CLI — Willow Grove app

b17: GEMWG · ΔΣ=42

## Fylgja powers

Fylgja lives in the **willow-1.9** checkout. Default root: `~/github/willow-1.9/willow/fylgja` (override with `WILLOW_FYLGJA_ROOT`).

1. Read `{ROOT}/powers/registry.json`.
2. Pick one id (or best `description` match).
3. Read exactly one `{ROOT}/powers/<file>`.

`using-fylgja-powers.md` and `powers/SURFACES.md` sit under that `{ROOT}`.

**Worktree seed:** At worktree creation, before the first code edit, ingest one KB seed atom — the non-derivable contract (wire format, interface, or invariant) a cold agent needs that cannot be read from the code. Record the atom ID in the first Grove post for the task. No build starts without it.

User instructions always win.
