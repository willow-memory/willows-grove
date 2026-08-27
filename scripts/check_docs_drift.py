#!/usr/bin/env python3
# b17: GRDDR · ΔΣ=42
"""scripts/check_docs_drift.py — stub for the docs-drift CI check.

Filled by Grove v0.9 PR 11. Present in PR 4 so the CI step in
`.github/workflows/tests.yml` can call it today without failing the job.

What PR 11 will make this do
----------------------------

The docs-drift check enforces two properties of the tree, as required by
`docs/INVARIANTS.md` §3 (doc discipline) and §10 (CI proves the invariants):

1. Every ``INVARIANTS.md §N`` reference that appears anywhere in code,
   tests, comments, docstrings, or CHANGELOG bullets resolves to a real
   anchor (``## §N — …``) inside ``docs/INVARIANTS.md``. A citation
   pointing at a non-existent section is a drift failure.

2. Every bullet added under ``CHANGELOG.md``'s ``[Unreleased]`` section
   cites the PR number it landed in (``PR N`` or ``#N``). This closes
   the "which PR added this?" gap that shows up when the changelog is
   read months later.

3. Every ``docs/INVARIANTS.md`` section has at least one CI-executable
   witness — a test file, a workflow step, or a script called from CI —
   named next to the invariant. Anchors that no CI step enforces are
   flagged for owner attention.

Until PR 11 lands this script is a no-op that exits 0 with a note. The
CI step is guarded on the existence of this file so downstream repos
that fork before PR 11 still get a green build.
"""

from __future__ import annotations

import sys


def main() -> int:
    print("docs-drift stub — filled by PR 11 (Grove v0.9). No checks run yet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
