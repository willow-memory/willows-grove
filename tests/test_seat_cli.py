# b17: GRSET ΔΣ=42
"""Tests for grove.seat_cli — the desk's command-line seat.

A fake one-script api stands in for willow-bot's, so no box, no model and no
network: each test scripts the human's keystrokes and reads what the seat
printed and which api calls it made.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from grove import onescript_reach
from grove import seat_boxes as bx
from grove import seat_cli as s
from grove import seat_say as say_mod

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def text(out):
    """Everything the seat printed, one string."""
    return "\n".join(out)


DOC = {"state": "populated", "why": "", "return": "rows", "tables": [{"id": "t1"}]}
ROW = {"path": "notes/a.md", "data": "# A", "cites": ["t1"], "claim": "from t1"}


class FakeApi:
    def __init__(self, **over):
        self.calls: list[tuple] = []
        self.res = {
            "checkin": {"report": {"hard_close": False, "lines": ["probes: 4/4"]}},
            "scope": {
                "spec": {"by": ["who"]},
                "subject": "serve:abc",
                "ids": ["t1"],
                "stack": [{"name": "who=human", "id": "t1" * 8, "rows": 2}],
            },
            "pooled": {"pooled": [], "count": 0, "code": 0},
            "needs": {"needs": [], "count": 0, "code": 0},
            "resume": {"resume": None, "code": 0},
            "serve": {"doc": DOC, "state": "populated", "why": ""},
            "escalate": {
                "task": "the task",
                "pieces": [],
                "answered": 0,
                "escalated": 0,
            },
            "take_proposals": {"out": {"proposals": []}},
            "checkout": {"screen": "MORNING SCREEN"},
        }
        self.res.update(over)

    def __getattr__(self, name):
        def call(*a, **k):
            self.calls.append((name, a[1:], k))
            got = self.res[name]
            return got(*a, **k) if callable(got) else got

        return call

    def names(self):
        return [c[0] for c in self.calls]


def bot(api, pieces=()):
    return s.Bot(
        api=api,
        cut=lambda doc, q, n: list(pieces),
        subject=lambda p: "proposal:" + p["path"],
        piece_chars=6000,
    )


SUBJ = "proposal:" + "a" * 16
EMPTY_DEPOSIT = {"state": "empty", "reason": "the pool is empty"}


class FakeDeposit:
    """The injected deposit: records the pool it was handed, returns `got`."""

    def __init__(self, got=None):
        self.got = got if got is not None else EMPTY_DEPOSIT
        self.pools: list[dict] = []

    def __call__(self, pool):
        self.pools.append(pool)
        if isinstance(self.got, BaseException):
            raise self.got
        return self.got


def seat(
    api,
    keys,
    *,
    pieces=(),
    flower=None,
    deposit=None,
    color=False,
    clock=None,
    say=None,
    today=None,
):
    out: list[str] = []
    it = iter(keys)

    def read(prompt):
        out.append(prompt)
        try:
            return next(it)
        except StopIteration:
            raise EOFError from None

    st = s.Seat(
        bot(api, pieces),
        cfg="cfg",
        flower=flower or (lambda p, q: pytest.fail("a cloud turn ran")),
        deposit=deposit or FakeDeposit(),
        say=say,
        read=read,
        write=out.append,
        color=color,
        clock=clock or (lambda: "09:14"),
        today=today or (lambda: date(2026, 10, 14)),
    )
    return st, out


def piece(
    rung, outcome="escalated", reason="local_escalate", h="h" * 64, rows=(), detail="d"
):
    return {
        "piece": h,
        "rung": rung,
        "model": "m",
        "outcome": outcome,
        "label": outcome if outcome == "answered" else f"escalated:{reason}",
        "reason": reason,
        "detail": detail,
        "cites": [],
        "rows": list(rows),
    }


def chain_result(*pieces_):
    return {
        "task": "the task",
        "pieces": list(pieces_),
        "answered": sum(p["outcome"] == "answered" for p in pieces_),
        "escalated": sum(p["outcome"] == "escalated" for p in pieces_),
    }


# --- the flow -------------------------------------------------------------------


def test_the_stages_run_in_order_and_check_out(capsys):
    api = FakeApi()
    st, out = seat(api, ["who", "", "the task", ""])
    assert st.run() == 0
    assert api.names() == [
        "checkin",
        "resume",
        "scope",
        "pooled",
        "serve",
        "escalate",
        "checkout",
        "pooled",
    ]
    assert "MORNING SCREEN" in text(out)
    prompts = [o for o in out if "▶" in o]
    assert [p.split(" ▶")[0] for p in prompts] == [
        "scope",
        "served",
        "chain",
        "chain",
    ]


def test_eof_mid_run_still_checks_out():
    api = FakeApi()
    st, _out = seat(api, ["who"])  # EOF at the served prompt
    assert st.run() == 0
    assert api.names()[-2:] == ["checkout", "pooled"]


def test_ctrl_c_mid_run_still_checks_out():
    api = FakeApi(serve=lambda *a, **k: (_ for _ in ()).throw(KeyboardInterrupt))
    st, _out = seat(api, ["who", ""])
    assert st.run() == 0
    assert api.names()[-2:] == ["checkout", "pooled"]


def test_a_hard_close_stops_before_scope_and_says_so():
    api = FakeApi(checkin={"report": {"hard_close": True, "lines": ["toolchain: no"]}})
    st, out = seat(api, [])
    assert st.run() == 1
    assert "scope" not in api.names()
    assert any("HARD CLOSE" in o for o in out)


def test_a_refused_checkin_opens_nothing_and_checks_nothing_out():
    api = FakeApi(checkin={"refused": "no law", "code": 2})
    st, out = seat(api, [])
    assert st.run() == 1
    assert api.names() == ["checkin"]
    assert "[unreachable] refused" in text(out) and "no law" in text(out)


# --- the key ----------------------------------------------------------------------


def test_no_seal_prompt_is_reachable_and_no_seal_is_called():
    """A full run, with a pass in the pool and a flowering turn: the seat never
    asks `seal ▶` and never calls a seal."""
    api = FakeApi(
        escalate=chain_result(
            piece("local", "answered", rows=[ROW]), piece("local", h="g" * 64)
        ),
        take_proposals={
            "out": {"proposals": [{**ROW, "verdict": "pass", "subject": SUBJ}]}
        },
    )
    st, out = seat(
        api,
        ["who", "", "the task", "", "y", ""],  # "" at more?: three boxes, two a page
        pieces=[{"hash": "g" * 64, "piece": {}}],
        flower=lambda p, q: {"code": 0, "summary": "", "rows": [ROW]},
    )
    assert st.run() == 0
    assert not any(o.startswith("seal ▶") for o in out)
    assert not [n for n in api.names() if n.startswith("seal")]
    assert any("pooled: proposal:notes/a.md" in o for o in out)


def test_the_scope_names_its_subject_and_asks_nothing_more():
    api = FakeApi()
    st, out = seat(api, ["who", "", ""])
    st.run()
    assert "serve:abc" in text(out)
    assert "serve" in api.names()


def test_an_empty_scope_is_said_and_nothing_is_served():
    api = FakeApi(scope={"spec": {}, "subject": None, "ids": [], "stack": []})
    st, out = seat(api, ["who"])
    st.run()
    assert "serve" not in api.names()
    assert "[empty] scope" in text(out) and "no table matches" in text(out)


# --- three states -------------------------------------------------------------------


@pytest.mark.parametrize(
    "state, why, shown",
    [
        ("populated", "", "populated"),
        ("empty", "narrow the stack", "empty — narrow the stack"),
        ("unreachable", "no serve key", "unreachable — no serve key"),
        (None, "", "unreachable — no answer"),
    ],
)
def test_each_served_state_reads_as_itself(state, why, shown):
    assert s.three_state(state, why) == shown


def test_the_served_state_is_printed():
    api = FakeApi(serve={"doc": {}, "state": "empty", "why": "over the cap"})
    st, out = seat(api, ["who", "", ""])
    st.run()
    assert "[empty] served" in text(out) and "empty — over the cap" in text(out)


def test_a_scope_with_no_past_seal_is_the_honest_empty_not_a_mint():
    why = "the scope has no human seal over this exact set"
    api = FakeApi(serve={"doc": {}, "state": "empty", "why": why})
    st, out = seat(api, ["who", "", ""])
    st.run()
    assert f"empty — {why}" in text(out)
    assert not [n for n in api.names() if n.startswith("seal")]


# --- the chain and flowering ------------------------------------------------------------


def test_local_answers_are_shown_pooled_and_not_sealed():
    api = FakeApi(escalate=chain_result(piece("local", "answered", rows=[ROW])))
    st, out = seat(api, ["who", "", "the task", ""])
    st.run()
    assert "pooled: proposal:notes/a.md" in text(out)
    assert not [n for n in api.names() if n.startswith("seal")]


def test_a_d0_answer_is_not_a_proposal():
    api = FakeApi(escalate=chain_result(piece("d0", "answered", rows=[{"answer": 1}])))
    st, out = seat(api, ["who", "", "the task", ""])
    st.run()
    assert not any("pooled:" in o for o in out)


def test_flowering_asks_first_and_sends_the_chains_own_piece():
    sent = []
    cut = [{"hash": "h" * 64, "piece": {"tables": ["the piece"]}}]
    flow = {"code": 0, "summary": "[onescript] rung=openrouter", "rows": [ROW]}
    api = FakeApi(
        escalate=chain_result(piece("local")),
        take_proposals={
            "out": {"proposals": [{**ROW, "verdict": "pass", "subject": "proposal:x"}]}
        },
    )
    st, out = seat(
        api,
        ["who", "", "the task", "y", ""],
        pieces=cut,
        flower=lambda p, q: sent.append((p, q)) or flow,
    )
    st.run()
    assert sent == [({"tables": ["the piece"]}, "the task")]
    take = next(c for c in api.calls if c[0] == "take_proposals")
    assert take[1] == ([ROW],) and take[2] == {"bite": "flowering"}
    assert "pooled: proposal:x" in text(out)
    assert "[onescript] rung=openrouter" in text(out)


def test_no_yes_no_cloud_turn():
    api = FakeApi(escalate=chain_result(piece("local")))
    st, _out = seat(
        api,
        ["who", "", "the task", "", ""],
        pieces=[{"hash": "h" * 64, "piece": {}}],
    )
    st.run()  # the default flower fails the test if it runs
    assert "take_proposals" not in api.names()


@pytest.mark.parametrize("reason", sorted(s.NO_FLOWER))
def test_what_code_decided_never_reaches_a_model(reason):
    api = FakeApi(escalate=chain_result(piece("local", reason=reason)))
    st, out = seat(
        api, ["who", "", "the task", ""], pieces=[{"hash": "h" * 64, "piece": {}}]
    )
    st.run()
    assert any("code decided" in o for o in out)
    assert not any(o.startswith("flowering ▶") for o in out)


def test_a_d0_escalation_flowers_over_the_whole_served_file():
    sent = []
    api = FakeApi(escalate=chain_result(piece("d0", reason="d0_escalate")))
    st, _out = seat(
        api,
        ["who", "", "the task", "y", ""],
        flower=lambda p, q: sent.append(p) or {"code": 0, "summary": "", "rows": []},
    )
    st.run()
    assert sent == [DOC]


def test_a_piece_missing_from_the_served_file_is_unreachable_not_guessed():
    api = FakeApi(escalate=chain_result(piece("local")))
    st, out = seat(api, ["who", "", "the task", ""], pieces=[])
    st.run()
    assert "[unreachable] flowering" in text(out)
    assert "the piece isn't in the served file" in text(out)


def test_a_cloud_escalate_row_is_never_a_proposal():
    esc = {"path": "ESCALATE", "data": "", "cites": [], "claim": "can't"}
    api = FakeApi(escalate=chain_result(piece("local")))
    st, out = seat(
        api,
        ["who", "", "the task", "y", ""],
        pieces=[{"hash": "h" * 64, "piece": {}}],
        flower=lambda p, q: {"code": 0, "summary": "", "rows": [esc]},
    )
    st.run()
    assert "take_proposals" not in api.names()
    assert any("stays on the human card" in o for o in out)


def test_a_judged_row_that_did_not_pass_is_shown_not_offered():
    api = FakeApi(
        escalate=chain_result(piece("local")),
        take_proposals={
            "out": {
                "proposals": [
                    {
                        "verdict": "link_fail",
                        "reason": "a cite is not in the served file",
                    }
                ]
            }
        },
    )
    st, out = seat(
        api,
        ["who", "", "the task", "y", ""],
        pieces=[{"hash": "h" * 64, "piece": {}}],
        flower=lambda p, q: {"code": 0, "summary": "", "rows": [ROW]},
    )
    st.run()
    assert "[blocked] link_fail" in text(out)
    assert "a cite is not in the served file" in text(out)
    assert not any("pooled:" in o for o in out)


# --- the close-out deposit -------------------------------------------------------------

POOL = {"pooled": [{"subject": SUBJ, **ROW}], "count": 1, "code": 0}
DEPOSITED = {
    "ok": True,
    "state": "populated",
    "count": 2,
    "deposited": [
        {"subject": SUBJ, "record_id": "r1", "pair_id": "p1", "status": "proposed"},
        {"subject": "proposal:bad", "status": "error", "error": "empty_claim"},
    ],
}


def test_checkout_deposits_the_pool_and_makes_one_seal_offer():
    api = FakeApi(pooled=POOL)
    dep = FakeDeposit(DEPOSITED)
    st, out = seat(api, ["who", "", ""], deposit=dep)
    st.run()
    assert dep.pools == [POOL]  # the deposit saw what api.pooled read
    at = lambda frag: next(i for i, o in enumerate(out) if frag in o)  # noqa: E731
    assert at("MORNING SCREEN") < at("2 in Nestor as drafts")
    assert at(SUBJ) and "| proposed" in out
    assert "| ERROR: empty_claim" in out  # an error pair, verbatim
    assert text(out).count("seal ↗") == 1 and s.NESTOR_UI in text(out)
    assert f"to seal: {SUBJ}" in text(out)  # the offer lists the deposited subjects
    assert not [n for n in api.names() if n.startswith("seal")]


def test_checkout_deposits_even_when_the_run_ended_early():
    dep = FakeDeposit(DEPOSITED)
    st, _out = seat(FakeApi(pooled=POOL), ["who"], deposit=dep)  # EOF at served
    st.run()
    assert len(dep.pools) == 1


def test_an_empty_pool_is_said_empty_and_offers_no_seal():
    st, out = seat(FakeApi(), ["who", "", ""])
    st.run()
    assert "[empty] deposit" in text(out) and "empty — the pool is empty" in text(out)
    assert not any("seal ↗" in o for o in out)


def test_an_unavailable_deposit_is_unreachable_not_empty_and_lists_the_pool():
    gone = {"state": "unreachable", "reason": s.NO_DEPOSIT}
    st, out = seat(FakeApi(pooled=POOL), ["who", "", ""], deposit=FakeDeposit(gone))
    st.run()
    assert "[unreachable] deposit" in text(out) and s.NO_DEPOSIT in text(out)
    assert "[changed] pooled, not deposited" in text(out) and SUBJ in text(out)
    assert "[empty] deposit" not in text(out)
    assert not any("seal ↗" in o for o in out)


def test_a_deposit_that_raises_is_unreachable_and_never_ends_the_close_out():
    dep = FakeDeposit(RuntimeError("db down"))
    st, out = seat(FakeApi(pooled=POOL), ["who", "", ""], deposit=dep)
    assert st.run() == 0
    assert "[unreachable] deposit" in text(out)
    assert "unreachable — RuntimeError: db down" in text(out)
    assert "pooled, not deposited" in text(out) and SUBJ in text(out)


def test_a_refused_pool_read_is_unreachable_and_deposits_nothing():
    dep = FakeDeposit(DEPOSITED)
    api = FakeApi(pooled={"refused": "box won't open", "code": 2})
    st, out = seat(api, ["who", "", ""], deposit=dep)
    st.run()
    assert "[unreachable] pool" in text(out) and "box won't open" in text(out)
    assert dep.pools == []


def test_a_pool_read_that_raises_is_unreachable_not_a_traceback():
    """F8: api.pooled itself raising must not escape the close-out."""

    def boom(*a, **k):
        raise RuntimeError("pool db down")

    dep = FakeDeposit(DEPOSITED)
    st, out = seat(FakeApi(pooled=boom), ["who", "", ""], deposit=dep)
    assert st.run() == 0
    assert "[unreachable] pool" in text(out)
    assert "unreachable — RuntimeError: pool db down" in text(out)
    assert dep.pools == [] and "seal ↗" not in text(out)


# --- the box stream ----------------------------------------------------------------

NEEDS = bx.Box("b5", "you", "needs you", "Ratify the work order", "local-flow §7")


def test_a_box_renders_its_kind_label_value_and_detail_plain():
    assert bx.render_box(NEEDS) == (
        "+- [needs you] needs you  b5\n| Ratify the work order\n| local-flow §7"
    )
    for kind, name in (
        ("dec", "decided"),
        ("pr", "changed"),
        ("block", "blocked"),
        ("pass", "routine pass"),
    ):
        assert f"[{name}]" in bx.render_box(bx.Box("x", kind, "l", "v"))


def test_a_64_char_hash_is_cut_to_twelve():
    h = "ab12" * 16
    got = bx.render_box(bx.Box(h, "pass", "pin", f"at {h}"))
    assert h not in got and h[:12] in got


def test_the_three_states_render_distinctly_and_say_why():
    full = bx.render_box(bx.Box("a", "pass", "served", "populated"))
    empty = bx.render_box(bx.Box("a", "pass", "served", "over the cap", state="empty"))
    gone = bx.render_box(
        bx.Box("a", "pass", "served", "no serve key", state="unreachable")
    )
    assert (
        full.startswith("+- [routine pass]") and full.splitlines()[1] == "| populated"
    )
    assert empty.startswith("+. [empty]") and empty.splitlines()[1] == ": over the cap"
    assert (
        gone.startswith("+! [unreachable]") and gone.splitlines()[1] == "! no serve key"
    )
    assert len({full[:2], empty[:2], gone[:2]}) == 3


def test_a_driven_run_never_collapses_unreachable_into_empty():
    api = FakeApi(serve={"doc": {}, "state": "unreachable", "why": "no serve key"})
    st, out = seat(api, ["who", "", ""])
    st.run()
    assert "[unreachable] served" in text(out) and "[empty] served" not in text(out)


def test_plain_cards_carry_no_escape_codes_off_a_tty(monkeypatch):
    class Pipe:
        def isatty(self):
            return False

    monkeypatch.setattr(sys, "stdout", Pipe())
    monkeypatch.delenv("NO_COLOR", raising=False)
    st, out = seat(FakeApi(pooled=POOL), ["who", "", "the task", ""], color=None)
    st.run()
    assert "\x1b" not in text(out) and "[routine pass]" in text(out)


@pytest.mark.parametrize(
    "tty, no_color, colored",
    [(True, None, True), (True, "1", False), (False, None, False), (False, "1", False)],
)
def test_color_needs_a_tty_and_no_no_color(tty, no_color, colored):
    class Out:
        def isatty(self):
            return tty

    env = {} if no_color is None else {"NO_COLOR": no_color}
    assert bx.use_color(Out(), env) is colored


def test_a_colored_card_is_the_plain_card_with_escapes():
    plain = bx.render_box(NEEDS)
    hot = bx.render_box(NEEDS, color=True)
    assert "\x1b[" in hot and ANSI.sub("", hot) == plain
    assert "38;2;230;179;76" in hot  # needs-you is the sun


def chip_at(out, start=0):
    """Index of the first chip row at or after ``start``."""
    return next(i for i in range(start, len(out)) if out[i].startswith("chips:"))


def lines_ok(out):
    """Every printed line is a card row, a reply line, the human's, or chrome."""
    ok = ("+", "|", ":", "!", "agent ·", "agent>", "you:")
    chrome = ("as noted at", "the pile ·", "legend:", "chips:")
    bad = []
    for o in out:
        if not o or o.startswith(ok) or o.startswith(chrome) or " ▶ " in o:
            continue
        bad.append(o)
    return bad


def rich_run(**seat_kw):
    pieces = [
        piece("local", "answered", h="a" * 64, rows=[ROW]),
        piece("local", h="b" * 64),
        piece("d0", "answered", h="c" * 64),
    ]
    api = FakeApi(
        escalate=chain_result(*pieces),
        pooled=POOL,
        take_proposals={
            "out": {"proposals": [{**ROW, "verdict": "pass", "subject": SUBJ}]}
        },
    )
    keys = ["who", "", "the task", "", "n", "thanks", "later", "The  TASK", "", ""]
    keys = seat_kw.pop("keys", keys)
    st, out = seat(
        api,
        keys,
        pieces=[{"hash": "b" * 64, "piece": {}}],
        deposit=FakeDeposit(DEPOSITED),
        **seat_kw,
    )
    st.run()
    return api, out


def test_everything_the_agent_says_is_inside_a_box_and_the_humans_line_is_plain():
    _api, out = rich_run()
    assert lines_ok(out) == []
    assert "you: the task" in out  # plain, marked `you`, not a card row


def test_the_pile_header_and_legend_come_before_the_turns():
    _api, out = rich_run()
    n = next(i for i, o in enumerate(out) if o.startswith("the pile ·"))
    assert out[n] == "the pile · 2 boxes on the record"
    assert out[n + 1].startswith("legend: needs you · decided · changed · blocked")
    assert n < next(i for i, o in enumerate(out) if o.startswith("chain ▶"))


def test_a_reply_is_boxes_then_one_sentence_from_the_boxes():
    _api, out = rich_run()
    t = text(out)
    assert "agent · code · said 2 boxes, no model asked" in t
    # the opening took the run's one "Morning." (O2), so this first reply has none
    first = next(
        o
        for i, o in enumerate(out)
        if o.startswith("agent> ") and out[i - 1].startswith("agent · code · said")
    )
    # "escalated 1" is still a problem count (no reassurance over it, 3b-ii,
    # Loki F-low), but the chain summary is said as a sentence, with no
    # "Heads up:" before a bare count (F6)
    assert first == (
        "agent> Local: d is still blocked, reason: local_escalate. "
        "The chain answered 2 and escalated 1."
    )
    assert out.index("agent · code · said 2 boxes, no model asked") < out.index(first)


