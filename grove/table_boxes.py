# b17: GRTBX ΔΣ=42
"""The table's boxes, and the narrator code checks (box-build R12, R21: the act).

SPEC rulings R12 and R21; SPEC-rival §8 R5-the-act; SPEC-documented §13 J7
and its conflicts C14, C15, C16; forge-convergence.md:634-636 ("narration at
the escalation points only ... a draft the world does not depend on");
box-stream-surfaces.md:18-22 ("code makes the boxes; a small model may say the
boxes as one sentence; code checks that sentence"); W3b audit B5, S1, S2, S3,
S4, idea side F1, F3, F4, F5.

Two readers, one rule about who may say what:

``served_boxes(doc)``  a served document's rows (the human sealed the scope;
    lore rows there passed ``lore.servable`` in one-script) as boxes whose
    ids are served ids. These are the only boxes a model may narrate: a
    fact box is ``kind="pass"`` with no role and one of ``FACT_LABELS``.
``scene_boxes(rows)``  raw record rows as boxes, code-only: every box carries
    ``role="record"``, so ``narrate`` says them in code and never hands them
    to a model. A lore row is kept only when the injected ``servable(row)``
    says so (the host has one-script's ``lore.servable``); with none given,
    raw lore is dropped (S3): an unsealed lore row never becomes a fact.

A decision, a seal, an escalated pick are boxes of another kind (``you``,
``dec``, ``block``): shown to the human, never said, never in the prompt
(C16, S1). A model's words never reach them: the escalate box says only
"the model's pick was refused" (S4).

What a model may do here is one thing: rewrite the code sentence
(``seat_boxes.compose``, one cited sentence per fact box) under
``seat_say.run_checks`` (every cite served, every box cited, nothing the
boxes lack) plus the table checks (R21, B5): no quotes at all in table
narration; per clause, every number and content word a clause holds must be
in the VALUE of the one box that clause cites, exactly, no stemming, glue
free, a spelled number a content word, each cite with a clause of its own; no fleet noun (DECISION.md §3: Willow,
Grove, Nestor, Jeles, SOIL, SAFE never reach a player; a word a fact box
itself holds is exempt, and plurals and possessives of a fleet noun are
caught). A sentence that fails any check is struck and the code sentence
stands; a model that is unreachable, silent, or escalates is the same
fallback, said why. ``earlier`` boxes (the thread) are filtered through
``facts`` and the same set goes to the prompt and the checks (S2).

A set piece (C15) is the one beat a flowering turn may be asked about, and
its answer is a ``draft`` box (``set_piece_draft``): ``role="draft"``, never
a fact box, so ``narrate`` never puts its words in the vocabulary and no row
is written from it. Code never rolls here, never picks a move, never seals.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from grove.seat_boxes import GLUE, Box, compose, lore_box
from grove.seat_say import (
    CHECK_NAMES,
    CITE,
    NUMBER,
    STOP,
    WORD,
    _fold,
    build_prompt,
    check_boxes_cited,
    check_cites_served,
    check_nothing_lacking,
)

#: DECISION.md §3: none of these reach a player.
FLEET_NOUNS = frozenset({"willow", "grove", "nestor", "jeles", "soil", "safe"})
#: The table checks (R21), after the first three of ``CHECK_NAMES``. The fourth
#: (quotes exact) is replaced: table narration quotes nothing at all.
TABLE_CHECK_NAMES = (
    *CHECK_NAMES[:3],
    "no quotes",
    "each clause from its box",
    "no fleet noun",
)
#: The labels of a fact box: what a served row may say as a fact.
FACT_LABELS = frozenset({"scene", "roll", "lore", "result"})
RECORD = "record"  # a box from raw record rows: code says it, no model does
DRAFT = "draft"
ESCALATE = "ESCALATE"
BANDS = ("strong", "weak", "miss")
DRAFT_DETAIL = "a draft the world does not depend on"
REFUSED = "the model's pick was refused"
_ESCALATE_RE = re.compile(r"^\s*ESCALATE\b", re.IGNORECASE)
_CLAUSE = re.compile(r"(.*?)\[(\w+)\]", re.S)


# --- the boxes -----------------------------------------------------------------


def _kind(row: dict) -> tuple[str, str]:
    """``(kind, what)`` of a record or served row. A served verdict row has
    ``what == "verdict"`` and its own ``what`` folded away, so a roll is told
    by its verdict and turn, not by a ``what: roll`` it may not carry."""
    kind = str(row.get("kind") or row.get("what") or "")
    what = str(row.get("what") or "")
    if kind == "verdict":
        v = row.get("verdict")
        if v in BANDS and _is_int(row.get("turn")):
            return kind, "roll"
        if v in ("decision", "result", "escalate", "open", "step", "agm_head"):
            return kind, str(v)
    return kind, what


def _is_int(v: object) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _one(text: object) -> str:
    return " ".join(str(text or "").split())


def box_of(row: dict, bid: str, role: str = "") -> Box | None:
    """One row as its box, or None when the row makes no box (an ``open``
    row, a step with no roll, a row of a kind the table does not say)."""
    kind, what = _kind(row)
    if kind == "lore":
        b = lore_box(row, bid)
        b.role = role
        return b
    if kind == "verdict" and what == "roll":
        total, verdict, turn = row.get("total"), row.get("verdict"), row.get("turn")
        detail = _one(row.get("reason"))
        if row.get("beat"):
            beat = f"beat {_one(row['beat'])}"
            detail = f"{detail} · {beat}" if detail else beat
        if not _is_int(total):
            return Box(
                bid, "pass", "roll", f"empty — turn {turn} has no total", state="empty"
            )
        return Box(
            bid,
            "pass",
            "roll",
            f"turn {turn} rolled {total}, {verdict}",
            detail,
            role=role,
        )
    if kind == "verdict" and what == "result":
        return Box(
            bid,
            "pass",
            "result",
            _one(row.get("reason")) or "the story ended",
            role=role,
        )
    if kind == "verdict" and what == "decision":
        fid = _one(row.get("fact_id") or row.get("beat") or "a beat")
        return Box(
            bid,
            "you",
            "decision",
            f"decision {fid} waits on you",
            _one(row.get("reason")),
        )
    if kind == "verdict" and what == "escalate":
        took = _one(row.get("took"))
        return Box(
            bid, "block", "escalate", REFUSED, f"code took {took}" if took else ""
        )
    if kind == "seal":
        subject = _one(row.get("subject"))[:12]
        return Box(
            bid,
            "dec",
            "seal",
            f"sealed {subject}" if subject else "sealed",
            _one(row.get("who")),
        )
    return None


def scene_boxes(
    rows: list[dict], servable: Callable[[dict], bool] | None = None
) -> list[Box]:
    """Record rows (``n``-stamped) as code-only boxes (``role="record"``), in
    record order: a ``scene`` box before the first roll of each scene, then
    the rolls, lore the injected ``servable`` passes (none passes with no
    ``servable``), result, and the shown-only boxes. Ids are the rows' own."""
    out: list[Box] = []
    seen_scene: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        bid = (
            f"r{row['n']}"
            if _is_int(row.get("n"))
            else f"h{_one(row.get('hash'))[:12]}"
        )
        kind, what = _kind(row)
        if kind == "lore" and not (servable is not None and servable(row)):
            continue
        scene = _one(row.get("scene") or (row.get("where") if what == "roll" else ""))
        if what == "roll" and scene and scene not in seen_scene:
            seen_scene.add(scene)
            out.append(Box(f"{bid}s", "pass", "scene", f"scene {scene}", role=RECORD))
        b = box_of(row, bid, RECORD)
        if b is not None:
            out.append(b)
    return out


