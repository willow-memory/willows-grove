"""tests/test_grove_html_standing_boot.py — the ambient strip has a source.

INVARIANTS.md §8: "The served page renders live state, not curated
data." `tests/test_grove_html_no_hardcoded_status.py` pins the negative
half — the strip must not claim "standing" / "grove stable" as static
text. This file pins the positive half: the strip's live-text slot is
wired to a boot module that reads an endpoint, so the placeholder is a
pre-fetch sentinel rather than the permanent answer.

Pinned here:
  1. the strip carries the `data-standing` slot and a
     `data-standing-state` attribute the boot module repaints;
  2. `/web/boot/standing-boot.js` is mounted as an ES module in <head>
     and exists on disk (so `/web/boot/…` resolves under grove_serve's
     StaticFiles mount);
  3. it is mounted BEFORE `/web/boot/layout-memory-boot.js`, which
     `tests/test_grove_html_boot_wire.py::test_boot_script_is_last_module_in_head`
     pins as the last module script in <head>;
  4. the page CSS paints the unreachable state differently from the
     others — INVARIANTS.md §1 is a visual contract, not just a wording
     one.

The browser-side behavior (what the slot actually says after /health
answers, or does not) is pinned in
`tests/e2e/standing-strip.spec.js`.
"""
from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

BOOT_SRC = "/web/boot/standing-boot.js"
LAYOUT_BOOT_SRC = "/web/boot/layout-memory-boot.js"


class StandingBootWireTests(unittest.TestCase):
    def setUp(self) -> None:
        import grove_html

        self.html = grove_html.render_page()
        self.head = self.html[: self.html.find("</head>")]

    def test_strip_carries_the_live_text_slot(self) -> None:
        """The boot module paints `[data-standing]`; without it in the
        served markup the strip would be static text again."""
        self.assertIn("data-standing>", self.html)
        self.assertIn('data-standing-state="loading"', self.html)

    def test_boot_module_mounted_as_es_module_in_head(self) -> None:
        self.assertIn(f'<script type="module" src="{BOOT_SRC}">', self.head)

    def test_boot_module_file_exists_on_disk(self) -> None:
        path = os.path.join(ROOT, "web", "boot", "standing-boot.js")
        self.assertTrue(os.path.isfile(path), f"expected boot module at {path}")

    def test_boot_module_precedes_layout_memory_boot(self) -> None:
        """layout-memory-boot must stay the last module script in <head>."""
        standing_idx = self.head.find(BOOT_SRC)
        layout_idx = self.head.find(LAYOUT_BOOT_SRC)
        self.assertNotEqual(standing_idx, -1)
        self.assertNotEqual(layout_idx, -1)
        self.assertLess(
            standing_idx,
            layout_idx,
            "standing-boot must be mounted before layout-memory-boot, which "
            "test_grove_html_boot_wire pins as the last module in <head>",
        )

    def test_unreachable_state_is_painted_distinctly(self) -> None:
        """INVARIANTS.md §1: unreachable must not look like the others."""
        self.assertIn('.strip[data-standing-state="unreachable"]', self.html)
        self.assertIn('.strip[data-standing-state="loading"]', self.html)

    def test_boot_module_reads_the_health_endpoint(self) -> None:
        """The slot's source is an endpoint, not a literal. A boot module
        that stopped fetching would re-open the m31 finding silently."""
        path = os.path.join(ROOT, "web", "boot", "standing-boot.js")
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
        self.assertIn('"/health"', source)
        self.assertIn("fetch(", source)


if __name__ == "__main__":
    unittest.main()
