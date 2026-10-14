# b17: GRSNE ΔΣ=42
"""The seat reads a Nestor store as boxes, read-only.

``read_store(path)`` opens a Nestor sqlite file with ``mode=ro`` and
``PRAGMA query_only``, reads ``tm_pairs`` and ``tm_rejections`` and answers a
``Reading``: a state, a reason, and the seat's ``Box`` cards already ranked
(``seat_boxes.rank``), so "where are we" can talk about a real store. It
writes nothing, takes no lock a writer waits on beyond sqlite's own read lock,
and imports nothing from Nestor: the schema is what is on disk, and a table or
column an older store lacks is tolerated.

Three states, never collapsed (INVARIANTS.md section 1):

    unreachable  no path configured, the file is missing or unreadable, is not
                 a sqlite file, or is not a Nestor store (neither ``tm_pairs``
                 nor ``tm_rejections``), or ``tm_pairs`` lacks a column this
                 reader needs. One ``unreachable`` box says the plain reason.
                 "Not configured" is ``unreachable`` and not ``empty``: the
                 seat cannot read anything, which is not the same as a store
                 that was read and holds nothing.
    empty        a readable Nestor store with no pairs and no rejections.
    populated    rows: the boxes below.

Row -> box (after ``web/demo/box-stream/shoebox-stream-v1.html``):

    sealed, live pair            dec    ``src → tgt``; the verifier and her
                                        reason, quoted exactly, in the detail
    sealed, then replaced        pr     ``src: "old" was replaced``; the old
                                        and the new reason, both exact (the
                                        lineage Nestor's own views do not show)
    draft, waiting               pr     ``src (draft)``; never said as fact:
                                        the detail says nobody has confirmed it.
                                        A draft is not a task (a person may
                                        have chosen to leave it), so it is
                                        ``changed``, not ``needs you``, unless
                                        the caller passes ``drafts_as="you"``
    draft that was a seal        pr     ``retired``: a baseline she unsealed
                                        (a verifier on a draft, origin
                                        ``unsealed:...``)
    rejection (a no)             block  the rejected text verbatim, never
                                        narrated; a ``reopen_when`` makes it a
                                        "not yet" with her condition quoted
    the count                    pass   ``14 sealed, 1 replaced, ...``

**Fiction stays visible.** A pair whose ``origin`` starts with ``fixture:``
carries that origin in its card, and its label says ``(fixture)``. A rejection
has no origin column, so when the store holds any fixture pair its rejection
cards and the count say the store is a fixture. The tag is never stripped.

A field is data: control characters (an escape sequence in a stored reason)
are dropped before a box is made, nothing else is changed, so a quoted reason
is exact apart from that.

A box's ``role`` says what it is when its kind does not: ``draft`` (a waiting
draft), ``more`` (a counted ``more`` box: rows not shown, not an item) and
``count`` (the summary). The seat's sentence and chips read the role, never
the words, so a count is not said as a decided item and is not a ``show me``
ref.

``lead_rank`` is the order "where are we" says them in (the count first, then
waiting drafts, refusals, decided, other changes), after the sketch; ``Reading
.boxes`` stays in the generic ``rank`` order.

Order is deterministic: kind rank, then ``created_at``, then row id. Each kind
shows its most recent ``CAPS[kind]`` boxes (oldest first) and one ``more`` box
counts the rest, so nothing is cut silently.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from grove.seat_boxes import Box, rank

#: Most boxes shown per kind; the rest are one counted ``more`` box.
CAPS = {"dec": 4, "pr": 4, "block": 3, "you": 4}
#: What a ``more`` box counts, by kind.
MORE_WORDS = {
    "dec": ("sealed", "sealed"),
    "pr": ("draft or change", "drafts or changes"),
    "block": ("rejection", "rejections"),
    "you": ("draft waiting", "drafts waiting"),
}
FIXTURE = "fixture:"
SQL_TIMEOUT = 2.0
NO_PATH = "no Nestor store is configured (WILLOW_NESTOR_DB / NESTOR_DB unset)"
_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")
#: ``tm_pairs`` columns this reader cannot do without; the rest default.
NEED_PAIRS = ("id", "source_text", "target_text", "status")
NEED_REJ = ("id", "query_norm", "target_text")


@dataclass
class Reading:
    """What one read of a store found. ``boxes`` is ranked and ready to show."""

    state: str  # populated | empty | unreachable
    reason: str = ""
    boxes: list[Box] = field(default_factory=list)
    #: sealed (every sealed row), live_sealed, replaced, draft (all drafts),
    #: waiting, retired, rejected, not_yet
    counts: dict[str, int] = field(default_factory=dict)
    #: the ``fixture:`` origins seen, sorted
    fixtures: list[str] = field(default_factory=list)
    #: kind -> boxes counted in a ``more`` box instead of shown
    omitted: dict[str, int] = field(default_factory=dict)


def _clean(text: object) -> str:
    return _CTRL.sub("", "" if text is None else str(text))


def _gone(state: str, why: str) -> Reading:
    # the seat's own three-state wording (grove.seat_cli.three_state)
    value = f"empty — {why}" if state == "empty" else f"unreachable — {why}"
    box = Box("nstate", "pass", "nestor store", value, state=state)
    return Reading(state, why, [box])


def _bid(prefix: str, key: str, seen: set[str]) -> str:
    """A short stable id from the row: ``n`` + five hex of its table and id."""
    digest = hashlib.sha1(f"{prefix}:{key}".encode()).hexdigest()
    for n in range(5, len(digest)):
        bid = "n" + digest[:n]
        if bid not in seen:
            seen.add(bid)
            return bid
    raise AssertionError("unreachable: sha1 prefixes exhausted")


def _columns(con: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]


def _rows(con: sqlite3.Connection, table: str, cols: list[str], want: tuple) -> list:
    """Rows as dicts with every ``want`` column present (absent: ``""``)."""
    have = [c for c in want if c in cols]
    sel = ", ".join(f'"{c}"' for c in have)
    order = ", ".join(c for c in ("created_at", "id") if c in cols) or "rowid"
    out = []
    for r in con.execute(f'SELECT {sel} FROM "{table}" ORDER BY {order}'):
        row = {c: "" for c in want}
        row.update({c: _clean(v) for c, v in zip(have, r, strict=True)})
        out.append(row)
    return out


PAIR_COLS = (
    "id",
    "source_text",
    "source_lang",
    "target_text",
    "target_lang",
    "status",
    "verifier",
    "origin",
    "created_at",
    "reason",
    "superseded_by",
)
REJ_COLS = (
    "id",
    "query_norm",
    "source_lang",
    "target_lang",
    "target_text",
    "verifier",
    "reason",
    "created_at",
    "reopen_when",
)


def _q(text: str) -> str:
    return f'"{text}"'


def _her(reason: str) -> str:
    """The human's words, quoted exactly; never invented when absent."""
    return f"reason: {_q(reason)}" if reason else "reason: none recorded"


