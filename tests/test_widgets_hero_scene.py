"""tests/test_widgets_hero_scene.py
b17: WGRV1  ΔΣ=42
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from textual.content import Content
from widgets.hero_scene import (
    _BLOOMS,
    _colorize_meadow,
    _colorize_trunk,
    _make_ground,
    _make_meadow,
    HeroScene,
)
from grove.apps.hero_format import format_ground_footer_markup


def test_make_meadow_is_string():
    assert isinstance(_make_meadow(0, 60), str)


def test_make_meadow_contains_bloom():
    content = _make_meadow(0, 60)
    assert any(f in content for f in _BLOOMS)


def test_make_meadow_cycles():
    frames = [_make_meadow(i, 60) for i in range(len(_BLOOMS))]
    assert len(set(frames)) > 1


def test_hero_scene_defaults_expanded():
    scene = HeroScene()
    assert scene.is_expanded() is True


def test_hero_scene_collapse_toggle():
    scene = HeroScene()
    scene.set_expanded(False)
    assert scene.is_expanded() is False
    scene.set_expanded(True)
    assert scene.is_expanded() is True


def test_ground_strip_markup_wind_left_backslashes():
    """Wind-L meadow uses backslashes; markup must not orphan [/] tags."""
    stats = {
        "vitals": {"pg": {"ok": True, "detail": "ok"}, "ollama": {"ok": True, "count": 1}},
        "grove_live": False,
        "kart": {"ok": False},
        "ledger": {"ok": True},
        "channels": {},
    }
    w = 80
    for frame in range(30):
        meadow_plain = _make_meadow(frame, w, "L")
        tx = w - 13
        trunk_plain = (" " * max(0, tx) + "║" + " " * max(0, w - tx - 1))[:w]
        trunk = _colorize_trunk(trunk_plain)
        meadow = _colorize_meadow(meadow_plain)
        ground = format_ground_footer_markup(stats)
        Content.from_markup(f"{trunk}\n{meadow}\n{ground}")