def served_boxes(doc: dict) -> list[Box]:
    """A served document's rows as boxes; each id is the served table id with
    the row's place in it (``<served id>_<i>``: ``_`` so ``seat_say.CITE`` reads it), so a cite is a served id.
    Only a table that is populated and ``human-sealed`` yields boxes (NIT-3).
    These are the boxes a model may be asked to say."""
    out: list[Box] = []
    if not isinstance(doc, dict) or doc.get("state") != "populated":
        why = _one(doc.get("why") if isinstance(doc, dict) else "no served document")
        state = (
            doc.get("state")
            if isinstance(doc, dict) and doc.get("state") in ("empty", "unreachable")
            else "unreachable"
        )
        return [Box("served", "pass", "served", f"{state} — {why}", state=state)]
    for t in doc.get("tables") or []:
        if not isinstance(t, dict):
            continue
        if (
            t.get("state", "populated") != "populated"
            or t.get("trust") != "human-sealed"
        ):
            continue  # NIT-3: only a sealed, populated table's rows are facts
        tid = str(t.get("id", ""))
        for i, row in enumerate(t.get("rows") or []):
            b = box_of(row, f"{tid}_{i}") if isinstance(row, dict) else None
            if b is not None:
                out.append(b)
    return out


def is_fact(box: Box) -> bool:
    """A box a model may say: a populated, served fact box (``kind="pass"``,
    no role, one of ``FACT_LABELS``). A record box, a draft, a decision, a
    seal, an escalate box: never."""
    return (
        box.state == "populated"
        and box.kind == "pass"
        and box.role == ""
        and box.label in FACT_LABELS
    )


