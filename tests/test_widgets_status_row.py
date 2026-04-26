"""tests/test_widgets_status_row.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.status_row import dot, color_for_ok

def test_dot_true():
    assert dot(True) == "●"

def test_dot_false():
    assert dot(False) == "○"

def test_dot_none():
    assert dot(None) == "◌"

def test_color_ok():
    assert color_for_ok(True) == "green"

def test_color_fail():
    assert color_for_ok(False) == "red"

def test_color_unknown():
    assert color_for_ok(None) == "yellow"
