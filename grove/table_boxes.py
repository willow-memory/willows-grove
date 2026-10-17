# b17: GRTBX ΔΣ=42
"""The table's boxes, and the narrator code checks (box-build R12: the act).

SPEC ruling R12; SPEC-rival §8 R5-the-act; SPEC-documented §13 J7 and its
conflicts C14, C15, C16; forge-convergence.md:634-636 ("narration at the
escalation points only ... a draft the world does not depend on");
box-stream-surfaces.md:18-22 ("code makes the boxes; a small model may say the
boxes as one sentence; code checks that sentence").

Roll and scene facts and sealed lore become boxes (``scene_boxes`` over record
rows, ``served_boxes`` over a served document): one ``roll`` box per verdict
row that rolled (``turn N rolled T, verdict``), one ``scene`` box per scene,
one ``lore`` box per lore row (``seat_boxes.lore_box``, N9), a ``result`` box.
A decision, a seal, an escalated pick: ``governance`` boxes (C16) -- shown to
the human, never narrated, never in the model's vocabulary.

What a model may do here is one thing: rewrite the code sentence
(``seat_boxes.compose`` over the fact boxes) under ``seat_say.run_checks``
(every cite served, every box cited, nothing the boxes lack, quotes exact)
plus two table checks: no fleet noun (DECISION.md §3: Willow, Grove, Nestor,
Jeles, SOIL, SAFE never reach a player) and no seal state narrated (C16). A
sentence that fails any check is struck and the code sentence stands; a model
that is unreachable, silent, or escalates is the same fallback, said why.

A set piece (C15) is the one beat a flowering turn may be asked about, and
its answer is a ``draft`` box (``set_piece_draft``): ``role="draft"``, never
a fact box, so ``narrate`` never puts its words in the vocabulary and no row
is written from it. Code never rolls here, never picks a move, never seals.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from grove.seat_boxes import Box, compose, lore_box
from grove.seat_say import CHECK_NAMES, WORD, _fold, build_prompt, passed, run_checks

#: DECISION.md §3: none of these reach a player.
FLEET_NOUNS = frozenset({"willow", "grove", "nestor", "jeles", "soil", "safe"})
#: C16: seal state is shown as a governance box, never narrated by a model.
SEAL_WORDS = frozenset(
    "seal seals sealed sealing unsealed ratify ratified ratifies canon canonical "
    "reject rejected rejects".split()
)
TABLE_CHECK_NAMES = (*CHECK_NAMES, "no fleet noun", "no seal state narrated")
GOVERNANCE = "governance"
DRAFT = "draft"
ESCALATE = "ESCALATE"
BANDS = ("strong", "weak", "miss")
DRAFT_DETAIL = "a draft the world does not depend on"
_ESCALATE_RE = re.compile(r"^\s*ESCALATE\b", re.IGNORECASE)


# --- the boxes -----------------------------------------------------------------


def _kind(row: dict) -> tuple[str, str]:
    """``(kind, what)`` of a record or served row. A served verdict row has
    ``what == "verdict"`` and its own ``what`` folded away, so a roll is told
    by its verdict and turn, not by a ``what: roll`` it may not carry."""
    kind = str(row.get("kind") or row.get("what") or "")
    what = str(row.get("what") or "")
    if kind == "verdict":
        v = row.get("verdict")
        if v in BANDS and isinstance(row.get("turn"), int):
            return kind, "roll"
        if v in ("decision", "result", "escalate", "open", "step", "agm_head"):
            return kind, str(v)
    return kind, what


def _one(text: object) -> str:
    return " ".join(str(text or "").split())


def box_of(row: dict, bid: str) -> Box | None:
    """One row as its box, or None when the row makes no box (an ``open``
    row, a step with no roll, a row of a kind the table does not say)."""
    kind, what = _kind(row)
    if kind == "lore":
        return lore_box(row, bid)
    if kind == "verdict" and what == "roll":
        total, verdict, turn = row.get("total"), row.get("verdict"), row.get("turn")
        detail = _one(row.get("reason"))
        if row.get("beat"):
            detail = (
                f"{detail} · beat {_one(row['beat'])}"
                if detail
                else f"beat {row['beat']}"
            )
        if total is None:
            return Box(
                bid, "pass", "roll", f"empty — turn {turn} has no total", state="empty"
            )
        return Box(
            bid, "pass", "roll", f"turn {turn} rolled {total}, {verdict}", detail
        )
    if kind == "verdict" and what == "result":
        return Box(bid, "pass", "result", _one(row.get("reason")) or "the story ended")
    if kind == "verdict" and what == "decision":
        fid = _one(row.get("fact_id") or row.get("beat") or "a beat")
        return Box(
            bid,
            "you",
            "decision",
            f"decision {fid} waits on you",
            _one(row.get("reason")),
            role=GOVERNANCE,
        )
    if kind == "verdict" and what == "escalate":
        return Box(
            bid,
            "you",
            "escalate",
            f"the model's pick was refused: {_one(row.get('reason'))}",
            f"to: {_one(row.get('to') or 'human')}",
            role=GOVERNANCE,
        )
    if kind == "seal":
        subject = _one(row.get("subject"))[:12]
        return Box(
            bid,
            "dec",
            "seal",
            f"sealed {subject}" if subject else "sealed",
            _one(row.get("who")),
            role=GOVERNANCE,
        )
    return None


def scene_boxes(rows: list[dict]) -> list[Box]:
    """Record rows (``n``-stamped) as boxes, in record order: a ``scene`` box
    before the first roll of each scene, then the rolls, lore, result, and the
    governance boxes. Ids are the rows' own (``r<n>``)."""
    out: list[Box] = []
    seen_scene: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        bid = (
            f"r{row['n']}"
            if isinstance(row.get("n"), int)
            else f"h{_one(row.get('hash'))[:12]}"
        )
        kind, what = _kind(row)
        scene = _one(row.get("scene") or (row.get("where") if what == "roll" else ""))
        if what == "roll" and scene and scene not in seen_scene:
            seen_scene.add(scene)
            out.append(Box(f"{bid}s", "pass", "scene", f"scene {scene}"))
        b = box_of(row, bid)
        if b is not None:
            out.append(b)
    return out


