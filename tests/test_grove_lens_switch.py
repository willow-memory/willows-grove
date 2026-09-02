"""tests/test_grove_lens_switch.py — lens switch demoted from hero (Jarvis).
b17: WGRV1  ΔΣ=42

C12 misfit / Jarvis addendum 2026-09-02: Governance / PM / PA must not be an
operator gearshift in the first viewport. The Web Component file may remain
on disk for harness or quiet tooling; the served page must not mount it.

Stdlib-only, per the pattern set by `tests/test_grove_serve.py`.
"""
from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class GroveLensSwitchDemotionTests(unittest.TestCase):
    def test_page_html_does_not_mount_lens_switch(self) -> None:
        from grove_html import render_page

        html = render_page()
        self.assertNotIn("<grove-lens-switch", html)
        self.assertNotIn("/web/components/grove-lens-switch.js", html)

    def test_page_is_one_jarvis_composition(self) -> None:
        """Brand strip + chat + dispatch without a mode switch row."""
        from grove_html import render_page

        html = render_page()
        self.assertIn('class="strip"', html)
        self.assertIn("<grove-chat", html)
        self.assertIn("<grove-dispatch-rail", html)
        self.assertNotIn('class="lens-row"', html)
        self.assertNotIn('data-lens="governance"', html)

    def test_component_file_retained_on_disk(self) -> None:
        component = os.path.join(ROOT, "web", "components", "grove-lens-switch.js")
        self.assertTrue(
            os.path.isfile(component),
            f"grove-lens-switch.js should remain for harness/quiet use at {component!r}",
        )


if __name__ == "__main__":
    unittest.main()
