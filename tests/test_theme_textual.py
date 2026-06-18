"""tests/test_theme_textual.py — grove palette → Textual CSS helpers."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grove.theme_textual import (
    ACCENT,
    FRESH_SHELL_CSS,
    HEALTHY,
    DOWN,
    markup_bold_accent,
    markup_status_dot,
)


def test_fresh_shell_css_has_nav_and_vitals():
    assert "NavBar #nav-vitals" in FRESH_SHELL_CSS
    assert "NavBar #nav-links" in FRESH_SHELL_CSS
    assert "#262626" in FRESH_SHELL_CSS or "background:" in FRESH_SHELL_CSS


def test_markup_helpers_use_palette():
    assert ACCENT in markup_bold_accent()
    assert HEALTHY in markup_status_dot(True)
    assert DOWN in markup_status_dot(False)
