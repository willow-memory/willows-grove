"""widgets/hero.py — Animated willow tree hero widget.
b17: WGRV1  ΔΣ=42
"""
import random
from textual.widgets import Static
from ._hero_state import set_meadow_wind

# 10-frame animation poses — L=lean left, C=center, R=lean right
# ƒ = hanging frond leaf, ║ = trunk. Source: willow_sway.py
# Base cycle: L(10) → C(10) → R(10), with pendulum easing and occasional reversal.

POSES: dict[str, list[str]] = {
    "L": [
        r"ƒƒ\ ƒ ƒ ƒ  /ƒ ƒ ",
        r"ƒ ƒ\ ƒ ƒ  / ƒ ƒ ",
        r"ƒ  ƒ\ ƒ  /  ƒ ƒ ",
        r"ƒ  ƒ \  / ƒ  ƒ  ",
        r"ƒ  ƒ  \/  ƒ  ƒ  ",
        r"ƒ  ƒ  ║   ƒ  ƒ  ",
        r"ƒ  ƒ ƒ║    ƒ  ƒ ",
        r"ƒ    ƒ║     ƒ  ƒ",
        r"ƒ     ║ƒ     ƒ  ",
        r"ƒ     ║ƒ      ƒ ",
    ],
    "C": [
        r"ƒƒ\ ƒ ƒ ƒ /ƒ ƒ  ",
        r"ƒ ƒ\ ƒ ƒ / ƒ ƒ  ",
        r"ƒ  ƒ\   /  ƒ ƒ  ",
        r"ƒ  ƒ \ / ƒ  ƒ   ",
        r"ƒ  ƒ  ║  ƒ  ƒ   ",
        r"ƒ   ƒ ║  ƒ  ƒ   ",
        r"ƒ   ƒ ║ƒ  ƒ  ƒ  ",
        r"ƒ    ƒ║    ƒ  ƒ ",
        r"ƒ     ║ƒ    ƒ  ƒ",
        r"ƒ     ║ƒ     ƒ  ",
    ],
    "R": [
        r"ƒ\ ƒ ƒ ƒ ƒ/ƒƒ   ",
        r"ƒ \ ƒ ƒ ƒ /ƒ ƒ  ",
        r"ƒ  \ ƒ ƒ /  ƒ ƒ ",
        r"ƒ ƒ \   /ƒ  ƒ ƒ ",
        r"ƒ ƒ  \ / ƒ  ƒ ƒ ",
        r"ƒ ƒ   ║  ƒ  ƒ ƒ ",
        r"ƒ  ƒ ƒ║   ƒ  ƒ  ",
        r"ƒ    ƒ║    ƒ  ƒ ",
        r"ƒ     ║ƒ    ƒ   ",
        r"ƒ     ║ ƒ    ƒ  ",
    ],
}

_POSE_ORDER = ["L", "C", "R"]

# Pendulum easing — seconds per frame within a pose.
# Slow at tips (frames 0-2, 8-9), fast through mid-swing (frames 4-6).
_FRAME_SPEED = [2.4, 2.1, 1.8, 1.5, 1.3, 1.3, 1.5, 1.8, 2.1, 2.4]

# Crown variants per lean direction — middle line shifts subtly left/right.
_CROWN_TOP  = " ƒ  * . * . *   "
_CROWN_MID  = {
    "L": "ƒ ƒ. ƒ . ƒ . ƒ  ",   # nudged left
    "C": "ƒ ƒ . ƒ . ƒ . ƒ ",   # centered
    "R": "ƒ ƒ  . ƒ . ƒ . ƒ",   # nudged right
}
_CROWN_BASE = "ƒ ƒ  (║ . .) ƒ  "


def advance_frame(pose: str, frame: int) -> tuple[str, int]:
    """Return (next_pose, next_frame) after advancing one step.

    At pose boundary, 15% chance to reverse direction instead of continuing,
    giving the tree an occasional 'barely pushed' feel.
    """
    frame += 1
    if frame >= len(POSES[pose]):
        idx = _POSE_ORDER.index(pose)
        if random.random() < 0.15:
            # reverse: step back toward previous pose
            idx = (idx - 1) % len(_POSE_ORDER)
        else:
            idx = (idx + 1) % len(_POSE_ORDER)
        pose  = _POSE_ORDER[idx]
        frame = 0
    return pose, frame


def frame_speed(frame: int) -> float:
    """Seconds to display this frame — pendulum easing."""
    return _FRAME_SPEED[frame]


def render_frame(pose: str, frame: int) -> tuple[str, str, str, str, str]:
    """Return (crown_top, crown_mid, crown_base, frond, trail_a, trail_b)."""
    return (
        _CROWN_TOP,
        _CROWN_MID[pose],
        _CROWN_BASE,
        POSES[pose][frame],
        POSES[pose][8],
        POSES[pose][9],
    )


class WillowHero(Static):
    """Animated weeping willow — pendulum-eased frond sway."""

    DEFAULT_CSS = """
    WillowHero {
        width: 22;
        height: 7;
        content-align: center bottom;
        color: $success;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pose  = "C"
        self._frame = 4
        self._timer = None

    def on_mount(self) -> None:
        self._schedule_next()
        self._redraw()

    def _schedule_next(self) -> None:
        speed = frame_speed(self._frame)
        self._timer = self.set_timer(speed, self._tick)

    def _tick(self) -> None:
        self._pose, self._frame = advance_frame(self._pose, self._frame)
        set_meadow_wind(self._pose)
        self._redraw()
        self._schedule_next()

    def _redraw(self) -> None:
        top, mid, base, frond, trail_a, trail_b = render_frame(self._pose, self._frame)
        self.update("\n".join([top, mid, base, frond, trail_a, trail_b]))