def test_more_shows_the_next_boxes_and_declining_keeps_them_in_the_pile():
    _api, out = rich_run()
    t = text(out)
    assert t.count("more? ▶") == 1 and "you: more" in out
    assert "agent> Oh, and local: d and d0: d are both routine. No rush." in t
    _api2, out2 = rich_run(keys=["who", "", "the task", "later", ""])
    assert "agent> Got it. It stays in the pile." in out2
    assert "agent> Oh, and" not in text(out2)  # the rest stayed in the pile


def test_small_talk_is_answered_by_code_with_no_boxes_and_no_api_call():
    api = FakeApi()
    st, out = seat(api, ["who", "", "thanks", "later", ""])
    st.run()
    assert "agent · code · no model, nothing served" in out
    assert "agent> Anytime." in out and "agent> Got it. It stays in the pile." in out
    assert "escalate" not in api.names()
    chat = out[out.index("you: thanks") :]
    assert not any(o.startswith(("+", "|")) for o in chat[:5])


def test_a_question_asked_again_is_shown_from_the_pile_with_its_timestamp():
    ticks = iter(["09:14", "09:14", "09:40", "09:41"])  # the opening reads one
    pieces = [piece("local", "answered", rows=[ROW])]
    api = FakeApi(escalate=chain_result(*pieces))
    st, out = seat(
        api,
        ["who", "", "status of the build", "Status  of the build", ""],
        clock=lambda: next(ticks),
    )
    st.run()
    assert api.names().count("escalate") == 1  # asked again: not recomputed
    stamp = "as noted at 09:14 · same boxes, nothing new since"
    assert out.count(stamp) == 1
    cards = lambda block: [o for o in block if o[:1] in "+|"]  # noqa: E731
    i1 = out.index("you: status of the build")
    i2 = out.index(stamp)
    first_cards = cards(out[i1 : chip_at(out, i1)])
    assert first_cards and cards(out[i2 : chip_at(out, i2)]) == first_cards
    assert "agent · code · shown again from the pile, no model asked now" in out
    assert "09:40" not in text(out)  # the second asking did not restamp


def test_the_sentence_is_glue_plus_box_facts_only():
    a = bx.Box("b1", "you", "needs you", "Ratify the work order")
    b = bx.Box("b2", "block", "blocked", "PR 712 waiting")
    c = bx.Box("b3", "pr", "changed", "PR 127 open")
    d = bx.Box("b4", "pr", "changed", "PR 714 open")
    assert bx.compose([a, b]) == (
        "You need to ratify the work order. PR 712's still waiting."
    )
    assert bx.compose([a, b], greet="Morning.").startswith("Morning. You need")
    assert bx.compose([c, d], first=False) == (
        "Oh, and PR 127 and PR 714 are both open. No rush."
    )
    assert bx.compose([c, d], page=2).startswith("Also, PR 127")
    assert bx.compose([c, d]) == "Looks like PR 127 and PR 714 are both open. No rush."
    down = bx.Box("b5", "pass", "served", "unreachable — no key", state="unreachable")
    assert bx.compose([down]) == "Heads up: I can't read the record right now. No key."
    assert bx.compose([]) == ""
    for word in ("morning", "still", "both", "heads up", "no rush", "looks like"):
        assert word in bx.GLUE


def test_the_pool_reads_into_the_states_the_deposit_expects():
    assert s.pool_state({"refused": "no box", "code": 2}) == {
        "state": "unreachable",
        "reason": "no box",
    }
    assert s.pool_state({"pooled": [], "count": 0, "code": 0}) == {
        "state": "empty",
        "reason": "the pool is empty",
    }
    assert s.pool_state(POOL) == {
        "state": "populated",
        "stdout_json": {"pooled": POOL["pooled"]},
    }


def test_the_default_deposit_is_unreachable_where_willow_mcp_is_absent(monkeypatch):
    for mod in ("willow_mcp", "willow_mcp.db", "willow_mcp.onescript_deposit"):
        monkeypatch.setitem(sys.modules, mod, None)  # import raises ImportError
    got = s.willow_mcp_deposit()(POOL)
    assert got["state"] == "unreachable" and s.NO_DEPOSIT in got["reason"]


def test_the_default_deposit_proposes_through_willow_mcp(monkeypatch):
    import types

    seen = {}

    def put(app_id, *, store, read_pool):
        seen["app"], seen["store"], seen["pool"] = app_id, store, read_pool()
        return {"state": "populated", "deposited": []}

    pkg = types.ModuleType("willow_mcp")
    db = types.ModuleType("willow_mcp.db")
    db.Store = lambda: "store"
    dep = types.ModuleType("willow_mcp.onescript_deposit")
    dep.deposit = put
    for name, mod in (
        ("willow_mcp", pkg),
        ("willow_mcp.db", db),
        ("willow_mcp.onescript_deposit", dep),
    ):
        monkeypatch.setitem(sys.modules, name, mod)
    assert s.willow_mcp_deposit()(POOL)["state"] == "populated"
    assert seen == {"app": "willow", "store": "store", "pool": s.pool_state(POOL)}


# --- the Rat rung -------------------------------------------------------------------


def fake_rat(tmp_path, body: str):
    """A stand-in `ratatosk` that records its argv and runs `body`."""
    script = tmp_path / "rat.py"
    script.write_text(
        "import json, sys\n"
        "a = sys.argv[1:]\n"
        f"open({str(tmp_path / 'argv.json')!r}, 'w').write(json.dumps(a))\n"
        "out = a[a.index('--out') + 1]\n" + body,
        encoding="utf-8",
    )
    return (sys.executable, str(script))


def test_the_rat_rung_asks_for_the_flowering_class_and_reads_rows(tmp_path):
    rat = fake_rat(
        tmp_path,
        f"open(out, 'w').write({json.dumps(json.dumps(ROW))} + '\\n')\n"
        "print('[onescript] rung=groq end=done')\n",
    )
    got = s.ratatosk_flowering(rat)({"tables": []}, "the task")
    argv = json.loads((tmp_path / "argv.json").read_text())
    assert argv[:3] == ["--onescript", "--class", "flowering"]
    assert "--model" not in argv and "--rung" not in argv
    assert argv[-1] == "the task"
    assert got == {
        "code": 0,
        "summary": "[onescript] rung=groq end=done",
        "rows": [ROW],
    }


def test_the_rat_rung_reports_a_refusal(tmp_path):
    rat = fake_rat(
        tmp_path,
        "sys.stderr.write('[onescript] refused: no usable rung'); sys.exit(2)\n",
    )
    got = s.ratatosk_flowering(rat)({}, "q")
    assert got["code"] == 2 and "no usable rung" in got["summary"] and got["rows"] == []


def test_the_rat_rung_has_a_timeout(tmp_path):
    rat = fake_rat(tmp_path, "import time; time.sleep(5)\n")
    got = s.ratatosk_flowering(rat, timeout=0.5)({}, "q")
    assert got["code"] == 1 and "no return" in got["summary"]


def test_a_missing_rat_is_said_not_raised():
    got = s.ratatosk_flowering(("/nonexistent/ratatosk",))({}, "q")
    assert got["code"] == 2 and "can't run" in got["summary"]


# --- finding willow-bot -------------------------------------------------------------


def test_no_willow_bot_is_unreachable(tmp_path):
    with pytest.raises(s.SeatUnavailable, match="unreachable"):
        s.load_bot(tmp_path)


