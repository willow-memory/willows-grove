# b17: GRSRC ΔΣ=42
"""The seat answers "what is on the table?" from what it already has.

Two sources, each read-only, each in its own state, merged into one box list:

    the record   ``api.needs`` (willow-bot's one script): the lines of the
                 morning screen's ``NEEDS YOU`` section, drawn from the record
                 the way check-out draws them, without checking out. It writes
                 the one ``invocation`` row every api read writes (as
                 ``api.resume`` and ``api.pooled`` do) and nothing else: no
                 ``reconcile`` row, the run stays open. Always asked.
    Nestor       ``grove/seat_nestor.py``, the store at ``WILLOW_NESTOR_DB``, only
                 when one is configured.

Three states each, never collapsed (INVARIANTS.md section 1):

    populated    a count box (``role="count"``, said on its own) and one
                 ``needs you`` box per line, nothing cut: the pages are the
                 seat's usual ``more?``.
    empty        the record was read and nothing waits on the human. One
                 ``empty`` box, said in its plain line.
    unreachable  ``api.needs`` raised, refused, or does not exist (an older
                 willow-bot), or answered something that is not a list of lines.
                 One ``unreachable`` box with the reason.

A Nestor store that is *not configured* is not a failed read: when the record
answered (``populated`` or ``empty``) it adds no box and the first record box
says, in its detail, that only the record was read. It is ``unreachable`` only
when it is configured and cannot be read, or when the record could not answer
either (so the turn is never left saying nothing).

A box's fields are the record line's own parts, re-laid and never reworded:
``proposal · own_idea: no · PATH · VERDICT[ · REASON]`` is a ``proposal`` box
(value ``proposal PATH: VERDICT``, detail ``own_idea: no`` and
``reason: REASON``), ``re-check row N (KIND) · WHY`` is a ``re-check`` box (value
``re-check row N (KIND)``, detail WHY), and any other line is a ``record`` box whose value is the line.

Which lines are a status question (``status_kind``): the line, lower-cased,
without its apostrophes, a closing ``?!.``, a leading ``please``/``ok``/``so``
and a trailing ``please``/``today``/``now``/``right now``/``this morning``,
with ``what is`` read as ``whats``, must equal one of ``STATUS_PHRASES`` or
``WHERE_PHRASES`` exactly. No substring match, no fuzzy match, no model: a line
that merely contains such a phrase ("what is on the table in table 3 of the
file") is a task for the chain. The rule is deterministic (95% that it does what
this paragraph says); the phrase list is a guess at how the human asks (70%).
"""

from __future__ import annotations

import hashlib
import re

from grove.seat_boxes import Box, plural
from grove.seat_nestor import Reading, _clean

#: Asked whole: the store's whole state (when one is configured) and the record.
WHERE_PHRASES = frozenset(
    {
        "where are we",
        "where am i",
        "where do we stand",
        "whats waiting",
        "status",
        "whats the status",
        "give me the status",
    }
)
#: Asked as what waits on the human: the record's needs-you lines, and the
#: Nestor store's waiting drafts. (``what is`` is read as ``whats``.)
STATUS_PHRASES = frozenset(
    {
        # the table
        "whats on the table",
        "whats on my table",
        "whats on the table for me",
        "whats on my plate",
        # what is next
        "whats next",
        "what next",
        "whats up next",
        "whats my next task",
        "whats the next task",
        "whats my next step",
        "whats the next step",
        "my next task",
        "next task",
        # what to do
        "what do i need to do",
        "what do i have to do",
        "what do i do next",
        "what should i do",
        "what should i do next",
        "what do you need from me",
        # what waits
        "what needs me",
        "what needs you",
        "what needs my attention",
        "what needs doing",
        "what needs to be done",
        "what needs a decision",
        "whats waiting on me",
        "whats waiting for me",
        "whats open",
        "whats pending",
        "whats outstanding",
        "whats left",
        "whats left to do",
        "anything waiting",
        "anything waiting on me",
        "anything for me",
    }
)
_LEAD = ("please ", "ok ", "okay ", "so ", "hey ", "and ")
_TRAIL = (
    " right now",
    " this morning",
    " for today",
    " please",
    " today",
    " now",
)


