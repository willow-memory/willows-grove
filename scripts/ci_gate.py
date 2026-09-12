#!/usr/bin/env python3
# b17: WGRV1 ΔΣ=42
"""scripts/ci_gate.py — the aggregate `test` job's verdict (fleet plan decision 5).

Branch protection requires one check named `test`. That job `needs:` every
other job in `.github/workflows/tests.yml` and runs `if: always()`, so it is
reached whatever the legs did — and that is the trap: `needs` means a failed
dependency *skips* the dependent by default, and GitHub does not treat a
skipped required check as a blocker. The first revision of the aggregate
proved it — persona-provenance failed the suite, `test` reported
`skipping`, and the PR read MERGEABLE with a red suite underneath.

So the verdict is explicit. This script is handed `toJSON(needs)` and exits
non-zero unless EVERY needed result is exactly `success`: `failure` is a
failure, `cancelled` is a failure, and `skipped` is a failure — a leg that
did not run has told us nothing, and this gate speaks for it. It is a
script rather than an `if:` expression so the same verdict can be planted
(`tests/test_ci_floor.py` feeds it a `needs` with one leg skipped and
asserts red) instead of trusted.

Usage: `python3 scripts/ci_gate.py '<json>'`, or the JSON on stdin.
"""

from __future__ import annotations

import json
import sys


def verdict(needs: dict) -> tuple[bool, list[str]]:
    """(all green, per-leg lines). A leg is green only when its `result` is
    exactly `success`; every other value, and a missing one, is red."""
    lines: list[str] = []
    ok = True
    for job in sorted(needs):
        result = (needs[job] or {}).get("result", "<missing>")
        green = result == "success"
        ok = ok and green
        lines.append(f"{'ok ' if green else 'RED'} {job}: {result}")
    if not needs:
        ok = False
        lines.append("RED <no needs>: the gate needs nothing, so it gates nothing")
    return ok, lines


def main(argv: list[str]) -> int:
    raw = argv[1] if len(argv) > 1 else sys.stdin.read()
    try:
        needs = json.loads(raw)
    except ValueError as err:
        print(f"::error::ci_gate: needs is not JSON ({err})", file=sys.stderr)
        return 2
    ok, lines = verdict(needs)
    for line in lines:
        print(line)
    if not ok:
        print(
            "::error::a needed job did not succeed — skipped and cancelled count "
            "as failures, a leg that did not run has told us nothing",
            file=sys.stderr,
        )
        return 1
    print("every leg green")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
