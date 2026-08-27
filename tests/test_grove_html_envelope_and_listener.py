# b17: WGRV1 ΔΣ=42
"""tests/test_grove_html_envelope_and_listener.py — pins finding M10.

Asserts that ``grove_html.render_page()`` honours INVARIANTS.md §1 + §8 for
the envelope surface and the persona-registry unreachable event:

  1. The served page MOUNTS ``<grove-envelope-panel…>`` — the panel that
     consumes the live ``/api/envelopes`` endpoint. §8 says every panel on
     the served page renders live state; a live endpoint that no served
     panel consumes violates the discipline.
  2. The served page LOADS the ``grove-envelope-panel`` component module
     (``/web/components/grove-envelope-panel.js``) so the tag upgrades.
  3. The served page CARRIES a page-level listener for the
     ``registry-unreachable`` event dispatched by
     ``<grove-persona-registry>`` — either an inline ``<script>`` that
     names the event, or a boot module reference (a
     ``registry-unreachable-boot.js`` ``<script>`` tag) whose file exists
     on disk. Without a listener the event fires into a page that has no
     mouth to speak with.

Must fail against pre-fix ``grove_html.py`` — the three needles are
absent from the current render.
"""
from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


PANEL_TAG = "<grove-envelope-panel"
PANEL_SRC = "/web/components/grove-envelope-panel.js"
EVENT_NAME = "registry-unreachable"
BOOT_SRC = "/web/boot/registry-unreachable-boot.js"


class EnvelopeAndListenerTests(unittest.TestCase):
    def setUp(self) -> None:
        import grove_html

        self.html = grove_html.render_page()

    def test_envelope_panel_element_mounted(self) -> None:
        """INVARIANTS.md §8: the served page consumes /api/envelopes via
        a <grove-envelope-panel> mount. A live endpoint that no served
        panel reads is a promise the page never keeps.
        """
        self.assertIn(
            PANEL_TAG,
            self.html,
            "served page must mount <grove-envelope-panel…>; "
            "/api/envelopes is live but no panel consumes it",
        )

    def test_envelope_panel_component_script_loaded(self) -> None:
        """The <grove-envelope-panel> tag needs its component module
        loaded so ``customElements.define`` runs and the tag upgrades.
        """
        self.assertIn(
            PANEL_SRC,
            self.html,
            "served page must load the grove-envelope-panel component "
            f"script at {PANEL_SRC}",
        )

    def test_registry_unreachable_listener_wired(self) -> None:
        """INVARIANTS.md §1 guidance: a component's state event has a
        page-level listener. ``registry-unreachable`` is dispatched by
        ``<grove-persona-registry>`` (bubbles + composed) — the served
        page must either carry an inline listener that names the event,
        or reference a boot module (``registry-unreachable-boot.js``)
        whose file exists on disk.
        """
        inline_listener = EVENT_NAME in self.html
        boot_referenced = BOOT_SRC in self.html
        if boot_referenced:
            boot_path = os.path.join(
                ROOT, "web", "boot", "registry-unreachable-boot.js"
            )
            self.assertTrue(
                os.path.isfile(boot_path),
                f"boot module referenced but not on disk: {boot_path}",
            )
        self.assertTrue(
            inline_listener or boot_referenced,
            "served page must wire a page-level listener for "
            f"'{EVENT_NAME}' — either an inline <script> naming the "
            "event, or a boot module reference. Neither found.",
        )


if __name__ == "__main__":
    unittest.main()
