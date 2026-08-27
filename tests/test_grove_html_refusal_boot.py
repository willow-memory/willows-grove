# b17: WGRV1 ΔΣ=42
"""tests/test_grove_html_refusal_boot.py — refusal auto-summon wiring.

Asserts that ``grove_html.render_page()``:

  1. Mounts the ``grove-refusal-chip`` component script in ``<head>``.
  2. Mounts ``/web/boot/refusal-summon-boot.js`` in ``<head>`` AFTER
     the ``grove-refusal-chip`` component script (so the custom element
     is ``customElements``-defined before the boot dispatches events at
     it).
  3. Ships a ``<div id="refusal-chip-mount">`` in ``<body>`` — the mount
     point the boot module summons chips into.

Also asserts the boot .js file exists on disk so ``/web/boot/…``
resolves under ``grove_serve.py``'s recursive ``/web`` StaticFiles mount.
"""
from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


CHIP_SRC = "/web/components/grove-refusal-chip.js"
BOOT_SRC = "/web/boot/refusal-summon-boot.js"


class RefusalBootWireTests(unittest.TestCase):
    def setUp(self) -> None:
        import grove_html
        self.html = grove_html.render_page()

    def test_refusal_chip_component_script_in_head(self) -> None:
        head_end = self.html.find("</head>")
        self.assertNotEqual(head_end, -1)
        head = self.html[:head_end]
        self.assertIn(
            f'<script type="module" src="{CHIP_SRC}">',
            head,
        )

    def test_boot_script_tag_present_in_head(self) -> None:
        head_end = self.html.find("</head>")
        self.assertNotEqual(head_end, -1)
        head = self.html[:head_end]
        self.assertIn(
            f'<script type="module" src="{BOOT_SRC}">',
            head,
        )

    def test_boot_script_comes_after_refusal_chip_component_script(self) -> None:
        head_end = self.html.find("</head>")
        head = self.html[:head_end]
        chip_idx = head.find(CHIP_SRC)
        boot_idx = head.find(BOOT_SRC)
        self.assertNotEqual(chip_idx, -1, "refusal-chip script must be in <head>")
        self.assertNotEqual(boot_idx, -1, "refusal-summon-boot script must be in <head>")
        self.assertLess(
            chip_idx,
            boot_idx,
            "grove-refusal-chip component script must precede refusal-summon-boot",
        )

    def test_refusal_chip_mount_present_in_body(self) -> None:
        body_start = self.html.find("<body>")
        self.assertNotEqual(body_start, -1)
        body = self.html[body_start:]
        self.assertIn('<div id="refusal-chip-mount"></div>', body)

    def test_boot_module_file_exists_on_disk(self) -> None:
        path = os.path.join(ROOT, "web", "boot", "refusal-summon-boot.js")
        self.assertTrue(
            os.path.isfile(path),
            f"expected boot module at {path}",
        )


if __name__ == "__main__":
    unittest.main()