def _tag(origin: str) -> str:
    return f"origin: {origin}" if origin.startswith(FIXTURE) else ""


def _lines(*parts: str) -> str:
    return "\n".join(p for p in parts if p)


def _pair_boxes(pairs: list[dict], drafts_as: str, seen: set[str]) -> list:
    """``(sort key, Box)`` for every pair row."""
    by_id = {p["id"]: p for p in pairs}
    out = []
    for p in pairs:
        fix = p["origin"].startswith(FIXTURE)
        mark = " (fixture)" if fix else ""
        who = p["verifier"] or "nobody"
        arrow = f"{p['source_text']} → {p['target_text']}"
        bid = _bid("pair", p["id"], seen)
        key = (p["created_at"], p["id"])
        if p["superseded_by"]:
            new = by_id.get(p["superseded_by"])
            now = new["target_text"] if new else ""
            value = f"{p['source_text']}: {_q(p['target_text'])} was replaced"
            detail = _lines(
                f"sealed by {who}, then replaced",
                f"now: {_q(now)}" if new else "now: not in this store",
                _tag(p["origin"]),
                _her(p["reason"]).replace("reason:", "reason then:", 1),
                (
                    _her(new["reason"]).replace("reason:", "reason now:", 1)
                    if new
                    else ""
                ),
            )
            out.append((key, Box(bid, "pr", f"changed{mark}", value, detail)))
        elif p["status"] == "sealed":
            detail = _lines(f"sealed by {who}", _tag(p["origin"]), _her(p["reason"]))
            out.append((key, Box(bid, "dec", f"sealed by {who}{mark}", arrow, detail)))
        elif p["status"] == "draft" and p["verifier"] and "unsealed" in p["origin"]:
            same = p["source_text"] == p["target_text"]
            value = (
                f"{p['source_text']} (retired)"
                if same
                else (f"{p['source_text']} {_q(p['target_text'])} (retired)")
            )
            detail = _lines(
                f"unsealed by {who}; no longer served as sealed",
                f"origin: {p['origin']}",
                _her(p["reason"]) if p["reason"] else "",
            )
            out.append((key, Box(bid, "pr", f"retired{mark}", value, detail)))
        elif p["status"] == "draft":
            kind = "you" if drafts_as == "you" else "pr"
            value = f"{p['source_text']} (draft)"
            detail = _lines(
                f"drafted: {_q(p['target_text'])}",
                "a draft: nobody has confirmed it, so it is not a fact",
                _tag(p["origin"]),
                _her(p["reason"]),
            )
            out.append(
                (
                    key,
                    Box(
                        bid, kind, f"draft, waiting{mark}", value, detail, role="draft"
                    ),
                )
            )
        # any other status is not a state the seat can say; it is counted only
    return out