def facts(boxes: list[Box]) -> list[Box]:
    return [b for b in boxes if is_fact(b)]


def sayable(boxes: list[Box]) -> list[Box]:
    """The boxes code says: the fact boxes and the record boxes."""
    return [
        b
        for b in boxes
        if b.state == "populated"
        and b.kind == "pass"
        and b.role in ("", RECORD)
        and b.label in FACT_LABELS
    ]


def shown(boxes: list[Box]) -> list[Box]:
    """The boxes shown beside the sentence and never said (C16)."""
    said = sayable(boxes)
    return [b for b in boxes if b not in said]


# --- the table checks (R21) --------------------------------------------------------

#: Every quote mark (NIT-1). `'` and `’` count only as quotes, not as the
#: apostrophe inside a word (``Grit's``, ``don’t``).
_QUOTE_MARKS = re.compile(r"[\"“”«»‘‚‛`″‟]|(?<![^\W\d_])['’]|['’](?![^\W\d_])")
#: Spelled numbers read as numbers (R21: normalised or refused).
NUMBER_WORDS = frozenset(
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
)
#: Words free in any clause: the seat's glue and function words.
#: R21b (H1): negators and hedges are never free in a table clause, whatever
#: the seat's glue or stop list says; an n't form splits to a word the box
#: lacks and is struck by the word rule.
NEGATORS = frozenset("not no nor never but yet still than".split())
#: Words free in any clause: the seat's glue and function words, less the
#: negators and hedges.
_FREE = frozenset(
    ({w for g in GLUE for w in WORD.findall(_fold(g))} | set(STOP)) - NEGATORS
)


def check_no_quotes(sentence: str) -> bool:
    """Table narration quotes nothing: a quote is no way past the boxes."""
    return not _QUOTE_MARKS.search(sentence)


def _value_words(b: Box) -> tuple[list[str], set[str]]:
    """The checkable vocabulary of a box: its VALUE only (R21 refinement):
    for a roll, turn N, total T and verdict V; a detail stays code's."""
    text = _fold(re.sub(r"['’]s\b", "", b.value))
    return NUMBER.findall(text), set(WORD.findall(text))


_ROLL_VALUE = re.compile(r"^turn (\d+) rolled (\d+)\b")
_AFTER_TURN = re.compile(r"\bturn\s+(\d+)")


def _numbers_match(clause: str, b: Box) -> bool:
    """Every number in the clause is the box's, exactly. For a roll box the
    number said after ``turn`` must be its turn N and any other number its
    total T, so ``turn 11 rolled 0`` is not ``turn 0 rolled 11`` while
    ``rolled 11 on turn 0`` is."""
    nums, _ = _value_words(b)
    got = NUMBER.findall(clause)
    m = _ROLL_VALUE.match(_fold(b.value))
    if m is None:
        return set(got) <= set(nums)
    turn, total = m.group(1), m.group(2)
    after_turn = _AFTER_TURN.findall(clause)
    if any(n != turn for n in after_turn):
        return False
    rest = list(got)
    for n in after_turn:
        rest.remove(n)
    return all(n == total for n in rest)


