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

After a reply the row of chips is built from the boxes just shown (``chips``):
a ``show me <ref>`` for the blocked box with a detail to open (else the first
populated box with one), where ``<ref>`` is a meaningful token (``ref_tokens``):
a number of two digits or more from its value, an id-like token (``PR 712``),
or its short box id (``b4``), never the first words of a value, and only if no
other shown box answers to it (no such token: no chip); the options of a needs-you
box whose detail splits on `` · `` into at least three short parts without a
digit (taken as the box says them, no more); and always ``later`` and
``thanks``. The row is capped at ``CHIP_CAP`` (choices are cut first, then the
``show me`` is left off when the choices fill the room). ``parse_follow`` reads
a typed line as a follow-up (``show me 712``, ``open 712``, a box id, ``the
second one``, ``that``, ``why``, ``go on``); the seat resolves it against the
last reply's boxes by fixed rules, in code.

A sentence lowercases a first word only when it is a known common word
(``lead``: ``STARTERS``, ``VERBS``), so a name keeps its capital; ``You need
to <verb>`` is said only of a value that starts with a task verb. A box's
``role`` (``draft``, ``more``, ``count``, set by the reader) decides how it is
said: a draft is ``X (draft) is waiting`` (a pair ``Both drafts are waiting:
X and Y``, never a bare list), a ``more`` box is a count apart (``10 more
sealed are in the store``), and neither the count nor a ``more`` box is ever a
``show me`` ref (``COUNTED``).

A count code says is pluralised (``plural``: ``1 box``, ``2 boxes``).
A sentence code ends is ended once (``terminate``): a quoted reason that ends
``."`` is not followed by a second full stop. ``why_sentence`` says the reason
of one box (the human's quoted words led by who said them, provenance dropped
with a ``(fixture)`` marker kept).

Color is gated on a tty and on ``NO_COLOR`` being unset. Anywhere else the
card is plain ASCII with no escape code.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from grove import onescript_reach

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


def one_script_module(name: str):
    """One of the one script's modules (``onescript.<name>``), from the
    willow-bot the seat reads (``$WILLOW_BOT_ROOT``, else the one reach's rule:
    ``$ONESCRIPT_HOME``, else beside this repo; flatten-2 F6.5). With none
    beside, the seat stops at import and says where it looked, in the reach's
    words."""
    got = os.environ.get("WILLOW_BOT_ROOT")
    home = Path(got).expanduser() / "one-script" if got else None
    try:
        return onescript_reach.module(name, home=home)
    except onescript_reach.Unreachable as e:
        raise ImportError(f"unreachable: {e}") from e


def _one_script_states():
    """The three states, once: willow-bot's ``onescript/states.py`` (flatten
    F5, F-18; the operator: "2 a")."""
    return one_script_module("states")


_states = _one_script_states()
STATES = _states.STATES
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
    #: What the box is, structurally, when its kind does not say: ``draft`` (a
    #: waiting draft, never a fact), ``more`` (a count of rows not shown) or
    #: ``count`` (the store's summary). Set by the reader that builds the box,
    #: never guessed from its words; ``""`` for every other box.
    role: str = ""


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
    state = _states.checked(box.state)
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
    return f"the pile · {plural(n, 'box', 'boxes')} on the record"


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
        why = (
            "(none quoted)"
            if name.startswith("your words")
            else "(code cite unchecked)"
        )
        chip = f"{mark} {name}" + (f" {why}" if st == "na" else "")
        if color and st != "na":
            chip = _paint(KINDS["pass"][1] if st is True else RUST, chip)
        chips.append(chip)
    return f"{prefix} " + " · ".join(chips)


#: A word or number that reads as a problem, so reassurance never follows it.
#: ``escalated N`` stays one for reassurance (no ``No rush.`` over it), but a
#: chain summary's count is not flagged ``Heads up:`` (``routine_count``): its
#: escalations have boxes of their own, which rank first and carry the flag.
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


#: Words a sentence may start with that lose their capital mid-sentence: a
#: closed list of common sentence-starters (never a name, so ``Tony`` stays
#: ``Tony``) and the task verbs a needs-you value may start with.
STARTERS = frozenset(
    "the a an this that these those it its both there here some one".split()
)
VERBS = frozenset(
    """add answer approve ask book call cancel check choose click close confirm
    create decide delete download email enter fix forward grant install join
    label merge move open pay phone pick pull push read reject reopen reply
    review rerun restart rotate run schedule seal send sign submit tell test
    unseal update upload verify write ratify""".split()
)


