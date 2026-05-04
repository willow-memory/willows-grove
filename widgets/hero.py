"""widgets/hero.py — Animated willow tree hero widget.
b17: WGRV1  ΔΣ=42
"""
from textual.widgets import Static

# 10-frame animation poses — L=lean left, C=center, R=lean right
# ƒ = hanging frond leaf, ║ = trunk. Source: willow_sway.py
# 30-frame loop: L(10) → C(10) → R(10) at 2s/frame

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

_POSE_ORDER = ["L", "C", "R"]  # L→C→R→L cycle (30 frames total)


def advance_frame(pose: str, frame: int) -> tuple[str, int]:
    """Return (next_pose, next_frame) after advancing one step."""
    frame += 1
    if frame >= len(POSES[pose]):
        idx   = (_POSE_ORDER.index(pose) + 1) % len(_POSE_ORDER)
        pose  = _POSE_ORDER[idx]
        frame = 0
    return pose, frame


def render_frame(pose: str, frame: int) -> str:
    return POSES[pose][frame]


# Willow canopy crown — rounded dome above the drooping frond row.
# ║ sits at column 6 of each 17-char row, matching the pose trunk position.
_SCENE_TOP = [
    " ƒ  * . * . *   ",   # sparse crown top
    "ƒ ƒ . ƒ . ƒ . ƒ ",   # leafy canopy body
    "ƒ ƒ  (║ . .) ƒ  ",   # canopy base — trunk visible
]

# Below the animated frond row: fronds drooping to ground level (pose C rows 8-9)
_SCENE_BOTTOM = [
    r"ƒ     ║ƒ    ƒ  ƒ",
    r"ƒ     ║ƒ     ƒ  ",
]


class WillowHero(Static):
    """Animated weeping willow — 30-frame drooping frond loop."""

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

    def on_mount(self) -> None:
        self.set_interval(2.0, self._tick)
        self._redraw()

    def _tick(self) -> None:
        self._pose, self._frame = advance_frame(self._pose, self._frame)
        self._redraw()

    def _redraw(self) -> None:
        frond = render_frame(self._pose, self._frame)
        lines = _SCENE_TOP + [frond] + _SCENE_BOTTOM
        self.update("\n".join(lines))
