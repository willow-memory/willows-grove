# b17: WGRV1 ΔΣ=42
"""Regression pin for tests/e2e/three-state-affordances.spec.js (INVARIANTS §1).

The visual-layer spec compares each panel's empty render against its
unreachable render and asserts they differ. The load-bearing property is
that the *rendered pixels the operator sees* differ — not an internal
JavaScript property on the element. If the probe appends `el._state` to
the compared string, a component whose empty and unreachable shadow
renders are byte-identical still passes the pin so long as its internal
`_state` differs. That is exactly the collapse INVARIANTS.md §1
("The empty state and the unreachable state look different to the
operator") forbids.

These two assertions pin the fix on-tree so a future edit cannot silently
re-widen the compared string and re-open the loophole.
"""
from pathlib import Path


SPEC = (
    Path(__file__).resolve().parent / "e2e" / "three-state-affordances.spec.js"
)


def _spec_text() -> str:
    assert SPEC.exists(), f"three-state-affordances.spec.js missing at {SPEC}"
    return SPEC.read_text(encoding="utf-8")


def test_probe_returns_only_rendered_html_not_internal_state_marker():
    """§1 pin: the empty/unreachable probes must return ONLY rendered HTML.

    Appending `'|' + (el._state || '')` to the returned string lets a
    component whose empty and unreachable shadow renders are byte-identical
    still pass the §1 pin as long as `el._state` differs. INVARIANTS.md §1
    (lines 51–52) says the two states "look different to the operator" —
    internal JS properties are not what the operator sees.
    """
    text = _spec_text()
    assert "'|' + (el._state" not in text, (
        "tests/e2e/three-state-affordances.spec.js still appends the internal "
        "`_state` marker to the compared string. A component whose empty and "
        "unreachable shadow renders are byte-identical then passes the §1 pin "
        "purely because `el._state` differs — defeating INVARIANTS.md §1. "
        "The probe must return only `root.innerHTML || ''`."
    )


def test_self_check_subtest_pins_the_revised_assertion():
    """§1 pin: the spec must include a self-check subtest that mounts a stub
    custom element whose empty and unreachable shadow renders are
    byte-identical, and asserts the revised (HTML-only) assertion FAILS
    against it. Without this self-check, a future edit could silently
    re-widen the compared string and no test would notice.
    """
    text = _spec_text()
    assert "self-check: identical HTML must fail the pin" in text, (
        "tests/e2e/three-state-affordances.spec.js must include a self-check "
        "subtest titled 'self-check: identical HTML must fail the pin' that "
        "mounts a byte-identical stub and asserts the revised assertion "
        "THROWS. Without it, a future widening of the compared string could "
        "silently re-open the §1 collapse."
    )