def lead(text: str) -> str:
    """Lowercase a sentence's first word only when it is a known common word
    (``STARTERS`` or ``VERBS``: Ratify, Phone, The), so a name (``Tony``), an
    acronym, a word with a digit and ``I`` keep their capital."""
    w = text.split(" ", 1)[0]
    if len(w) > 1 and w[0].isupper() and w[1:].isalpha() and w[1:].islower():
        if w.lower() in STARTERS | VERBS:
            return w[0].lower() + text[1:]
    return text


def is_verb_phrase(text: str) -> bool:
    """A value that starts with a known task verb, so ``You need to <it>``
    reads; a name, a count or a draft does not."""
    words = text.split()
    return len(words) > 1 and words[0].lower() in VERBS and lead(text) != text


def cap(text: str) -> str:
    return text[:1].upper() + text[1:]


#: A sentence already ends: ``.`` ``?`` ``!``, or one of those just inside a
#: closing quote or bracket (``..."``), which a human's quoted words may carry.
ENDED = re.compile(r"[.?!][\"”')\]]*$")


def terminate(text: str) -> str:
    """``text`` as a sentence: a full stop only if it does not already end in
    ``.``/``?``/``!`` (or one of them closed by a quote), so a quoted reason
    ending ``one."`` is never followed by a second ``.`` (``one.".``). The
    words inside the quotes are never touched."""
    text = text.rstrip()
    return text if not text or ENDED.search(text) else text + "."


#: A lore row's label (box-build R11/R12, W3a audit N9): one sealed world fact
#: as one box. The fact is the value, said as itself; where it belongs (the
#: scene) is the detail. Its id is the row's own (``r<n>``) or the served id.
LORE = "lore"


def lore_box(row: dict, bid: str) -> Box:
    """One ``lore`` record row (``fact``, ``where``) as a box. The fact is a
    served, human-sealed line and is said word for word; the box carries no
    status, so nothing about it reads as a problem or a task."""
    fact = " ".join(str(row.get("fact") or "").split())
    where = " ".join(str(row.get("where") or "").split())
    if not fact:
        return Box(bid, "pass", LORE, "empty — a lore row with no fact", state="empty")
    return Box(bid, "pass", LORE, fact, f"of {where}" if where else "")


def plural(n: int, one: str, many: str = "") -> str:
    """``n`` and its noun, pluralised: ``1 box``, ``2 boxes``, ``0 boxes``.
    ``many`` is the plural form when it is not ``one`` + ``s``."""
    return f"{n} {one if n == 1 else many or one + 's'}"


#: The record's own stamp, ``api._now()`` in willow-bot: UTC, whole seconds, and
#: the zone written out as a trailing ``Z`` (``2026-10-12T08:30:00Z``). Only
#: this exact form is read; any other shape (no ``Z``, an offset, a bare date,
#: not a string) is no date, never a guess.
SEAL_STAMP = "%Y-%m-%dT%H:%M:%SZ"
MONTHS = (
    "January February March April May June July "
    "August September October November December"
).split()


def sealed_on(stamp: object, today: date | None = None) -> str:
    """When the human sealed, said humanly, from ``api.resume``'s ``sealed_at``
    (the seal row's own stamp) and nothing else: ``earlier today`` when the
    stamp's date is ``today``, else ``on 12 October`` (``on 12 October 2025``
    when the year is not ``today``'s, or when ``today`` is not given). The stamp
    is UTC (its ``Z`` is explicit) and its date is read as written, not
    converted to a local zone; ``today`` is the UTC date and only chooses
    between "earlier today" and the date. A stamp in the future of ``today`` is
    said as its date. ``""`` for a missing or unreadable stamp: no date is
    invented."""
    if not isinstance(stamp, str):
        return ""
    try:
        day = datetime.strptime(stamp, SEAL_STAMP).date()
    except ValueError:
        return ""
    if today is not None and day == today:
        return "earlier today"
    named = f"{day.day} {MONTHS[day.month - 1]}"
    if today is None or day.year != today.year:
        named += f" {day.year}"
    return f"on {named}"