def test_willow_bot_root_comes_from_the_env_then_beside_the_grove(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("WILLOW_BOT_ROOT", str(tmp_path))
    assert s.bot_root() == tmp_path
    monkeypatch.delenv("WILLOW_BOT_ROOT")
    assert s.bot_root() == s.GROVE_ROOT.parent / "willow-bot"


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="scripts/grove-seat is a POSIX launcher; a Windows runner's bare "
    "`bash` is the WSL stub (as with scripts/grove-serve-run)",
)
def test_the_launcher_reports_no_willow_bot(tmp_path):
    done = subprocess.run(
        ["bash", str(s.GROVE_ROOT / "scripts" / "grove-seat")],
        env={"PATH": "/usr/bin:/bin", "WILLOW_BOT_ROOT": str(tmp_path)},
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert done.returncode == 2 and "unreachable" in done.stderr


# --- 3b-ii: the local model's sentence, the four checks, the fallback -------------

MODEL = say_mod.MODEL
GOOD_CODE = "agent> Looks like the chain answered 1 and escalated 0. Local: d. No rush."


def tagged(make):
    """A fake `say`: reads the box tags out of the prompt it is given and
    returns ``make(*tags)``. Records every prompt."""

    def say(prompt):
        say.prompts.append(prompt)
        return make(*re.findall(r"^\[(\w+)\] ", prompt, re.M))

    say.prompts = []
    return say


def good(a, b):
    return f"Looks like both answered 1, escalated 0 [{a}] and local: d [{b}]."


def model_run(say, keys=("who", "", "the task", ""), **over):
    api = FakeApi(escalate=chain_result(piece("local", "answered")), **over)
    st, out = seat(api, list(keys), say=say)
    return st.run(), out, api


def test_a_model_sentence_that_passes_stands_with_its_four_chips():
    say = tagged(good)
    code, out, _api = model_run(say)
    assert code == 0
    assert f"agent · {MODEL} · said 2 boxes" in out
    sentence = next(o for o in out if o.startswith("agent> Looks like"))
    assert re.fullmatch(
        r"agent> Looks like both .* \[\w+\] and local: d \[\w+\]\.", sentence
    )
    assert (
        "checks: ✓ every cite was served · ✓ every box cited · "
        "✓ nothing the boxes lack · – your words quoted exactly (none quoted)"
    ) in out
    assert "[struck]" not in text(out) and GOOD_CODE not in out
    assert len(say.prompts) == 1


def test_the_prompt_carries_the_facts_the_glue_the_voice_and_the_human():
    say = tagged(good)
    model_run(say)
    p = say.prompts[0]
    assert "answered 1, escalated 0" in p and "local: d" in p
    assert "The human asked: the task" in p
    assert all(w in p for w in bx.GLUE)
    assert say_mod.VOICE in p and "glue words only" in say_mod.VOICE


BAD = {
    "cite-unserved": (lambda a, b: good(a, b).replace("d [", "d [zz9] ["), 0),
    "box-omitted": (lambda a, b: f"Looks like answered 1, escalated 0 [{a}].", 1),
    "invented-fact": (
        lambda a, b: (
            f"Looks like both answered 140, escalated 0 [{a}] and local: d [{b}]."
        ),
        2,
    ),
    "misquote": (
        lambda a, b: (
            f'Looks like both "answered 1, escalated 0" [{a}] and local: d [{b}].'
        ),
        3,
    ),
}


@pytest.mark.parametrize("which", sorted(BAD))
def test_each_check_catches_its_violation_and_code_replaces_the_sentence(which):
    make, idx = BAD[which]
    code, out, _api = model_run(tagged(make))
    assert code == 0
    assert f"agent · {MODEL} · failed a check · replaced by a code sentence" in out
    struck = next(o for o in out if o.startswith("agent> ~~"))
    assert struck.endswith("~~ [struck]")
    chips = next(o for o in out if o.startswith("checks:"))
    marks = [c.strip()[0] for c in chips.removeprefix("checks:").split(" · ")]
    assert marks[idx] == "✗" and marks.count("✗") == 1, chips
    assert out.index(struck) < out.index(GOOD_CODE)  # the code sentence beneath it
    said = [o for o in out if o.startswith("agent> ") and "~~" not in o]
    # stage lines, the opening (O2) and the closing (O4) aside
    assert [o for o in said if " is empty" not in o and "pooled" not in o] == [
        GOOD_CODE
    ]


def test_an_invented_word_fails_nothing_the_boxes_lack_so_voice_cannot_add_a_fact():
    wow = lambda a, b: f"Wow, great news: {good(a, b)}"  # noqa: E731
    _code, out, _api = model_run(tagged(wow))
    assert "[struck]" in text(out) and "✗ nothing the boxes lack" in text(out)


def test_checks_by_hand():
    a = bx.Box("b1", "block", "blocked", "PR 712 waiting", "126 tests pass")
    b = bx.Box("b2", "you", "needs you", "Ratify the work order")
    both = [a, b]
    ok = "Morning. PR 712's still waiting, 126 tests pass [b1]. Ratify the work order [b2]."
    assert say_mod.run_checks(ok, both) == [True, True, True, "na"]
    assert say_mod.check_cites_served("x [b1] [b9]", both) is False
    assert say_mod.check_boxes_cited("x [b1]", both) is False
    assert say_mod.check_nothing_lacking(ok.replace("126", "140"), both) is False
    assert (
        say_mod.check_nothing_lacking(ok.replace("waiting", "failing"), both) is False
    )
    said = 'You said "where are we" [b1] [b2]'
    assert say_mod.check_quotes(said, "where  are WE today") is True
    assert say_mod.check_quotes(said, "what is up") is False
    assert say_mod.check_quotes("no quote here", "x") == "na"


def test_a_quoted_number_the_human_said_still_has_to_come_from_a_box():
    # Loki C1: the human's question carries 500; no box does.
    boxes = [
        bx.Box("b1", "pass", "check", "error fixed"),
        bx.Box("b2", "pass", "p", "x"),
    ]
    human = "is the 500 error fixed"
    s_ = 'Looks like both "500" error fixed [b1] [b2]'
    assert say_mod.check_quotes(s_, human) is True  # it IS the human's word
    assert say_mod.check_nothing_lacking(s_, boxes, human) is False
    assert say_mod.run_checks(s_, boxes, human)[2] is False
    # a quote of a value an actual box holds is not struck
    held = [bx.Box("b1", "pass", "check", "500 error fixed"), boxes[1]]
    ok = 'Looks like "500" error fixed [b1] and x [b2]'
    assert say_mod.check_nothing_lacking(ok, held, human) is True
    assert say_mod.run_checks(ok, held, human) == [True, True, True, True]


def test_a_verbatim_quote_of_the_humans_words_passes_but_only_the_words():
    boxes = [bx.Box("b1", "pass", "chain", "answered 1")]
    human = "where are we"
    quoted = 'Looks like "where are we" answered 1 [b1].'
    assert say_mod.check_quotes(quoted, human) is True
    assert say_mod.check_nothing_lacking(quoted, boxes, human) is True
    assert say_mod.run_checks(quoted, boxes, human) == [True, True, True, True]
    # the same words unquoted are the model's own and still fail
    bare = "Looks like where are we answered 1 [b1]."
    assert say_mod.check_nothing_lacking(bare, boxes, human) is False
    # a quoted span that is not the human's gets no pass
    other = 'Looks like "who goes there" answered 1 [b1].'
    assert say_mod.check_nothing_lacking(other, boxes, human) is False
    # an invented word beside a good quote still fails
    extra = 'Looks like "where are we" zebra answered 1 [b1].'
    assert say_mod.check_nothing_lacking(extra, boxes, human) is False
    # a non-Latin word outside the quote still fails closed
    cyr = 'Looks like "where are we" Иван answered 1 [b1].'
    assert say_mod.check_nothing_lacking(cyr, boxes, human) is False
    # a number in a verbatim quote still has to come from a box
    num = 'Looks like "where are 500" answered 1 [b1].'
    assert say_mod.check_nothing_lacking(num, boxes, "where are 500") is False


def test_a_word_in_a_script_the_scan_cant_read_fails_closed():
    boxes = [bx.Box("b1", "pass", "chain", "answered 1")]
    latin = "Looks like answered 1 [b1]."
    assert say_mod.check_nothing_lacking(latin, boxes) is True
    assert (
        say_mod.check_nothing_lacking("Looks like answered 1 Иван [b1].", boxes)
        is False
    )
    assert (
        say_mod.check_nothing_lacking("Looks like answered 1 я [b1].", boxes) is False
    )
    assert (
        say_mod.check_nothing_lacking("Looks like answered 1 李 [b1].", boxes) is False
    )
    # accents fold; a non-Latin word the box itself holds is the box's word
    cafe = [bx.Box("b1", "pass", "chain", "café ok")]
    assert say_mod.check_nothing_lacking("Looks like cafe ok [b1].", cafe) is True
    ivan = [bx.Box("b1", "pass", "chain", "Иван ok")]
    assert say_mod.check_nothing_lacking("Looks like Иван ok [b1].", ivan) is True


def test_a_cites_only_string_is_not_a_sentence_and_code_says_the_line():
    boxes = [bx.Box("b1", "pass", "chain", "answered 1")]
    for empty in ("[b1]", " [b1] . ", "[b1] 1"):
        assert say_mod.check_nothing_lacking(empty, boxes) is False, empty
        assert say_mod.passed(say_mod.run_checks(empty, boxes)) is False, empty
    code, out, _api = model_run(tagged(lambda a, b: f"[{a}] [{b}]"))
    assert code == 0
    assert f"agent · {MODEL} · failed a check · replaced by a code sentence" in out
    assert any(o.startswith("agent> ~~[") and o.endswith("[struck]") for o in out)
    assert GOOD_CODE in out


def test_a_nonzero_value_suppresses_no_rush():
    calm = bx.Box("b1", "pass", "chain", "answered 2, escalated 0")
    for bad in (
        bx.Box("b2", "pass", "exit", "exit non-zero"),
        bx.Box("b3", "pass", "exit", "ended", "returned nonzero"),
    ):
        assert "No rush" not in bx.compose([bad]), bad
        assert "No rush" not in bx.compose([calm, bad])
    assert bx.compose([calm]).endswith("No rush.")


def test_a_quote_the_one_scripts_gate_cant_verify_fails_even_if_it_reads_right():
    seen = []

    def claims(text_, facts):
        seen.append(facts)
        return [{"kind": "quote", "verdict": "unverified"}]

    s_ = 'Looks like "where are we" [b1] [b2].'
    both = [bx.Box("b1", "pass", "chain", "x"), bx.Box("b2", "pass", "p", "y")]
    assert say_mod.check_quotes(s_, "where are we") is True
    assert say_mod.check_quotes(s_, "where are we", claims) is False
    assert seen == [{"operator_text": "where are we"}]
    boom = lambda *a: (_ for _ in ()).throw(RuntimeError("gate down"))  # noqa: E731
    assert say_mod.check_quotes(s_, "where are we", boom) is False
    assert say_mod.run_checks(s_, both, "where are we")[3] is True


def test_load_bot_hands_the_seat_the_one_scripts_claims_gate(
    monkeypatch, request, tmp_path
):
    """A one script on disk (the real reach and states, stubs for the rest),
    found through the one reach (flatten-2 F6.5); nothing of an earlier import
    is reused, and nothing of this one is left behind."""
    got = os.environ.get("WILLOW_BOT_ROOT")
    real = Path(got) / "one-script" if got else onescript_reach.where()["onescript"]
    if real is None or not (real / "onescript" / "reach.py").is_file():
        if os.environ.get("CI"):
            pytest.fail(f"CI has no willow-bot's one script at {real}")
        pytest.skip("willow-bot's one script is not beside this repo")
    pkg = tmp_path / "one-script" / "onescript"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    for name in ("states", "reach"):
        (pkg / f"{name}.py").write_text(
            (real / "onescript" / f"{name}.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    (pkg / "api.py").write_text("", encoding="utf-8")
    (pkg / "escalate.py").write_text("cut = len\nPIECE_CHARS = 7\n", encoding="utf-8")
    (pkg / "gate.py").write_text('check_claims = "the gate"\n', encoding="utf-8")
    (pkg / "proposals.py").write_text("subject = str\n", encoding="utf-8")

    def ours(m):
        return m == "onescript" or m.startswith("onescript.")

    before = {m: mod for m, mod in sys.modules.items() if ours(m)}
    for name in before:
        del sys.modules[name]

    def put_back():
        for name in [m for m in sys.modules if ours(m)]:
            del sys.modules[name]
        sys.modules.update(before)

    request.addfinalizer(put_back)
    monkeypatch.setattr(sys, "path", list(sys.path))
    assert s.load_bot(tmp_path).claims == "the gate"


@pytest.mark.parametrize(
    "boom, state, why",
    [
        (
            say_mod.SayUnreachable("connection refused"),
            "unreachable",
            "connection refused",
        ),
        (RuntimeError("model crashed"), "unreachable", "RuntimeError: model crashed"),
        ("   ", "empty", "said nothing"),
    ],
)
def test_a_model_that_cant_be_asked_is_its_own_state_and_code_says_the_line(
    boom, state, why
):
    def say(prompt):
        if isinstance(boom, BaseException):
            raise boom
        return boom

    code, out, _api = model_run(say)
    assert code == 0
    assert f"[{state}] say" in text(out) and f"{state} — {MODEL}: {why}" in text(out)
    other = "empty" if state == "unreachable" else "unreachable"
    assert f"[{other}] say" not in text(out)  # never collapsed into the other state
    assert f"agent · code · {MODEL} {state} · said 2 boxes by code" in out
    assert GOOD_CODE in out and "checks:" not in text(out)  # code's line, no chips


def test_asked_again_replays_the_model_reply_without_asking_the_model():
    say = tagged(good)
    ticks = iter(["09:14", "09:14", "09:40", "09:41"])  # the opening reads one
    api = FakeApi(escalate=chain_result(piece("local", "answered")))
    out: list[str] = []
    keys = iter(["who", "", "status of the build", "Status  of the build", ""])

    def read(prompt):
        out.append(prompt)
        try:
            return next(keys)
        except StopIteration:
            raise EOFError from None

    st = s.Seat(
        bot(api),
        cfg="cfg",
        deposit=FakeDeposit(),
        say=say,
        read=read,
        write=out.append,
        color=False,
        clock=lambda: next(ticks),
    )
    st.run()
    assert len(say.prompts) == 1 and api.names().count("escalate") == 1
    assert (
        f"agent · {MODEL} at 09:14 · shown again from the pile, no model asked now"
        in out
    )
    assert any(
        o.startswith("checks as they passed at 09:14: ✓ every cite") for o in out
    )


def test_a_struck_reply_is_replayed_struck():
    bad = BAD["invented-fact"][0]
    api = FakeApi(escalate=chain_result(piece("local", "answered")))
    ticks = iter(["09:14", "09:14", "09:40"])  # the opening reads one
    out: list[str] = []
    keys = iter(["who", "", "q", "Q", ""])

    def read(prompt):
        try:
            return next(keys)
        except StopIteration:
            raise EOFError from None

    s.Seat(
        bot(api),
        cfg="cfg",
        deposit=FakeDeposit(),
        say=tagged(bad),
        read=read,
        write=out.append,
        color=False,
        clock=lambda: next(ticks),
    ).run()
    assert sum(o.endswith("~~ [struck]") for o in out) == 2
    assert sum(o == GOOD_CODE for o in out) == 2


def test_a_struck_sentence_is_marked_in_words_and_in_color_only_by_addition():
    plain = bx.struck_line("a b")
    hot = bx.struck_line("a b", color=True)
    assert plain == "agent> ~~a b~~ [struck]"
    assert "\x1b[9" in hot and ANSI.sub("", hot) == plain


def test_no_say_is_the_code_only_seat_and_never_touches_ollama(monkeypatch):
    monkeypatch.setattr(
        say_mod.urllib.request,
        "build_opener",
        lambda *a: pytest.fail("the code-only seat reached for Ollama"),
    )
    code, out, _api = model_run(None)
    assert code == 0 and GOOD_CODE in out
    assert "agent · code · said 2 boxes, no model asked" in out


def test_main_wires_the_ollama_say(monkeypatch):
    seen = {}

    class Fake:
        def __init__(self, bot_, cfg, **kw):
            seen.update(kw)

        def run(self):
            return 0

    monkeypatch.setattr(s, "load_bot", lambda root: "bot")
    monkeypatch.setattr(s, "config", lambda b, r: "cfg")
    monkeypatch.setattr(s, "Seat", Fake)
    assert s.main() == 0 and callable(seen["say"])


# --- flags that write nothing: --help, --version, a bad flag, --check -----------------


@pytest.fixture
def no_session(monkeypatch):
    """Tripwires: a flag path must not load the bot, build a Seat or check in."""
    monkeypatch.setattr(s, "load_bot", lambda root: pytest.fail("the bot was loaded"))
    monkeypatch.setattr(s, "Seat", lambda *a, **k: pytest.fail("a session was opened"))


def test_help_prints_usage_and_exits_0_without_a_session(no_session, capsys):
    assert s.main(["--help"]) == 0
    out = capsys.readouterr().out
    assert "usage: grove-seat" in out and "--check" in out


def test_version_prints_the_grove_version_and_exits_0(no_session, capsys):
    assert s.main(["--version"]) == 0
    out = capsys.readouterr().out.strip()
    assert out == f"grove-seat {s.grove_version()}"
    assert re.fullmatch(r"grove-seat \d+\.\d+\.\d+.*", out)


@pytest.mark.parametrize("argv", [["--chek"], ["stray"], ["--check", "--bogus"]])
def test_an_unknown_flag_or_argument_exits_2_before_the_bot_loads(
    no_session, capsys, argv
):
    assert s.main(argv) == 2
    assert "usage: grove-seat" in capsys.readouterr().err


def bot_tree(tmp_path):
    api = tmp_path / "one-script" / "onescript" / "api.py"
    api.parent.mkdir(parents=True)
    api.write_text("", encoding="utf-8")
    return tmp_path


def probed(monkeypatch, tmp_path, *, root=True, ollama=("populated", "up"), rat=True):
    monkeypatch.setenv("WILLOW_BOT_ROOT", str(bot_tree(tmp_path) if root else tmp_path))
    monkeypatch.setattr(s, "ollama_probe", lambda model: ollama)
    monkeypatch.setattr(
        s, "resolve_ratatosk", lambda: sys.executable if rat else "nope"
    )
    monkeypatch.setattr(s.shutil, "which", lambda name: None)


def test_check_all_populated_exits_0_and_checks_in_nothing(
    no_session, monkeypatch, tmp_path, capsys
):
    probed(monkeypatch, tmp_path)
    assert s.main(["--check"]) == 0
    out = capsys.readouterr().out.splitlines()
    assert [ln.split()[0] for ln in out] == ["bot", "python", "ratatosk", "ollama"]
    assert all(" populated" in ln for ln in out)


@pytest.mark.parametrize(
    ("over", "label", "state"),
    [
        ({"root": False}, "bot root", "unreachable"),
        ({"rat": False}, "ratatosk", "unreachable"),
        ({"ollama": ("unreachable", "refused")}, "ollama", "unreachable"),
        ({"ollama": ("empty", "qwen3:4b is not installed")}, "ollama", "empty"),
    ],
)
def test_check_names_each_failure_in_its_own_state_and_exits_nonzero(
    no_session, monkeypatch, tmp_path, capsys, over, label, state
):
    probed(monkeypatch, tmp_path, **over)
    assert s.main(["--check"]) == 1
    lines = capsys.readouterr().out.splitlines()
    mine = next(ln for ln in lines if ln.startswith(label))
    assert f" {state}" in mine
    assert sum("populated" in ln for ln in lines) == 3


def test_check_never_calls_the_api(monkeypatch, tmp_path, capsys):
    api = FakeApi()
    probed(monkeypatch, tmp_path)
    monkeypatch.setattr(s, "load_bot", lambda root: bot(api))
    assert s.main(["--check"]) == 0
    assert api.calls == []


def test_the_probe_reads_tags_and_tells_up_from_installed():
    tags = json.dumps({"models": [{"name": "qwen3:4b"}]}).encode()
    op = Opener(tags)
    assert say_mod.ollama_probe("qwen3:4b", "127.0.0.1:11434", opener=op)[0] == (
        "populated"
    )
    req, timeout = op.seen[0]
    assert req.full_url == "http://127.0.0.1:11434/api/tags"
    assert req.data is None and timeout == 2.0
    state, why = say_mod.ollama_probe("llama3.2:3b", opener=Opener(tags))
    assert state == "empty" and "not installed" in why


@pytest.mark.parametrize(
    "result", [OSError("refused"), b"not json", json.dumps({"x": 1}).encode()]
)
def test_the_probe_is_unreachable_not_empty_when_it_gets_no_answer(result):
    assert say_mod.ollama_probe(opener=Opener(result))[0] == "unreachable"


def test_the_probe_refuses_a_non_loopback_host_without_asking():
    op = Opener(b"{}")
    state, why = say_mod.ollama_probe(host="10.0.0.5:11434", opener=op)
    assert state == "unreachable" and "not loopback" in why and op.seen == []


# --- --no-say and --model -----------------------------------------------------------


@pytest.fixture
def wired(monkeypatch):
    """main() with a fake Seat: what it was built with, and the models asked."""
    seen = {"asked": []}

    class Fake:
        def __init__(self, bot_, cfg, **kw):
            seen.update(kw)

        def run(self):
            return 0

    real = s.ollama_say
    monkeypatch.setattr(s, "load_bot", lambda root: "bot")
    monkeypatch.setattr(s, "config", lambda b, r: "cfg")
    monkeypatch.setattr(s, "Seat", Fake)
    monkeypatch.setattr(
        s, "ollama_say", lambda model: seen["asked"].append(model) or real(model=model)
    )
    return seen


def test_no_say_runs_code_only_and_never_builds_the_ollama_say(wired):
    assert s.main(["--no-say"]) == 0
    assert wired["say"] is None and wired["asked"] == []


def test_model_flag_picks_the_reply_model_for_the_seat_and_the_say(wired):
    assert s.main(["--model", "llama3.2:3b"]) == 0
    assert wired["model"] == "llama3.2:3b" and wired["asked"] == ["llama3.2:3b"]
    assert callable(wired["say"])


def test_model_flag_wins_over_the_env_and_the_env_stands_without_it(wired, monkeypatch):
    monkeypatch.setattr(s, "MODEL", "from-env")  # GROVE_SAY_MODEL, read at import
    assert s.main([]) == 0 and wired["model"] == "from-env"
    assert s.main(["--model", "from-flag"]) == 0 and wired["model"] == "from-flag"


def test_a_qwen3_model_from_the_flag_still_gets_no_think(wired, monkeypatch):
    op = Opener(json.dumps({"response": "ok"}).encode())
    monkeypatch.setattr(say_mod.urllib.request, "build_opener", lambda *a: op)
    assert s.main(["--model", "qwen3:8b"]) == 0
    assert wired["say"]("hi") == "ok"
    body = json.loads(op.seen[0][0].data)
    assert body["model"] == "qwen3:8b" and body["prompt"] == "hi /no_think"


@pytest.mark.parametrize(
    "argv",
    [["--no-say", "--model", "x"], ["--model", "x", "--no-say"], ["--model", " "]],
)
def test_no_say_with_a_model_or_a_blank_model_exits_2_before_the_bot_loads(
    no_session, capsys, argv
):
    assert s.main(argv) == 2
    assert "usage: grove-seat" in capsys.readouterr().err


def test_model_flag_without_a_name_is_a_usage_error(no_session, capsys):
    assert s.main(["--model"]) == 2


def test_check_probes_the_flagged_model_and_skips_ollama_under_no_say(
    no_session, monkeypatch, tmp_path, capsys
):
    probed(monkeypatch, tmp_path)
    asked = []
    monkeypatch.setattr(
        s, "ollama_probe", lambda m: asked.append(m) or ("populated", m)
    )
    assert s.main(["--check", "--model", "llama3.2:3b"]) == 0
    assert asked == ["llama3.2:3b"] and "ollama" in capsys.readouterr().out
    assert s.main(["--check", "--no-say"]) == 0 and asked == ["llama3.2:3b"]
    assert "ollama" not in capsys.readouterr().out


# --- the default say: Ollama on loopback --------------------------------------------


class Resp:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self.body


class Opener:
    def __init__(self, result):
        self.result, self.seen = result, []

    def open(self, req, timeout=None):
        self.seen.append((req, timeout))
        if isinstance(self.result, BaseException):
            raise self.result
        return Resp(self.result)


def test_the_default_say_posts_to_generate_on_loopback_and_drops_thinking():
    op = Opener(json.dumps({"response": "<think>hm</think> Looks like it."}).encode())
    say = say_mod.ollama_say(model="qwen3:4b", host="127.0.0.1:11434", opener=op)
    got = say("the prompt")
    assert got == "Looks like it."
    req, _t = op.seen[0]
    assert req.full_url == "http://127.0.0.1:11434/api/generate"
    body = json.loads(req.data)
    assert body["model"] == "qwen3:4b" and body["stream"] is False
    assert body["prompt"] == "the prompt /no_think" and body["think"] is False


@pytest.mark.parametrize(
    "host",
    [
        "0.0.0.0:11434",
        "10.0.0.5:11434",
        "http://example.com:11434",
        "https://127.0.0.1",
        "x:y",
    ],
)
def test_a_host_that_is_not_loopback_is_not_asked(host):
    op = Opener(b"{}")
    with pytest.raises(say_mod.SayUnreachable, match="loopback|host:port"):
        say_mod.ollama_say(host=host, opener=op)("p")
    assert op.seen == []  # nothing left the box


@pytest.mark.parametrize("host", ["localhost:9", "http://127.0.0.1:9", "[::1]:11434"])
def test_loopback_hosts_are_asked(host):
    assert say_mod.ollama_base(host).startswith("http://")


def test_ollama_host_comes_from_the_environment(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "0.0.0.0:11434")
    with pytest.raises(say_mod.SayUnreachable, match="loopback"):
        say_mod.ollama_base()
    monkeypatch.delenv("OLLAMA_HOST")
    assert say_mod.ollama_base() == "http://127.0.0.1:11434"


def test_a_missing_tag_a_bad_reply_and_a_refusal_are_unreachable():
    import urllib.error

    nf = urllib.error.HTTPError("u", 404, "nf", None, None)
    with pytest.raises(say_mod.SayUnreachable, match="tag not installed"):
        say_mod.ollama_say(opener=Opener(nf))("p")
    with pytest.raises(say_mod.SayUnreachable, match="no response field"):
        say_mod.ollama_say(opener=Opener(b'{"x": 1}'))("p")
    with pytest.raises(say_mod.SayUnreachable, match="JSONDecodeError"):
        say_mod.ollama_say(opener=Opener(b"not json"))("p")
    with pytest.raises(say_mod.SayUnreachable, match="ConnectionRefusedError"):
        say_mod.ollama_say(opener=Opener(ConnectionRefusedError("no")))("p")
    with pytest.raises(say_mod.SayUnreachable):  # a real closed loopback port
        say_mod.ollama_say(host="127.0.0.1:1", timeout=5)("p")


# --- Loki's two low findings ----------------------------------------------------------


def test_a_checkout_that_raises_is_unreachable_and_the_closeout_still_runs():
    """F-low: api.checkout raising must not escape run() or lose the deposit."""

    def boom(*a, **k):
        raise RuntimeError("morning db down")

    dep = FakeDeposit(DEPOSITED)
    st, out = seat(FakeApi(checkout=boom, pooled=POOL), ["who", "", ""], deposit=dep)
    assert st.run() == 0
    assert "[unreachable] morning screen" in text(out)
    assert "unreachable — RuntimeError: morning db down" in text(out)
    assert dep.pools == [POOL] and text(out).count("seal ↗") == 1


def test_no_rush_follows_what_a_box_says_not_its_kind():
    calm = bx.Box("b1", "pass", "chain", "answered 2, escalated 0")
    sore = bx.Box("b2", "pass", "chain", "answered 2, escalated 1")
    assert bx.compose([calm]).endswith("No rush.")
    for bad in (
        sore,
        bx.Box("b3", "pass", "check", "3 failed"),
        bx.Box("b4", "pr", "changed", "PR 9 open", "refused by the gate"),
        bx.Box("b5", "dec", "decided", "errors: 2"),
        bx.Box("b6", "pass", "gate", "hard closed"),
    ):
        assert "No rush" not in bx.compose([bad]), bad
        assert "No rush" not in bx.compose([calm, bad])
    # kind still holds as before
    assert "No rush" not in bx.compose([bx.Box("b7", "you", "needs you", "Pick one")])


# --- resume: serve the sealed snapshot (B part 2) ---------------------------------------

PINNED = {"by": ["who"], "match": {}, "upto": 41}
SEALED = "serve:9439efca"
GROWN = "serve:4ae0b332"


def resumed(**kw):
    return {"spec": PINNED, "subject": SEALED, "code": 0, **kw}


def scope_at(subject):
    return {
        "spec": {"by": ["who"], "match": {}, "upto": 99},
        "subject": subject,
        "ids": ["t1"],
        "stack": [{"name": "who=human", "id": "t1" * 8, "rows": 2}],
    }


def offers(out):
    """The seal cards as one string each (a card is several lines)."""
    cards, mine = [], None
    for o in out:
        if "seal ↗" in o:
            mine = [o]
            cards.append(mine)
        elif mine is not None and o.startswith("|"):
            mine.append(o)
        else:
            mine = None
    return ["\n".join(c) for c in cards]


def test_resume_hit_serves_the_pinned_spec_and_skips_group_by():
    api = FakeApi(resume=resumed())
    st, out = seat(api, ["", ""])  # cap, then check out
    assert st.run() == 0
    assert "scope" not in api.names()[: api.names().index("serve")]
    serve = next(c for c in api.calls if c[0] == "serve")
    assert serve[1][0] == PINNED and serve[1][0]["upto"] == 41
    assert not any(o.startswith("scope ▶") for o in out)
    body = text(out)
    assert "sealed snapshot" in body and SEALED in body and "upto=41" in body


def test_resume_none_bootstraps_a_fresh_scope_as_before():
    api = FakeApi(resume={"resume": None, "code": 0})
    st, out = seat(api, ["who", "", ""])
    assert st.run() == 0
    assert api.names()[:5] == ["checkin", "resume", "scope", "pooled", "serve"]
    assert any(o.startswith("scope ▶") for o in out)
    assert "sealed snapshot" not in text(out)
    assert serve_spec(api) == {"by": ["who"]}


def serve_spec(api):
    return next(c for c in api.calls if c[0] == "serve")[1][0]


@pytest.mark.parametrize(
    "boom",
    [RuntimeError("no such verb"), AttributeError("resume"), KeyError("resume")],
)
def test_resume_raising_is_unreachable_not_empty_and_falls_back(boom):
    def bad(*a, **k):
        raise boom

    api = FakeApi(resume=bad)
    st, out = seat(api, ["who", "", ""])
    assert st.run() == 0
    body = text(out)
    assert "unreachable —" in body and "scoping fresh instead" in body
    assert "empty — " not in body.split("scoping fresh")[0].splitlines()[-1]
    assert "scope" in api.names() and "serve" in api.names()
    assert serve_spec(api) == {"by": ["who"]}


def test_resume_refused_is_unreachable_and_falls_back():
    api = FakeApi(resume={"refused": "box won't open", "code": 2})
    st, out = seat(api, ["who", "", ""])
    assert st.run() == 0
    assert "unreachable — box won't open" in text(out)
    assert "scope" in api.names()


def test_closeout_offers_the_grown_subject_when_it_differs():
    api = FakeApi(resume=resumed(), scope=scope_at(GROWN))
    st, out = seat(api, ["", ""])
    assert st.run() == 0
    grown_call = next(c for c in api.calls if c[0] == "scope")
    assert grown_call[2]["by"] == ["who"] and grown_call[2]["match"] == {}
    # asked before the box closes, while the desk can still be scoped
    assert api.names().index("scope") < api.names().index("checkout")
    got = offers(out)
    assert len(got) == 1 and GROWN in got[0] and "advance the snapshot" in got[0]


def test_closeout_adds_the_grown_subject_to_the_one_offer_beside_drafts():
    dep = FakeDeposit(
        {"state": "populated", "deposited": [{"subject": SUBJ, "status": "draft"}]}
    )
    api = FakeApi(resume=resumed(), scope=scope_at(GROWN))
    st, out = seat(api, ["", ""], deposit=dep)
    assert st.run() == 0
    got = offers(out)
    assert len(got) == 1
    assert SUBJ in got[0] and GROWN in got[0]


def test_closeout_makes_no_offer_when_the_grown_subject_is_the_sealed_one():
    api = FakeApi(resume=resumed(), scope=scope_at(SEALED))
    st, out = seat(api, ["", ""])
    assert st.run() == 0
    assert offers(out) == []


def test_a_fresh_scope_session_asks_for_no_grown_scope():
    api = FakeApi()
    st, out = seat(api, ["who", "", ""])
    assert st.run() == 0
    assert api.names().count("scope") == 1  # the bootstrap one only
    assert "advance the snapshot" not in text(out)


def test_the_grown_scope_refused_is_shown_not_offered():
    api = FakeApi(resume=resumed(), scope={"refused": "no open box", "code": 2})
    st, out = seat(api, ["", ""])
    assert st.run() == 0
    assert "unreachable — no open box" in text(out)
    assert offers(out) == []


def test_the_seat_never_seals_or_mints_on_the_resume_path():
    api = FakeApi(resume=resumed(), scope=scope_at(GROWN))
    st, _out = seat(api, ["", ""])
    assert st.run() == 0
    assert not {n for n in api.names() if "seal" in n or "mint" in n or "key" in n}


# --- the launcher's venv order ----------------------------------------------------------


def fake_python(path, name):
    path.mkdir(parents=True)
    exe = path / "python3"
    exe.write_text(f"#!/bin/sh\necho {name}\n", encoding="utf-8")
    exe.chmod(0o755)


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="scripts/grove-seat is a POSIX launcher",
)
def test_grove_venv_defaults_to_the_bot_venv_and_has_no_mcp_rung(tmp_path):
    home = tmp_path / "home"
    fake_python(home / "venvs" / "willow-mcp" / "bin", "mcp")
    fake_python(home / "venvs" / "willow-bot" / "bin", "bot")
    fake_python(tmp_path / "mine" / "bin", "explicit")
    env = {"PATH": "/usr/bin:/bin", "WILLOW_HOME": str(home)}

    def which(**extra):
        done = subprocess.run(
            ["bash", str(s.GROVE_ROOT / "scripts" / "grove-seat")],
            env={**env, **extra},
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        return done.stdout.strip()

    assert which() == "bot"  # the bot venv ships the seat runtime
    assert which(GROVE_VENV=str(tmp_path / "mine")) == "explicit"  # override wins
    (home / "venvs" / "willow-bot" / "bin" / "python3").unlink()
    assert which() != "mcp"  # no mcp rung: never the mcp venv


def launch(env, **extra):
    done = subprocess.run(
        ["bash", str(s.GROVE_ROOT / "scripts" / "grove-seat")],
        env={**env, **extra},
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return done.stdout.strip(), done.stderr


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="scripts/grove-seat is a POSIX launcher",
)
def test_bot_venv_new_home_wins_over_legacy_without_a_warning(tmp_path):
    home = tmp_path / "home"
    fake_python(home / "willow-bot" / "venvs" / "willow-bot" / "bin", "new")
    fake_python(home / "venvs" / "willow-bot" / "bin", "legacy")
    env = {"PATH": "/usr/bin:/bin", "WILLOW_HOME": str(home)}
    out, err = launch(env)
    assert out == "new"
    assert "warning" not in err


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="scripts/grove-seat is a POSIX launcher",
)
def test_bot_venv_legacy_home_is_used_with_a_warning_naming_the_new_home(tmp_path):
    home = tmp_path / "home"
    fake_python(home / "venvs" / "willow-bot" / "bin", "legacy")
    env = {"PATH": "/usr/bin:/bin", "WILLOW_HOME": str(home)}
    out, err = launch(env)
    assert out == "legacy"
    assert err.count("\n") == 1  # one line
    assert "warning" in err and str(home / "willow-bot" / "venvs" / "willow-bot") in err


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="scripts/grove-seat is a POSIX launcher",
)
def test_grove_venv_still_wins_over_both_bot_homes_and_is_quiet(tmp_path):
    home = tmp_path / "home"
    fake_python(home / "willow-bot" / "venvs" / "willow-bot" / "bin", "new")
    fake_python(home / "venvs" / "willow-bot" / "bin", "legacy")
    fake_python(tmp_path / "mine" / "bin", "explicit")
    env = {"PATH": "/usr/bin:/bin", "WILLOW_HOME": str(home)}
    out, err = launch(env, GROVE_VENV=str(tmp_path / "mine"))
    assert out == "explicit"
    assert "warning" not in err


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="scripts/grove-seat is a POSIX launcher",
)
def test_no_bot_venv_anywhere_falls_through_to_python3(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    out, err = launch({"PATH": "/usr/bin:/bin", "WILLOW_HOME": str(home)})
    assert "warning" not in err
    assert out not in ("new", "legacy")


@pytest.mark.skipif(
    sys.platform == "win32" or shutil.which("bash") is None,
    reason="scripts/grove-seat is a POSIX launcher",
)
@pytest.mark.parametrize("layout", ["both", "new", "old", "none"])
@pytest.mark.parametrize(
    "box_env",
    [
        {"WILLOW_HOME": "{h}"},
        {"WILLOW_VAULT_BOX": "{h}"},
        {"WILLOW_HOME": " ", "WILLOW_VAULT_BOX": " {h} "},
        {"WILLOW_HOME": "{h}/missing", "WILLOW_VAULT_BOX": "{h}"},
        {"WILLOW_HOME": "rel/box"},
        {},
    ],
)
def test_the_launcher_and_resolve_venv_agree(tmp_path, layout, box_env):
    """F-17: grove-seat's shell rule and resolve_venv (the bot's
    willow_bot.paths) pick the same bot venv, or none, every time."""
    home = tmp_path / "home"
    home.mkdir()
    if layout in ("both", "new"):
        fake_python(home / "willow-bot" / "venvs" / "willow-bot" / "bin", "new")
    if layout in ("both", "old"):
        fake_python(home / "venvs" / "willow-bot" / "bin", "legacy")
    env = {k: v.format(h=home) for k, v in box_env.items()}
    want = s.resolve_venv(env, "/usr", "/usr", tmp_path / "grove")
    out, _ = launch({"PATH": "/usr/bin:/bin", **env})
    py = want / "bin" / "python3" if want is not None else None
    if py is not None and py.is_file():
        assert out == ("new" if "willow-bot/venvs" in str(want) else "legacy")
    else:
        assert out not in ("new", "legacy")


# --- ratatosk resolution and the say timeout ----------------------------------------


def test_ratatosk_resolves_beside_sys_executable(tmp_path, monkeypatch):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "ratatosk").write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(sys, "executable", str(bindir / "python3"))
    assert s.resolve_ratatosk() == str(bindir / "ratatosk")


