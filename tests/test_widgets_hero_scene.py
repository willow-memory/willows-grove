"""tests/test_widgets_hero_scene.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from widgets.hero_scene import _GROUND, _BLOOMS, _make_meadow


def test_ground_contains_tilde():
    assert "~" in _GROUND


def test_make_meadow_is_string():
    assert isinstance(_make_meadow(0, 60), str)


def test_make_meadow_contains_bloom():
    content = _make_meadow(0, 60)
    assert any(f in content for f in _BLOOMS)


def test_make_meadow_cycles():
    frames = [_make_meadow(i, 60) for i in range(len(_BLOOMS))]
    assert len(set(frames)) > 1


def test_make_meadow_respects_width():
    for w in (40, 60, 80):
        assert len(_make_meadow(0, w)) <= w