def _tokens(text: str) -> list[str]:
    """Words and numbers of a folded text, in order, possessive 's dropped.
    Compares a sentence to its boxes' text, never a pile key: search tuning, not the pile's key rule (flatten-2 F11)."""
    return re.findall(r"[^\W_]+", _fold(re.sub(r"['’]s\b", "", text)))


def check_clauses(sentence: str, boxes: list[Box]) -> bool:
    """Per clause (the text up to each ``[id]`` cite): every number and every
    content word in the clause is in the VALUE of the one box the clause
    cites; glue and function words are free, negators and hedges never
    (R21b H1); numbers compare exactly, a roll's turn after ``turn`` and its
    total elsewhere; every other word matches exactly, no stemming
    (``missed`` is not ``miss``); a spelled number is a content word. A lore
    box is said by code only: a model clause citing one must be the box's
    exact value, token for token (R21b H2). A roll clause must say the
    box's total or its verdict, not just ``turn`` (H4). Each cite needs a
    clause of its own (NIT-2), and a trailing clause with no cite may hold
    no content word, negator or number."""
    by_id = {b.id: b for b in boxes}
    end = 0
    for m in _CLAUSE.finditer(sentence):
        clause, cid = m.group(1), m.group(2)
        end = m.end()
        b = by_id.get(cid)
        if b is None:
            return False
        if b.label == "lore":  # H2: word for word, or not at all
            if _tokens(clause) != _tokens(b.value):
                return False
            continue
        _, words = _value_words(b)
        text = _fold(re.sub(r"['’]s\b", "", clause))
        got_nums = NUMBER.findall(text)
        content = [w for w in WORD.findall(text) if w not in _FREE]
        if not _numbers_match(text, b):
            return False
        if any(w not in words for w in content):
            return False
        if not got_nums and not content:
            return False  # NIT-2: a cite with no clause of its own
        roll = _ROLL_VALUE.match(_fold(b.value))
        if roll is not None:  # H4: the total or the verdict, not just "turn"
            verdict = _fold(b.value).split()[-1]
            if roll.group(2) not in got_nums and verdict not in content:
                return False
    tail = _fold(sentence[end:])
    if NUMBER.search(tail) or any(w not in _FREE for w in WORD.findall(tail)):
        return False
    return True


def _noun_stem(w: str) -> str:
    for suf in ("'s", "’s", "es", "s"):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            return w[: -len(suf)]
    return w


def check_no_fleet_noun(sentence: str, boxes: list[Box] | None = None) -> bool:
    """No fleet noun, nor a plural or possessive of one, unless a fact box
    itself holds that exact word (a willow by the ford is the world's)."""
    held = set()
    for b in boxes or []:
        held |= set(WORD.findall(_fold(f"{b.value} {b.detail}")))
    for w in WORD.findall(_fold(re.sub(r"['’]s\b", "'s", sentence))):
        if w in held:
            continue
        if w in FLEET_NOUNS or _noun_stem(w) in FLEET_NOUNS:
            return False
    return True


def table_checks(
    sentence: str, boxes: list[Box], human: str = "", earlier: list[Box] | None = None
) -> list:
    """The checks in ``TABLE_CHECK_NAMES`` order. ``earlier`` is this run's
    thread, already filtered through ``facts``."""
    earlier = facts(earlier or [])
    cited_earlier = [b for b in earlier if b.id in set(CITE.findall(sentence))]
    return [
        check_cites_served(sentence, boxes, earlier),
        check_boxes_cited(sentence, boxes),
        check_nothing_lacking(sentence, boxes, human, earlier),
        check_no_quotes(sentence),
        check_clauses(sentence, [*boxes, *cited_earlier]),
        check_no_fleet_noun(sentence, [*boxes, *cited_earlier]),
    ]


def passed(results: list) -> bool:
    return not any(r is False for r in results)


# --- the narrator ---------------------------------------------------------------


def code_sentence(boxes: list[Box]) -> str:
    """The sentence code says: ``seat_boxes.compose`` per sayable box, each
    cited, so a run of rolls is not folded into ``are all routine``."""
    return " ".join(
        s
        for s in (
            compose([b], cite=True, look=False, rush=False) for b in sayable(boxes)
        )
        if s
    )


