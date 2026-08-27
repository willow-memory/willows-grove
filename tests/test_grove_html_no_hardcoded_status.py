# b17: WGRV1 ΔΣ=42
"""tests/test_grove_html_no_hardcoded_status.py — pins finding m31.

INVARIANTS.md §8: 'The served page renders live state, not curated
data.' Constraint 1 (DESIGN_CONSTRAINTS.md): '"I could not reach the
source" must never collapse into "there is nothing there."'

``grove_html._TOP_STRIP`` used to render the fleet-standing indicator
as static markup — the literal text "standing" and "grove stable" —
with no endpoint, no state check, and no path by which an unreachable
seam could ever change what the operator sees. The operator read
"grove stable" whether or not any seam was actually reachable, which
is exactly the collapse Constraint 1 forbids.

This test reads ``render_page()``'s output and asserts neither string
appears as visible top-strip text. It allows the words to appear in
CSS classes/ids (e.g. ``class="standing"``) since those are not
operator-visible claims — only bare visible text between tags matters.

Must fail against pre-fix ``grove_html.py`` — the top strip currently
renders ``<span>standing</span>`` and ``<span>grove stable</span>``
verbatim.
"""
from __future__ import annotations

import os
import re
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# Matches visible text content between tags, e.g. <span>standing</span>
# captures "standing". Deliberately narrow (no attribute values) so a
# class="standing" or id="grove-stable" would NOT trip this — only text
# a human actually reads on the page counts as a "static status claim".
_VISIBLE_TEXT_RE = re.compile(r">([^<>]+)<")


def _visible_text_fragments(html: str) -> list[str]:
    return [frag.strip() for frag in _VISIBLE_TEXT_RE.findall(html) if frag.strip()]


class NoHardcodedStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        import grove_html

        self.html = grove_html.render_page()
        self.visible = _visible_text_fragments(self.html)

    def test_top_strip_does_not_claim_standing_as_visible_text(self) -> None:
        """INVARIANTS.md §8 / Constraint 1: 'standing' must not appear as
        static visible text — that is a status claim with no source
        behind it. It may still appear in a class/id/comment.
        """
        self.assertNotIn(
            "standing",
            self.visible,
            "top strip must not render the bare word 'standing' as "
            "visible text with no live source behind it (INVARIANTS.md "
            "§8, Constraint 1)",
        )

    def test_top_strip_does_not_claim_grove_stable_as_visible_text(self) -> None:
        """INVARIANTS.md §8 / Constraint 1: 'grove stable' must not
        appear as static visible text — the operator would read it as
        true regardless of whether any seam is reachable.
        """
        self.assertNotIn(
            "grove stable",
            self.visible,
            "top strip must not render the static claim 'grove stable' "
            "as visible text with no endpoint or state check behind it "
            "(INVARIANTS.md §8, Constraint 1)",
        )


if __name__ == "__main__":
    unittest.main()
