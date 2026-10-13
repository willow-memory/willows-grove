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

A reply's boxes are ranked (``rank``): a heads-up (``empty``/``unreachable``)
first, then needs you, blocked, decided, changed, routine pass, stable within
a kind. ``compose`` says them in short sentences, one phrasing per kind, built
only from the box's label, value and detail plus the glue list; an
``unreachable`` or ``empty`` box also gets a plain line in words
(``plain_line``), apart from its card. Those fixed lines are code's own words,
not glue, as in the sketch's code-only unreachable reply; the model is never
asked to say them and they are not run through the four checks.

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
RUST = (217, 100, 92)  # --rust: a failed check
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


def struck_line(text: str, color: bool = False) -> str:
    """A sentence a check failed: struck through, and marked in words so the
    plain path (no color, no escape code) still tells it from a standing one."""
    body = f"~~{text}~~"
    if color:
        body = f"\x1b[9;2m{body}{RESET}"
    return f"agent> {body} [struck]"


def checks_line(results: list, names: tuple[str, ...], prefix: str, color: bool) -> str:
    """The four check chips: ``✓`` passed, ``✗`` failed, ``–`` none to check."""
    chips = []
    for name, st in zip(names, results, strict=True):
        mark = "✓" if st is True else "✗" if st is False else "–"
        chip = f"{mark} {name}" + (" (none quoted)" if st == "na" else "")
        if color and st != "na":
            chip = _paint(KINDS["pass"][1] if st is True else RUST, chip)
        chips.append(chip)
    return f"{prefix} " + " · ".join(chips)


#: A word or number that reads as a problem, so reassurance never follows it.
PROBLEM = re.compile(
    r"\b(?:escalated|refused|failed|errors?|problems?|denied|stuck)\b\W{0,3}[1-9]\d*"
    r"|\b[1-9]\d*\s+(?:escalated|refused|failed|errors?|problems?|denied)\b"
    r"|\b(?:refused|failed|error|unreachable|denied|hard[- ]closed?|non[- ]?zero)\b",
    re.I,
)


def problem(box: Box) -> bool:
    """A box that carries something non-ideal, by what it says, not its kind."""
    return bool(PROBLEM.search(f"{box.label} {box.value} {box.detail}"))


#: Reply order, most pressing first: needs you, blocked, decided, changed, then
#: the routine pass (the web sketch's priority, ``box-stream-v1.3.html``).
PRIORITY = ("you", "block", "dec", "pr", "pass")
#: ``Part``: a run of the sentence and the box id it cites (None: glue).
Part = tuple[str, "str | None"]
STATE_PREFIX = re.compile(r"^(?:unreachable|empty)\s*[—–-]+\s*", re.I)
#: A block's value ending in one of these reads "<head>'s still <status>".
STATUS = re.compile(
    r"^(?P<head>.+?)\s+(?P<st>waiting|blocked|stuck|held|pending)$", re.I
)
#: The adjective a same-kind pair falls back to when its values share no word.
BOTH = {"you": "need you", "block": "still blocked", "dec": "decided"}
TAIL_WORDS = {"block": 6, "dec": 2}
#: Said when the record can't be read: fixed code words, as in the sketch's
#: unreachable scene. Only the why after it comes from a box.
CANT_READ = "I can't read the record right now"


def rank(boxes: list[Box]) -> list[Box]:
    """Boxes in reply order: a heads-up (an ``empty`` or ``unreachable`` box)
    first, then needs you, blocked, decided, changed, routine pass. Stable:
    boxes of one kind keep the order they came in. A kind not in the list
    sorts after the routine pass."""

    def key(b: Box) -> int:
        if b.state != "populated":
            return -1
        return PRIORITY.index(b.kind) if b.kind in PRIORITY else len(PRIORITY)

    return sorted(boxes, key=key)


def _val(text: str) -> str:
    """A box field as a sentence reads it: one line, hashes short, no full stop."""
    return short(" ".join(str(text).split())).rstrip(".")


