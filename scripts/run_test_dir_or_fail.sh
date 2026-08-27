#!/usr/bin/env bash
# b17: GRTDG · ΔΣ=42
#
# scripts/run_test_dir_or_fail.sh — docs/INVARIANTS.md §10 CI witness.
#
# Wraps a pytest run against a test directory that may legitimately
# still be an empty scaffold (nothing but .gitkeep), so the CI step
# that calls this can run unconditionally instead of behind a
# hashFiles(...) guard.
#
# A hashFiles('DIR/test_*.py') guard goes silently false — and the
# step silently no-ops — the moment a future PR either:
#   (a) drains the directory back down to .gitkeep (fine — that's the
#       scaffold case and should stay a clean no-op), or
#   (b) renames its test files off the test_*.py / *_test.py
#       convention while real `def test_` bodies stay inside (not
#       fine — pytest's own default discovery would also miss them,
#       and nothing would ever say so).
#
# hashFiles can't tell those two apart because it only ever looks at
# filenames. This script looks at contents instead:
#   - no .py files at all               -> legitimate scaffold, exit 0
#   - .py files, none define a test     -> loud failure, exit 1
#   - .py files, at least one real test -> hand off to pytest for real
#
# Usage: run_test_dir_or_fail.sh <dir> [pytest-args...]
set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "usage: $0 <test-dir> [pytest-args...]" >&2
    exit 2
fi

DIR="$1"
shift

if [ ! -d "$DIR" ]; then
    echo "check: $DIR does not exist — nothing to run."
    exit 0
fi

PY_FILES=()
while IFS= read -r -d '' f; do
    PY_FILES+=("$f")
done < <(find "$DIR" -type f -name '*.py' -print0)

if [ "${#PY_FILES[@]}" -eq 0 ]; then
    echo "check: $DIR has no .py files (scaffold only) — skipping, no CI witness expected yet (docs/INVARIANTS.md §10)."
    exit 0
fi

if ! grep -lE 'def test_' "${PY_FILES[@]}" > /dev/null 2>&1; then
    echo "FAIL: $DIR contains .py files but none define a test (no 'def test_' found in any of them)." >&2
    echo "This is exactly the silent no-op a hashFiles('$DIR/test_*.py') guard misses when files are" >&2
    echo "renamed off the test_*.py convention. Restore the test_*.py / *_test.py naming pytest" >&2
    echo "expects, or add real tests — an empty CI witness is a docs/INVARIANTS.md §10 violation." >&2
    exit 1
fi

exec python3 -m pytest "$@" "$DIR"