def opening(
    resume: tuple, pool: tuple, greet: str = "", today: date | None = None
) -> str:
    """The run's one opening sentence, from what ``api.resume`` and
    ``api.pooled`` already returned (no call of its own). ``resume`` is
    ``("sealed", subject, upto[, sealed_at])``, ``("none",)`` or
    ``("unreachable",)``; the subject is said in the short form the cards use
    (``short``: a 64-hex hash is its first twelve characters); ``pool`` is ``("populated", n)``, ``("empty",)`` or
    ``("unreachable",)``. Each state has its own clause, so an unreadable
    resume or pool is never said as "nothing to pick up". A sealed snapshot
    with a readable ``sealed_at`` names when it was sealed (``sealed_on``): "the
    snapshot you sealed on 12 October (serve:abc, rows up to 41)"; without one
    (an older willow-bot, or a stamp that doesn't read) it is the plain "the
    sealed snapshot serve:abc (rows up to 41)", no date. ``greet`` leads it,
    once per run."""
    if resume[0] == "sealed":
        when = sealed_on(resume[3], today) if len(resume) > 3 else ""
        if when:
            rows = f", rows up to {resume[2]}" if resume[2] is not None else ""
            head = f"Picking up from the snapshot you sealed {when} ({short(resume[1])}{rows})"
        else:
            upto = f" (rows up to {resume[2]})" if resume[2] is not None else ""
            head = f"Picking up from the sealed snapshot {short(resume[1])}{upto}"
    elif resume[0] == "none":
        head = "No snapshot has been sealed yet, so I'm scoping fresh"
    else:
        head = "I couldn't read the last sealed snapshot, so I'm scoping fresh"
    if pool[0] == "populated":
        tail = f"{plural(pool[1], 'proposal')} still pooled from earlier runs"
    elif pool[0] == "empty":
        tail = "nothing is pooled from earlier runs"
    else:
        tail = "I couldn't read the pool, so I can't say what is still pooled"
    text = terminate(f"{head}; {tail}")
    return f"{greet} {text}".strip() if greet else text


def carry_over(pool: tuple) -> str:
    """The closing sentence: what stays pooled for next time, from the pool
    ``api.pooled`` read at check-out. ``("populated", n)``, ``("empty",)`` or
    ``("unreachable",)``, each said differently."""
    if pool[0] == "populated":
        n = pool[1]
        return (
            f"{plural(n, 'proposal')} stay{'s' if n == 1 else ''} pooled for next time."
        )
    if pool[0] == "empty":
        return "Nothing stays pooled for next time."
    return "I couldn't read the pool, so I can't say what stays pooled for next time."


def bare(text: str) -> str:
    """``text`` without the one full stop ``terminate`` may have added."""
    return text[:-1] if text.endswith(".") else text


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
        return f"{CANT_READ}. {terminate(cap(reason))}" if reason else f"{CANT_READ}."
    if box.state == "empty":
        base = f"{cap(_val(box.label))} is empty"
        return terminate(f"{base}: {reason}") if reason else f"{base}."
    return ""


#: A detail line that only says where a box came from, not why: its origin, the
#: store-holds-fixture-rows note, or the count's "fiction, not a real trail".
PROVENANCE = re.compile(
    r"^(?:origin\b|fiction, not a real trail|.*\bthe store holds fixture rows\b)", re.I
)
#: A detail line that is not the reason and not fiction either: a record
#: proposal's ``own_idea:`` mark and the record count's own notes. The card keeps
#: them; ``why`` leaves them out and does not mark the box a fixture.
NOTE = re.compile(
    r"^(?:own_idea:|from the record's NEEDS YOU|no Nestor store is configured\b)",
    re.I,
)
#: Detail lines that name who decided (the speaker of a reason), by form.
SPEAKER_NO = re.compile(r"^a no from (?P<who>.+?)(?::|$)", re.I)
SPEAKER_BY = re.compile(r"^rejected by (?P<who>.+)$", re.I)
SPEAKER_SEAL = re.compile(r"^sealed by (?P<who>.+?)(?P<then>, then replaced)?$", re.I)
#: A reason line: ``reason: "her words"`` (quoted) or ``reason: empty_scope``.
REASON = re.compile(r"^reason(?P<when> then| now)?: (?P<text>.+)$", re.I)
QUOTED = re.compile(r'^"(?P<q>.*)"$', re.S)
NOBODY = "nobody"
FIXTURE_MARK = "(fixture)"