def _key(text: str) -> str:
    t = " ".join(str(text).lower().split())
    t = t.replace("'", "").replace("’", "").rstrip("?!. ")
    for _ in range(3):  # a few fillers may stack: "ok so what is next, please"
        before = t
        for w in _LEAD:
            if t.startswith(w):
                t = t[len(w) :]
        for w in _TRAIL:
            if t.endswith(w):
                t = t[: -len(w)].rstrip(" ,")
        if t == before:
            break
    return t.replace("what is ", "whats ", 1) if t.startswith("what is ") else t


def status_kind(text: str) -> str | None:
    """``"where"`` (the whole state), ``"needs"`` (what waits on the human) or
    ``None`` (not a status question: a task, or something else the seat knows)."""
    k = _key(text)
    if k in WHERE_PHRASES:
        return "where"
    return "needs" if k in STATUS_PHRASES else None


def _gone(state: str, why: str) -> Reading:
    value = f"empty — {why}" if state == "empty" else f"unreachable — {why}"
    return Reading(state, why, [Box("rstate", "pass", "record", value, state=state)])


def _bid(line: str, seen: set[str]) -> str:
    digest = hashlib.sha1(line.encode()).hexdigest()
    for n in range(5, len(digest)):
        bid = "r" + digest[:n]
        if bid not in seen:
            seen.add(bid)
            return bid
    raise AssertionError("unreachable: sha1 prefixes exhausted")


PROPOSAL = "proposal · "
RECHECK = re.compile(r"re-check (?P<row>row \d+ \([^)]*\)) · (?P<why>.+)", re.S)


def item_box(line: str, seen: set[str]) -> Box:
    """One NEEDS YOU line as a ``needs you`` box: its own parts, re-laid."""
    bid = _bid(line, seen)
    if line.startswith(PROPOSAL):
        parts = line[len(PROPOSAL) :].split(" · ")
        if len(parts) >= 3 and parts[0].startswith("own_idea:"):
            detail = parts[0]
            if len(parts) > 3:
                detail += "\nreason: " + " · ".join(parts[3:])
            return Box(
                bid, "you", "proposal", f"proposal {parts[1]}: {parts[2]}", detail
            )
    m = RECHECK.fullmatch(line)
    if m:
        return Box(bid, "you", "re-check", f"re-check {m['row']}", m["why"])
    return Box(bid, "you", "record", line)


def _counts(items: list[Box]) -> str:
    names = {"proposal": "proposal", "re-check": "re-check", "record": "other"}
    out = []
    for label in names:
        n = sum(b.label == label for b in items)
        if n:
            out.append(plural(n, names[label]))
    return ", ".join(out)


def read_needs(api: object, cfg: object) -> Reading:
    """The record's NEEDS YOU as boxes, by ``api.needs``. Never raises: a read
    that fails is an ``unreachable`` reading. One ``invocation`` row, no other."""
    try:
        res = api.needs(cfg)  # type: ignore[attr-defined]
    except Exception as e:  # noqa: BLE001 - an older willow-bot has no needs
        why = (
            "this willow-bot has no needs read (the one script is older)"
            if isinstance(e, AttributeError)
            else f"{type(e).__name__}: {e}"
        )
        return _gone("unreachable", why)
    if not isinstance(res, dict) or "refused" in res:
        why = res.get("refused") if isinstance(res, dict) else "not a needs record"
        return _gone("unreachable", _clean(why))
    lines = res.get("needs")
    if not isinstance(lines, list) or not all(isinstance(x, str) for x in lines):
        return _gone("unreachable", "the needs read is not a list of lines")
    lines = [x for x in (" ".join(_clean(x).split()) for x in lines) if x]
    if not lines:
        return _gone("empty", "nothing on the record waits on you")
    seen: set[str] = {"rstate"}
    items = [item_box(x, seen) for x in lines]
    count = Box(
        _bid("count", seen),
        "pass",
        "record",
        f"{len(items)} waiting on you: {_counts(items)}",
        "from the record's NEEDS YOU, read without checking out",
        role="count",
    )
    return Reading("populated", "", [count, *items], {"waiting": len(items)})
