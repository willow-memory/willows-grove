"""tests/test_widgets_help_nav.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from widgets.help_nav import HelpSectionSelected, HelpNavRow


def test_help_section_selected_stores_section():
    msg = HelpSectionSelected("shortcuts")
    assert msg.section == "shortcuts"


def test_help_nav_row_stores_section():
    row = HelpNavRow("overview", "Overview")
    assert row._section == "overview"