def why_sentence(box: Box) -> str:
    """``why`` over a populated box: the reason, said as a person would, from
    the box's own detail. ``""`` when the detail holds nothing but provenance.

    The human's own words (a ``reason: "..."`` line) are quoted exactly and led
    by who said them (``Nieves said no: "Not little."``, ``Nieves sealed it:
    "..."``, ``Nieves said not yet: "..."``); a reason with no quotes (a chain
    box's ``reason: empty_scope``) is ``Reason: empty_scope``; any other line is
    kept as the box has it. Provenance lines (origin, the fixture note) are not
    the reason and are left out of the sentence, but a box that carried one is
    still a fixture, so the sentence ends ``(fixture)``: fiction stays visible
    (the card keeps the lines). Never a doubled full stop."""
    lines = [" ".join(ln.split()) for ln in box.detail.split("\n") if ln.strip()]
    fixture = "(fixture" in box.label or any(PROVENANCE.match(ln) for ln in lines)
    head = ""
    rest: list[str] = []
    for ln in lines:
        m = SPEAKER_NO.match(ln) or SPEAKER_BY.match(ln) or SPEAKER_SEAL.match(ln)
        who = cap(m["who"]) if m and m["who"].lower() != NOBODY else ""
        if PROVENANCE.match(ln) or NOTE.match(ln):
            continue
        if SPEAKER_NO.match(ln):
            head = head or (f"{who} said no" if who else "A no")
        elif SPEAKER_BY.match(ln):
            head = head or (f"{who} said not yet" if who else "")
        elif SPEAKER_SEAL.match(ln):
            then = ", then it was replaced" if m["then"] else ""
            head = head or (f"{who} sealed it{then}" if who else "")
        else:
            rest.append(ln)
    out: list[str] = []
    voiced = False
    plain = any(REASON.match(ln) and not REASON.match(ln)["when"] for ln in rest)
    order = rest
    if head and plain:  # her words come right after who said them
        order = [ln for ln in rest if REASON.match(ln)] + [
            ln for ln in rest if not REASON.match(ln)
        ]
    for ln in order:
        m = REASON.match(ln)
        q = QUOTED.match(m["text"]) if m else None
        if m and q:
            key = "Reason" + (m["when"] or "").lower()
            if head and not voiced and not m["when"]:
                out.append(f'{head}: "{q["q"]}"')
                voiced = True
            else:
                out.append(f'{key}: "{q["q"]}"')
        elif m:
            out.append(f"Reason: {_val(m['text'])}")
        else:
            line = _val(ln).replace(" · ", ", ")
            if head.endswith("not yet") and line.lower().startswith("not yet, "):
                line = line[len("not yet, ") :]  # the head already said it
            out.append(cap(line))
    if head and not voiced:
        out.insert(0, head)
    if not out:
        return ""
    if fixture:
        out[-1] += f" {FIXTURE_MARK}"
    return " ".join(terminate(x) for x in out)


def _tail(box: Box) -> str:
    """The last ``·`` part of a one-line detail, if short enough to say."""
    detail = " ".join(box.detail.split())
    last = _val(detail.split(" · ")[-1]) if detail else ""
    limit = TAIL_WORDS.get(box.kind, 0)
    if not last or len(last.split()) > limit or last.lower() == _val(box.value).lower():
        return ""
    return last


#: The chain's summary value, ``answered N, escalated M``.
CHAIN_COUNT = re.compile(r"answered\s+(\d+),\s*escalated\s+(\d+)", re.I)
#: A needs-you value is a short phrase (``PR 712``) at most this many words,
#: with no ``: ; , ( )`` inside; "<value> needs you" is said only of one.
SHORT_YOU_WORDS = 6
INNER_PUNCT = re.compile(r"[:;,()]")


def routine_count(b: Box) -> bool:
    """The chain's own ``answered N, escalated M`` summary: a count, not a
    problem to flag. Its escalated pieces are boxes of their own."""
    return b.kind == "pass" and bool(CHAIN_COUNT.fullmatch(_val(b.value)))


def _fact(b: Box) -> str:
    """A box's value as a sentence part. The chain's ``answered N, escalated
    M`` said alone reads ``The chain answered N and escalated M`` (label, numbers
    and verbs from the box; ``The`` and ``and`` are fixed words), never a bare
    count; any other value is itself. The seat gives that summary ``role="count"``,
    so it is always said alone, never in a pair or a list."""
    v = _val(b.value)
    m = CHAIN_COUNT.fullmatch(v)
    if m and b.kind == "pass" and len(_val(b.label).split()) == 1:
        return f"The {_val(b.label)} answered {m[1]} and escalated {m[2]}"
    return v


