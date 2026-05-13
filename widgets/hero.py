"""widgets/hero.py — Animated willow tree hero widget.
b17: WGRV1  ΔΣ=42
"""
import logging
import random
import traceback
from textual.widgets import Static
from ._hero_state import set_meadow_wind, is_bloop, is_gerald, tick_gerald, gerald_frame

log = logging.getLogger("hero")

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

# Crown — per-frame variants so the whole tree breathes, not just the frond row.
# 10 frames each, aligned to the pose frame index.

_CROWN_TOP_FRAMES = [
    " ƒ  * . * . *   ",
    " ƒ  . * . * .   ",
    " ƒ  * . * . *   ",
    " ƒ  . . * . *   ",
    "ƒƒ  * . * . *   ",
    " ƒ  * . * . .   ",
    " ƒ  * . * . *   ",
    " ƒ  . * . * *   ",
    "ƒƒ  * . * . *   ",
    " ƒ  * . * . *   ",
]

_CROWN_MID_FRAMES = {
    "L": [
        "ƒ ƒ. ƒ . ƒ . ƒ  ",
        "ƒ ƒ .ƒ . ƒ . ƒ  ",
        "ƒ ƒ. ƒ . ƒ . ƒ  ",
        "ƒ ƒ .ƒ .ƒ . ƒ   ",
        "ƒ ƒ. ƒ . ƒ . ƒ  ",
        "ƒ ƒ .ƒ . ƒ .ƒ   ",
        "ƒ ƒ. ƒ . ƒ . ƒ  ",
        "ƒ ƒ .ƒ . ƒ . ƒ  ",
        "ƒ ƒ. ƒ .ƒ . ƒ   ",
        "ƒ ƒ .ƒ . ƒ . ƒ  ",
    ],
    "C": [
        "ƒ ƒ . ƒ . ƒ . ƒ ",
        "ƒ ƒ . ƒ .ƒ . ƒ  ",
        "ƒ ƒ . ƒ . ƒ . ƒ ",
        "ƒ ƒ .ƒ . ƒ . ƒ  ",
        "ƒ ƒ . ƒ . ƒ . ƒ ",
        "ƒ ƒ . ƒ . ƒ .ƒ  ",
        "ƒ ƒ . ƒ . ƒ . ƒ ",
        "ƒ ƒ .ƒ . ƒ . ƒ  ",
        "ƒ ƒ . ƒ . ƒ . ƒ ",
        "ƒ ƒ . ƒ .ƒ . ƒ  ",
    ],
    "R": [
        "ƒ ƒ  . ƒ . ƒ . ƒ",
        "ƒ ƒ  .ƒ . ƒ . ƒ ",
        "ƒ ƒ  . ƒ . ƒ . ƒ",
        "ƒ ƒ  . ƒ .ƒ . ƒ ",
        "ƒ ƒ  . ƒ . ƒ . ƒ",
        "ƒ ƒ  .ƒ . ƒ .ƒ  ",
        "ƒ ƒ  . ƒ . ƒ . ƒ",
        "ƒ ƒ  . ƒ .ƒ . ƒ ",
        "ƒ ƒ  . ƒ . ƒ . ƒ",
        "ƒ ƒ  .ƒ . ƒ . ƒ ",
    ],
}

_CROWN_BASE_FRAMES = [
    "ƒ ƒ  (║ . .) ƒ  ",
    "ƒ ƒ  (║ . .)ƒ   ",
    "ƒ ƒ  (║ . .) ƒ  ",
    "ƒ ƒ. (║ . .) ƒ  ",
    "ƒ ƒ  (║ . .) ƒ  ",
    "ƒ ƒ  (║ . .)ƒ   ",
    "ƒ ƒ  (║ . .) ƒ  ",
    "ƒ ƒ. (║ . .) ƒ  ",
    "ƒ ƒ  (║ . .) ƒ  ",
    "ƒ ƒ  (║ . .)ƒ   ",
]


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


def render_frame(pose: str, frame: int) -> tuple[str, str, str, str, str, str]:
    """Return (crown_top, crown_mid, crown_base, frond, trail_a, trail_b)."""
    return (
        _CROWN_TOP_FRAMES[frame],
        _CROWN_MID_FRAMES[pose][frame],
        _CROWN_BASE_FRAMES[frame],
        POSES[pose][frame],
        POSES[pose][8],
        POSES[pose][9],
    )


# Per-character summer color overrides.
# CSS color (#4ade80) is the default for ƒ frond chars — only exceptions listed here.
_CHAR_COLORS: dict[str, str] = {
    "║": "#a16207",   # trunk — warm bark brown
    "*": "#fbbf24",   # crown stars — sunlight gold
    ".": "#6ee7b7",   # crown dots — dappled mint
    "(": "#34d399",   # crown base parens — emerald
    ")": "#34d399",
    # Gerald at midnight — headless rotisserie chicken
    "°": "#fbbf24",   # absent head spot — gold
    ">": "#f97316",   # wing — warm orange
    "<": "#f97316",   # wing — warm orange
    "~": "#f97316",   # body — warm orange
}
_BRANCH_CHARS = frozenset("\\/")


def _gerald_overlay(lines: list[str], gframe: int) -> list[str]:
    """Sweep headless chicken silhouette across crown rows (rows 0-2)."""
    w   = len(lines[0]) if lines else 17
    # x sweeps from 2 to w-4 across GERALD_DURATION frames
    x   = max(0, min(w - 4, 2 + gframe * 2))
    out = list(lines)
    def _put(row: int, pos: int, text: str) -> None:
        if 0 <= row < len(out):
            s = out[row]
            end = min(len(s), pos + len(text))
            out[row] = s[:pos] + text[:end - pos] + s[end:]
    _put(0, x + 1, "°")      # absent head — one char
    _put(1, x,     ">~<")    # wings + body — three chars
    _put(2, x + 1, "|")      # neck stump — one char
    return out


def _colorize(line: str) -> str:
    """Apply summer Rich markup to one tree art line."""
    out = []
    for ch in line:
        if ch in _CHAR_COLORS:
            out.append(f"[{_CHAR_COLORS[ch]}]{ch}[/]")
        elif ch in _BRANCH_CHARS:
            out.append(f"[#86efac]{ch}[/]")   # branches — sun-dappled light green
        else:
            out.append(ch)
    return "".join(out)


class WillowHero(Static):
    """Animated weeping willow — pendulum-eased frond sway."""

    DEFAULT_CSS = """
    WillowHero {
        width: 22;
        height: 7;
        content-align: center bottom;
        color: #4ade80;
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
        try:
            if is_gerald():
                tick_gerald()
            if not is_bloop():
                self._pose, self._frame = advance_frame(self._pose, self._frame)
                set_meadow_wind(self._pose)
                self._redraw()
        except Exception:
            log.error("WillowHero._tick crash:\n%s", traceback.format_exc())
        finally:
            self._schedule_next()

    def _redraw(self) -> None:
        try:
            top, mid, base, frond, trail_a, trail_b = render_frame(self._pose, self._frame)
            lines = [top, mid, base, frond, trail_a, trail_b]
            if is_gerald():
                lines = _gerald_overlay(lines, gerald_frame())
            self.update("\n".join(_colorize(l) for l in lines))
        except Exception:
            log.error("WillowHero._redraw crash (pose=%s frame=%d):\n%s",
                      self._pose, self._frame, traceback.format_exc())