def served_boxes(doc: dict) -> list[Box]:
    """A served document's rows as boxes; each id is the served table id with
    the row's place in it (``<served id>.<i>``), so a cite is a served id."""
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
        tid = str(t.get("id", ""))
        for i, row in enumerate(t.get("rows") or []):
            b = box_of(row, f"{tid}.{i}") if isinstance(row, dict) else None
            if b is not None:
                out.append(b)
    return out


def facts(boxes: list[Box]) -> list[Box]:
    """The boxes a model may say: populated, and neither governance nor draft."""
    return [
        b for b in boxes if b.state == "populated" and b.role not in (GOVERNANCE, DRAFT)
    ]


def shown(boxes: list[Box]) -> list[Box]:
    """The boxes shown beside the sentence and never narrated (C16)."""
    return [b for b in boxes if b not in facts(boxes)]


# --- the two table checks --------------------------------------------------------


def check_no_fleet_noun(sentence: str) -> bool:
    return not any(w in FLEET_NOUNS for w in WORD.findall(_fold(sentence)))


def check_no_seal_talk(sentence: str) -> bool:
    return not any(w in SEAL_WORDS for w in WORD.findall(_fold(sentence)))


def table_checks(
    sentence: str, boxes: list[Box], human: str = "", claims=None, earlier=None
) -> list:
    """``run_checks`` plus the two table checks, in ``TABLE_CHECK_NAMES`` order."""
    return [
        *run_checks(sentence, boxes, human, claims, earlier),
        check_no_fleet_noun(sentence),
        check_no_seal_talk(sentence),
    ]


# --- the narrator ---------------------------------------------------------------


def code_sentence(fact_boxes: list[Box]) -> str:
    """The sentence code says over the fact boxes: ``seat_boxes.compose`` per
    box, each cited, so a run of rolls is not folded into ``are all routine``."""
    return " ".join(
        s
        for s in (compose([b], cite=True, look=False, rush=False) for b in fact_boxes)
        if s
    )


def narrate(
    boxes: list[Box],
    human: str = "",
    say: Callable[[str], str] | None = None,
    claims=None,
    earlier: list[Box] | None = None,
) -> dict:
    """The sentence for a scene. Code's stands unless the model's rewrite
    passes every check. Returns ``sentence``, ``source`` (``code`` /
    ``model``), ``code`` (the code sentence), ``model`` (what the model said,
    or None), ``checks`` (``TABLE_CHECK_NAMES`` order, or None when no model
    was asked), ``struck``, ``escalated`` (the model answered ESCALATE: the
    human's), ``why`` and ``shown`` (the governance and draft boxes)."""
    fb = facts(boxes)
    code = code_sentence(fb)
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
        out["why"] = "no fact box to say"
        return out
    if say is None:
        out["why"] = "no model asked"
        return out
    try:
        got = say(build_prompt(fb, human, earlier=None))
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
        out["why"] = (
            f"the model escalated: {got[len(ESCALATE) :].strip(' :-') or 'no reason'}"
        )
        return out
    checks = table_checks(got, fb, human, claims, earlier)
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


def is_fact(box: Box) -> bool:
    return box in facts([box])