def _single(b: Box) -> list[Part]:
    v = _val(b.value)
    tail = _tail(b)
    if b.role == "more":  # a count of rows not shown, never a decided/changed item
        return [(f"{v} {'is' if v.startswith('1 ') else 'are'} in the store", b.id)]
    if b.role == "draft":  # a draft is never a fact, nor a task to "do"
        return [(f"{v} is waiting{' on you' if b.kind == 'you' else ''}", b.id)]
    if b.kind == "you":
        words = v.split()
        if is_verb_phrase(v):
            return [(f"You need to {lead(v)}", b.id)]
        if len(words) > SHORT_YOU_WORDS or INNER_PUNCT.search(v):
            return [("This needs you: ", None), (v, b.id)]  # no dangling suffix
        return [(f"{v} needs you", b.id)]
    if b.kind == "block":
        m = STATUS.match(v)
        body = (
            f"{m['head']}'s still {m['st'].lower()}" if m else f"{v} is still blocked"
        )
        return [(f"{body}, {tail}" if tail else body, b.id)]
    if b.kind == "dec":
        return [(f"{v} is decided and {tail}" if tail else f"{v} is decided", b.id)]
    return [(_fact(b), b.id)]


def clause(box: Box) -> str:
    """One box as the phrase code says it, from its own facts and glue."""
    if box.state != "populated":
        return bare(plain_line(box))
    return "".join(t for t, _ in _single(box))


#: The neutral verb a pair or a run of three or more says when its values share
#: no word. One source: ``BOTH`` (you, block, dec) covers the pressing kinds,
#: this the changed and routine ones, and a pair reads it too.
RUN_VERB = {"dec": "decided", "pr": "changed", "pass": "routine"}


#: The closed set of words a shared last word may be said as a verb. Only a
#: genuine status reads right ("PR 1 and PR 2 are both open"); free text that
#: happens to end alike ("local: a short answer", "local: another answer")
#: does not, and takes the kind's fixed word. From the sketches' PR lines
#: (``box-stream-v1.3``: open, waiting, "tests pass"), ``STATUS`` above
#: (waiting, blocked, stuck, held, pending), the box labels (``KINDS``,
#: ``seat_nestor``: changed, retired, decided, sealed, blocked), and the plain
#: states a PR or a check is in (merged, closed, failed, passed, green, red,
#: done, ready).
STATUS_WORDS = frozenset(
    "open merged closed blocked waiting pending stuck held failed passed "
    "green red done ready sealed decided changed retired".split()
)


def _shared_status(words: list[list[str]]) -> str:
    """The last word every value shares, if it is a status word, else ``""``.
    One rule for a pair and a run."""
    last = words[0][-1].lower() if words[0] else ""
    if last in STATUS_WORDS and all(
        len(w) > 1 and w[-1].lower() == last for w in words
    ):
        return words[0][-1]
    return ""


def _pair(a: Box, b: Box) -> list[Part]:
    """Two boxes of one kind in one phrase, with ``both``: ``are both <word>``
    where the word is the last word the values share when it is a status word
    (``STATUS_WORDS``; "answer" or "rows" is not one), else the kind's fixed
    word (``BOTH``, else ``RUN_VERB``: changed, routine). A pair always ends
    with a verb; only a kind with no fixed word at all keeps a leading
    ``both``."""
    va, vb = _val(a.value), _val(b.value)
    if a.role == "draft" and a.kind != "you":
        return [
            ("Both drafts are waiting: ", None),
            (va, a.id),
            (" and ", None),
            (vb, b.id),
        ]
    if a.kind == "you":
        return [
            ("Both need you: ", None),
            (lead(va), a.id),
            (" and ", None),
            (lead(vb), b.id),
        ]
    wa, wb = va.split(), vb.split()
    word = _shared_status([wa, wb])
    if word:
        return [
            (" ".join(wa[:-1]), a.id),
            (" and ", None),
            (" ".join(wb[:-1]), b.id),
            (f" are both {word}", None),
        ]
    verb = BOTH.get(a.kind) or RUN_VERB.get(a.kind)
    if verb:
        return [(va, a.id), (" and ", None), (vb, b.id), (f" are both {verb}", None)]
    return [("both ", None), (va, a.id), (" and ", None), (vb, b.id)]