def test_ratatosk_falls_back_to_path_when_absent(tmp_path, monkeypatch):
    (tmp_path / "bin").mkdir()
    monkeypatch.setattr(sys, "executable", str(tmp_path / "bin" / "python3"))
    assert s.resolve_ratatosk() == "ratatosk"


def test_the_resolved_ratatosk_reaches_escalate_and_flowering(tmp_path, monkeypatch):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    rat = bindir / "ratatosk"
    rat.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(sys, "executable", str(bindir / "python3"))
    seen: list = []
    real = s.ratatosk_flowering
    monkeypatch.setattr(
        s,
        "ratatosk_flowering",
        lambda cmd=("ratatosk",), **k: seen.append(cmd) or real(cmd, **k),
    )
    api = FakeApi()
    st = s.Seat(
        bot(api),
        cfg="cfg",
        deposit=FakeDeposit(),
        read=lambda p: "",
        write=lambda x: None,
        color=False,
    )
    assert seen == [(str(rat),)]  # the default flowering rung
    st.chain("the task")
    esc = [c for c in api.calls if c[0] == "escalate"]
    assert esc and esc[0][2]["ratatosk"] == (str(rat),)


@pytest.mark.parametrize("model", [s.MODEL, "qwen3:8b"])
def test_the_chain_local_rung_uses_the_seats_one_model(model):
    api = FakeApi()
    st = s.Seat(
        bot(api),
        cfg="cfg",
        deposit=FakeDeposit(),
        read=lambda p: "",
        write=lambda x: None,
        color=False,
        model=model,
    )
    st.chain("the task")
    esc = [c for c in api.calls if c[0] == "escalate"]
    assert esc and esc[0][2]["model"] == model


def test_say_timeout_defaults_to_300_and_honors_the_env():
    assert say_mod.say_timeout({}) == 300.0
    assert say_mod.say_timeout({"GROVE_SAY_TIMEOUT": "45.5"}) == 45.5
    for bad in ("", "soon", "0", "-3", "nan", "inf"):
        assert say_mod.say_timeout({"GROVE_SAY_TIMEOUT": bad}) == 300.0


# --- still pooled: the start card (api.pooled, read for display) ------------------------


def pool_of(*subjects):
    items = [
        {
            "subject": x,
            "path": "notes/a.md",
            "data": "# A",
            "cites": ["t1"],
            "claim": "c",
        }
        for x in subjects
    ]
    return {"pooled": items, "count": len(items), "code": 0}


def pooled_card(out):
    """The ``still pooled`` card as one string (a header, then its bar lines)."""
    i = next(n for n, o in enumerate(out) if "still pooled" in o)
    j = i
    while j + 1 < len(out) and out[j + 1][:1] in "|:!" and out[j + 1][1:2] == " ":
        j += 1
        if out[j].startswith(("served", "chain")):
            break
    return "\n".join(out[i : j + 1])


def test_pooled_at_start_shows_one_populated_card_with_a_count_and_subjects():
    api = FakeApi(pooled=pool_of("proposal:aaa", "proposal:bbb", "proposal:ccc"))
    st, out = seat(api, ["who", "", ""])
    assert st.run() == 0
    # one card; the opening sentence also says "still pooled" (O2), as a line
    assert sum("still pooled" in o for o in out if o[:2] == "+-") == 1
    card = pooled_card(out)
    assert "3 from earlier runs, unsealed" in card
    assert "proposal:aaa; proposal:bbb (+1 more)" in card and "ccc" not in card
    assert card.splitlines()[0].startswith("+-")  # populated


def test_pooled_at_start_empty_is_its_own_state():
    st, out = seat(FakeApi(), ["who", "", ""])
    assert st.run() == 0
    card = pooled_card(out)
    assert card.splitlines()[0].startswith("+.")
    assert "empty — nothing pooled from earlier runs" in card


@pytest.mark.parametrize(
    "bad",
    [
        RuntimeError("no such verb"),
        AttributeError("pooled"),
        {"refused": "box won't open", "code": 2},
        {"pooled": "nope"},
    ],
)
def test_pooled_at_start_unreachable_is_a_card_not_a_crash(bad):
    def pooled(*a, **k):
        if isinstance(bad, BaseException):
            raise bad
        return bad

    api = FakeApi(pooled=pooled)
    st, out = seat(api, ["who", "", ""])
    assert st.run() == 0
    card = pooled_card(out)
    assert card.splitlines()[0].startswith("+!")
    assert "unreachable —" in card and "empty — " not in card
    assert "served" in api.names() or "serve" in api.names()


def test_pooled_at_start_is_read_only_and_leaves_the_resume_snapshot_alone():
    dep = FakeDeposit()
    api = FakeApi(resume=resumed(), pooled=pool_of("proposal:aaa"))
    st, out = seat(api, ["", ""], deposit=dep)
    assert st.run() == 0
    assert st.sealed == {"spec": PINNED, "subject": SEALED}
    assert (
        serve_spec(api) == PINNED
        and "scope" not in api.names()[: api.names().index("serve")]
    )
    assert api.names().index("pooled") < api.names().index("serve")
    assert not {n for n in api.names() if "seal" in n or "mint" in n or "take" in n}
    # the start read deposits nothing; only the close-out deposit sees the pool
    assert len(dep.pools) == 1


def test_pooled_at_start_is_skipped_when_nothing_is_served():
    api = FakeApi(scope={"refused": "no open box", "code": 2})
    st, out = seat(api, ["who"])
    st.run()
    assert not any("still pooled" in o for o in out)


def test_pooled_at_start_a_non_record_answer_is_unreachable():
    st, out = seat(FakeApi(pooled="garbage"), [])
    st.pooled_at_start()
    assert pooled_card(out).splitlines()[0].startswith("+!")
    assert "not a pool record" in text(out)


# --- step 1: rank, per-kind phrasing, glue, greeting, plain lines -------------------

DEMO = {
    "b1": bx.Box(
        "b1",
        "dec",
        "decided",
        "Phone only proposes",
        "seal in Nestor on the box · recorded",
    ),
    "b2": bx.Box("b2", "pr", "changed", "PR #127 open", "grid rows JE–JI · baton 9"),
    "b3": bx.Box("b3", "pr", "changed", "PR #714 open", "untracks 3 bytecode files"),
    "b4": bx.Box(
        "b4", "block", "blocked", "PR 712 waiting", "broker verb · 126 tests pass"
    ),
    "b5": bx.Box(
        "b5", "you", "needs you", "Ratify the work order", "local-flow-and-ui §7"
    ),
}


def demo(*ids):
    return [DEMO[i] for i in ids]


def test_rank_is_needs_you_blocked_decided_changed_pass_stable_heads_up_first():
    p1 = bx.Box("p1", "pass", "x", "ok")
    p2 = bx.Box("p2", "pass", "x", "ok2")
    down = bx.Box("d", "pass", "served", "unreachable — no key", state="unreachable")
    gap = bx.Box("g", "pass", "chain", "empty — none", state="empty")
    odd = bx.Box("o", "weird", "x", "v")
    got = bx.rank(
        [
            p1,
            odd,
            DEMO["b2"],
            p2,
            DEMO["b1"],
            DEMO["b4"],
            down,
            DEMO["b5"],
            gap,
            DEMO["b3"],
        ]
    )
    assert [b.id for b in got] == [
        "d",
        "g",
        "b5",
        "b4",
        "b1",
        "b2",
        "b3",
        "p1",
        "p2",
        "o",
    ]


def test_the_demo_scenes_read_like_the_sketch():
    assert bx.compose(demo("b5", "b4"), greet="Morning.") == (
        "Morning. You need to ratify the work order. PR 712's still waiting, 126 tests pass."
    )
    assert bx.compose(demo("b1", "b2", "b3"), first=False) == (
        "Oh, and phone only proposes is decided and recorded; "
        "PR #127 and PR #714 are both open. No rush."
    )


def sketch_glue(html: str) -> tuple[str, ...]:
    """The free glue words a box-stream sketch declares (``const GLUE = [...]``);
    a sketch with no such list is a failure, never an empty tuple."""
    found = re.search(r"const GLUE = \[(.*?)\];", html)
    assert found, "the sketch declares no GLUE list"
    return tuple(re.findall(r"'([^']+)'", found.group(1)))


def test_sketch_glue_catches_a_planted_drift():
    """Planted: a sketch whose list drifts from the seat's reads as different,
    and a sketch with no list fails rather than passing as empty."""
    assert sketch_glue("const GLUE = ['morning', 'oh'];") == ("morning", "oh")
    drifted = "const GLUE = [" + ", ".join(f"'{w}'" for w in bx.GLUE[:-1]) + "];"
    assert sketch_glue(drifted) != bx.GLUE
    with pytest.raises(AssertionError):
        sketch_glue("const OTHER = ['morning'];")


def test_glue_is_the_sketchs_list_and_the_model_may_use_exactly_it():
    html = (s.GROVE_ROOT / "web/demo/box-stream/box-stream-v1.3.html").read_text(
        "utf-8"
    )
    assert sketch_glue(html) == bx.GLUE
    assert say_mod.GLUE is bx.GLUE
    prompt = say_mod.build_prompt(demo("b5"), "where are we")
    assert "Free words, and only these: " + ", ".join(bx.GLUE) in prompt


SETS = [
    ("b5", "b4"),
    ("b1", "b2", "b3"),
    ("b2", "b3"),
    ("b5",),
    ("b4", "b1"),
    ("b5", "b4", "b1", "b2", "b3"),
]


@pytest.mark.parametrize("ids", SETS)
@pytest.mark.parametrize("page", [0, 1, 2])
def test_the_code_sentence_passes_the_checks_a_model_sentence_faces(ids, page):
    """Cited, the code sentence passes all four checks. Uncited (as it is
    shown today), cites-served and quotes pass, nothing-lacking passes, and
    only ``every box cited`` is False (there is no tag to find)."""
    boxes = bx.rank(demo(*ids))
    cited = bx.compose(
        boxes, page=page, greet="Morning." if not page else "", cite=True
    )
    assert say_mod.passed(say_mod.run_checks(cited, boxes, "where are we")), cited
    assert say_mod.run_checks(cited, boxes)[3] == "na"
    plain = bx.compose(boxes, page=page)
    r = say_mod.run_checks(plain, boxes, "where are we")
    assert r == [True, False, True, "na"], plain


def test_a_made_up_fact_would_not_pass_the_same_check():
    boxes = demo("b5", "b4")
    s_ = bx.compose(boxes, cite=True).replace("126", "140")
    assert say_mod.run_checks(s_, boxes)[2] is False


def test_empty_and_unreachable_have_their_own_plain_lines():
    down = bx.Box(
        "b1",
        "pass",
        "served",
        "unreachable — The box wasn't found.",
        state="unreachable",
    )
    gap = bx.Box(
        "b2",
        "pass",
        "still pooled",
        "empty — nothing pooled from earlier runs",
        state="empty",
    )
    assert (
        bx.plain_line(down)
        == "I can't read the record right now. The box wasn't found."
    )
    assert (
        bx.plain_line(gap) == "Still pooled is empty: nothing pooled from earlier runs."
    )
    assert bx.plain_line(DEMO["b5"]) == ""
    assert bx.compose([down]).startswith("Heads up: I can't read the record right now.")
    assert "can't read" not in bx.compose([gap]) and "No rush" not in bx.compose([gap])
    assert bx.compose([gap]) != bx.compose([down])
    assert all(ord(c) < 128 for c in bx.plain_line(down) + bx.plain_line(gap))


def test_a_stage_that_is_unreachable_or_empty_also_says_so_in_words():
    """A stage no sentence covers says its state in a plain line. (The pool at
    start and check-out and the resume are covered by the opening and closing
    sentences instead: see ``test_a_card_the_opening_says_has_no_plain_line``.)"""
    st, out = seat(
        FakeApi(scope={"spec": {}, "subject": "serve:x", "ids": [], "stack": []}),
        ["who"],
    )
    st.run()
    assert "[empty] scope" in text(out)
    assert "agent> Scope is empty: no table matches; nothing to serve." in out
    assert "I can't read" not in text(out)


def agent_lines(out):
    return [o for o in out if o.startswith("agent> ")]


def test_a_card_the_opening_says_has_no_plain_line():
    def boom(*a, **k):
        raise RuntimeError("pool db down")

    def start(api):
        """The lines up to the served stage: the cards, the plain lines and the
        opening."""
        _a, out, _line = start_opening(api)
        return out[: next(i for i, o in enumerate(out) if o.startswith("served ▶"))]

    # pool empty at start: the card stays, "Still pooled is empty" is not said
    head = start(FakeApi())
    assert "[empty] still pooled" in text(head)
    assert not any("Still pooled is empty" in o for o in head)
    assert sum("nothing is pooled from earlier runs" in o for o in head) == 1
    assert sum("nothing pooled from earlier runs" in o for o in head) == 1  # card
    # unreadable pool: the reason stays on the card, the words are said once
    head = start(FakeApi(pooled=boom))
    assert "[unreachable] still pooled" in text(head)
    assert "unreachable — RuntimeError: pool db down" in text(head)
    assert not any("can't read the record" in o for o in head)
    assert sum("couldn't read the pool" in o for o in agent_lines(head)) == 1
    # unreadable resume: same
    head = start(FakeApi(resume=boom))
    assert "[unreachable] resume" in text(head)
    assert not any("can't read the record" in o for o in head)
    assert sum("couldn't read the last sealed snapshot" in o for o in head) == 1


def test_an_unreadable_resume_with_no_opening_is_still_said_once_in_words():
    def boom(*a, **k):
        raise RuntimeError("no such verb")

    st, out = seat(
        FakeApi(resume=boom, scope={"refused": "no open box", "code": 2}), ["who"]
    )
    st.run()
    said = [o for o in agent_lines(out) if "no such verb" in o]
    assert said == [
        "agent> I can't read the record right now. RuntimeError: no such verb; "
        "scoping fresh instead."
    ]
    assert not any("couldn't read" in o for o in out)  # no opening was said


def test_a_closing_card_the_closing_says_has_no_plain_line():
    # empty pool, empty deposit: "Nothing stays pooled" says it, once
    st, out = seat(FakeApi(), ["who", "", ""])
    st.run()
    assert "[empty] deposit" in text(out)
    assert not any("Deposit is empty" in o for o in out)
    assert closing_of(out) == "agent> Nothing stays pooled for next time."
    # unreadable pool at check-out: the card, then the closing in words, once
    calls = []

    def pooled(*a, **k):
        calls.append(1)
        if len(calls) > 1:
            raise RuntimeError("pool db down")
        return pool_of()

    st, out = seat(FakeApi(pooled=pooled), ["who", "", ""])
    st.run()
    assert "[unreachable] pool" in text(out)
    assert not any("can't read the record" in o for o in out)
    assert sum("couldn't read the pool" in o for o in agent_lines(out)) == 1
    # a populated pool whose deposit failed is a different fact: still said
    st, out = seat(
        FakeApi(pooled=pool_of("proposal:aaa")),
        ["who", "", ""],
        deposit=FakeDeposit({"state": "unreachable", "reason": "no key"}),
    )
    st.run()
    assert "agent> I can't read the record right now. No key." in out
    assert closing_of(out) == "agent> 1 proposal stays pooled for next time."


def test_each_unreachable_read_is_said_in_words_exactly_once():
    def boom(*a, **k):
        raise RuntimeError("x")

    st, out = seat(FakeApi(resume=boom, pooled=boom), ["who", "", ""])
    st.run()
    words = [o for o in agent_lines(out) if "read" in o]
    assert len(words) == 2  # the opening (both reads) and the closing (the pool)
    assert "couldn't read the last sealed snapshot" in words[0]
    assert "couldn't read the pool" in words[0]
    assert "couldn't read the pool" in words[1]
    assert not any("can't read the record" in o for o in out)


def test_the_greeting_is_once_per_run_before_noon_from_the_injected_clock():
    for at, greets in (("09:14", True), ("13:05", False), ("garbled", False)):
        st, out = seat(FakeApi(), ["", ""], clock=lambda at=at: at)
        st.converse("k1", demo("b5", "b4", "b1"), "q")  # two pages: PAGE=2
        st.converse("k2", demo("b1"), "q")
        said = [o for o in out if o.startswith("agent> ")]
        assert sum("Morning." in o for o in said) == (1 if greets else 0), (at, said)
        assert (not greets) or "Morning." in said[0]


def test_converse_ranks_then_pages_the_ranked_list():
    st, out = seat(
        FakeApi(),
        [""],
    )
    p = bx.Box("p", "pass", "x", "fine")
    st.converse("k", [p, DEMO["b1"], DEMO["b4"], DEMO["b5"]], "q")
    heads = [o for o in out if o.startswith(("+-", "+.", "+!"))]
    assert [h.split("] ")[0] for h in heads[:2]] == ["+- [needs you", "+- [blocked"]
    said = [o for o in out if o.startswith("agent> ")]
    assert said[0].startswith("agent> Morning. You need to ratify")
    assert said[1].startswith("agent> Oh, and phone only proposes is decided")


# --- chips, chip answers and follow-ups ------------------------------------------


def demo_boxes():
    return [
        bx.Box("b1", "dec", "decided", "phone only proposes", "recorded"),
        bx.Box("b2", "pr", "changed", "PR #127 open", "grid rows JE–JI · baton 9"),
        bx.Box("b3", "pr", "changed", "PR #714 open", "untracks 3 bytecode files"),
        bx.Box(
            "b4", "block", "blocked", "PR 712 waiting", "broker verb · 126 tests pass"
        ),
        bx.Box(
            "b5", "you", "needs you", "Ratify the work order", "local-flow-and-ui §7"
        ),
    ]


GATE = [
    bx.Box("c1", "block", "step", "Check-in hard-closed", "the box did not open"),
    bx.Box("c2", "block", "gate", "ruff 0.16.10", "installed in the venv"),
    bx.Box(
        "c5",
        "you",
        "needs you",
        "Pick one",
        "put it back · keep as a grant · block · stop",
    ),
]


def thread_run(keys, boxes=None, **kw):
    """A run whose chain turns are fixed boxes, so a follow-up has something to
    resolve against. ``api.escalate`` must never be called by a follow-up."""
    api = FakeApi()
    st, out = seat(api, ["who", "", *keys, ""], **kw)

    def chain(task):
        st.you(task)
        st.converse(s._norm(task), list(boxes or demo_boxes()), task)

    st.chain = chain
    st.run()
    return api, out


ALL = ["", ""]  # accept both more? prompts: the whole demo list is shown


def chips_of(out):
    return [o for o in out if o.startswith("chips:")]


def after(out, you, nth=0):
    """The lines printed after the human's ``you: <you>`` (the nth time)."""
    i = [k for k, o in enumerate(out) if o == f"you: {you}"][nth]
    nxt = next(
        (j for j in range(i + 1, len(out)) if out[j].startswith(("you:", "chain ▶"))),
        len(out),
    )
    return out[i + 1 : nxt]


def test_the_chip_row_comes_from_the_boxes_just_shown():
    row = bx.chips(bx.rank(demo_boxes())).row()
    assert row == "chips: [show me 712] [later] [thanks]"  # the blocked box, by number
    assert bx.chips(GATE).row() == (
        "chips: [put it back] [keep as a grant] [block] [stop] [later] [thanks]"
    )
    assert (
        bx.chips([bx.Box("b1", "pass", "x", "fine")]).row() == "chips: [later] [thanks]"
    )


def test_a_ref_must_be_unique_and_comes_only_from_the_boxs_own_value():
    twin = [
        bx.Box("b1", "block", "blocked", "PR 712 waiting", "why"),
        bx.Box("b2", "block", "blocked", "PR 712 held", "why"),
    ]
    assert bx.chips(twin).show == "show me b1"  # number shared: the box id, not words
    same = [
        bx.Box("zzz", "block", "x", "PR 7 waiting", "d"),
        bx.Box("yyy", "pr", "x", "PR 7 waiting", "d"),
    ]
    assert bx.chips(same).show == ""  # nothing names one box alone: no chip


