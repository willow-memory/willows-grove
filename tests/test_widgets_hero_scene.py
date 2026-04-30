"""tests/test_widgets_hero_scene.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.hero_scene import GROUND_LINE, make_ground_content

def test_ground_line_contains_tilde():
    assert "~" in GROUND_LINE

def test_make_ground_content_contains_grass():
    content = make_ground_content()
    assert "|" in content

def test_make_ground_content_is_string():
    assert isinstance(make_ground_content(), str)

def test_make_ground_content_contains_flower():
    content = make_ground_content()
    assert "✿" in content