def _run(group: list[Box]) -> list[Part]:
    """A run of one kind: one box, a pair, or (decided, changed, pass) a list.
    A list of three or more ends with a verb, as a pair does: ``are all <word>``
    where the word is the last word every value shares when it is a status word
    (``STATUS_WORDS``: ``PR 1, PR 2 and PR 3 are all open``), else the kind's fixed word (``RUN_VERB``: decided, changed,
    routine). A draft run says ``The drafts are waiting:`` instead."""
    if len(group) == 1:
        return _single(group[0])
    if len(group) == 2:
        return _pair(*group)
    parts: list[Part] = []
    draft = group[0].role == "draft"
    vals = [_val(b.value) for b in group]
    end = RUN_VERB.get(group[0].kind, "") if not draft else ""
    if group[0].kind != "dec" and not draft:
        words = [v.split() for v in vals]
        last = _shared_status(words)
        if last:
            vals, end = [" ".join(w[:-1]) for w in words], last
    if draft:
        parts.append(("The drafts are waiting: ", None))
    for i, b in enumerate(group):
        sep = ", " if i < len(group) - 2 else " and "
        parts += [(vals[i], b.id)] + ([(sep, None)] if i < len(group) - 1 else [])
    if end:
        parts.append((f" are all {end}", None))
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
    rush: bool = True,
    look: bool = True,
) -> str:
    """One reply's sentence from box facts and glue. Deterministic; no model.

    A short sentence per box, in the order given (``rank`` puts the pressing
    ones first): ``You need to ratify the work order. PR 712's still waiting,
    126 tests pass.`` Decided, changed and routine boxes share one
    ``;``-joined sentence, two of a kind say ``both`` and three or more end
    ``are all <word>`` (``_run``). ``greet`` opens it
    (``Morning.``); a page after the first opens ``Oh, and`` (the second) or
    ``Also,`` (later); ``Looks like`` opens a first page that is all routine;
    ``Heads up:`` precedes a problem or an unreachable box, whose plain line
    (``I can't read the record right now. <why>.``) is fixed code words; and
    ``No rush.`` ends a reply only when nothing needs the human, blocks, or
    went wrong, and only once per turn (``rush=False`` leaves it off a later
    page). ``cite=True`` tags each fact with its box ``[id]`` the way a
    model sentence is tagged, so the checks can be run over it. ``look=False``
    leaves ``Looks like`` off a first page that is all routine (a count that
    orients the reply is said as itself)."""
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
            line = bare(plain_line(b))
            parts = [(line, b.id)] if line else []
            sents.append((parts, "heads" if b.state == "unreachable" else "plain"))
            i += 1
            continue
        j = i
        while (
            j < len(boxes)
            and boxes[j].state == "populated"
            and (boxes[j].kind, boxes[j].role == "draft") == (b.kind, b.role == "draft")
            and not {"more", "count"} & {b.role, boxes[j].role}
        ):
            j += 1
        j = max(j, i + 1)
        group = boxes[i:j]
        i = j
        if b.role in ("more", "count") or (
            b.kind in ("you", "block") and len(group) > 2
        ):
            sents += [(_single(g), "hard") for g in group]
        else:
            soft = b.kind not in ("you", "block") and b.role not in ("draft", "count")
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
            b.id in {i for _, i in parts if i} and problem(b) and not routine_count(b)
            for b in boxes
            if b.state == "populated"
        )
        if hot and not flagged and parts:
            parts = [("Heads up: ", None), (lead(parts[0][0]), parts[0][1]), *parts[1:]]
            flagged = True
        out.append(parts)
        hot_at.append(hot)
    calm = (
        not broken
        and not bad
        and not any(b.kind in ("you", "block") or b.role == "draft" for b in boxes)
    )
    kinds_ok = all(b.kind in ("dec", "pr", "pass") for b in boxes)
    prefix = ""
    if page > 0:
        prefix = "Oh, and " if page == 1 else "Also, "
    elif calm and kinds_ok and look:
        prefix = "Looks like "
    if prefix:
        for n, parts in enumerate(out):
            if parts and folded[n][1] in ("soft", "hard") and not hot_at[n]:
                out[n] = [(prefix, None), (lead(parts[0][0]), parts[0][1]), *parts[1:]]
                break
    text = " ".join(terminate(cap(_render(p, cite))) for p in out if p)
    if greet:
        text = f"{greet} {text}".strip()
    return f"{text} No rush." if calm and text and rush else text