def _rejection_boxes(rows: list[dict], fixture_store: bool, seen: set[str]) -> list:
    out = []
    for r in rows:
        who = r["verifier"] or "nobody"
        not_yet = bool(r["reopen_when"])
        value = f"{_q(r['target_text'])} for {r['query_norm']}"
        fixture = (
            "origin not recorded; the store holds fixture rows" if fixture_store else ""
        )
        detail = _lines(
            f"not yet, reopen when: {_q(r['reopen_when'])}"
            if not_yet
            else f"a no from {who}: never serve this",
            f"rejected by {who}" if not_yet else "",
            fixture,
            _her(r["reason"]),
        )
        label = ("not yet" if not_yet else "a no") + f" · rejected by {who}"
        label += " (fixture store)" if fixture_store else ""
        key = (r["created_at"], r["id"])
        out.append(
            (key, Box(_bid("rej", r["id"], seen), "block", label, value, detail))
        )
    return out


def _has_reason(box: Box) -> bool:
    return "reason: none recorded" not in box.detail and "reason" in box.detail


def _cap(items: list, seen: set[str]) -> tuple[list[Box], dict[str, int]]:
    """Per kind: ``CAPS`` boxes shown oldest first, then a ``more`` box.

    Which are shown: a row with a reason of her own outranks one without (her
    words are the substance), then the most recent."""
    kinds: dict[str, list] = {}
    for key, box in sorted(items, key=lambda kb: (kb[0], kb[1].id)):
        kinds.setdefault(box.kind, []).append(box)
    boxes, omitted = [], {}
    for kind, group in kinds.items():
        cap = CAPS.get(kind, len(group))
        said = [i for i, b in enumerate(group) if _has_reason(b)]
        rest_i = [i for i in range(len(group)) if i not in said]
        keep = sorted((said[::-1] + rest_i[::-1])[:cap])
        shown, rest = [group[i] for i in keep], len(group) - len(keep)
        boxes += shown
        if rest > 0:
            omitted[kind] = rest
            bid = _bid("more", kind, seen)
            boxes.append(
                Box(
                    bid,
                    kind,
                    f"more · {len(shown)} shown",
                    f"{rest} more {MORE_WORDS.get(kind, ('box', 'boxes'))[rest != 1]}",
                    "older ones, in the store and not shown here",
                    role="more",
                )
            )
    return boxes, omitted


def _summary(counts: dict[str, int], fixtures: list[str], seen: set[str]) -> Box:
    parts = [f"{counts['live_sealed']} sealed"]
    if counts["replaced"]:
        parts.append(f"{counts['replaced']} replaced")
    if counts["waiting"]:
        parts.append(f"{counts['waiting']} draft{'s' * (counts['waiting'] != 1)}")
    if counts["retired"]:
        parts.append(f"{counts['retired']} retired")
    if counts["rejected"]:
        parts.append(f"{counts['rejected']} rejected")
    value = ", ".join(parts) + (" (fixture)" if fixtures else "")
    detail = (
        f"fiction, not a real trail: {', '.join(fixtures)}"
        if fixtures
        else "counted from the store, nothing guessed"
    )
    return Box(
        _bid("pass", "count", seen),
        "pass",
        "nestor store",
        value,
        detail,
        role="count",
    )