def test_a_ref_is_a_number_an_id_like_token_or_the_box_id_never_first_words():
    d0 = bx.Box(
        "b7116acfef88",
        "you",
        "escalated",
        "d0: the scope is 'empty': nothing served",
        "r",
    )
    assert bx.ref_tokens(d0) == []  # no number, no id token, a hash id: no chip
    assert bx.chips([d0]).show == ""
    assert bx.chips([d0]).row() == "chips: [later] [thanks]"
    one = bx.Box("zz", "block", "x", "step 7 of 9 waiting", "d")
    assert bx.ref_tokens(one) == []  # one digit is no ref
    ver = bx.Box("zz", "block", "x", "ruff 0.16.10 missing", "d")
    assert bx.ref_tokens(ver) == []  # parts of a version are no ref
    hexish = bx.Box("zz", "block", "x", "run 7476c1338860 held", "d")
    assert bx.ref_tokens(hexish) == []
    pr = bx.Box("b4", "block", "x", "PR 712 waiting", "d")
    assert bx.ref_tokens(pr) == ["712", "PR 712", "b4"]
    assert bx.ref_tokens(bx.Box("zz", "pr", "x", "PR #714 open"))[:1] == ["714"]
    twin = [pr, bx.Box("b5", "block", "x", "Issue 712 held", "d")]
    assert bx.unique_ref(pr, twin) == "PR 712"  # the number is shared, the token isn't
    assert bx.matches(pr, "pr 712") and not bx.matches(twin[1], "pr 712")


def test_options_need_three_short_digitless_parts_and_the_row_is_capped():
    two = bx.Box("b1", "you", "needs you", "Ratify", "local-flow · section seven")
    assert bx.options(two) == []
    digits = bx.Box("b1", "you", "needs you", "Ratify", "a · b · section 7")
    assert bx.options(digits) == []
    many = bx.Box("b1", "you", "x", "Pick", " · ".join(f"opt{c}" for c in "abcdefg"))
    assert len(bx.chips([many]).labels()) == bx.CHIP_CAP
    blk = bx.Box("b2", "block", "x", "PR 9 waiting", "detail")
    full = bx.Box("b1", "you", "x", "Pick", "one · two · three · four")
    assert bx.chips([full, blk]).show == ""  # choices fill the row: no show me
    dup = bx.Box("b1", "you", "x", "Pick", "One · one · later · thanks · two")
    assert bx.options(dup) == ["One", "two"]


def test_the_chip_row_is_ascii_safe_of_control_and_bracket_characters():
    odd = bx.Box("b1", "you", "x", "Pick", "[red]\x1b one · two\x07 · three")
    row = bx.chips([odd]).row()
    assert "\x1b" not in row and "\x07" not in row and "[[" not in row


def test_a_reply_ends_with_its_chips_and_a_choice_is_only_acknowledged():
    api, out = thread_run(["check in", "", "put it back", "block"], boxes=GATE)
    assert chips_of(out)[0].startswith("chips: [put it back] [keep as a grant]")
    assert after(out, "put it back") == [
        "agent · code · no model, nothing served",
        "agent> Got it: put it back.",
    ]
    assert api.names().count("escalate") == 0
    # the row is spent once a choice is made: a second goes to the chain as today
    assert "agent> Got it: block." not in out


def test_thanks_and_later_after_a_reply_are_answered_by_code():
    api, out = thread_run(["status of the build", "thanks", "later"])
    assert "agent> Anytime." in out and "agent> Got it. It stays in the pile." in out
    assert "escalate" not in api.names()


def test_a_choice_not_offered_is_not_taken_for_one():
    _api, out = thread_run(["status of the build", "put it back"])
    assert not any("Got it: put it back" in o for o in out)


def test_show_me_a_ref_shows_the_box_again_in_full_with_a_code_sentence():
    api, out = thread_run(["status of the build", *ALL, "show me 712"])
    got = after(out, "show me 712")
    assert got[0].startswith("+- [blocked] blocked  b4")
    assert "| PR 712 waiting" in got and "| broker verb · 126 tests pass" in got
    assert got[-2:] == [
        "agent · code · no model, nothing served",
        "agent> PR 712's still waiting, 126 tests pass.",
    ]
    assert "escalate" not in api.names()


@pytest.mark.parametrize("line", ["open 712", "B4", "show me b4", "Show me 712?"])
def test_open_and_a_box_id_name_the_same_box(line):
    _api, out = thread_run(["status of the build", *ALL, line])
    assert after(out, line)[0].startswith("+- [blocked] blocked  b4")


def test_ordinals_count_the_boxes_the_last_reply_showed():
    _api, out = thread_run(["status of the build", *ALL, "the second one"])
    assert after(out, "the second one")[0].startswith("+- [blocked] blocked  b4")
    _api, out = thread_run(["status of the build", *ALL, "the first"])
    assert after(out, "the first")[0].startswith("+- [needs you] needs you  b5")


def test_that_is_the_first_of_the_last_page_then_the_box_last_opened():
    _api, out = thread_run(["status of the build", "n", "that"])
    assert after(out, "that")[0].startswith("+- [needs you] needs you  b5")
    _api, out = thread_run(
        ["status of the build", *ALL, "that"]
    )  # the last page: b3 alone
    assert after(out, "that")[0].startswith("+- [changed] changed  b3")
    _api, out = thread_run(["status of the build", *ALL, "show me 712", "that one"])
    assert after(out, "that one")[0].startswith("+- [blocked] blocked  b4")


@pytest.mark.parametrize("line", ["why", "Why?", "what's that", "tell me more"])
def test_why_says_the_boxs_detail_by_code(line):
    api, out = thread_run(["status of the build", *ALL, "show me 712", line])
    got = after(out, line)
    assert got == [
        "agent · code · no model, nothing served",
        "agent> Broker verb, 126 tests pass.",
    ]
    assert "escalate" not in api.names()


def test_why_on_a_box_without_detail_says_so_and_on_a_bare_state_says_its_reason():
    boxes = [bx.Box("b1", "dec", "decided", "phone only proposes")]
    _api, out = thread_run(["status of the build", "why"], boxes=boxes)
    assert (
        "agent> Phone only proposes is decided. Nothing more is on the record for it."
        in out
    )
    down = [bx.Box("b1", "pass", "served", "unreachable — no key", state="unreachable")]
    _api, out = thread_run(["status of the build", "why"], boxes=down)
    assert f"agent> {bx.CANT_READ}. No key." in out


def test_an_ordinal_past_what_was_shown_is_a_plain_line_never_a_guess():
    boxes = demo_boxes()[:3]  # 3 boxes: pages of two, one box left behind more?
    _api, out = thread_run(["status of the build", "n", "the third one"], boxes=boxes)
    got = after(out, "the third one")
    assert got[-1].startswith("agent> I showed 2 boxes (")
    assert got[-1].endswith("so there is no third one.")
    assert not any(o.startswith("+-") for o in got)


def test_a_ref_that_fits_two_boxes_is_said_not_guessed():
    boxes = [
        bx.Box("b1", "block", "x", "PR 712 waiting", "d"),
        bx.Box("b2", "pr", "x", "PR 712 open", "d"),
    ]
    api, out = thread_run(["status of the build", "show me 712"], boxes=boxes)
    got = after(out, "show me 712")
    assert got[-1] == 'agent> "712" fits 2 boxes: b1: PR 712 waiting; b2: PR 712 open.'
    assert "escalate" not in api.names()


def test_go_on_shows_the_next_page_by_code_then_says_nothing_is_left():
    # decline the first more? so the pile keeps the rest, then ask for it
    api, out = thread_run(["status of the build", "n", "go on", "go on", "next"])
    first = after(out, "go on")
    assert "agent · code · said 2 boxes, no model asked" in first
    assert (
        "agent> Oh, and phone only proposes is decided and recorded; PR #127 open. No rush."
        in first
    )
    assert chips_of(first) == []  # one box still behind it
    last = after(out, "go on", 1)
    assert any("b3" in o for o in last) and "agent> Also, PR #714 open." in last
    assert chips_of(last)  # the pile is empty: the row is offered
    assert after(out, "next") == [
        "agent · code · no model, nothing served",
        "agent> Nothing more in the pile.",
    ]
    assert "escalate" not in api.names()


def test_a_follow_up_with_no_reply_before_it_goes_to_the_chain_as_today():
    api = FakeApi()
    st, out = seat(api, ["who", "", "show me 712", ""])
    st.run()
    assert api.names().count("escalate") == 1  # no turn yet: it is a task


def test_show_me_that_no_shown_box_answers_to_is_a_plain_line_not_the_chain():
    """T1: after a turn, ``show me 14`` is a follow-up that found nothing: one
    code line quoting the words, listing what was shown; no escalate, no model."""
    api, out = thread_run(["status of the build", *ALL, "show me 14"])
    got = after(out, "show me 14")
    assert got[-1] == (
        'agent> Nothing I showed answers to "14"; I showed: b5, 712, b1, 127 and 1 more.'
    )
    assert "agent · code · no model, nothing served" in got
    assert "escalate" not in api.names()
    assert not any(o.startswith("+-") for o in got)  # no card, no row


@pytest.mark.parametrize(
    "line,said",
    [
        ("Open Tony?", "Tony"),
        ("show 9999", "9999"),
        ("SHOW ME  the Stack!", "the Stack"),
    ],
)
def test_unmatched_show_forms_quote_the_words_exactly(line, said):
    api, out = thread_run(["status of the build", *ALL, line])
    got = after(out, line)
    assert any(
        o.startswith(f'agent> Nothing I showed answers to "{said}"') for o in got
    )
    assert api.names().count("escalate") == 0


def test_unmatched_show_lists_a_few_refs_and_counts_the_rest():
    boxes = [bx.Box(f"b{n}", "pass", "routine pass", f"check {n}") for n in range(1, 8)]
    line = s.Seat.unmatched("show me zzz", "zzz", boxes)
    assert line == (
        'Nothing I showed answers to "zzz"; I showed: b1, b2, b3, b4 and 3 more.'
    )
    assert s.Seat.unmatched("open x", "x", []) == 'Nothing I showed answers to "x".'


def test_unmatched_show_after_a_store_turn_is_also_a_plain_line(tmp_path):
    p = fixture_store(tmp_path, "s.db")
    api, out = nestor_run(["where are we", "show me 99999"], p)
    got = after(out, "show me 99999")
    assert any(o.startswith('agent> Nothing I showed answers to "99999"') for o in got)
    assert "escalate" not in api.names()


def test_a_line_that_resolves_to_nothing_goes_to_the_chain_as_today():
    calls = []
    api = FakeApi()
    st, out = seat(
        api,
        ["who", "", "status of the build", "show me the stack", "b99", "the sky", ""],
    )
    st.chain = lambda task: (
        st.you(task),
        calls.append(task),
        st.converse(task, demo_boxes()[:2], task),
    )
    st.run()
    # "show me the stack" is a follow-up that found nothing: a code line (T1)
    assert calls == ["status of the build", "b99", "the sky"]


def test_asked_again_still_replays_and_a_follow_up_leaves_no_row():
    ticks = iter(["09:14", "09:14", "09:40", "09:41"])  # the opening reads one
    api, out = thread_run(
        ["status of the build", *ALL, "show me 712", "Status  of the build", "why"],
        clock=lambda: next(ticks),
    )
    assert "as noted at 09:14 · same boxes, nothing new since" in out
    writes = {"take_proposals", "checkin", "checkout", "escalate"}
    assert not [n for n in api.names() if n == "escalate" or n == "take_proposals"]
    assert writes  # (the only api calls are the stages around the turns)


def test_a_follow_up_never_asks_the_model():
    asked = []

    def sayer(prompt):
        asked.append(prompt)
        return "x"

    _api, out = thread_run(
        ["status of the build", "n", "go on", "show me 712", "why", "the first one"],
        say=sayer,
    )
    assert len(asked) == 1  # only the first reply's sentence; none for the follow-ups


# --- the gate's venv is the seat's venv (F1) ------------------------------------------


def _py(path):
    path.mkdir(parents=True)
    (path / "python3").write_text("", encoding="utf-8")


def rv(env, tmp_path, prefix="/usr", base="/usr"):
    return s.resolve_venv(env, prefix, base, tmp_path / "grove")


def test_gate_venv_is_the_running_venv_when_the_interpreter_is_one(tmp_path):
    home = tmp_path / "home"
    _py(home / "venvs" / "willow-bot" / "bin")  # the legacy one exists too
    env = {"WILLOW_HOME": str(home)}
    got = rv(env, tmp_path, prefix=str(tmp_path / "run"), base="/usr")
    assert got == tmp_path / "run"


def test_gate_venv_follows_the_launcher_order_outside_a_venv(tmp_path):
    home = tmp_path / "home"
    new = home / "willow-bot" / "venvs" / "willow-bot"
    old = home / "venvs" / "willow-bot"
    mine = tmp_path / "mine"
    env = {"WILLOW_HOME": str(home), "GROVE_VENV": str(mine)}
    _py(old / "bin")
    assert rv(env, tmp_path) == old  # legacy, when it is all there is
    _py(new / "bin")
    assert rv(env, tmp_path) == new  # D2 beats legacy
    _py(mine / "bin")
    assert rv(env, tmp_path) == mine  # GROVE_VENV beats both


def test_gate_venv_skips_a_grove_venv_with_no_python_and_ends_at_dot_venv(tmp_path):
    home = tmp_path / "home"
    env = {"WILLOW_HOME": str(home), "GROVE_VENV": str(tmp_path / "gone")}
    _py(tmp_path / "grove" / ".venv" / "bin")
    assert rv(env, tmp_path) == tmp_path / "grove" / ".venv"


def test_gate_venv_with_nothing_is_the_d2_path_not_the_legacy_one(tmp_path):
    (tmp_path / "home").mkdir()
    env = {"WILLOW_HOME": str(tmp_path / "home")}
    want = tmp_path / "home" / "willow-bot" / "venvs" / "willow-bot"
    assert rv(env, tmp_path) == want


def test_gate_venv_box_is_the_bots_rule(tmp_path):
    """F-17: the box is WILLOW_HOME, else WILLOW_VAULT_BOX, an existing
    absolute directory; one that is not is refused, never passed over; no box
    is no venv, never a guessed home."""
    vb = tmp_path / "vb"
    _py(vb / "willow-bot" / "venvs" / "willow-bot" / "bin")
    assert (
        rv({"WILLOW_VAULT_BOX": str(vb)}, tmp_path)
        == vb / "willow-bot" / "venvs" / "willow-bot"
    )
    assert rv({"WILLOW_HOME": "  ", "WILLOW_VAULT_BOX": str(vb)}, tmp_path) == (
        vb / "willow-bot" / "venvs" / "willow-bot"
    )  # blank is unset
    for bad in ("rel/box", str(tmp_path / "missing")):
        assert rv({"WILLOW_HOME": bad, "WILLOW_VAULT_BOX": str(vb)}, tmp_path) is None
    assert rv({}, tmp_path) is None


def test_the_box_rule_is_read_from_the_seats_own_willow_bot(tmp_path, monkeypatch):
    """Where willow-bot is is the seat's (its WILLOW_BOT_ROOT, as seat_boxes
    reads it), not part of the box env judged: with no willow-bot beside
    Grove (CI checks it out inside), the rule is still the bot's; with none
    named and none beside, no box, never a guess."""
    bot = os.environ.get("WILLOW_BOT_ROOT") or str(s.GROVE_ROOT.parent / "willow-bot")
    if not (Path(bot) / "willow_bot" / "paths.py").is_file():
        pytest.skip(f"no willow-bot at {bot}")
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(s, "GROVE_ROOT", tmp_path / "grove")  # nothing beside
    monkeypatch.setenv("WILLOW_BOT_ROOT", bot)
    assert s._bot_box({"WILLOW_HOME": str(home)}) == home
    monkeypatch.delenv("WILLOW_BOT_ROOT")
    assert s._bot_box({"WILLOW_HOME": str(home)}) is None


def test_config_hands_the_gate_the_resolved_venv(tmp_path, monkeypatch):
    home = tmp_path / "home"
    new = home / "willow-bot" / "venvs" / "willow-bot"
    _py(new / "bin")
    monkeypatch.setenv("WILLOW_HOME", str(home))
    monkeypatch.delenv("GROVE_VENV", raising=False)
    monkeypatch.setattr(sys, "prefix", sys.base_prefix)

    class Cfg:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    api = FakeApi()
    api.Config = Cfg
    api.default_keyring = lambda: None
    api.default_nestor_db = lambda: None
    cfg = s.config(bot(api), tmp_path / "bot", tmp_path / "grove")
    assert cfg.venv == new


# --- check-in cards take their kind from the row's status (F2) -------------------------

TESTS_LINE = "tests: onescript: failed: 23 failed, 375 passed, 10 skipped in 16.03s"
TOOL_LINE = "toolchain: ruff: can't run on the box: not installed; pinned 0.16.7"
GATES = [
    {"gate": "tests", "where": "onescript", "verdict": "failing",
     "why": "failed: 23 failed, 375 passed, 10 skipped in 16.03s"},
    {"gate": "toolchain", "where": "ruff", "verdict": "unreachable",
     "why": "can't run on the box: not installed; pinned 0.16.7"},
    {"gate": "freshness", "where": "g", "verdict": "satisfied", "why": "3 ahead"},
]  # fmt: skip


def checkin_cards(report):
    api = FakeApi(checkin={"report": report})
    st, out = seat(api, [])
    st.run()
    return text(out)


def test_a_failed_test_run_in_the_check_in_is_blocked_not_a_routine_pass():
    out = checkin_cards(
        {"hard_close": True, "lines": [TESTS_LINE, TOOL_LINE], "gates": GATES}
    )
    assert "[blocked] check-in" in out
    assert "[routine pass] check-in" not in out
    assert out.count("[blocked] check-in") == 3  # two lines + the HARD CLOSE card


def test_a_record_break_line_of_a_hard_close_is_blocked_too():
    out = checkin_cards({"hard_close": True, "lines": ["record: broken at n=4"]})
    assert "[blocked] check-in" in out


def test_a_clean_check_in_line_stays_a_routine_pass():
    out = checkin_cards({"hard_close": False, "lines": ["probes: 4/4"]})
    assert "[routine pass] check-in" in out


def test_checkin_kind_reads_the_gate_verdict_not_the_words():
    ok = {"gate": "tests", "where": "x", "verdict": "satisfied", "why": "failed 0"}
    rep = {"hard_close": False, "gates": [ok]}
    assert s.checkin_kind("tests: x: failed 0", rep) == "pass"
    bad = {**ok, "verdict": "failing"}
    assert s.checkin_kind("tests: x: failed 0", {"gates": [bad]}) == "block"


# --- the stage prompts: defaults stated, a refused answer said plainly (F4) ---------------

BY_REFUSAL = (
    "group by one or more of ('who', 'what', 'when', 'where'), got ('where are we',)"
)


def scope_says(res_ok):
    """A scope api that refuses any ``by`` outside the four words."""

    def call(cfg, by=(), **_):
        if any(w not in ("who", "what", "when", "where") for w in by):
            return {"refused": BY_REFUSAL, "code": 1}
        return res_ok

    return call


def test_the_prompts_state_their_defaults_plainly():
    api = FakeApi()
    _st, out = seat(api, ["", ""])
    _st.run()
    assert "scope ▶ group by (enter = who): " in out
    assert "served ▶ cap in characters (enter = 48000): " in out


def test_a_refused_group_by_is_said_plainly_and_asked_again_not_unreachable():
    api = FakeApi()
    api.res["scope"] = scope_says(api.res["scope"])
    st, out = seat(api, ["where are we", "", ""])
    assert st.run() == 0
    body = text(out)
    assert 'Group by takes who, what, when or where; you said "where are we".' in body
    assert "[unreachable]" not in body and "can't read the record" not in body
    assert sum(1 for o in out if o.startswith("scope ▶")) == 2  # asked again
    assert "serve" in api.names()  # and then the run went on


def test_group_by_words_are_trimmed_and_enter_takes_the_default():
    api = FakeApi()
    api.res["scope"] = scope_says(api.res["scope"])
    st, _out = seat(api, ["who, what", "", ""])
    st.run()
    assert [c for c in api.calls if c[0] == "scope"][0][2]["by"] == ["who", "what"]


def test_any_other_scope_refusal_stays_a_refused_card():
    api = FakeApi(scope={"refused": "no open box", "code": 2})
    st, out = seat(api, [""])
    assert st.run() == 0
    assert "[unreachable] refused" in text(out) and "Group by takes" not in text(out)


def test_a_cap_that_is_not_a_whole_number_is_said_plainly_and_asked_again():
    api = FakeApi()
    st, out = seat(api, ["", "lots", "0", "-5", "100", ""])
    assert st.run() == 0
    body = text(out)
    assert 'The cap takes a whole number, 1 or more; you said "lots".' in body
    assert 'you said "0"' in body and 'you said "-5"' in body
    assert "[blocked]" not in body
    assert [c for c in api.calls if c[0] == "serve"][0][2]["max_chars"] == 100


# --- small talk: greetings, acknowledgements, help, farewells (F5) ------------------------


def talk(*lines):
    api = FakeApi()
    st, out = seat(api, ["", "", *lines, ""])
    assert st.run() == 0
    return api, text(out)


@pytest.mark.parametrize(
    "word", ["hi", "Hello", "hey", "morning", "Good morning", "hi!"]
)
def test_a_greeting_is_answered_by_code_not_the_chain(word):
    api, out = talk(word)
    assert s.HELLO in out and "escalate" not in api.names()


@pytest.mark.parametrize("word", ["ok", "okay", "cool", "got it", "sure"])
def test_an_acknowledgement_is_answered_by_code_not_the_chain(word):
    api, out = talk(word)
    assert "agent> Got it." in out and "escalate" not in api.names()


@pytest.mark.parametrize("word", ["help", "what can you do", "What can you do?"])
def test_help_lists_what_the_seat_understands_in_a_fixed_line(word):
    api, out = talk(word)
    assert s.HELP in out and "escalate" not in api.names()
    for part in ('"where are we"', "show me", "why", "second one", "go on", "later"):
        assert part in s.HELP


