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

The table (SPEC R13, no new panel): when the seat is pointed at a table box
(``GROVE_SEAT_BOX``, see ``seat_cli.config``), ``api.needs`` also hands back the
wagers and the table's own lines, and ``item_box`` lays them out like the rest:

    wager ID reconciled · ...           a ``wager`` box, ``needs you`` (the grade is
                                        yours): the forecast, the outcome and code's
                                        score, one detail line each
    wager ID escalate to human · WHY    a ``wager`` box, ``needs you``: a forecast
                                        waiting on your outcome seal or tip
    wager ID seal unreachable · WHY     an ``unreachable`` ``wager`` box
    table verdict session S · ...       a ``verdict session`` box: ``needs you`` while
                                        a tip seal is waited on, ``decided`` once it
                                        covers it, ``unreachable`` when the tip was
                                        not checked here (no human key)
    table agm_head STATE · ...          an ``agm_head`` box: ``satisfied`` decided,
                                        ``failing`` blocked, ``unreachable`` and
                                        ``unanchored`` (an ``empty`` box) apart

A decision beat awaiting a seal is a ``proposal`` line already. A line is
scrubbed before it is a box (``scrub``): the human key's own hex, a ``seed`` or
``key`` set to a value, and a long hex run that is not a 64-hex hash or a 40-hex commit
never reach the screen, wherever a record's text put them.

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
#: Asked for the table's story: the served fact boxes said as one sentence by
#: ``table_boxes.narrate`` (a model's, checked, else code's). Same exact-match
#: rule as the status phrases; no substring, no model.
STORY_PHRASES = frozenset(
    {
        "what happened at the table",
        "whats happened at the table",
        "what happened at the table so far",
        "narrate the table",
        "tell me the story",
        "the story so far",
        "whats the story so far",
        "tell me what happened at the table",
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


def story_kind(text: str) -> bool:
    """Whether the line asks for the table's story (``STORY_PHRASES``)."""
    return _key(text) in STORY_PHRASES


def status_kind(text: str) -> str | None:
    """``"where"`` (the whole state), ``"needs"`` (what waits on the human) or
    ``None`` (not a status question: a task, or something else the seat knows)."""
    k = _key(text)
    if k in WHERE_PHRASES:
        return "where"
    return "needs" if k in STATUS_PHRASES else None


def _gone(state: str, why: str, source: str = "record") -> Reading:
    value = f"empty — {why}" if state == "empty" else f"unreachable — {why}"
    bid = "rstate" if source == "record" else "tstate"
    return Reading(state, why, [Box(bid, "pass", source, value, state=state)])


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
WAGER = re.compile(
    r"wager (?P<id>\S+) (?P<state>reconciled|escalate to human|seal unreachable)"
    r" · (?P<rest>.+)",
    re.S,
)
#: a session id never holds ` · ` (N8): such a line is not read as a session
SESSION = re.compile(
    r"table verdict session (?P<sid>(?:(?! · ).)+?) · (?P<rest>\d+ rows · .+)", re.S
)
AGM = re.compile(
    r"table agm_head (?P<state>satisfied|failing|unreachable|unanchored)"
    r"(?: · (?P<rest>.+))?",
    re.S,
)
#: What a line must not carry onto the screen (see ``scrub``).
WITHHELD = "[withheld]"
_NAMED = r"\w*(?:key|seed|secret|token|passphrase|password)\w*"
#: ``HUMAN_KEY=...``, ``seed: ...``, ``GROVE_SEAT_HUMAN_KEY=...``: the whole field
#: (up to the next `` · `` or the end of the line) is the value.
_ASSIGNED = re.compile(rf"\b{_NAMED}\s*[:=]\s*[^\n]*?(?= · |\n|$)", re.I)
#: ``seed <hex or base64>``: a secret's name, then a long token, no colon.
_NAMED_VALUE = re.compile(rf"\b{_NAMED}\s+[A-Za-z0-9+/_=-]{{16,}}", re.I)
_HEX_RUN = re.compile(r"[0-9a-fA-F]{24,}")
_HEX_PART = re.compile(
    r"(?<![0-9A-Za-z])(?=[0-9a-f]*[a-f])[0-9a-f]{8,}(?![0-9A-Za-z])", re.I
)
_B64_RUN = re.compile(
    r"(?<![A-Za-z0-9+/_=-])[A-Za-z0-9+/_-]{32,}={0,2}(?![A-Za-z0-9+/_=-])"
)
#: Where a 64-hex is a record's own hash (a subject, the run's version): a
#: ``proposal:``/``serve:``/``tip:N:`` subject or ``run``. A 40-hex is a commit
#: only after ``commit``/``sha``/``green on``/``head``.
_HASH_AFTER = re.compile(
    r"(?:\b(?:proposal|serve|outcome|forecast|seal|run)[: ]|\btip:\d+:)$", re.I
)
_SHA_AFTER = re.compile(r"(?:\b(?:commit|sha1?|green on|head)\W{0,3})$", re.I)


def _hex_ok(line: str, m: re.Match, known: tuple[str, ...]) -> bool:
    run = m.group(0)
    before = line[: m.start()]
    after = line[m.end() : m.end() + 1]
    if before[-1:].isalnum() or after.isalnum():
        return False  # glued into a word: no boundary, no hash
    if run in known:
        return True
    if len(run) == 64:
        return bool(_HASH_AFTER.search(before))
    if len(run) == 40:
        return bool(_SHA_AFTER.search(before))
    return False


def scrub(line: str, secrets: tuple[str, ...] = (), known: tuple[str, ...] = ()) -> str:
    """The line with what must not reach the screen replaced by ``[withheld]``:

    * every known secret (``secrets``: the key's text and hex, as given);
    * the value of any ``...key/seed/secret/token/password...`` set with ``:`` or
      ``=`` (the whole field), and ``seed <long token>`` without a colon;
    * hex runs of 24 or more characters, anywhere, **unless** the run is a record
      hash in its place: a 64-hex after ``proposal:``, ``serve:``, ``tip:N:``,
      ``outcome:``, ``forecast:``, ``seal:`` or ``run``, a 40-hex after
      ``commit``/``sha``/``green on``/``head``, or a hash handed in ``known``
      (a bare 64-hex, a ``0x`` hex, a hex glued into a word are withheld);
    * 8-or-more-character hex pieces that together make 24 or more (a key split
      by spaces or `` · ``);
    * a base64 or base64url run of 32 or more characters with a digit and both
      cases (a random-looking token, not a snake_case name or a path)."""
    for sec in secrets:
        if sec and len(sec) >= 4:
            line = line.replace(sec, WITHHELD)
    line = _ASSIGNED.sub(WITHHELD, line)
    line = _NAMED_VALUE.sub(WITHHELD, line)
    line = re.sub(r"0[xX][0-9a-fA-F]{8,}", WITHHELD, line)
    line = _HEX_RUN.sub(
        lambda m: m.group(0) if _hex_ok(line, m, known) else WITHHELD, line
    )

    # a key cut in pieces: adjacent hex pieces (space or ' · ') adding up to a key
    def pieces(m: re.Match) -> str:
        n = sum(len(x) for x in re.findall(r"[0-9a-fA-F]+", m.group(0)))
        return WITHHELD if n >= 24 else m.group(0)

    line = re.sub(
        rf"{_HEX_PART.pattern}(?:(?: · | ){_HEX_PART.pattern})+",
        pieces,
        line,
        flags=re.I,
    )

    def b64(m: re.Match) -> str:
        t = m.group(0)
        mixed = (
            any(c.isdigit() for c in t)
            and any(c.isupper() for c in t)
            and any(c.islower() for c in t)
        )
        return WITHHELD if mixed else t

    return _B64_RUN.sub(b64, line)


def _parts(rest: str) -> str:
    """The line's ` · ` parts, one detail line each (a detail that splits on
    ` · ` would be read as chip options, which a score is not)."""
    return "\n".join(x for x in (p.strip() for p in rest.split(" · ")) if x)


def _tip_kind(tip: str) -> tuple[str, str]:
    """(kind, state) of a verdict session's tip clause."""
    if tip.startswith("covered by"):
        return "dec", "populated"
    if tip.startswith("waiting on"):
        return "you", "populated"
    return "block", "unreachable"  # not checked here: no human key was handed over


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
    if m := WAGER.fullmatch(line):  # R13: the forecast, its outcome, its score
        if m["state"] == "seal unreachable":
            return Box(
                bid,
                "block",
                "wager",
                f"unreachable — wager {m['id']} seal: {m['rest']}",
                state="unreachable",
            )
        return Box(
            bid, "you", "wager", f"wager {m['id']} {m['state']}", _parts(m["rest"])
        )
    if m := SESSION.fullmatch(line):  # R13: a verdict session, and its tip
        parts = m["rest"].split(" · ")
        kind, state = _tip_kind(parts[-1])
        value = f"table verdict session {m['sid']}"
        if state == "unreachable":
            value = f"unreachable — {value}: {parts[-1]}"
            parts = parts[:-1]
        return Box(
            bid, kind, "verdict session", value, _parts(" · ".join(parts)), state=state
        )
    if m := AGM.fullmatch(line):  # R13: the ai-game-master ledger head
        state, rest = m["state"], m["rest"] or ""
        value = f"table agm_head {state}"
        if state == "unanchored":
            return Box(
                bid, "pass", "agm_head", f"empty — {rest or value}", state="empty"
            )
        if state == "unreachable":
            return Box(
                bid,
                "block",
                "agm_head",
                f"unreachable — {rest or value}",
                state="unreachable",
            )
        return Box(
            bid,
            "block" if state == "failing" else "dec",
            "agm_head",
            value,
            _parts(rest),
        )
    return Box(bid, "you", "record", line)


def _counts(items: list[Box]) -> str:
    names = {
        "proposal": "proposal",
        "re-check": "re-check",
        "wager": "wager",
        "verdict session": "verdict session",
        "agm_head": "agm_head",
        "record": "other",
    }
    out = []
    for label in names:
        n = sum(b.label == label for b in items)
        if n:
            out.append(plural(n, names[label]))
    return ", ".join(out)


def read_needs(
    api: object,
    cfg: object,
    *,
    human_key: object = None,
    read_head: object = None,
    secrets: tuple[str, ...] = (),
) -> Reading:
    """The record's NEEDS YOU as boxes, by ``api.needs``. Never raises: a read
    that fails is an ``unreachable`` reading. One ``invocation`` row, no other.

    ``human_key`` (a file outside the box) and ``read_head`` (the table's ledger
    reader) are handed to ``api.needs`` only when set, so a box that is no
    table's, and an older willow-bot, are asked exactly as before. ``secrets``
    are strings no line may show (``scrub``)."""
    kw = {k: v for k, v in (("human_key", human_key), ("read_head", read_head)) if v}
    try:
        res = api.needs(cfg, **kw)  # type: ignore[attr-defined]
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
    lines = [
        x for x in (scrub(" ".join(_clean(x).split()), secrets) for x in lines) if x
    ]
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