#: ``where are we`` order, after ``shoebox-stream-v1.html`` (its first reply is
#: the count box, its ``more`` is the drafts): the count orients, then what
#: is still open (waiting drafts), then what is refused, then what is decided,
#: then any other change, with a kind's counted ``more`` box last in its group.
LEAD = {"pass": 1, "you": 2, "draft": 2, "block": 3, "dec": 4, "pr": 5}


def lead_rank(boxes: list[Box]) -> list[Box]:
    """Boxes in the order "where are we" says them: a heads-up first (an
    ``empty`` or ``unreachable`` reading), then the count, then waiting drafts,
    refusals, decided, other changes. Stable within a group; deterministic.
    ``what needs me`` and a chain turn keep the generic ``rank``."""

    def key(b: Box) -> tuple[int, int]:
        if b.state != "populated":
            return (0, 0)
        more = b.role == "more"
        draft = b.role == "draft"
        return (
            LEAD["draft" if draft else b.kind] if (draft or b.kind in LEAD) else 6,
            more,
        )

    return sorted(boxes, key=key)


def read_store(path: str | Path | None, *, drafts_as: str = "pr") -> Reading:
    """Read a Nestor sqlite store, read-only, as ranked seat boxes.

    ``drafts_as="you"`` raises waiting drafts to ``needs you``; the default
    keeps them ``changed`` because a draft may be one the human chose to leave.
    Never raises on a bad store: that is an ``unreachable`` reading."""
    if path is None or not str(path).strip():
        return _gone("unreachable", NO_PATH)
    p = Path(path).expanduser()
    if not p.is_file():
        return _gone("unreachable", f"no Nestor store at {p}")
    try:
        con = sqlite3.connect(
            f"{p.resolve().as_uri()}?mode=ro", uri=True, timeout=SQL_TIMEOUT
        )
    except sqlite3.Error as e:
        return _gone("unreachable", f"can't open {p} read-only ({e})")
    try:
        con.execute("PRAGMA query_only = ON")
        return _read(con, p, drafts_as)
    except sqlite3.Error as e:
        return _gone("unreachable", f"{p} is not a readable Nestor store ({e})")
    finally:
        con.close()


def _read(con: sqlite3.Connection, p: Path, drafts_as: str) -> Reading:
    tables = {
        r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if not {"tm_pairs", "tm_rejections"} & tables:
        return _gone("unreachable", f"{p} is not a Nestor store (no tm_pairs table)")
    pairs: list[dict] = []
    rejs: list[dict] = []
    if "tm_pairs" in tables:
        cols = _columns(con, "tm_pairs")
        if missing := [c for c in NEED_PAIRS if c not in cols]:
            return _gone("unreachable", f"tm_pairs lacks {', '.join(missing)}")
        pairs = _rows(con, "tm_pairs", cols, PAIR_COLS)
    if "tm_rejections" in tables:
        cols = _columns(con, "tm_rejections")
        if missing := [c for c in NEED_REJ if c not in cols]:
            return _gone("unreachable", f"tm_rejections lacks {', '.join(missing)}")
        rejs = _rows(con, "tm_rejections", cols, REJ_COLS)
    if not pairs and not rejs:
        return _gone("empty", "the store holds no pairs and no rejections")

    seen: set[str] = {"nstate"}
    fixtures = sorted({x["origin"] for x in pairs if x["origin"].startswith(FIXTURE)})
    sealed = [x for x in pairs if x["status"] == "sealed"]
    drafts = [x for x in pairs if x["status"] == "draft" and not x["superseded_by"]]
    retired = [x for x in drafts if x["verifier"] and "unsealed" in x["origin"]]
    counts = {
        "sealed": len(sealed),
        "live_sealed": len([x for x in sealed if not x["superseded_by"]]),
        "replaced": len([x for x in pairs if x["superseded_by"]]),
        "draft": len(drafts),
        "waiting": len(drafts) - len(retired),
        "retired": len(retired),
        "rejected": len(rejs),
        "not_yet": len([x for x in rejs if x["reopen_when"]]),
    }
    items = _pair_boxes(pairs, drafts_as, seen)
    items += _rejection_boxes(rejs, bool(fixtures), seen)
    boxes, omitted = _cap(items, seen)
    boxes.append(_summary(counts, fixtures, seen))
    return Reading("populated", "", rank(boxes), counts, fixtures, omitted)