@pytest.mark.parametrize("word", ["bye", "done", "quit", "Bye!"])
def test_a_farewell_checks_out_like_an_empty_line(word):
    api = FakeApi()
    st, out = seat(api, ["", "", word, "never read"])
    assert st.run() == 0
    assert api.names()[-2:] == ["checkout", "pooled"]
    assert "escalate" not in api.names() and f"you: {word}" in out
    assert not any(o.startswith("chain ▶") for o in out[out.index(f"you: {word}") :])


def test_small_talk_replies_use_only_glue_or_fixed_lines():
    for reply in s.SMALL_TALK.values():
        assert reply in (s.HELLO, s.HELP, "Anytime.", "Got it.", s.STAY)
    glue = {g.capitalize() for g in bx.GLUE}
    assert {"Anytime", "Got it"} <= glue


def test_declining_more_still_says_the_pile_keeps_it():
    api = FakeApi(
        escalate={
            "task": "t",
            "answered": 3,
            "escalated": 0,
            "pieces": [
                {"piece": f"p{i}" * 8, "label": f"L{i}", "rung": "d0",
                 "outcome": "answered", "detail": f"d{i}"}
                for i in range(3)
            ],
        }
    )  # fmt: skip
    st, out = seat(api, ["", "", "task", "ok", ""])
    st.run()
    assert f"agent> {s.STAY}" in out


# --- phrasing on real data (F6) -----------------------------------------------------------

LONG_YOU = bx.Box(
    "b7116acfef88",
    "you",
    "escalated:empty_scope",
    "d0: the scope is 'empty': the scope has no human seal over this exact set; "
    "nothing served",
    "reason: empty_scope",
)
CHAIN = bx.Box("b4", "pass", "chain", "answered 0, escalated 1")


def test_a_long_needs_you_value_is_not_given_a_dangling_suffix():
    said = bx.compose([LONG_YOU])
    assert said.startswith("This needs you: d0: the scope is 'empty'")
    assert "nothing served needs you" not in said and said.endswith("nothing served.")
    assert bx.cap(bx.clause(LONG_YOU)).startswith("This needs you: ")


def test_a_short_needs_you_value_keeps_its_suffix_and_a_verb_phrase_its_lead():
    assert bx.compose([bx.Box("b1", "you", "x", "PR 712")]) == "PR 712 needs you."
    got = bx.compose([bx.Box("b1", "you", "x", "Ratify the work order")])
    assert got == "You need to ratify the work order."
    comma = bx.Box("b1", "you", "x", "PR 712, 713")
    assert "needs you: PR 712, 713" in bx.compose([comma])


def test_the_chain_count_is_a_sentence_and_never_a_heads_up_over_a_bare_count():
    got = bx.compose([LONG_YOU, CHAIN])
    assert "The chain answered 0 and escalated 1." in got
    assert "Heads up: answered" not in got and "Heads up" not in got
    assert "No rush" not in got  # an escalation is still no calm
    assert bx.compose([CHAIN]) == "The chain answered 0 and escalated 1."
    calm = bx.Box("b2", "pass", "chain", "answered 2, escalated 0")
    assert bx.compose([calm]).endswith("the chain answered 2 and escalated 0. No rush.")
    still = bx.Box("b3", "pass", "check", "3 failed")
    assert "Heads up: " in bx.compose([still])  # a real problem still is one


def test_no_rush_is_said_at_most_once_per_turn():
    boxes = [bx.Box(f"b{i}", "pass", "x", f"fine {i}") for i in range(1, 5)]
    api = FakeApi()
    st, out = seat(api, ["who", "", "task", "", ""])

    def chain(task):
        st.you(task)
        st.converse(s._norm(task), list(boxes), task)

    st.chain = chain
    st.run()
    assert text(out).count("No rush") == 1
    assert bx.compose(boxes[:2], rush=False).endswith("are both routine.")
    assert bx.compose(boxes[:2]).endswith("No rush.")


# --- "where are we" / "what needs me": the Nestor store, read-only -----------------------

from types import SimpleNamespace  # noqa: E402

from tests.test_seat_nestor import PAIRS, REJS, make, pair  # noqa: E402


def nestor_run(keys, path):
    api = FakeApi()
    st, out = seat(api, ["who", "", *keys, ""])
    st.cfg = SimpleNamespace(nestor_db=path)
    assert st.run() == 0
    return api, out


def store_cards(lines):
    """A turn's printed lines without the record's own ``empty`` card, which
    these store tests (a FakeApi whose record holds nothing) all lead with."""
    out, skip = [], False
    for ln in lines:
        if ln.startswith("+. [empty] record  rstate"):
            skip = True
        elif skip and ln.startswith(":"):
            continue
        else:
            skip = False
            out.append(ln)
    return out


def small_store(tmp_path):
    rows = [
        pair(1, "Hola", "Hello", reason="Settled it once."),
        pair(2, "Adios", "Bye", status="draft", reason="Not sure yet."),
    ]
    rej = ("r1", "hola", "es", "en", "Howdy", "ana", "Too American.", "2026-02-01", "")
    return make(tmp_path / "n.db", rows, [rej], schema=(PAIRS, REJS))


def test_where_are_we_with_no_store_is_the_records_answer_never_the_chain():
    # the record answered (here: nothing waits), so a store that is not
    # configured is not an "unreachable" box; the card says only the record was read
    api, out = nestor_run(["where are we"], None)
    body = text(out)
    assert "+. [empty] record  rstate" in body
    assert "no Nestor store is configured, so only the record was read" in body
    assert "[unreachable]" not in body and "nstate" not in body
    assert "agent> Record is empty: nothing on the record waits on you." in body
    assert "escalate" not in api.names()
    assert api.names().count("needs") == 1


def test_where_are_we_reads_the_store_and_follow_ups_work_on_its_boxes(tmp_path):
    p = small_store(tmp_path)
    before = p.read_bytes()
    api, out = nestor_run(["Where are we?", "", "the second one", "why", "go on"], p)
    body = text(out)
    assert "[blocked]" in body and '"Howdy" for hola' in body
    assert "Adios (draft)" in body and "(fixture)" in body
    assert "escalate" not in api.names()
    assert "Hola → Hello" in body  # opened by 'the second one' or 'go on'
    assert 'reason: "Too American."' in body or "Too American." in body
    assert p.read_bytes() == before  # the seat wrote nothing to the store


def test_where_are_we_empty_store_is_empty_not_unreachable(tmp_path):
    p = make(tmp_path / "e.db", schema=(PAIRS, REJS))
    _api, out = nestor_run(["where are we"], p)
    body = text(out)
    assert "+. [empty]" in body and "Nestor store is empty" in body
    assert "[unreachable]" not in body


def test_where_are_we_missing_file_says_the_path(tmp_path):
    _api, out = nestor_run(["where are we"], tmp_path / "gone.db")
    assert "no Nestor store at" in text(out) and "gone.db" in text(out)


def test_what_needs_me_lists_only_the_waiting_drafts_as_drafts(tmp_path):
    api, out = nestor_run(["what needs me?"], small_store(tmp_path))
    body = text(out)
    assert "[needs you]" in body and "Adios (draft)" in body
    assert "[blocked]" not in body and "[decided]" not in body
    assert "agent> " in body and "Adios → Bye" not in body
    assert "escalate" not in api.names()


def test_what_needs_me_with_nothing_waiting_says_so(tmp_path):
    p = make(tmp_path / "d.db", [pair(1, "Hola", "Hello")], schema=(PAIRS, REJS))
    _api, out = nestor_run(["what needs me"], p)
    body = text(out)
    # two empties, each its own card: the record's and the store's waiting drafts
    assert "+. [empty] record  rstate" in body
    assert "+. [empty] nestor drafts  nwait" in body and "none waiting on you" in body
    assert "[needs you]" not in body and "[unreachable]" not in body


def test_asking_again_after_the_store_changed_is_a_fresh_read(tmp_path):
    p = small_store(tmp_path)
    api = FakeApi()
    st, out = seat(api, ["who", "", "where are we", "", "where are we", "", ""])
    st.cfg = SimpleNamespace(nestor_db=p)
    orig = st.status
    calls = []

    def status(task):
        if calls:  # the store grows between the two asks
            import sqlite3

            con = sqlite3.connect(p)
            con.execute("DELETE FROM tm_rejections")
            con.commit()
            con.close()
        calls.append(task)
        orig(task)

    st.status = status
    st.run()
    body = text(out)
    assert "same boxes, nothing new since" not in body
    assert body.count("[blocked]") == 1  # the second read lost the rejection


def test_help_mentions_the_store_turn():
    assert '"where are we"' in s.HELP and '"what needs me"' in s.HELP
    assert "Nestor" in s.HELP


# --- why: the reason, said naturally; no doubled full stop -------------------------------


def fixture_store(tmp_path, name="f.db"):
    rows = [
        pair(1, "Hola", "Hello", reason="Settled it once.", origin="fixture:demo"),
        pair(
            2,
            "Adios",
            "Bye",
            status="draft",
            reason="Leaving it.",
            origin="fixture:demo",
        ),
    ]
    rej = (
        "r1",
        "hola",
        "es",
        "en",
        "Howdy",
        "ana",
        "Not little. Never.",
        "2026-02-01",
        "",
    )
    ny = (
        "r2",
        "casa",
        "es",
        "en",
        "the house",
        "ana",
        "Guessing.",
        "2026-02-02",
        "the photo",
    )
    return make(tmp_path / name, rows, [rej, ny], schema=(PAIRS, REJS))


def why_of(tmp_path, which):
    from grove.seat_nestor import read_store

    path = fixture_store(tmp_path, f"f{len(list(tmp_path.iterdir()))}.db")
    box = next(b for b in read_store(path).boxes if which(b))
    return s.Seat.detail_sentence(box)


def test_why_on_a_no_is_who_said_no_and_her_words_exactly(tmp_path):
    got = why_of(tmp_path, lambda b: b.label.startswith("a no"))
    assert got == 'Ana said no: "Not little. Never." (fixture).'
    assert '"Not little. Never."' in got  # her words, exact
    assert "origin" not in got and "never serve" not in got


def test_why_keeps_the_fixture_marker_when_it_drops_the_provenance_line(tmp_path):
    for which in (lambda b: b.kind == "dec", lambda b: b.label.startswith("not yet")):
        got = why_of(tmp_path, which)
        assert got.endswith("(fixture).") and "origin" not in got


def test_why_on_a_seal_a_not_yet_and_a_draft(tmp_path):
    seal = why_of(tmp_path, lambda b: b.kind == "dec")
    assert seal == 'Ana sealed it: "Settled it once." (fixture).'
    ny = why_of(tmp_path, lambda b: b.label.startswith("not yet"))
    assert (
        ny.startswith('Ana said not yet: "Guessing."')
        and 'Reopen when: "the photo"' in ny
    )
    dr = why_of(tmp_path, lambda b: "draft" in b.label)
    assert 'Reason: "Leaving it."' in dr and "nobody has confirmed it" in dr


def test_why_on_a_chain_box_is_its_reason_with_no_provenance_noise():
    b = bx.Box("b1", "block", "x", "scope held", "reason: empty_scope")
    assert s.Seat.detail_sentence(b) == "Reason: empty_scope."


@pytest.mark.parametrize(
    "text",
    ['She said "Go."', 'Is it "ready?"', "Done!", "Plain", "Wait (really).", ""],
)
def test_terminate_never_doubles_the_end(text):
    got = bx.terminate(text)
    assert not got.endswith(('.".', '?".', '!".', "..")) and got.startswith(text)
    assert bx.terminate(got) == got


def test_a_quoted_reason_ending_a_value_is_not_followed_by_a_second_full_stop():
    q = bx.Box("b1", "pass", "x", 'she wrote "done."')
    assert bx.compose([q], rush=False) == 'Looks like she wrote "done."'
    assert s.Seat.open_sentence(q) == 'She wrote "done."'
    two = bx.compose([q, bx.Box("b2", "you", "y", 'sign "here?"')])
    assert '".' not in two.replace('."', "").replace('?"', "") and not two.endswith(
        '".'
    )
    gone = bx.Box("b3", "pass", "x", 'unreachable — said "no."', state="unreachable")
    assert bx.plain_line(gone).endswith('Said "no."')
    assert bx.compose([gone]).endswith('Said "no."')


def test_a_chip_choice_ending_in_a_quote_is_acknowledged_without_a_second_stop():
    box = bx.Box("b1", "you", "x", "Pick", 'say "ok." · say "no." · say "later."')
    _api, out = thread_run(["status of the build", 'say "ok."'], boxes=[box])
    assert 'agent> Got it: say "ok."' in out and 'agent> Got it: say "ok.".' not in out


# --- counts code says are pluralised ("1 box", "2 boxes") --------------------------------


@pytest.mark.parametrize(
    "n, got", [(0, "0 boxes"), (1, "1 box"), (2, "2 boxes"), (10, "10 boxes")]
)
def test_plural_says_one_box_and_n_boxes(n, got):
    assert bx.plural(n, "box", "boxes") == got
    assert bx.pile_header(n) == f"the pile · {got} on the record"
    assert bx.plural(1, "row") == "1 row" and bx.plural(3, "row") == "3 rows"


def test_the_who_line_says_one_box_when_a_page_holds_one():
    boxes = demo_boxes()[:3]  # pages of two: the second page is one box
    _api, out = thread_run(
        ["status of the build", "", "status of the build", ""], boxes=boxes
    )
    t = text(out)
    assert "agent · code · said 2 boxes, no model asked" in t
    assert t.count("agent · code · said 1 box, no model asked") == 1
    assert "shown again from the pile" in t  # the replay who-line carries no count
    assert "1 boxes" not in t


def test_a_one_row_table_and_a_one_draft_deposit_are_not_plural():
    assert s.row_count(1) == "1 row" and s.row_count(136) == "136 rows"
    assert s.row_count("?") == "? rows"


def test_ten_more_sealed_and_one_more_in_the_pile_read_right(tmp_path):
    rows = [pair(n, f"s{n}", f"t{n}", reason=f"r{n}.") for n in range(1, 16)]
    p = make(tmp_path / "t.db", rows, [], schema=(PAIRS, REJS))
    from grove.seat_nestor import read_store

    vals = [b.value for b in read_store(p).boxes]
    assert "11 more sealed" in vals
    one = make(tmp_path / "o.db", rows[:5], [], schema=(PAIRS, REJS))
    assert "1 more sealed" in [b.value for b in read_store(one).boxes]


def test_one_more_rejection_and_one_box_shown_are_singular(tmp_path):
    from grove.seat_nestor import read_store

    rej = [
        (f"r{n}", f"q{n}", "es", "en", f"t{n}", "ana", f"no {n}.", f"2026-02-0{n}", "")
        for n in range(1, 6)
    ]
    p = make(tmp_path / "r.db", [], rej, schema=(PAIRS, REJS))
    vals = [b.value for b in read_store(p).boxes]
    assert "2 more rejections" in vals
    p2 = make(tmp_path / "r2.db", [], rej[:4], schema=(PAIRS, REJS))
    assert "1 more rejection" in [b.value for b in read_store(p2).boxes]
    one = [bx.Box("b1", "dec", "decided", "phone only proposes", "recorded")]
    _api, out = thread_run(["status of the build", "the third one"], boxes=one)
    assert (
        "agent> I showed 1 box (b1: phone only proposes), so there is no third one."
        in out
    )


# --- "where are we" leads with the count, then what is open (the shoebox sketch) ---------


def test_lead_rank_is_count_then_drafts_then_refusals_then_decided(tmp_path):
    from grove.seat_nestor import lead_rank, read_store

    got = read_store(fixture_store(tmp_path, "l.db"))
    order = [b.label.split(" ·")[0].split(" (")[0] for b in lead_rank(got.boxes)]
    assert order == [
        "nestor store",
        "draft, waiting",
        "a no",
        "not yet",
        "sealed by ana",
    ]
    generic = [
        b.kind for b in got.boxes
    ]  # the reading itself is still the generic rank
    assert generic == ["block", "block", "dec", "pr", "pass"]
    down = read_store(tmp_path / "nope.db")
    assert lead_rank(down.boxes) == down.boxes  # a heads-up still leads alone


def test_where_are_we_opens_with_the_count_then_the_open_items(tmp_path):
    p = fixture_store(tmp_path, "w.db")
    before = hashlib.sha256(p.read_bytes()).hexdigest()
    api, out = nestor_run(["where are we"], p)
    t = text(out)
    first = store_cards(after(out, "where are we"))
    assert first[0].startswith("+- [routine pass] nestor store")  # the count first
    said = next(o for o in first if o.startswith("agent> "))
    assert said.startswith(
        "agent> Record is empty: nothing on the record waits on you. "
        "1 sealed, 1 draft, 2 rejected (fixture). "
    )
    assert "Adios (draft) is waiting." in said  # a draft, never a fact
    assert (
        "said 6 boxes, no model asked" in t and "more?" not in t
    )  # one page: the record card and the five
    assert "Looks like" not in t and "No rush" not in t  # a refusal is in the store
    drafts = t.index("[changed] draft, waiting")
    assert t.index("[routine pass]") < drafts < t.index("[blocked]")
    assert "escalate" not in api.names()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == before  # still read-only


def test_the_count_page_keeps_no_rush_when_the_store_holds_no_refusal(tmp_path):
    p = make(
        tmp_path / "c.db",
        [pair(1, "Hola", "Hello", reason="Once.")],
        [],
        schema=(PAIRS, REJS),
    )
    _api, out = nestor_run(["where are we"], p)
    said = next(o for o in after(out, "where are we") if o.startswith("agent> "))
    # the empty record card is a heads-up, so no "No rush."
    assert said == (
        "agent> Record is empty: nothing on the record waits on you. "
        "1 sealed (fixture). Hola → Hello is decided."
    )


def test_a_chain_turn_and_what_needs_me_keep_the_generic_rank(tmp_path):
    p = fixture_store(tmp_path, "n.db")
    _api, out = nestor_run(["what needs me"], p)
    first = store_cards(after(out, "what needs me"))
    assert first[0].startswith("+- [needs you] draft, waiting")
    _api, out = thread_run(["status of the build"])  # a chain turn: generic rank
    assert after(out, "status of the build")[0].startswith("+- [needs you]")


def test_lead_rank_puts_a_heads_up_first_and_a_more_box_last_in_its_group():
    from grove.seat_nestor import lead_rank

    mk = bx.Box
    boxes = [
        mk("a", "dec", "more · 4 shown", "11 more sealed", role="more"),
        mk("b", "dec", "sealed by x", "s1 → t1"),
        mk("c", "pr", "more · 4 shown", "2 more drafts or changes", role="more"),
        mk("d", "pr", "changed", "c1"),
        mk("e", "pr", "draft, waiting", "d1 (draft)", role="draft"),
        mk("f", "block", "a no", "r1"),
        mk("g", "pass", "nestor store", "3 sealed"),
        mk("h", "pass", "nestor store", "unreachable — gone", state="unreachable"),
    ]
    assert [b.id for b in lead_rank(boxes)] == list("hgefbadc")


# --- names keep their capital; drafts and counts are not said as facts -------------------


def _draft(i, value, kind="pr"):
    return bx.Box(i, kind, "draft, waiting", f"{value} (draft)", role="draft")


def test_a_name_keeps_its_capital_and_only_known_words_lose_theirs():
    assert bx.lead("Tony (draft)") == "Tony (draft)"
    assert bx.lead("Tony → Antonio") == "Tony → Antonio"
    assert bx.lead("Ratify the work order") == "ratify the work order"
    assert bx.lead("The house") == "the house" and bx.lead("PR 712") == "PR 712"
    assert bx.lead("I understand") == "I understand"
    say = bx.compose(
        [_draft("a", "Ana"), bx.Box("b", "dec", "d", "Tony → Antonio")], False
    )
    assert "Tony → Antonio" in say and "tony" not in say


def test_you_need_to_is_said_only_of_a_verb_phrase_never_a_draft_or_a_name():
    ok = bx.compose([bx.Box("b1", "you", "x", "Ratify the work order")])
    assert ok == "You need to ratify the work order."
    one = bx.compose([_draft("a", "Tony", "you")])
    assert one == "Tony (draft) is waiting on you."
    assert (
        bx.compose([bx.Box("b1", "you", "x", "Tony Smith")]) == "Tony Smith needs you."
    )
    the = bx.compose([bx.Box("b1", "you", "x", "The roof")])
    assert "need to" not in the  # a starter that is not a verb
    page = bx.compose([_draft("a", "Tony", "you")], False, page=1)
    assert page == "Oh, and Tony (draft) is waiting on you."
    assert "need to" not in page


def test_draft_pairs_and_lists_have_a_verb_and_keep_the_draft_marker():
    one = bx.compose([_draft("a", "Tony")])
    assert one == "Tony (draft) is waiting."
    two = bx.compose([_draft("a", "Ana"), _draft("b", "Luz")])
    assert two == "Both drafts are waiting: Ana (draft) and Luz (draft)."
    three = bx.compose([_draft("a", "Ana"), _draft("b", "Luz"), _draft("c", "Eva")])
    assert three == "The drafts are waiting: Ana (draft), Luz (draft) and Eva (draft)."
    later = bx.compose([_draft("a", "Ana"), _draft("b", "Luz")], False, page=2)
    assert later.startswith("Also, both drafts are waiting: Ana (draft)")
    both_you = bx.compose([_draft("a", "Ana", "you"), _draft("b", "Luz", "you")])
    assert both_you == "Both need you: Ana (draft) and Luz (draft)."


def test_a_more_box_is_a_count_said_apart_never_paired_into_a_fact():
    more = bx.Box("m", "dec", "more · 4 shown", "10 more sealed", role="more")
    dec = bx.Box("d", "dec", "sealed", "me hago cargo → I understand")
    got = bx.compose([dec, more], page=0, look=False)
    assert got == (
        "Me hago cargo → I understand is decided. 10 more sealed are in the store."
        " No rush."
    )
    one = bx.Box("m", "pr", "more · 1 shown", "1 more draft or change", role="more")
    chg = bx.Box("c", "pr", "changed", 'x: "a" was replaced')
    got = bx.compose([chg, one], page=0, look=False)
    assert "both" not in got and "1 more draft or change is in the store." in got
    two = bx.compose([more, bx.Box("n", "pr", "more", "2 more drafts", role="more")])
    assert "both" not in two and "are decided" not in two