def lead(text: str) -> str:
    """Lowercase a sentence's first word when it is only capitalized (Ratify,
    Phone), never an acronym, a name with a digit, or ``I``."""
    w = text.split(" ", 1)[0]
    if len(w) > 1 and w[0].isupper() and w[1:].isalpha() and w[1:].islower():
        return w[0].lower() + text[1:]
    return text


def cap(text: str) -> str:
    return text[:1].upper() + text[1:]


def why(box: Box) -> str:
    """The reason a non-populated box gives: its value without the state word."""
    v = _val(box.value)
    got = STATE_PREFIX.sub("", v).strip()
    return "" if got.lower() in ("unreachable", "empty") else got


def plain_line(box: Box) -> str:
    """The plain sentence for an ``empty`` or ``unreachable`` box (the sketch's
    ``I can't read the record right now. <why>.``): fixed code words, the
    reason from the box. Populated: ``""``."""
    reason = why(box)
    if box.state == "unreachable":
        return f"{CANT_READ}. {cap(reason)}." if reason else f"{CANT_READ}."
    if box.state == "empty":
        base = f"{cap(_val(box.label))} is empty"
        return f"{base}: {reason}." if reason else f"{base}."
    return ""


def _tail(box: Box) -> str:
    """The last ``·`` part of a one-line detail, if short enough to say."""
    detail = " ".join(box.detail.split())
    last = _val(detail.split(" · ")[-1]) if detail else ""
    limit = TAIL_WORDS.get(box.kind, 0)
    if not last or len(last.split()) > limit or last.lower() == _val(box.value).lower():
        return ""
    return last


def _single(b: Box) -> list[Part]:
    v = _val(b.value)
    tail = _tail(b)
    if b.kind == "you":
        words = v.split()
        if len(words) > 1 and lead(v) != v:
            return [(f"You need to {lead(v)}", b.id)]
        return [(f"{v} needs you", b.id)]
    if b.kind == "block":
        m = STATUS.match(v)
        body = (
            f"{m['head']}'s still {m['st'].lower()}" if m else f"{v} is still blocked"
        )
        return [(f"{body}, {tail}" if tail else body, b.id)]
    if b.kind == "dec":
        return [(f"{v} is decided and {tail}" if tail else f"{v} is decided", b.id)]
    return [(v, b.id)]


def clause(box: Box) -> str:
    """One box as the phrase code says it, from its own facts and glue."""
    if box.state != "populated":
        return plain_line(box).rstrip(".")
    return "".join(t for t, _ in _single(box))


def _pair(a: Box, b: Box) -> list[Part]:
    """Two boxes of one kind in one phrase, with ``both``."""
    va, vb = _val(a.value), _val(b.value)
    if a.kind == "you":
        return [
            ("Both need you: ", None),
            (lead(va), a.id),
            (" and ", None),
            (lead(vb), b.id),
        ]
    wa, wb = va.split(), vb.split()
    share = len(wa) > 1 and len(wb) > 1 and wa[-1].lower() == wb[-1].lower()
    if share and wa[-1].isalpha() and len(wa[-1]) > 2:
        return [
            (" ".join(wa[:-1]), a.id),
            (" and ", None),
            (" ".join(wb[:-1]), b.id),
            (f" are both {wa[-1]}", None),
        ]
    if a.kind in BOTH:
        return [
            (va, a.id),
            (" and ", None),
            (vb, b.id),
            (f" are both {BOTH[a.kind]}", None),
        ]
    return [("both ", None), (va, a.id), (" and ", None), (vb, b.id)]


def _run(group: list[Box]) -> list[Part]:
    """A run of one kind: one box, a pair, or (decided, changed, pass) a list."""
    if len(group) == 1:
        return _single(group[0])
    if len(group) == 2:
        return _pair(*group)
    parts: list[Part] = []
    for i, b in enumerate(group):
        sep = ", " if i < len(group) - 2 else " and "
        parts += [(_val(b.value), b.id)] + ([(sep, None)] if i < len(group) - 1 else [])
    return parts


