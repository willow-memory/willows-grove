# b17: WGRV1 ΔΣ=42
"""Regression pin for tests/e2e/seed-canon.spec.js (INVARIANTS §9 + §10).

Loki finding #18 (M15-seed-canon-pixel-baseline): the six per-movement
pixel-baseline subtests in `tests/e2e/seed-canon.spec.js` were shipped as
`test.skip(...)` scaffolds carrying a 'pixel compare — follow-up' comment.
Every visual-regression assertion for `/seed/{1..6}` was permanently
inert — the comparator promised at spec lines 6–11 ("pixel baselines
match within tolerance") did not exist.

The delivered fix wires raw `pixelmatch` (with `pngjs` for PNG decode)
against the PR-3 baselines at `tests/regression/screenshots/seed/{1..6}.png`,
reading the baseline file directly rather than routing through Playwright's
per-spec `toMatchSnapshot` outputPath (which refuses traversal outside the
snapshot subdir). When the baseline file is absent on the build box, the
subtest calls Playwright's runtime `test.skip()` and reports SKIPPED
(never a fake pass).

These two assertions pin the fix on-tree so a future edit cannot silently
re-skip the pixel subtests or drop the `pixelmatch` wiring and re-open the
inert-comparator hole.
"""
from pathlib import Path


SPEC = Path(__file__).resolve().parent / "e2e" / "seed-canon.spec.js"


def _spec_text() -> str:
    assert SPEC.exists(), f"seed-canon.spec.js missing at {SPEC}"
    return SPEC.read_text(encoding="utf-8")


def test_pixel_baseline_subtests_are_not_test_skipped():
    """§9 + §10 pin: the six per-movement pixel-baseline subtests must NOT be
    declared with the 'pixel compare — follow-up' deferral scaffold.

    The Loki finding names the exact marker: `test.skip(...pixel compare
    — follow-up)` at spec:115. If that marker string returns to the file,
    the six visual-regression assertions are inert again — every /seed/{n}
    pixel diff is fake-green regardless of what the renderer emits.
    """
    text = _spec_text()
    assert "pixel compare — follow-up" not in text, (
        "tests/e2e/seed-canon.spec.js still carries the 'pixel compare — "
        "follow-up' deferral marker — the six per-movement pixel-baseline "
        "subtests are `test.skip`ed and every visual-regression assertion "
        "is inert. Loki finding #18 (M15-seed-canon-pixel-baseline): wire "
        "raw pixelmatch against the PR-3 baselines and enable all six "
        "subtests."
    )
    # Belt-and-suspenders: the specific `test.skip(...matches its baseline`
    # scaffold string used at spec:115 must not reappear either. A future
    # edit that renames the follow-up comment but keeps the skip is still
    # a re-opened hole.
    assert "matches its baseline within tolerance (pixel compare" not in text, (
        "tests/e2e/seed-canon.spec.js still declares the pixel-baseline "
        "subtest with the '(pixel compare ...)' skip scaffold. Enable the "
        "six subtests via raw pixelmatch (Loki finding #18)."
    )


def test_pixelmatch_is_imported():
    """§9 + §10 pin: the fix wires `pixelmatch` against the on-disk PR-3
    baselines. Without a pixelmatch import, no byte-buffer compare exists
    and the promise at spec lines 6–11 ("pixel baselines match within
    tolerance") is decorative. Loki finding #18 names pixelmatch as the
    comparator to use.
    """
    text = _spec_text()
    has_single = "require('pixelmatch')" in text
    has_double = 'require("pixelmatch")' in text
    assert has_single or has_double, (
        "tests/e2e/seed-canon.spec.js does not import `pixelmatch`. The "
        "six per-movement pixel-baseline subtests cannot compare rendered "
        "pixels against tests/regression/screenshots/seed/{1..6}.png "
        "without a comparator. Add `const pixelmatch = require('pixelmatch');` "
        "(and `const { PNG } = require('pngjs');` for PNG decode) and wire "
        "the compare against the baseline file read directly from disk. "
        "Loki finding #18 (M15-seed-canon-pixel-baseline)."
    )
