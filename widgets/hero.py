"""widgets/hero.py — Animated willow tree hero widget.
b17: WGRV1  ΔΣ=42
"""
from textual.widgets import Static

# 10-frame animation poses — L=lean left, C=center, R=lean right
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


_SCENE_TOP = [
    "        ,",
    "       /|\\",
    "      / | \\",
]

_SCENE_BOTTOM = [
    "      |   |",
    "   ~~~|~~~|~~~",
]


class WillowHero(Static):
    """Animated 10-frame willow tree sway. Cycles L→C→R→C→L."""

    DEFAULT_CSS = """
    WillowHero {
        height: 8;
        content-align: center middle;
        color: $success;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pose  = "C"
        self._frame = 4

    def on_mount(self) -> None:
        self.set_interval(0.18, self._tick)
        self._render()

    def _tick(self) -> None:
        self._pose, self._frame = advance_frame(self._pose, self._frame)
        self._render()

    def _render(self) -> None:
        branch = render_frame(self._pose, self._frame)
        lines  = _SCENE_TOP + [f"    {branch}"] + _SCENE_BOTTOM
        self.update("\n".join(lines))
