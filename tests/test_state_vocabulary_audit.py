# b17: WGRV1 ΔΣ=42
"""tests/test_state_vocabulary_audit.py — one grep for INVARIANTS.md §1.

PR-14 carryover #4 / #11 (docs/design/pr14-carryovers.md). PR 9 caught
`grove-dispatch-rail` on the pre-§1 vocabulary (`loading|ready|error`)
and normalized it. Every panel written in the same batch was a candidate
for the same drift, and nothing on-tree stopped a new one from inventing
its own words.

§1's vocabulary is `loading | populated | empty | unreachable`. Anything
outside it either collapses two states into one word or invents a fourth
the readers never produce — both of which end with the operator unable
to tell "I could not reach the source" from "there is nothing there".

This test greps every state literal out of `web/components/*.js` — both
the `this._state = "…"` assignments and the `data-state="…"` attribute
values the shadow CSS branches on — and asserts each one is either §1
vocabulary or an explicitly-allowlisted in-flight sentinel named below.

Adding a word here is a deliberate act with a reason attached; drifting
into one is not.
"""
from __future__ import annotations

import os
import re
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPONENTS_DIR = os.path.join(ROOT, "web", "components")

# INVARIANTS.md §1 — the three states, plus the pre-fetch sentinel every
# panel starts in before its first answer arrives.
SECTION_1_VOCABULARY = frozenset({"loading", "populated", "empty", "unreachable"})

# Sentinels that are NOT §1 states and are allowed only because they name
# a transient the operator is actively watching, never a settled answer.
# Each entry needs a reason; an unexplained addition is drift.
ALLOWED_SENTINELS = {
    # <grove-chat> LEFT column: the operator's line is in flight to
    # /api/journal. Settles into a rendered atom or the unreachable
    # banner — it is never a resting state.
    "sending",
}

ALLOWED = SECTION_1_VOCABULARY | set(ALLOWED_SENTINELS)

# `this._state = …` / `el._state = …` assignments. The right-hand side is
# captured whole rather than as a single literal, because the settle path
# is written as a ternary
# (`this._state = list.length > 0 ? "populated" : "empty";`) and a pattern
# that only reads the first quoted token would silently miss half the
# vocabulary — which is exactly how this audit would rot into a no-op.
_ASSIGN_RE = re.compile(r"_state\s*=\s*([^;\n]+)")
_LITERAL_RE = re.compile(r"[\"']([a-z-]+)[\"']")
# `data-state="…"` — the attribute the shadow CSS branches on, i.e. what
# actually reaches the operator's eye.
_ATTR_RE = re.compile(r"data-state=[\\\"']+([a-z-]+)")
# `setAttribute("data-state", "…")` with a literal value.
_SETATTR_RE = re.compile(
    r"setAttribute\(\s*[\"']data-state[\"']\s*,\s*[\"']([a-z-]+)[\"']"
)


def _component_files() -> list[str]:
    return sorted(
        os.path.join(COMPONENTS_DIR, name)
        for name in os.listdir(COMPONENTS_DIR)
        if name.endswith(".js")
    )


def _state_literals(source: str) -> set[str]:
    found: set[str] = set()
    for expression in _ASSIGN_RE.findall(source):
        found.update(_LITERAL_RE.findall(expression))
    for pattern in (_ATTR_RE, _SETATTR_RE):
        found.update(pattern.findall(source))
    return found


class StateVocabularyAuditTests(unittest.TestCase):
    def test_components_dir_exists(self) -> None:
        """Sanity: a moved components dir must fail loudly, not vacuously
        pass by finding nothing to audit."""
        self.assertTrue(
            os.path.isdir(COMPONENTS_DIR), f"missing {COMPONENTS_DIR}"
        )
        self.assertTrue(_component_files(), "no components found to audit")

    def test_every_state_literal_is_section_1_vocabulary(self) -> None:
        offenders: dict[str, set[str]] = {}
        for path in _component_files():
            with open(path, encoding="utf-8") as fh:
                literals = _state_literals(fh.read())
            stray = literals - ALLOWED
            if stray:
                offenders[os.path.basename(path)] = stray
        self.assertEqual(
            offenders,
            {},
            "state literals outside INVARIANTS.md §1's vocabulary "
            f"({sorted(SECTION_1_VOCABULARY)}) and the allowlisted "
            f"sentinels ({sorted(ALLOWED_SENTINELS)}): {offenders}. "
            "Either use the §1 word or add the sentinel to "
            "ALLOWED_SENTINELS with the reason it is not a resting state.",
        )

    def test_the_audit_actually_reads_state_literals(self) -> None:
        """Guard against a regex that silently stops matching — the
        failure mode that turns this whole file into a green no-op."""
        seen: set[str] = set()
        for path in _component_files():
            with open(path, encoding="utf-8") as fh:
                seen |= _state_literals(fh.read())
        self.assertIn(
            "unreachable",
            seen,
            "the audit found no 'unreachable' literal anywhere in "
            "web/components/*.js — the patterns have stopped matching",
        )
        self.assertIn("populated", seen)

    def test_pre_section_1_vocabulary_is_gone(self) -> None:
        """The specific words PR 9 found on grove-dispatch-rail. Named
        explicitly so a revert is caught by name, not just by set-diff.
        """
        for path in _component_files():
            with open(path, encoding="utf-8") as fh:
                literals = _state_literals(fh.read())
            for stale in ("ready", "error", "ok", "failed"):
                self.assertNotIn(
                    stale,
                    literals,
                    f"{os.path.basename(path)} uses the pre-§1 state word "
                    f"'{stale}' — PR 9 normalized this vocabulary once "
                    "already",
                )


if __name__ == "__main__":
    unittest.main()
