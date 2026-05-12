# Architecture Decision Records (ADRs) — Grove repo

**b17:** ADRRD · ΔΣ=42  

## Naming

- Pattern: `ADR-YYYYMMDD-<slug>.md` in this directory.
- One decision per ADR; link **receipts** (Grove `grove.messages.id` and git SHAs) — **refs not blobs**.

## Required sections

1. **Decision** — one sentence.
2. **Context** — why this mattered.
3. **Alternatives considered**
4. **Consequences**
5. **Receipts** — Grove message id(s); optional `git:` SHA lines.

## Sources

- Ratified discussion in Grove is harvested by `scripts/grove_docs_extract.py` (candidate list under [`../generated/`](../generated/README.md)).
- Human authors promote candidates to accepted ADRs by editing files here.

## Quality gate

No ADR without **≥1 receipt** (message id or commit hash).