def _render(parts: list[Part], cite: bool) -> str:
    return "".join(f"{t} [{i}]" if cite and i else t for t, i in parts)


def compose(
    boxes: list[Box],
    first: bool = True,
    *,
    page: int | None = None,
    greet: str = "",
    cite: bool = False,
) -> str:
    """One reply's sentence from box facts and glue. Deterministic; no model.

    A short sentence per box, in the order given (``rank`` puts the pressing
    ones first): ``You need to ratify the work order. PR 712's still waiting,
    126 tests pass.`` Decided, changed and routine boxes share one
    ``;``-joined sentence, and two of a kind say ``both``. ``greet`` opens it
    (``Morning.``); a page after the first opens ``Oh, and`` (the second) or
    ``Also,`` (later); ``Looks like`` opens a first page that is all routine;
    ``Heads up:`` precedes a problem or an unreachable box, whose plain line
    (``I can't read the record right now. <why>.``) is fixed code words; and
    ``No rush.`` ends a reply only when nothing needs the human, blocks, or
    went wrong. ``cite=True`` tags each fact with its box ``[id]`` the way a
    model sentence is tagged, so the checks can be run over it."""
    if not boxes:
        return ""
    page = (0 if first else 1) if page is None else page
    broken = any(b.state != "populated" for b in boxes)
    bad = any(b.state == "populated" and problem(b) for b in boxes)
    sents: list[tuple[list[Part], str]] = []  # (parts, kind: heads | soft | hard)
    i = 0
    while i < len(boxes):
        b = boxes[i]
        if b.state != "populated":
            line = plain_line(b)[:-1]
            parts = [(line, b.id)] if line else []
            sents.append((parts, "heads" if b.state == "unreachable" else "plain"))
            i += 1
            continue
        j = i
        while (
            j < len(boxes) and boxes[j].state == "populated" and boxes[j].kind == b.kind
        ):
            j += 1
        group = boxes[i:j]
        i = j
        if b.kind in ("you", "block") and len(group) > 2:
            sents += [(_single(g), "hard") for g in group]
        else:
            soft = b.kind not in ("you", "block")
            sents.append((_run(group), "soft" if soft else "hard"))
    # fold neighbouring soft sentences into one, joined by "; "
    folded: list[tuple[list[Part], str]] = []
    for parts, kind in sents:
        if kind == "soft" and folded and folded[-1][1] == "soft":
            prev = folded[-1][0]
            folded[-1] = (
                prev + [("; ", None)] + [(lead(parts[0][0]), parts[0][1])] + parts[1:],
                "soft",
            )
        else:
            folded.append((parts, kind))
    # a problem box gets heads up, once
    flagged = False
    out: list[list[Part]] = []
    hot_at: list[bool] = []
    for parts, kind in folded:
        hot = kind == "heads" or any(
            b.id in {i for _, i in parts if i} and problem(b)
            for b in boxes
            if b.state == "populated"
        )
        if hot and not flagged and parts:
            parts = [("Heads up: ", None), (lead(parts[0][0]), parts[0][1]), *parts[1:]]
            flagged = True
        out.append(parts)
        hot_at.append(hot)
    calm = not broken and not bad and not any(b.kind in ("you", "block") for b in boxes)
    kinds_ok = all(b.kind in ("dec", "pr", "pass") for b in boxes)
    prefix = ""
    if page > 0:
        prefix = "Oh, and " if page == 1 else "Also, "
    elif calm and kinds_ok:
        prefix = "Looks like "
    if prefix:
        for n, parts in enumerate(out):
            if parts and folded[n][1] in ("soft", "hard") and not hot_at[n]:
                out[n] = [(prefix, None), (lead(parts[0][0]), parts[0][1]), *parts[1:]]
                break
    body = ". ".join(cap(_render(p, cite)) for p in out if p)
    text = f"{body}." if body else ""
    if greet:
        text = f"{greet} {text}".strip()
    return f"{text} No rush." if calm and text else text
