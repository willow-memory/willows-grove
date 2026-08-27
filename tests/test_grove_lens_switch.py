"""tests/test_grove_lens_switch.py — mount verification for <grove-lens-switch>.
b17: WGRV1  ΔΣ=42

The Web Component itself is a vanilla-JS file with no build step (D9); its
syntax is validated separately by `node --check`. This suite is the Python-
side contract: the rendered Grove page must actually reference the component
and its script, and the script tag must point at a real file on disk so the
StaticFiles mount in `grove_serve.py` can serve it.

Stdlib-only, per the pattern set by `tests/test_grove_serve.py`.
"""
from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class GroveLensSwitchMountTests(unittest.TestCase):
    def test_page_html_contains_lens_switch_element(self) -> None:
        from grove_html import render_page

        html = render_page()
        self.assertIn("<grove-lens-switch", html)

    def test_page_html_references_lens_switch_module(self) -> None:
        from grove_html import render_page

        html = render_page()
        self.assertIn("/web/components/grove-lens-switch.js", html)
        # The script tag must actually be a module — plain <script> would not
        # load the component's `export` block cleanly and the browser would
        # miscount the syntax as classic script.
        self.assertIn('type="module"', html)

    def test_component_file_exists_on_disk(self) -> None:
        component = os.path.join(ROOT, "web", "components", "grove-lens-switch.js")
        self.assertTrue(
            os.path.isfile(component),
            f"grove-lens-switch.js is missing at {component!r}",
        )

    def test_component_declares_default_lens_pa(self) -> None:
        """C12 — PA is the least-surprising landing on first boot."""
        component = os.path.join(ROOT, "web", "components", "grove-lens-switch.js")
        with open(component, "r", encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn('DEFAULT_LENS = "pa"', src)
        self.assertIn('grove:lens:v1', src)


if __name__ == "__main__":
    unittest.main()