def test_the_count_and_more_boxes_are_never_a_show_me_ref():
    count = bx.Box(
        "nd1", "pass", "nestor store", "14 sealed, 3 drafts", "x", role="count"
    )
    more = bx.Box(
        "nm2", "dec", "more · 4 shown", "10 more sealed", "older", role="more"
    )
    other = bx.Box("n123", "dec", "sealed", "a → b", "sealed by ana")
    assert bx.ref_tokens(count) == [] and bx.ref_tokens(more) == []
    assert bx.chips([count, more]).show == ""
    assert bx.chips([count, more, other]).show == "show me n123"
    assert not bx.matches(count, "14") and not bx.matches(more, "10")
    assert not bx.matches(count, "14 sealed") and bx.matches(count, "nd1")
    # the same value on an ordinary box is still a ref
    plain = bx.Box("b9", "pass", "tests", "14 sealed", "d")
    assert bx.ref_tokens(plain)[0] == "14" and bx.matches(plain, "14")


def test_show_me_a_count_does_not_open_the_count_box(tmp_path):
    p = fixture_store(tmp_path, "s.db")
    _api, out = nestor_run(["where are we", "show me 1"], p)
    got = after(out, "show me 1")
    assert not any(o.startswith("+- [routine pass] nestor store") for o in got)


def big_store(tmp_path):
    rows = [pair(n, f"s{n}", f"t{n}", reason=f"r{n}.") for n in range(1, 11)]
    rows += [
        pair(20 + n, f"d{n}", f"e{n}", status="draft", reason=f"why {n}.")
        for n in range(1, 4)
    ]
    rej = [
        (f"r{n}", f"q{n}", "es", "en", f"t{n}", "ana", f"no {n}.", f"2026-02-0{n}", "")
        for n in range(1, 3)
    ]
    return make(tmp_path / "big.db", rows, rej, schema=(PAIRS, REJS))


def test_where_are_we_on_a_big_store_takes_two_more_presses_not_six(tmp_path):
    p = big_store(tmp_path)
    before = hashlib.sha256(p.read_bytes()).hexdigest()
    _api, out = nestor_run(["where are we", "", "", "the third one"], p)
    asks = [o for o in out if o.startswith("more? ▶")]
    assert len(asks) == 2  # page one, then two more pages
    first = after(out, "where are we")
    assert first[0].startswith("+. [empty] record")  # the record's heads-up leads
    first = store_cards(first)
    assert first[0].startswith("+- [routine pass] nestor store")  # then the count
    shown = [o for o in first if o.startswith("+- [")]
    assert len(shown) == 1 + s.STORE_PAGE  # the count plus one store page
    assert sum(o.startswith("+- [changed] draft, waiting") for o in first) == 3
    said = next(o for o in first if o.startswith("agent> "))
    assert "The drafts are waiting: d1 (draft), d2 (draft) and d3 (draft)." in said
    nxt = after(out, "more")
    assert sum(o.startswith("+- [") for o in nxt) == s.STORE_PAGE
    ordinal = after(out, "the third one")
    # counts shown boxes: the record's empty card, the count, then the first draft
    assert ordinal[0].startswith("+- [changed] draft, waiting")
    assert hashlib.sha256(p.read_bytes()).hexdigest() == before


def test_the_chain_keeps_its_two_boxes_a_page():
    assert s.PAGE == 2 and s.STORE_PAGE > s.PAGE
    t = s.Turn("t", [bx.Box(f"b{i}", "dec", "d", f"v{i}") for i in range(5)])
    assert [len(t.take()) for _ in range(3)] == [2, 2, 1]


def test_a_store_turn_asked_again_replays_what_was_shown(tmp_path):
    p = big_store(tmp_path)
    _api, out = nestor_run(["where are we", "", "", "where are we"], p)
    assert "as noted at" in text(out)


def test_a_run_of_three_decided_boxes_has_a_verb():
    dec = [bx.Box(f"d{i}", "dec", "sealed", f"a{i} → b{i}") for i in range(3)]
    got = bx.compose(dec, page=0, look=False, rush=False)
    assert got == "A0 → b0, a1 → b1 and a2 → b2 are all decided."


@pytest.mark.parametrize("kind,word", [("pr", "changed"), ("pass", "routine")])
def test_a_run_of_three_changed_or_routine_boxes_has_a_verb(kind, word):
    mixed = [
        bx.Box(f"b{i}", kind, "x", v)
        for i, v in enumerate(["PR 1 open", "PR 2 merged", "tests ok"])
    ]
    got = bx.compose(mixed, page=0, look=False, rush=False)
    assert got == f"PR 1 open, PR 2 merged and tests ok are all {word}."


@pytest.mark.parametrize("kind", ["pr", "pass"])
def test_a_run_of_three_that_shares_a_status_word_says_it(kind):
    same = [bx.Box(f"b{i}", kind, "x", f"PR {i} open") for i in range(3)]
    got = bx.compose(same, page=0, look=False, rush=False)
    assert got == "PR 0, PR 1 and PR 2 are all open."
    one = [bx.Box(f"b{i}", kind, "x", f"PR {i} open") for i in range(2)]
    assert "all" not in bx.compose(
        one, page=0, look=False, rush=False
    )  # a pair keeps both


def test_unmatched_show_falls_back_to_box_ids_and_skips_counts():
    boxes = [
        bx.Box("n4ee2a", "pr", "changed", "Tony (draft)", role="draft"),
        bx.Box("n9", "pass", "routine pass", "14 sealed", role="count"),
        bx.Box("n76c05", "pr", "changed", "la casa (draft)", role="draft"),
    ]
    assert s.Seat.unmatched("show me 14", "14", boxes) == (
        'Nothing I showed answers to "14"; I showed: n4ee2a, n76c05.'
    )


@pytest.mark.parametrize("kind,word", [("pr", "changed"), ("pass", "routine")])
def test_a_pair_of_changed_or_routine_boxes_has_a_verb(kind, word):
    two = [
        bx.Box(f"b{i}", kind, "x", v) for i, v in enumerate(["PR 1 open", "tests ok"])
    ]
    got = bx.compose(two, page=0, look=False, rush=False)
    assert got == f"PR 1 open and tests ok are both {word}."
    assert bx.RUN_VERB[kind] == word  # one source of truth with a run


@pytest.mark.parametrize("kind", ["pr", "pass"])
def test_a_pair_that_shares_a_status_word_says_it(kind):
    two = [bx.Box(f"b{i}", kind, "x", f"PR {i} open") for i in range(2)]
    got = bx.compose(two, page=0, look=False, rush=False)
    assert got == "PR 0 and PR 1 are both open."


@pytest.mark.parametrize("kind", ["pr", "pass"])
def test_a_shared_last_word_that_is_not_a_status_gets_the_fixed_word(kind):
    word = bx.RUN_VERB[kind]
    two = [
        bx.Box("b1", kind, "x", "local: a short answer"),
        bx.Box("b2", kind, "x", "local: another answer"),
    ]
    got = bx.compose(two, page=0, look=False, rush=False)
    assert got == f"Local: a short answer and local: another answer are both {word}."
    three = [bx.Box(f"b{i}", kind, "x", f"table {i} rows") for i in range(3)]
    got = bx.compose(three, page=0, look=False, rush=False)
    assert got == f"Table 0 rows, table 1 rows and table 2 rows are all {word}."


def test_a_count_box_is_never_grouped_with_other_boxes():
    """The store's count is said on its own, before a pair or a run."""
    count = bx.Box("n1", "pass", "count", "14 sealed, 3 open", role="count")
    for others in (1, 2, 3):
        rest = [bx.Box(f"b{i}", "pass", "x", f"check {i} ok") for i in range(others)]
        for order in ([count, *rest], [*rest, count]):
            got = bx.compose(order, page=0, look=False, rush=False)
            assert "14 sealed, 3 open" in got
            assert "14 sealed, 3 open and" not in got
            assert "and 14 sealed" not in got
            assert ", 14 sealed" not in got


@pytest.mark.parametrize(
    "target,ref",
    [
        ("14", True),
        ("9999", True),
        ("PR 712", True),
        ("#714", True),
        ("ABC-123", True),
        ("b4", True),
        ("n4ee2a", True),
        ("pull request #714", True),
        ("the 5th one", True),
        ("the stack", True),
        ("Tony", True),
        ("the tests that failed", False),
        ("the failing tests from yesterday", False),
        ("me the tests that failed 14", False),
        ("", False),
    ],
)
def test_a_show_me_target_is_a_reference_or_a_task(target, ref):
    assert bx.looks_like_ref(target) is ref


def test_a_show_me_task_after_a_turn_still_reaches_the_chain():
    """U2: a longer show-me that matches no box reads as a task, not a ref."""
    calls = []
    api = FakeApi()
    st, out = seat(
        api, ["who", "", "status of the build", "show me the tests that failed", ""]
    )
    st.chain = lambda task: (
        calls.append(task),
        st.you(task),
        st.converse(task, demo_boxes()[:2], task),
    )
    st.run()
    assert calls == ["status of the build", "show me the tests that failed"]
    assert not any("Nothing I showed answers" in o for o in out)


@pytest.mark.parametrize("line", ["show me 14", "open #999", "show me PR 99999"])
def test_a_show_me_reference_that_matches_nothing_stays_a_plain_line(line):
    api, out = thread_run(["status of the build", *ALL, line])
    assert any(
        o.startswith("agent> Nothing I showed answers to") for o in after(out, line)
    )
    assert "escalate" not in api.names()


# --- O2: an opening that picks up from last time --------------------------------------


def start_opening(api, clock=None, keys=("who", "", "")):
    st, out = seat(api, list(keys), clock=clock)
    assert st.run() == 0
    n = next(i for i, o in enumerate(out) if o.startswith("served ▶"))
    return api, out, [o for o in out[:n] if o.startswith("agent> ")][-1]


def test_opening_picks_up_from_the_sealed_snapshot_and_the_pool_count():
    api = FakeApi(resume=resumed(), pooled=pool_of("proposal:aaa", "proposal:bbb"))
    _a, out, line = start_opening(api)
    assert line == (
        f"agent> Morning. Picking up from the sealed snapshot {SEALED} "
        "(rows up to 41); 2 proposals still pooled from earlier runs."
    )
    assert "agent · code · no model, nothing served" in out


def test_opening_with_nothing_sealed_and_nothing_pooled_is_a_plain_line():
    _a, _o, line = start_opening(FakeApi())
    assert line == (
        "agent> Morning. No snapshot has been sealed yet, so I'm scoping fresh; "
        "nothing is pooled from earlier runs."
    )


def test_opening_one_pooled_is_singular():
    _a, _o, line = start_opening(FakeApi(pooled=pool_of("proposal:aaa")))
    assert "; 1 proposal still pooled from earlier runs." in line


def test_opening_keeps_the_three_states_apart():
    def boom(*a, **k):
        raise RuntimeError("no such verb")

    lines = {
        "resume-none+empty": start_opening(FakeApi())[2],
        "resume-down": start_opening(FakeApi(resume=boom))[2],
        "resume-refused": start_opening(
            FakeApi(resume={"refused": "box won't open", "code": 2})
        )[2],
        "pool-down": start_opening(FakeApi(pooled=boom))[2],
        "pool-refused": start_opening(FakeApi(pooled={"refused": "x", "code": 2}))[2],
        "pool-full": start_opening(FakeApi(pooled=pool_of("proposal:aaa")))[2],
    }
    assert (
        "couldn't read the last sealed snapshot, so I'm scoping fresh"
        in lines["resume-down"]
    )
    assert lines["resume-down"].split("; ")[1] == (
        "nothing is pooled from earlier runs."
    )
    assert lines["resume-refused"] == lines["resume-down"]
    assert (
        "I couldn't read the pool, so I can't say what is still pooled"
        in lines["pool-down"]
    )
    assert lines["pool-refused"] == lines["pool-down"]
    assert "nothing is pooled" not in lines["pool-down"]  # down is never empty
    assert "No snapshot has been sealed yet" in lines["pool-down"]
    assert len(set(lines.values())) == 4  # none, down, pool-down, pool-full differ


def test_opening_carries_the_one_morning_and_the_first_reply_does_not_repeat_it():
    pieces = [piece("local", "answered", rows=[ROW])]
    api = FakeApi(escalate=chain_result(*pieces))
    st, out = seat(api, ["who", "", "status of the build", ""])
    st.run()
    agent = [o for o in out if o.startswith("agent> ")]
    greeted = [o for o in agent if "Morning." in o]
    assert len(greeted) == 1 and "scoping fresh" in greeted[0]


def test_opening_afternoon_has_no_greeting_and_still_says_the_state():
    _a, _o, line = start_opening(FakeApi(), clock=lambda: "15:02")
    assert line.startswith("agent> No snapshot has been sealed yet")


def test_opening_makes_no_api_call_of_its_own_and_asks_no_model():
    asked = []
    api = FakeApi(resume=resumed(), pooled=pool_of("proposal:aaa"))
    st, out = seat(api, ["", ""], say=lambda p: asked.append(p) or "x")
    st.run()
    assert api.names().count("resume") == 1
    assert api.names().count("pooled") == 2  # the start read, and the close-out's
    assert asked == []
    assert not {n for n in api.names() if "seal" in n or "mint" in n or "take" in n}


def test_opening_is_not_said_when_nothing_is_served():
    st, out = seat(FakeApi(scope={"refused": "no open box", "code": 2}), ["who"])
    st.run()
    assert not any("scoping fresh" in o or "Picking up" in o for o in out)


# --- O4: a closing that carries over --------------------------------------------------


def closing_of(out):
    """The closing line: the last agent sentence of the run."""
    return [o for o in out if o.startswith("agent> ")][-1]


def test_closing_says_what_stays_pooled_for_next_time():
    api = FakeApi(pooled=pool_of("proposal:aaa", "proposal:bbb"))
    st, out = seat(api, ["who", "", ""], deposit=FakeDeposit(DEPOSITED))
    assert st.run() == 0
    assert closing_of(out) == "agent> 2 proposals stay pooled for next time."
    # beside the one seal offer, after it
    assert len(offers(out)) == 1
    assert max(i for i, o in enumerate(out) if "seal ↗" in o) < len(out) - 1


def test_closing_one_pooled_is_singular():
    st, out = seat(FakeApi(pooled=pool_of("proposal:aaa")), ["who", "", ""])
    st.run()
    assert closing_of(out) == "agent> 1 proposal stays pooled for next time."


def test_closing_empty_pool_is_its_own_line():
    st, out = seat(FakeApi(), ["who", "", ""])
    st.run()
    assert closing_of(out) == "agent> Nothing stays pooled for next time."


@pytest.mark.parametrize(
    "bad",
    [RuntimeError("no such verb"), {"refused": "box won't open", "code": 2}, "junk"],
)
def test_closing_unreadable_pool_is_never_said_as_empty(bad):
    calls = []

    def pooled(*a, **k):
        calls.append(1)
        if len(calls) == 1:  # the start read answers; the close-out read fails
            return pool_of()
        if isinstance(bad, BaseException):
            raise bad
        return bad

    st, out = seat(FakeApi(pooled=pooled), ["who", "", ""])
    assert st.run() == 0
    line = closing_of(out)
    assert line == (
        "agent> I couldn't read the pool, so I can't say what stays pooled "
        "for next time."
    )
    assert "Nothing stays pooled" not in text(out)


def test_closing_is_said_on_every_way_out_and_writes_nothing():
    dep = FakeDeposit()
    for keys in (["who", "", ""], ["who", "", "bye"], ["who", ""]):  # empty, bye, EOF
        api = FakeApi(pooled=pool_of("proposal:aaa"))
        st, out = seat(api, keys, deposit=dep)
        assert st.run() == 0
        assert closing_of(out) == "agent> 1 proposal stays pooled for next time."
        assert not {n for n in api.names() if "seal" in n or "mint" in n or "take" in n}
    assert all(
        len(p["pooled"]) == 1 for p in dep.pools
    )  # the deposit saw the same pool


def test_closing_on_ctrl_c_still_carries_over():
    def read_c(prompt):
        if prompt.startswith("chain"):
            raise KeyboardInterrupt
        return {"scope ▶ group by (enter = who): ": "who"}.get(prompt, "")

    out: list[str] = []
    st = s.Seat(
        bot(FakeApi(pooled=pool_of("proposal:aaa"))),
        cfg="cfg",
        deposit=FakeDeposit(),
        read=read_c,
        write=out.append,
        color=False,
        clock=lambda: "09:14",
    )
    assert st.run() == 0
    assert closing_of(out) == "agent> 1 proposal stays pooled for next time."


def test_closing_after_a_deposit_error_still_counts_the_pool():
    dep = FakeDeposit({"state": "unreachable", "reason": "no willow-mcp"})
    st, out = seat(
        FakeApi(pooled=pool_of("proposal:aaa")), ["who", "", ""], deposit=dep
    )
    st.run()
    assert closing_of(out) == "agent> 1 proposal stays pooled for next time."
    assert len(dep.pools) == 1  # the one deposit; the closing did not add another


# --- O3: the model sees the thread ------------------------------------------------------

H1, H2, H3, H4 = "a" * 64, "c" * 64, "e" * 64, "f" * 64
ID1, ID2, ID3 = H1[:12], H2[:12], H3[:12]


def threaded_run(say, tasks=("first task", "second task"), hashes=(H1, H2, H3, H4)):
    """A run of several chain turns, each answering one different piece."""
    calls = []

    def esc(*a, **k):
        calls.append(1)
        return chain_result(piece("local", "answered", h=hashes[len(calls) - 1]))

    api = FakeApi(escalate=esc)
    st, out = seat(api, ["who", "", *tasks, ""], say=say)
    assert st.run() == 0
    return st, out


def thread_say(make):
    def say(prompt):
        say.prompts.append(prompt)
        # the tags under "Boxes:" (this page's), not the thread's
        page = prompt.split("Boxes:")[1]
        tags = [ln[1 : ln.index("]")] for ln in page.splitlines() if ln[:1] == "["]
        return make(*tags)

    say.prompts = []
    return say


def threaded(a, b, extra=""):
    return f"Looks like both answered 1, escalated 0 [{a}] and local: d [{b}]{extra}."


def test_the_first_prompt_has_no_thread_and_the_second_carries_the_first_reply():
    say = thread_say(threaded)
    threaded_run(say)
    assert "Earlier in this conversation" not in say.prompts[0]
    p = say.prompts[1]
    assert "Earlier in this conversation" in p
    thread = p.split("Boxes:")[0]
    assert "The human asked earlier: first task" in thread
    assert f"[{ID1}] routine pass: local: d" in thread
    assert "[b5] routine pass: answered 1, escalated 0" in thread
    assert thread.index("asked earlier: first task") < thread.index(
        "asked: second task"
    )
    assert f"[{ID1}]" not in p.split("Boxes:")[1]  # the current page lists its own


def test_the_thread_is_capped_at_the_last_two_replies():
    say = thread_say(threaded)
    tasks = ("first task", "second task", "third task", "fourth task")
    threaded_run(say, tasks=tasks)
    third = say.prompts[2].split("Boxes:")[0]
    assert "first task" in third and "second task" in third  # two replies back
    fourth = say.prompts[3].split("Boxes:")[0]
    assert "first task" not in fourth and "second task" in fourth
    assert say_mod.THREAD_TURNS == 2
    assert f"[{ID1}]" not in fourth and f"[{ID2}]" in fourth


def test_a_cite_to_a_box_from_an_earlier_turn_of_this_run_passes():
    say = thread_say(lambda a, b: threaded(a, b, f", still local: d [{ID1}]"))
    _st, out = threaded_run(say)
    t = text(out)
    assert f"agent · {MODEL} · said 2 boxes" in out
    sentence = next(o for o in out if o.endswith(f"still local: d [{ID1}]."))
    assert sentence.startswith("agent> Looks like both")
    assert "[struck]" not in t.split("you: second task")[1]
    # the first turn cited nothing earlier and failed nothing either
    assert t.count("✓ every cite was served · ✓ every box cited") == 2


def test_a_cite_to_a_box_never_shown_is_struck_and_the_code_sentence_stands():
    say = thread_say(lambda a, b: threaded(a, b, ", still local: d [zz9zz9zz9zz9]"))
    _st, out = threaded_run(say)
    second = text(out).split("you: second task")[1]
    assert "agent> ~~Looks like both" in second and "[struck]" in second
    assert "✗ every cite was served" in second
    assert GOOD_CODE in out  # the code sentence beneath it


def test_a_cite_to_a_box_older_than_the_thread_is_not_served():
    # shown this run (turn one) but out of the prompt's window by turn four
    say = thread_say(lambda a, b: threaded(a, b, f", still local: d [{ID1}]"))
    tasks = ("first task", "second task", "third task", "fourth task")
    _st, out = threaded_run(say, tasks=tasks)
    fourth = text(out).split("you: fourth task")[1]
    assert "✗ every cite was served" in fourth and "[struck]" in fourth
    third = text(out).split("you: third task")[1].split("you: fourth task")[0]
    assert "✗ every cite was served" not in third  # still in the window then


def test_a_box_from_a_previous_run_is_never_served():
    # run one shows ID1; a fresh Seat (run two) has no thread, so a cite to it is
    # a cite to a box that run never showed
    threaded_run(thread_say(threaded))
    say = thread_say(lambda a, b: threaded(a, b, f", still local: d [{ID1}]"))
    _st, out = threaded_run(say, tasks=("only task",), hashes=(H2,))
    assert "Earlier in this conversation" not in say.prompts[0]
    assert "✗ every cite was served" in text(out) and "[struck]" in text(out)


def test_every_box_cited_is_about_the_current_page_only():
    # cites the earlier box and one current box, omits the other current box
    say = thread_say(
        lambda a, b: (
            f"Looks like answered 1, escalated 0 [{a}], still local: d [{ID1}]."
        )
    )
    _st, out = threaded_run(say)
    second = text(out).split("you: second task")[1]
    assert "✗ every box cited" in second and "[struck]" in second