def narrate(
    boxes: list[Box],
    human: str = "",
    say: Callable[[str], str] | None = None,
    earlier: list[Box] | None = None,
) -> dict:
    """The sentence for a scene. Code's stands unless the model's rewrite of
    the served fact boxes passes every check. Returns ``sentence``,
    ``source`` (``code`` / ``model``), ``code`` (the code sentence),
    ``model`` (what the model said, or None), ``checks``
    (``TABLE_CHECK_NAMES`` order, or None when no model was asked),
    ``struck``, ``escalated`` (the model answered ESCALATE: the human's),
    ``why`` and ``shown`` (the boxes never said)."""
    fb = facts(boxes)
    earlier = facts(earlier or [])
    code = code_sentence(boxes)
    out = {
        "sentence": code,
        "source": "code",
        "code": code,
        "model": None,
        "checks": None,
        "struck": False,
        "escalated": False,
        "why": "",
        "shown": shown(boxes),
    }
    if not fb:
        out["why"] = (
            "no served fact box: code only" if sayable(boxes) else "no fact box to say"
        )
        return out
    if say is None:
        out["why"] = "no model asked"
        return out
    try:
        got = say(build_prompt(fb, human, earlier=[("", earlier)] if earlier else None))
    except Exception as e:  # noqa: BLE001 - a model problem never escapes
        out["why"] = f"unreachable: {type(e).__name__}: {e}"
        return out
    if not isinstance(got, str) or not got.strip():
        out["why"] = "the model said nothing"
        return out
    got = " ".join(got.split())
    out["model"] = got
    if _ESCALATE_RE.match(got):
        out["escalated"] = True
        # R21b: the model's own words (its ESCALATE reason) never reach a card, a
        # who-line or the screen; the human is told only that it escalated.
        out["why"] = "the model escalated"
        return out
    checks = table_checks(got, fb, human, earlier)
    out["checks"] = checks
    if passed(checks):
        out["sentence"], out["source"] = got, "model"
        return out
    out["struck"] = True
    failed = [n for n, r in zip(TABLE_CHECK_NAMES, checks, strict=True) if r is False]
    out["why"] = "struck: " + ", ".join(failed)
    return out


# --- the set piece: a draft, never a fact ----------------------------------------


def set_piece_draft(
    flowering: Callable[[str, list[Box]], object],
    boxes: list[Box],
    prompt: str,
    bid: str = "draft",
) -> Box:
    """One flowering turn on a set piece (C15): ``flowering(prompt, facts)``
    returns ratatosk-shaped rows (``path``, ``data``, ``claim``) or raises.
    Its first row with text becomes a ``draft`` box; an ESCALATE row is an
    ``empty`` draft with its reason; a raise is ``unreachable``. The box is
    ``role="draft"`` in every state, so it is never a fact: ``facts`` leaves
    it out, ``narrate`` never says it, and nothing writes it to a record."""
    try:
        rows = flowering(prompt, facts(boxes))
    except Exception as e:  # noqa: BLE001 - the cloud turn is never trusted to behave
        return Box(
            bid,
            "pr",
            "set piece",
            f"unreachable — {type(e).__name__}: {e}",
            DRAFT_DETAIL,
            state="unreachable",
            role=DRAFT,
        )
    rows = [r for r in (rows if isinstance(rows, list) else []) if isinstance(r, dict)]
    marks = [r for r in rows if r.get("path") == ESCALATE]
    if marks:
        why = _one(marks[0].get("claim")) or "no reason given"
        return Box(
            bid,
            "pr",
            "set piece",
            f"empty — the cloud turn escalated: {why}",
            DRAFT_DETAIL,
            state="empty",
            role=DRAFT,
        )
    for r in rows:
        data = r.get("data")
        if isinstance(data, str) and data.strip():
            return Box(bid, "pr", "set piece", _one(data), DRAFT_DETAIL, role=DRAFT)
    return Box(
        bid,
        "pr",
        "set piece",
        "empty — the cloud turn proposed nothing",
        DRAFT_DETAIL,
        state="empty",
        role=DRAFT,
    )
