# b17: WGRV1 ΔΣ=42
"""tests/test_refusal_summon_shape.py — refusal-summon boot module contract.

Python-side test that ``web/boot/refusal-summon-boot.js`` exports the
shape the served page expects (INVARIANTS.md §1 + §8):

  * exposes ``window.groveNestorAsk`` — a console/operator summon helper.
  * POSTs to ``/api/nestor/decide`` — the D11 decision endpoint.
  * handles ``state === "unreachable"`` distinctly (does not swallow 503).
  * dispatches the ``nestor-refusal`` window CustomEvent on ``refused``.
  * dispatches ``nestor-refusal`` with ``mode: "unreachable"`` on the
    503/unreachable path.

Text-level assertions — the JS is not executed in this test. The
Playwright end-to-end that exercises the wiring is PR 9's job; this
test pins the file's *contract* so a rewrite that drops a required
piece is caught at unit-test time.
"""
from __future__ import annotations

import os
import re
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOT_PATH = os.path.join(ROOT, "web", "boot", "refusal-summon-boot.js")


class RefusalSummonShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(BOOT_PATH, "r", encoding="utf-8") as fh:
            cls.src = fh.read()

    def test_file_exists(self) -> None:
        self.assertTrue(
            os.path.isfile(BOOT_PATH),
            f"expected refusal-summon-boot module at {BOOT_PATH}",
        )

    def test_exposes_groveNestorAsk_on_window(self) -> None:
        # window.groveNestorAsk is the console-summon entry point named
        # in the module's JSDoc contract.
        self.assertRegex(
            self.src,
            r"window\s*\.\s*groveNestorAsk\s*=",
            "boot module must assign window.groveNestorAsk",
        )

    def test_ask_helper_accepts_a_claim(self) -> None:
        # The internal ask function takes a single string argument named
        # `claim` — the caller's proposed act/assertion.
        self.assertRegex(
            self.src,
            r"function\s+_groveNestorAsk\s*\(\s*claim\s*\)",
            "expected async function _groveNestorAsk(claim) signature",
        )

    def test_posts_to_nestor_decide(self) -> None:
        # POST /api/nestor/decide — the D11 endpoint per §4's coverage table.
        self.assertIn(
            '/api/nestor/decide',
            self.src,
            "boot module must reference the /api/nestor/decide endpoint",
        )
        # method: POST — belt-and-braces so nobody switches this to GET.
        self.assertRegex(
            self.src,
            r'method:\s*["\']POST["\']',
            "the /api/nestor/decide call must use method:POST",
        )

    def test_sends_claim_in_json_body(self) -> None:
        # The claim goes into the body as JSON — {"claim": ...}.
        self.assertRegex(
            self.src,
            r'JSON\.stringify\s*\(\s*\{\s*claim',
            "the fetch body must carry the claim under a `claim` key",
        )

    def test_dispatches_nestor_refusal_event(self) -> None:
        # The window CustomEvent name is contractual — the chip listens
        # for exactly this string.
        self.assertIn(
            '"nestor-refusal"',
            self.src,
            "boot module must dispatch a `nestor-refusal` CustomEvent",
        )
        self.assertRegex(
            self.src,
            r'window\s*\.\s*dispatchEvent\s*\(\s*new\s+CustomEvent\s*\(',
            "the event must be dispatched via window.dispatchEvent(new CustomEvent(...))",
        )

    def test_handles_refused_verdict(self) -> None:
        # On verdict==="refused" the boot fires the event with the
        # verbatim refusal payload (V5).
        self.assertRegex(
            self.src,
            r'verdict\s*===\s*["\']refused["\']',
            "boot module must branch on verdict === 'refused'",
        )

    def test_handles_unreachable_state_distinctly(self) -> None:
        # INVARIANTS.md §1: 503 with state="unreachable" is a distinct
        # summon path — the 503 must not be silently swallowed.
        self.assertRegex(
            self.src,
            r'state\s*===\s*["\']unreachable["\']',
            "boot module must branch on state === 'unreachable' (INVARIANTS §1)",
        )
        # And it must tag the event detail with mode: "unreachable" so
        # the chip picks the subdued render path.
        self.assertRegex(
            self.src,
            r'mode:\s*["\']unreachable["\']',
            "the unreachable-branch event detail must carry mode: 'unreachable'",
        )

    def test_unreachable_and_refused_dispatch_the_same_event(self) -> None:
        # Both branches summon via `nestor-refusal` — the chip is the
        # one renderer, differentiated by `mode`.
        dispatches = re.findall(r'new\s+CustomEvent\s*\(\s*EVENT_NAME', self.src)
        self.assertGreaterEqual(
            len(dispatches),
            2,
            "expected at least two EVENT_NAME dispatches (refused + unreachable)",
        )

    def test_declares_decide_url_constant(self) -> None:
        # A named constant, not a stray literal — the URL is the wire
        # contract with grove_serve.py's route table.
        self.assertRegex(
            self.src,
            r'DECIDE_URL\s*=\s*["\']/api/nestor/decide["\']',
            "expected a DECIDE_URL constant pinning /api/nestor/decide",
        )


if __name__ == "__main__":
    unittest.main()
