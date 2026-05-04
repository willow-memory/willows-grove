"""widgets/hero.py — Animated willow tree hero widget.
b17: WGRV1  ΔΣ=42
"""
from textual.widgets import Static

# Weeping willow — canopy dome + hanging fronds sway L→C→R→C→L
# Each pose: 10 frames of the hanging-frond row only.
# _SCENE_TOP + [frond_row] + _SCENE_BOTTOM = full tree.

POSES: dict[str, list[str]] = {
    "L": [  # fronds blown right by wind from left
        r"  `. . | ..`    ",
        r"  `. . |. .`    ",
        r"  `. . |  .`    ",
        r"   `. .|  .`    ",
        r"   `. .|   `    ",
        r"   `.  |   `    ",
        r"   `.  |  .`    ",
        r"   `. .|  .`    ",
        r"   `. .| . `    ",
        r"  `. . | . `    ",
    ],
    "C": [  # calm center
        r"  `. . | . .`   ",
        r"  `. .  . . `   ",
        r"  `. . | . .`   ",
        r"  ` . .|. . `   ",
        r"  `. . | . .`   ",
        r"   `. .|. .`    ",
        r"  `. . | . .`   ",
        r"  ` . .| . `    ",
        r"  `. . | . .`   ",
        r"   `. .| .`     ",
    ],
    "R": [  # fronds blown left by wind from right
        r"    `. .| . .`  ",
        r"    `. | . .`   ",
        r"    ` .| . .`   ",
        r"    `.  . . .`  ",
        r"    `   | . .`  ",
        r"    `   |. .`   ",
        r"    `. .|. .`   ",
        r"    `. .| .`    ",
        r"   `. . | .`    ",
        r"  `. .  | .`    ",
    ],
}

_POSE_ORDER = ["L", "C", "R"]


def advance_frame(pose: str, frame: int) -> tuple[str, int]:
    frame += 1
    if frame >= len(POSES[pose]):
        idx  = (_POSE_ORDER.index(pose) + 1) % len(_POSE_ORDER)
        pose = _POSE_ORDER[idx]
        frame = 0
    return pose, frame


def render_frame(pose: str, frame: int) -> str:
    return POSES[pose][frame]


# Weeping willow: round canopy dome, trunk visible through it
_SCENE_TOP = [
    "     * . * . *   ",
    "    ( . . . . )  ",
    "   ( .  . | . )  ",
]

# Lower fronds + trunk — no ground line (ground is the full-width strip below)
_SCENE_BOTTOM = [
    "    ` . | . `    ",
    "      ` | `      ",
    "        |        ",
]


class WillowHero(Static):
    """Animated weeping willow — drooping fronds sway L→C→R→C→L."""

    DEFAULT_CSS = """
    WillowHero {
        width: 22;
        height: 7;
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
        self.set_interval(2.0, self._tick)
        self._redraw()

    def _tick(self) -> None:
        self._pose, self._frame = advance_frame(self._pose, self._frame)
        self._redraw()

    def _redraw(self) -> None:
        frond = render_frame(self._pose, self._frame)
        lines = _SCENE_TOP + [frond] + _SCENE_BOTTOM
        self.update("\n".join(lines))