# --- chips and follow-ups ------------------------------------------------------

#: The most chips one row carries, ``later`` and ``thanks`` included.
CHIP_CAP = 6
#: A needs-you box's detail reads as options when it splits on `` · `` into at
#: least this many short, digit-free parts (two parts are ambiguous with a
#: plain ``fact · fact`` detail, so they are not taken as a question).
OPTION_MIN = 3
OPTION_WORDS = 4
LATER, THANKS = "later", "thanks"
NUMBER = re.compile(r"\d+(?:\.\d+)*")
WORD = re.compile(r"[^\W_]+(?:['’.-][^\W_]+)*")
_UNSAFE = re.compile(r"[\[\]\x00-\x1f\x7f]")
ORDINALS = {
    "first": 0,
    "1st": 0,
    "second": 1,
    "2nd": 1,
    "third": 2,
    "3rd": 2,
    "fourth": 3,
    "4th": 3,
}
MORE_WORDS = frozenset({"go on", "more", "next"})
WHY_WORDS = frozenset({"why", "what's that", "whats that", "tell me more"})
THAT_WORDS = frozenset({"that", "that one"})
SHOW = re.compile(r"(?:show me|show|open)\s+(.+)")
ORDINAL = re.compile(r"(?:the\s+)?(" + "|".join(ORDINALS) + r")(?:\s+one)?")


@dataclass
class Chips:
    """The chip row after a reply: an optional ``show me <ref>``, the choices a
    needs-you box carries, then always ``later`` and ``thanks``."""

    show: str = ""
    choices: list[str] = field(default_factory=list)

    def labels(self) -> list[str]:
        return [*([self.show] if self.show else []), *self.choices, LATER, THANKS]

    def row(self) -> str:
        return "chips: " + " ".join(f"[{c}]" for c in self.labels())


#: Roles that are a count of things, not a thing: never a ``show me`` ref.
COUNTED = ("count", "more")


def _label(text: str) -> str:
    return _UNSAFE.sub("", _val(text)).strip()


def _words(text: str) -> list[str]:
    return [w.lower() for w in WORD.findall(str(text))]


def options(box: Box) -> list[str]:
    """The options a populated needs-you box carries, only as its own one-line
    detail says them: split on `` · ``, at least ``OPTION_MIN`` parts, each at
    most ``OPTION_WORDS`` words and without a digit. ``[]`` otherwise."""
    detail = box.detail.strip()
    if box.state != "populated" or box.kind != "you" or not detail or "\n" in detail:
        return []
    parts = [_label(p) for p in detail.split(" · ")]
    if len(parts) < OPTION_MIN or not all(parts):
        return []
    if any(len(p.split()) > OPTION_WORDS or any(c.isdigit() for c in p) for p in parts):
        return []
    seen: set[str] = set()
    out = []
    for p in parts:
        if p.lower() not in seen | {LATER, THANKS}:
            seen.add(p.lower())
            out.append(p)
    return out


def matches(box: Box, text: str) -> bool:
    """Does ``text`` name this box: its id, a number in its value, or the whole
    words its value starts with."""
    want = " ".join(_words(text))
    if not want:
        return False
    if box.role in COUNTED:  # a count names no item: only its own id opens it
        return want == box.id.lower()
    ids = {" ".join(_words(m)) for m in ID_TOKEN.findall(str(box.value))}
    if want == box.id.lower() or want in NUMBER.findall(str(box.value)) or want in ids:
        return True
    value = " ".join(_words(box.value))
    return value == want or value.startswith(want + " ")


#: A number a ref may be: two digits or more, not part of a dotted version, a
#: hash or a word (``126`` yes; ``7``, ``0.16.10``, ``7476c13`` no).
REF_NUMBER = re.compile(r"(?<![\w.])\d{2,}(?![\w]|\.\d)")
#: An id-like token: letters, a space or dash, then a number (``PR 712``,
#: ``ABC-123``).
ID_TOKEN = re.compile(r"\b[A-Za-z]{1,6}[ -]#?\d{2,}\b(?![\w.]\w)")
#: A box id short enough to type (``b4``, ``c1``); a hash id is not one.
SHORT_ID = re.compile(r"[A-Za-z]\d{1,3}")