def test_the_code_only_path_is_unaffected_by_the_thread():
    st, out = threaded_run(None)
    assert text(out).count("code · said 2 boxes, no model asked") == 2
    assert GOOD_CODE in out
    assert [e[0] for e in st.exchanges] == ["first task", "second task"]


def test_an_earlier_boxs_facts_count_only_when_the_sentence_cites_it():
    old = bx.Box("b1", "block", "blocked", "PR 712 waiting", "126 tests pass")
    new = bx.Box("b2", "pass", "routine pass", "answered 1")
    ok = "PR 712 is still waiting [b1] and answered 1 [b2]."
    assert say_mod.passed(say_mod.run_checks(ok, [new], earlier=[old]))
    # the fact of the earlier box, said without its tag
    bare = "PR 712 is still waiting and answered 1 [b2]."
    assert say_mod.run_checks(bare, [new], earlier=[old])[2] is False
    # and not at all when it is not an earlier box
    assert say_mod.run_checks(ok, [new])[0] is False
    # a quote is the current line's alone
    q = 'PR 712 is still waiting [b1] and "answered 1" [b2].'
    assert say_mod.run_checks(q, [new], "answered 1", earlier=[old])[3] is True
    assert say_mod.run_checks(q, [new], "", earlier=[old])[3] is False


# --- the chain's count is said on its own, never paired with a piece ---------------


def chain_sentences(*pieces_, keys=("who", "", "task", "", "", "")):
    st, out = seat(FakeApi(escalate=chain_result(*pieces_)), list(keys))
    st.run()
    return [o for o in out if o.startswith("agent> ")][1:-1]


def test_the_chain_count_is_a_count_box_and_is_said_alone():
    api = FakeApi(escalate=chain_result(piece("local", "answered")))
    st, _out = seat(api, [])
    seen = []
    st.converse = lambda key, boxes, human="", **k: seen.extend(boxes)
    st.chain("task")
    assert [b.role for b in seen] == ["count", ""]
    assert seen[0].value == "answered 1, escalated 0"
    # a lone answered piece: the count is a sentence, the piece its own
    assert chain_sentences(piece("local", "answered")) == [
        "agent> Looks like the chain answered 1 and escalated 0. Local: d. No rush."
    ]
    # never "answered 1, escalated 0 and local: d are both routine"
    assert not any("are both" in s for s in chain_sentences(piece("local", "answered")))


def test_the_chain_count_never_joins_a_pair_or_a_run_but_pieces_still_pair():
    count = bx.Box("c", "pass", "chain", "answered 1, escalated 0", role="count")
    p1 = bx.Box("p1", "pass", "local", "local: a", "")
    p2 = bx.Box("p2", "pass", "local", "d0: b", "")
    for boxes in ([count, p1], [p1, count], [count, p1, p2], [p1, count, p2]):
        t = bx.compose(boxes, look=False)
        assert "answered 1 and escalated 0" in t and "both" not in t.split(".")[0]
        assert "answered 1, escalated 0 and" not in t
    # the pieces after the count are still paired by their kind's verb
    assert (
        bx.compose([p1, p2])
        == "Looks like local: a and d0: b are both routine. No rush."
    )
    # three pieces: the count and the first piece, then the other two as a pair
    got = chain_sentences(
        piece("local", "answered", h="a" * 64),
        piece("local", "answered", h="b" * 64),
        piece("local", "answered", h="c" * 64),
    )
    assert got[0].startswith("agent> Looks like the chain answered 3 and escalated 0.")
    assert got[1] == "agent> Oh, and local: d and local: d are both routine."


def test_the_chain_count_is_not_a_show_me_ref():
    st, out = seat(
        FakeApi(escalate=chain_result(piece("local", "answered"))),
        ["who", "", "task", "", "show me 1", ""],
    )
    st.run()
    assert not any(o.startswith("chips:") and "show me" in o for o in out)


# --- the opening names when the human sealed ---------------------------------------


def sealed_opening(sealed_at="2026-10-12T08:30:00Z", **kw):
    res = resumed() if sealed_at is None else resumed(sealed_at=sealed_at)
    api = FakeApi(resume=res, pooled=pool_of("proposal:aaa"))
    st, out = seat(api, ["", ""], **kw)
    st.run()
    n = next(i for i, o in enumerate(out) if o.startswith("served ▶"))
    return [o for o in out[:n] if o.startswith("agent> ")][-1]


def test_opening_names_the_day_the_human_sealed():
    # the stamp is UTC with an explicit Z; its date is read as written
    assert sealed_opening() == (
        f"agent> Morning. Picking up from the snapshot you sealed on 12 October "
        f"({SEALED}, rows up to 41); 1 proposal still pooled from earlier runs."
    )
    # late in the UTC day stays that UTC day: no conversion to a local zone
    assert "on 12 October (" in sealed_opening("2026-10-12T23:59:59Z")
    assert "on 13 October (" in sealed_opening("2026-10-13T00:00:00Z")


FULL_SUBJECT = (
    "serve:" + "9439efcacd2c441c3807dce2f2364895d428f59fb27799f56e89cd6607ec5121"
)


@pytest.mark.parametrize("sealed_at", ["2026-10-12T08:30:00Z", None])
def test_opening_says_the_subject_in_the_short_form_the_cards_use(sealed_at):
    # api.resume returns the whole 64-hex subject; the cards short() it, so the
    # opening does too, with or without a seal date
    res = resumed(subject=FULL_SUBJECT)
    if sealed_at:
        res["sealed_at"] = sealed_at
    st, out = seat(FakeApi(resume=res, pooled=pool_of("proposal:aaa")), ["who", "", ""])
    st.run()
    n = next(i for i, o in enumerate(out) if o.startswith("served ▶"))
    line = [o for o in out[:n] if o.startswith("agent> ")][-1]
    assert "(serve:9439efcacd2c" in line or "snapshot serve:9439efcacd2c " in line
    assert "9439efcacd2c4" not in line


def test_opening_same_day_seal_is_earlier_today():
    line = sealed_opening("2026-10-14T01:02:03Z")
    assert "the snapshot you sealed earlier today (" in line
    assert " on " not in line.split("(")[0]


def test_opening_other_year_names_the_year_and_a_future_stamp_its_date():
    assert "sealed on 31 December 2025 (" in sealed_opening("2025-12-31T10:00:00Z")
    assert "sealed on 15 October (" in sealed_opening("2026-10-15T10:00:00Z")


def test_opening_without_sealed_at_is_todays_wording_and_invents_no_date():
    line = sealed_opening(None)
    assert line == (
        f"agent> Morning. Picking up from the sealed snapshot {SEALED} "
        "(rows up to 41); 1 proposal still pooled from earlier runs."
    )


@pytest.mark.parametrize(
    "bad",
    [
        None,
        "",
        "yesterday",
        "2026-10-12",
        "2026-10-12T08:30:00",  # no zone
        "2026-10-12T08:30:00+02:00",  # an offset: not the record's form
        "2026-10-12T08:30:00.123Z",
        "2026-13-45T99:99:99Z",
        20261012,
        ["2026-10-12T08:30:00Z"],
    ],
)
def test_opening_with_an_unreadable_sealed_at_says_no_date(bad):
    line = sealed_opening(bad)
    assert "the sealed snapshot" in line
    assert "you sealed" not in line and "earlier today" not in line


def test_the_seal_date_comes_from_the_return_not_the_clock():
    # the same stamp reads the same whatever "today" is, except earlier-today
    a = sealed_opening("2026-10-12T08:30:00Z", today=lambda: date(2026, 10, 20))
    b = sealed_opening("2026-10-12T08:30:00Z", today=lambda: date(2026, 10, 14))
    assert a == b
    assert "sealed on 12 October (" in a

    # an unreachable resume invents no date either
    def boom(*a, **k):
        raise RuntimeError("x")

    st, out = seat(FakeApi(resume=boom), ["", ""])
    st.run()
    assert not any("you sealed" in o for o in out)


def test_sealed_on_is_pure_and_total():
    d = date(2026, 10, 14)
    assert bx.sealed_on("2026-10-14T00:00:00Z", d) == "earlier today"
    assert bx.sealed_on("2026-01-01T00:00:00Z", d) == "on 1 January"
    assert bx.sealed_on("2026-01-01T00:00:00Z") == "on 1 January 2026"
    assert bx.sealed_on(None, d) == ""
    assert bx.sealed_on("garbage", d) == ""
    # opening() stays total for a short resume tuple (the three-item form)
    assert "the sealed snapshot serve:x (rows up to 3)" in bx.opening(
        ("sealed", "serve:x", 3), ("empty",)
    )


# --- a status question is answered from the record's NEEDS YOU (and the store) ----------

from grove import seat_record as srec  # noqa: E402

RECORD_NEEDS = [
    "proposal · own_idea: no · who-ran-it · link_fail · a cite is not in the served file",
    "proposal · own_idea: no · port 8767 · pass",
    *(
        f"re-check row {n} (write) · made by run version 7e6157d7be41, now 21a0b50e23f7"
        for n in (9, 20, 49, 54, 86)
    ),
]


def needs_of(lines=RECORD_NEEDS):
    return {"needs": list(lines), "count": len(lines), "code": 0}


def status_run(keys, api=None, path=None):
    api = api or FakeApi(needs=needs_of())
    st, out = seat(api, ["who", "", *keys, ""])
    st.cfg = SimpleNamespace(nestor_db=path)
    assert st.run() == 0
    return api, out


@pytest.mark.parametrize(
    "line, kind",
    [
        ("what is on the table today?", "needs"),
        ("What's on the table", "needs"),
        ("what’s on the table?", "needs"),
        ("what is on my plate", "needs"),
        ("what is my next task", "needs"),
        ("what's next", "needs"),
        ("what is next, please", "needs"),
        ("ok so what's next?", "needs"),
        ("what do I need to do today", "needs"),
        ("what should I do next", "needs"),
        ("what needs me", "needs"),
        ("What needs me right now?", "needs"),
        ("what is waiting on me", "needs"),
        ("where are we", "where"),
        ("Where are we?", "where"),
        ("status", "where"),
    ],
)
def test_status_phrases_are_matched_whole_after_normalisation(line, kind):
    assert srec.status_kind(line) == kind


@pytest.mark.parametrize(
    "line",
    [
        "what is on the table in table 3 of the file",
        "what is the next task in the served file",
        "what is next to the door",
        "where are we in the second table",
        "tell me what is on the table",
        "what is the color of the night sky",
        "whats",
        "",
    ],
)
def test_a_line_that_only_contains_a_status_phrase_is_still_a_task(line):
    assert srec.status_kind(line) is None


def test_the_morning_questions_read_the_record_and_never_the_chain():
    api, out = status_run(["what is on the table today?", "", "what is my next task"])
    body = text(out)
    assert "escalate" not in api.names()
    assert api.names().count("needs") == 2  # one invocation row each, no other call
    assert "7 waiting on you: 2 proposals, 5 re-checks" in body
    assert "proposal who-ran-it: link_fail" in body
    assert "re-check row 9 (write)" in body
    assert "[unreachable]" not in body and "rung" not in body


def test_the_records_boxes_are_needs_you_cards_with_the_lines_own_parts():
    _api, out = status_run(["what is on the table"])
    got = after(out, "what is on the table")
    assert got[0].startswith("+- [routine pass] record  r")
    assert got[1:4] == [
        "| 7 waiting on you: 2 proposals, 5 re-checks",
        "| from the record's NEEDS YOU, read without checking out",
        "| no Nestor store is configured, so only the record was read",
    ]
    t = "\n".join(got)
    assert "[needs you] proposal" in t and "| own_idea: no" in t
    assert "| reason: a cite is not in the served file" in t
    assert "| made by run version 7e6157d7be41, now 21a0b50e23f7" in t


def test_follow_ups_work_on_the_records_boxes():
    api, out = status_run(
        [
            "what is on the table",
            "",
            "the second one",
            "why",
            "show me 20",
            "show me row 49",
            "go on",
        ]
    )
    assert "escalate" not in api.names()
    said = lambda you: next(  # noqa: E731
        o for o in after(out, you) if o.startswith("agent> ")
    )
    assert said("the second one") == (
        "agent> This needs you: proposal who-ran-it: link_fail."
    )
    assert said("why") == "agent> Reason: a cite is not in the served file."
    assert said("show me 20") == "agent> This needs you: re-check row 20 (write)."
    assert any("re-check row 49 (write)" in o for o in after(out, "show me row 49"))
    assert said("go on") == "agent> Nothing more in the pile."


def test_every_page_is_said_from_its_boxes_and_the_rest_waits_behind_more():
    _api, out = status_run(["what needs me", ""])
    first = after(out, "what needs me")
    assert sum(o.startswith("+- [needs you]") for o in first) == 4  # STORE_PAGE
    assert any(o.startswith("more? ▶ 3 more") for o in first)
    said = [o for o in first if o.startswith("agent> ")]
    assert said and "re-check row 49" not in said[0]
    assert any("re-check row 86 (write)" in o for o in out)  # after "more"


def test_an_unconfigured_store_does_not_make_the_turn_unreachable():
    for kind in ("what is on the table", "where are we"):
        _api, out = status_run([kind])
        body = text(out)
        assert "[unreachable]" not in body and "nstate" not in body
        assert "No Nestor store is configured" not in body


def test_a_record_with_nothing_waiting_is_empty_not_unreachable():
    api = FakeApi(needs=needs_of([]))
    _a, out = status_run(["what's next"], api)
    body = text(out)
    assert "+. [empty] record  rstate" in body
    assert "agent> Record is empty: nothing on the record waits on you." in body
    assert "[unreachable]" not in body and "escalate" not in api.names()


@pytest.mark.parametrize(
    "res",
    [
        RuntimeError("boom"),
        {"refused": "no law", "code": 2},
        {"needs": "not a list"},
        "nope",
    ],
)
def test_an_unreadable_record_is_unreachable_with_its_reason_and_the_store_still_answers(
    tmp_path, res
):
    def needs(*a, **k):
        if isinstance(res, Exception):
            raise res
        return res

    p = small_store(tmp_path)
    api = FakeApi(needs=needs)
    _a, out = status_run(["what needs me"], api, p)
    body = text(out)
    assert "+! [unreachable] record  rstate" in body
    assert "I can't read the record right now." in body
    assert "Adios (draft)" in body  # the store's own answer, still given
    assert "escalate" not in api.names()


def test_nothing_answering_says_both_unreachable():
    api = FakeApi(needs=lambda *a, **k: (_ for _ in ()).throw(KeyError("needs")))
    _a, out = status_run(["what is on the table"], api)
    body = text(out)
    assert "+! [unreachable] record  rstate" in body
    assert "+! [unreachable] nestor store  nstate" in body


def test_an_older_willow_bot_with_no_needs_is_unreachable_and_says_so():
    got = srec.read_needs(object(), None)
    assert got.state == "unreachable" and "no needs read" in got.reason
    assert got.boxes[0].state == "unreachable"


def test_the_record_and_the_store_are_merged_each_in_its_own_state(tmp_path):
    p = small_store(tmp_path)
    before = hashlib.sha256(p.read_bytes()).hexdigest()
    api, out = status_run(["what is on the table today?", "", "", "why"], None, p)
    body = text(out)
    assert "7 waiting on you: 2 proposals, 5 re-checks" in body
    assert "Adios (draft)" in body and "[needs you] draft, waiting" in body
    assert "[blocked]" not in body and "[decided]" not in body  # only what waits
    assert "only the record was read" not in body  # the store was read as well
    assert "escalate" not in api.names()
    assert hashlib.sha256(p.read_bytes()).hexdigest() == before


def test_where_are_we_shows_the_stores_whole_state_beside_the_record(tmp_path):
    p = small_store(tmp_path)
    _api, out = status_run(["where are we"], None, p)
    body = text(out)
    assert "7 waiting on you" in body and "1 sealed, 1 draft, 1 rejected" in body


def test_a_record_that_changed_is_read_fresh_and_one_that_did_not_is_replayed():
    lines = [RECORD_NEEDS[0]]
    api = FakeApi(needs=lambda *a, **k: needs_of(lines))
    st, out = seat(
        api, ["who", "", "what is on the table", "what is on the table", "", ""]
    )
    st.cfg = SimpleNamespace(nestor_db=None)
    orig = st.status
    asks = []

    def status(task):
        if asks:
            lines.append(RECORD_NEEDS[1])  # the record grows between the two asks
        asks.append(task)
        orig(task)

    st.status = status
    st.run()
    body = text(out)
    assert "same boxes, nothing new since" not in body
    assert "1 waiting on you: 1 proposal" in body
    assert "2 waiting on you: 2 proposals" in body


def test_the_same_record_asked_twice_comes_back_from_the_pile():
    api, out = status_run(["what is on the table", "", "what is on the table", ""])
    assert "same boxes, nothing new since" in text(out)
    assert api.names().count("needs") == 2 and "escalate" not in api.names()


def test_the_seat_status_turn_writes_nothing_of_its_own():
    api, _out = status_run(["what is on the table"])
    assert [n for n in api.names() if n not in ("checkin", "resume", "scope")][:3] == [
        "pooled",
        "serve",
        "needs",
    ]


def test_help_names_the_status_questions():
    for phrase in ('"what is on the table"', '"what needs me"', '"where are we"'):
        assert phrase in s.HELP


def test_the_first_page_shows_both_sources_proposals_then_drafts_then_re_checks(
    tmp_path,
):
    p = small_store(tmp_path)
    _api, out = status_run(["what needs me", ""], None, p)
    first = after(out, "what needs me")
    cards = [o for o in first if o.startswith("+- [")]
    assert [c.split("]")[1].split("  ")[0].strip() for c in cards[:5]] == [
        "record",
        "proposal",
        "proposal",
        "draft, waiting (fixture)",
        "re-check",
    ]


# --- an answer with no detail is never said as "Local:." ---------------------------------


def chain_said(*pieces_, keys=("task", "")):
    api = FakeApi(escalate=chain_result(*pieces_))
    st, out = seat(api, ["who", "", *keys, ""])
    st.cfg = SimpleNamespace(nestor_db=None)
    st.run()
    return out


def test_an_answered_piece_with_no_detail_says_its_first_claim():
    row = {
        "path": "table",
        "data": "x",
        "cites": ["t"],
        "claim": "The  table\nholds 3 rows",
    }
    out = chain_said(piece("local", "answered", rows=[row], detail=""))
    assert "| local: The table holds 3 rows" in out
    assert not any(o.endswith("Local:.") or "Local:." in o for o in out)


def test_a_long_claim_is_cut_to_the_cap_with_an_ellipsis():
    row = {"path": "t", "data": "", "cites": ["t"], "claim": "word " * 100}
    out = chain_said(piece("local", "answered", rows=[row], detail=""))
    card = next(o for o in out if o.startswith("| local: word"))
    assert len(card) == len("| local: ") + s.CLAIM_CHARS and card.endswith("…")


@pytest.mark.parametrize(
    "rows", [[], [{"claim": "", "data": ""}], [{"claim": None}], ["not a row"]]
)
def test_a_local_answer_with_nothing_to_say_is_said_plainly(rows):
    out = chain_said(piece("local", "answered", rows=rows, detail=""))
    assert "| the local model gave an empty answer" in out
    said = [o for o in after(out, "task") if o.startswith("agent> ")]
    assert " The local model gave an empty answer." in said[-1]
    assert not any("Local:." in o for o in out)


def test_willow_bots_silent_empty_answer_is_a_blocked_box_with_its_detail():
    out = chain_said(
        piece(
            "local",
            "escalated",
            "silent",
            detail="the local model gave an empty answer",
        )
    )
    assert "| local: the local model gave an empty answer" in out
    assert "| reason: silent" in out


def test_a_rung_errors_stderr_tail_reaches_the_card_and_the_sentence():
    why = "/v/bin/ratatosk exited 1: Traceback | model qwen3:4b not found"
    out = chain_said(piece("local", "escalated", "rung_error", detail=why))
    assert f"| local: {why}" in out
    said = [o for o in after(out, "task") if o.startswith("agent> ")]
    assert any("model qwen3:4b not found" in o for o in said)


# --- a reply model that times out right after the local rung ------------------------------


def timeout_say(prompt):
    raise say_mod.SayUnreachable(
        "qwen3:4b at http://127.0.0.1:11434: TimeoutError: timed out"
    )


def test_a_reply_that_times_out_after_a_local_rung_names_the_likely_cause():
    code, out, _api = model_run(timeout_say)
    body = text(out)
    assert code == 0 and "[unreachable] say" in body
    assert (
        "TimeoutError: timed out (the chain's local rung had just asked this Ollama for m;"
        in body
    )
    assert "the reply may have waited behind it)" in body
    assert f"agent · code · {MODEL} unreachable · said 2 boxes by code" in out
    assert GOOD_CODE in out  # code's sentence stands, as for any unreachable model


@pytest.mark.parametrize(
    "got, boom",
    [
        (piece("d0", "answered"), timeout_say),  # no local request was made
        (piece("hash", "answered"), timeout_say),  # reused from the record
        (
            piece("local", "answered"),
            say_mod.SayUnreachable("qwen3:4b: connection refused"),
        ),  # not a timeout
    ],
)
def test_no_hint_without_a_local_rung_request_or_without_a_timeout(got, boom):
    api = FakeApi(escalate=chain_result(got))
    st, out = seat(api, ["who", "", "the task", ""], say=boom)
    assert st.run() == 0
    assert "just asked this Ollama" not in text(out)


def test_the_hint_is_for_the_chain_turn_only_not_a_later_reply():
    api = FakeApi(
        escalate=chain_result(piece("local", "answered")),
        needs={"needs": ["proposal · own_idea: no · p.md · pass"], "count": 1},
    )
    st, out = seat(
        api, ["who", "", "the task", "what is on the table", ""], say=timeout_say
    )
    st.cfg = SimpleNamespace(nestor_db=None)
    assert st.run() == 0
    status = after(out, "what is on the table")
    assert "[unreachable] say" in "\n".join(status)
    assert "just asked this Ollama" not in "\n".join(status)
    assert st.rung_models == []
