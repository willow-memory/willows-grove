# b17: WGRV1 ΔΣ=42
"""tests/test_grove_html_boot_wire.py — grove_html boot-script mount check.

Asserts that ``grove_html.render_page()``:
  1. references ``/web/boot/layout-memory-boot.js`` as an ES module in
     ``<head>``, and
  2. does so AFTER the ``grove-card`` component script tag if one is
     present (so ``customElements.define("grove-card", …)`` has run by
     the time the boot module walks the DOM by tag name).

Also asserts the boot .js file exists on disk so ``/web/boot/…`` resolves
under ``grove_serve.py``'s recursive ``/web`` StaticFiles mount.
"""
from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class BootWireTests(unittest.TestCase):
    def setUp(self) -> None:
        import grove_html
        self.html = grove_html.render_page()

    def test_boot_script_tag_present_in_head(self) -> None:
        head_end = self.html.find("</head>")
        self.assertNotEqual(head_end, -1, "render_page must have </head>")
        head = self.html[:head_end]
        self.assertIn("/web/boot/layout-memory-boot.js", head)
        # Loaded as an ES module, per D9's no-build-step discipline.
        self.assertIn(
            '<script type="module" src="/web/boot/layout-memory-boot.js">',
            head,
        )

    def test_grove_card_component_script_is_mounted(self) -> None:
        """The grove-card component script is on the served page.

        This used to be a tolerated absence: the assertion below skipped
        itself when the tag was missing, on the stated premise that the
        component was "imported transitively today" and that a later PR
        would mount one. Neither held. Nothing in the tree imported
        `grove-card.js` except `web/harness.html`, so `<grove-card>` was
        never defined on the served page at all — `layout-memory-boot.js`
        walked `querySelectorAll("grove-card[id]")` against an empty set
        on every load, and layout memory was live under test and inert in
        production.

        A skip cannot pin an ordering discipline, because the state it
        skips on is the state where the discipline is being violated.
        Presence is asserted here so the ordering test below has
        something real to order.
        """
        self.assertIn(
            '<script type="module" src="/web/components/grove-card.js">',
            self.html,
            "grove-card.js must be mounted or customElements.define("
            '"grove-card", …) never runs on the served page.',
        )

    def test_boot_script_comes_after_grove_card_component_script(self) -> None:
        """The boot tag comes after the component tag in document order.

        `layout-memory-boot.js` walks the DOM by tag name, so every
        `customElements.define(…)` it depends on must already have run.
        """
        boot_idx = self.html.find(
            "/web/boot/layout-memory-boot.js"
        )
        self.assertNotEqual(boot_idx, -1)
        card_idx = self.html.find("/web/components/grove-card.js")
        self.assertNotEqual(
            card_idx,
            -1,
            "grove-card component script missing — see "
            "test_grove_card_component_script_is_mounted.",
        )
        self.assertLess(
            card_idx,
            boot_idx,
            "grove-card component script must precede boot script",
        )

    def test_boot_script_is_last_module_in_head(self) -> None:
        """Boot walks the DOM by tag name and must run after all sibling
        component scripts have registered their custom elements. The
        simplest way to guarantee that on the served page today is: put
        the boot tag LAST among the ``<script type="module">`` tags in
        ``<head>``.
        """
        head_end = self.html.find("</head>")
        head = self.html[:head_end]
        # Collect module-script srcs in document order.
        needle = '<script type="module" src="'
        srcs: list[str] = []
        cursor = 0
        while True:
            i = head.find(needle, cursor)
            if i == -1:
                break
            start = i + len(needle)
            end = head.find('"', start)
            if end == -1:
                break
            srcs.append(head[start:end])
            cursor = end + 1
        self.assertIn("/web/boot/layout-memory-boot.js", srcs)
        self.assertEqual(
            srcs[-1],
            "/web/boot/layout-memory-boot.js",
            f"boot must be last module script; got order: {srcs}",
        )

    def test_boot_module_file_exists_on_disk(self) -> None:
        path = os.path.join(ROOT, "web", "boot", "layout-memory-boot.js")
        self.assertTrue(
            os.path.isfile(path),
            f"expected boot module at {path}",
        )


if __name__ == "__main__":
    unittest.main()