def ref_tokens(box: Box) -> list[str]:
    """What a ``show me`` ref may be, in order: a number of two digits or more
    from the value (``712``), an id-like token from it (``PR 712``), then the
    box's own short id (``b4``). Never the first words of a value. ``[]`` when
    the box has none."""
    if box.role in COUNTED:
        return []
    value = str(box.value)
    out = REF_NUMBER.findall(value) + ID_TOKEN.findall(value)
    if SHORT_ID.fullmatch(box.id):
        out.append(box.id)
    return list(dict.fromkeys(out))


def unique_ref(box: Box, boxes: list[Box]) -> str:
    """A ref only this box answers to (``ref_tokens``, the first that no other
    shown box answers to). ``""`` when none is unique: no ``show me`` chip."""
    for c in ref_tokens(box):
        if [b for b in boxes if matches(b, c)] == [box]:
            return _label(c)
    return ""


def chips(boxes: list[Box]) -> Chips:
    """The chip row for the boxes a turn showed. Choices come from the first
    needs-you box that carries options (``options``), capped so the row stays
    within ``CHIP_CAP`` with ``later`` and ``thanks``. A ``show me <ref>`` chip
    follows only if the row has room: the blocked box with a detail to open,
    else the first populated box with one, whose ref is unique among the
    boxes."""
    room = CHIP_CAP - 2
    got: list[str] = []
    for b in boxes:
        got = options(b)
        if got:
            break
    out = Chips(choices=got[:room])
    if len(out.choices) < room:
        order = sorted(
            (
                b
                for b in boxes
                if b.state == "populated"
                and b.detail
                and not options(b)
                and b.role not in COUNTED
            ),
            key=lambda b: b.kind != "block",  # stable: rank order within
        )
        for b in order:
            ref = unique_ref(b, boxes)
            if ref:
                out.show = f"show me {ref}"
                break
    return out


def _fold(text: str) -> str:
    t = " ".join(str(text).lower().replace("’", "'").split())
    return t.rstrip("?!. ")


#: Most words a ``show me`` target may have and still read as a reference.
REF_WORDS = 2
#: A numbered reference with up to two words before it (``pr 712``, ``#714``,
#: ``abc-123``, ``pull request #714``) or an ordinal figure (``the 5th one``).
NUMBERED = re.compile(
    r"(?:[a-z]+[ -]){0,2}#?\d[\w.-]*|(?:the\s+)?\d+(?:st|nd|rd|th)(?:\s+one)?"
)


def looks_like_ref(target: str) -> bool:
    """Whether the text after ``show me`` / ``open`` reads as a reference to
    something shown, not a task. A reference is the whole target being a number
    or an id-like token (``NUMBERED``: ``14``, ``PR 712``, ``#714``,
    ``ABC-123``, ``n4ee2a``, ``pull request #714``, ``the 5th one``), an
    ordinal (``ORDINAL``), or a short phrase of at most ``REF_WORDS`` words
    (``the stack``). Anything longer (``the tests that failed``) reads as a
    task, even if a number is in it. Deterministic; only the words decide."""
    t = _fold(target)
    return bool(
        t
        and (
            len(t.split()) <= REF_WORDS or NUMBERED.fullmatch(t) or ORDINAL.fullmatch(t)
        )
    )


def parse_follow(line: str) -> tuple[str, str, bool] | None:
    """A typed line read as a follow-up: ``(kind, arg, prefixed)`` or None.
    Kinds: ``more``, ``why``, ``that``, ``ord`` (arg the 0-based index) and
    ``ref`` (arg the text after ``show me`` / ``open``; a bare line is a ref
    only when ``prefixed`` is False and it later matches a box id)."""
    t = _fold(line)
    if t in MORE_WORDS:
        return ("more", "", False)
    if t in WHY_WORDS:
        return ("why", "", False)
    m = SHOW.fullmatch(t)
    inner, prefixed = (m[1], True) if m else (t, False)
    o = ORDINAL.fullmatch(inner)
    if o:
        return ("ord", str(ORDINALS[o[1]]), prefixed)
    if inner in THAT_WORDS:
        return ("that", "", prefixed)
    return ("ref", inner, prefixed) if inner else None
