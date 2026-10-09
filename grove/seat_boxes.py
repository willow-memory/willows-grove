# b17: GRSET ΔΣ=42
"""The seat's box stream: boxes, cards, and the sentence code says over them.

Mirrors ``web/demo/box-stream/box-stream-v1.3.html`` in a terminal. Nothing
here talks to a model: a sentence is composed by code from box facts plus a
fixed glue list, so every number, name and status comes from a box and only
the glue is free.

A card has three states, never collapsed (INVARIANTS.md section 1): a
populated card in its kind's color, an ``empty`` card (faint, dashed rule,
reason) and an ``unreachable`` card (amber, its own rule and bar, reason).
They differ in marker and glyph, not only in color, so the plain path, which
is what tests and CI read, tells them apart.

Color is gated on a tty and on ``NO_COLOR`` being unset. Anywhere else the
card is plain ASCII with no escape code.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass

#: The only free words in a sentence (``GLUE`` in the web sketch).
GLUE = (
    "morning",
    "oh",
    "and",
    "also",
    "still",
    "both",
    "heads up",
    "no rush",
    "looks like",
    "anytime",
    "got it",
)
#: Box kind -> (name shown, loam-palette rgb). From box-stream-v1.3 ``:19-27``.
KINDS: dict[str, tuple[str, tuple[int, int, int]]] = {
    "you": ("needs you", (230, 179, 76)),  # --sun
    "dec": ("decided", (70, 167, 123)),  # --emerald
    "pr": ("changed", (143, 214, 185)),  # --mint
    "block": ("blocked", (229, 137, 59)),  # --amber
    "pass": ("routine pass", (134, 184, 111)),  # --frond
}
FAINT = (111, 100, 83)
AMBER = KINDS["block"][1]
STATES = ("populated", "empty", "unreachable")
#: state -> (top rule, bar). The glyphs differ so no color is needed to tell.
RULE = {"populated": "+-", "empty": "+.", "unreachable": "+!"}
BAR = {"populated": "|", "empty": ":", "unreachable": "!"}
SHORT = 12
HASH64 = re.compile(r"\b[0-9a-fA-F]{64}\b")
RESET = "\x1b[0m"


@dataclass
class Box:
    id: str
    kind: str
    label: str
    value: str
    detail: str = ""
    state: str = "populated"


def use_color(stream: object = None, environ: dict | None = None) -> bool:
    """Color only on a tty with ``NO_COLOR`` unset (or empty, per no-color.org)."""
    out = stream if stream is not None else sys.stdout
    env = os.environ if environ is None else environ
    isatty = getattr(out, "isatty", None)
    return bool(isatty and isatty()) and not env.get("NO_COLOR")


def short(text: str) -> str:
    """A 64-hex hash reads as its first twelve characters."""
    return HASH64.sub(lambda m: m.group(0)[:SHORT], str(text))


def _paint(rgb: tuple[int, int, int], text: str, bold: bool = False) -> str:
    r, g, b = rgb
    return f"\x1b[{'1;' if bold else ''}38;2;{r};{g};{b}m{text}{RESET}"


def render_box(box: Box, color: bool = False) -> str:
    """One card. Plain mode::

    +- [needs you] Ratify  b5
    | the work order
    | local-flow-and-ui section 7
    """
    state = box.state if box.state in STATES else "unreachable"
    if state == "populated":
        name, rgb = KINDS.get(box.kind, ("note", FAINT))
    else:
        name, rgb = state, (AMBER if state == "unreachable" else FAINT)
    bar = BAR[state]
    head = f"{RULE[state]} [{name}] {short(box.label)}  {short(box.id)}"
    rows = [(short(box.value), True)]
    if box.detail:
        rows += [(short(ln), False) for ln in box.detail.split("\n")]
    rows = [(ln, strong) for text, strong in rows for ln in text.split("\n")]
    if not color:
        return "\n".join([head, *(f"{bar} {ln}" for ln, _ in rows)])
    lines = [_paint(rgb, head, bold=True)]
    for ln, strong in rows:
        tone = rgb if strong else FAINT
        lines.append(f"{_paint(rgb, bar)} {_paint(tone, ln, bold=strong)}")
    return "\n".join(lines)


def legend(color: bool = False) -> str:
    names = [name for name, _ in KINDS.values()]
    if not color:
        return "legend: " + " · ".join(names)
    return "legend: " + " · ".join(
        _paint(rgb, f"■ {name}") for name, rgb in KINDS.values()
    )


def pile_header(n: int) -> str:
    return f"the pile · {n} boxes on the record"


def human_line(text: str, color: bool = False) -> str:
    """The human's typed line: plain, marked ``you``. Not a box."""
    return f"{_paint((239, 230, 213), 'you', bold=True) if color else 'you'}: {text}"


def who_line(text: str, color: bool = False) -> str:
    line = f"agent · {text}"
    return _paint(FAINT, line) if color else line


def say_line(text: str, color: bool = False) -> str:
    return f"agent> {text}"


def clause(box: Box) -> str:
    if box.state != "populated":
        return f"{box.label} is {box.value}"
    if box.kind == "you":
        return f"{box.value} needs you"
    if box.kind == "block":
        return f"{box.value} is still blocked"
    return box.value


def compose(boxes: list[Box], first: bool = True) -> str:
    """One sentence from box facts and glue. Deterministic; no model."""
    if not boxes:
        return ""
    broken = any(b.state != "populated" for b in boxes)
    opener = "Heads up: " if broken else "Looks like " if first else "Oh, and "
    parts = [clause(b) for b in boxes]
    if len(parts) == 1:
        body = parts[0]
    elif len(parts) == 2:
        both = "both " if boxes[0].kind == boxes[1].kind and not broken else ""
        body = f"{both}{parts[0]} and {parts[1]}"
    else:
        body = ", ".join(parts[:-1]) + f" and {parts[-1]}"
    calm = not broken and not any(b.kind in ("you", "block") for b in boxes)
    return f"{opener}{body}.{' No rush.' if calm else ''}"
