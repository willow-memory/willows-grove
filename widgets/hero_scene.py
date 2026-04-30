"""widgets/hero_scene.py — HeroScene: full-width band with willow tree + ground strip.
b17: WGRV1  ΔΣ=42
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from .hero import WillowHero


GROUND_LINE = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

_SCENE_ELEMENTS = [
    "✿", "|", "✿", "|", "⬡", "|", "♟", "|", "✿", "|",
    "⌁", "|", "✦", "|", "✿", "|", "⬡", "|", "♞", "|", "✿",
]


def make_ground_content() -> str:
    """Return the static ground strip text for Phase 1."""
    scene_row = "  " + " ".join(_SCENE_ELEMENTS) + "  "
    return f"{scene_row}\n  {GROUND_LINE}"


class GroundStrip(Static):
    """Phase 1: static scene strip. Phase 1.5 adds animation."""

    DEFAULT_CSS = """
    GroundStrip {
        width: 1fr;
        height: 10;
        color: #3fb950;
        padding: 2 2 0 2;
        content-align: left bottom;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(make_ground_content(), **kwargs)


class HeroScene(Horizontal):
    """Full-width band: WillowHero (left) + GroundStrip (center, 1fr)."""

    DEFAULT_CSS = """
    HeroScene {
        height: 10;
        background: #0d1117;
        border-bottom: solid #30363d;
    }
    HeroScene WillowHero {
        width: 28;
    }
    """

    def compose(self) -> ComposeResult:
        yield WillowHero()
        yield GroundStrip()
