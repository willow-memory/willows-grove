# b17: GRSET ΔΣ=42
"""Tests for grove.seat_cli — the desk's command-line seat.

A fake one-script api stands in for willow-bot's, so no box, no model and no
network: each test scripts the human's keystrokes and reads what the seat
printed and which api calls it made.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys

import pytest

from grove import seat_boxes as bx
from grove import seat_cli as s

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


def seat(api, keys, *, pieces=(), flower=None, deposit=None, color=False, clock=None):
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
        read=read,
        write=out.append,
        color=color,
        clock=clock or (lambda: "09:14"),
    )
    return st, out


def piece(rung, outcome="escalated", reason="local_escalate", h="h" * 64, rows=()):
    return {
        "piece": h,
        "rung": rung,
        "model": "m",
        "outcome": outcome,
        "label": outcome if outcome == "answered" else f"escalated:{reason}",
        "reason": reason,
        "detail": "d",
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
        "scope",
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
    first = next(o for o in out if o.startswith("agent> "))
    assert (
        first == "agent> Looks like both answered 2, escalated 1 and local: d. No rush."
    )
    assert out.index("agent · code · said 2 boxes, no model asked") < out.index(first)


def test_more_shows_the_next_boxes_and_declining_keeps_them_in_the_pile():
    _api, out = rich_run()
    t = text(out)
    assert t.count("more? ▶") == 1 and "you: more" in out
    assert "agent> Oh, and local: d is still blocked and d0: d." in t
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
    ticks = iter(["09:14", "09:40", "09:41"])
    pieces = [piece("local", "answered", rows=[ROW])]
    api = FakeApi(escalate=chain_result(*pieces))
    st, out = seat(
        api,
        ["who", "", "where are we", "Where  are we", ""],
        clock=lambda: next(ticks),
    )
    st.run()
    assert api.names().count("escalate") == 1  # asked again: not recomputed
    stamp = "as noted at 09:14 · same boxes, nothing new since"
    assert out.count(stamp) == 1
    cards = lambda block: [o for o in block if o[:1] in "+|"]  # noqa: E731
    i1 = out.index("you: where are we")
    i2 = out.index(stamp)
    first_cards = cards(out[i1 : out.index(s.CHIPS, i1)])
    assert first_cards and cards(out[i2 : out.index(s.CHIPS, i2)]) == first_cards
    assert "agent · code · shown again from the pile, no model asked now" in out
    assert "09:40" not in text(out)  # the second asking did not restamp


def test_the_sentence_is_glue_plus_box_facts_only():
    a = bx.Box("b1", "you", "needs you", "Ratify the work order")
    b = bx.Box("b2", "block", "blocked", "PR 712 waiting")
    c = bx.Box("b3", "pr", "changed", "PR 127 open")
    d = bx.Box("b4", "pr", "changed", "PR 714 open")
    assert bx.compose([a, b]) == (
        "Looks like Ratify the work order needs you and PR 712 waiting is still blocked."
    )
    assert bx.compose([c, d], first=False) == (
        "Oh, and both PR 127 open and PR 714 open. No rush."
    )
    down = bx.Box("b5", "pass", "served", "unreachable — no key", state="unreachable")
    assert bx.compose([down]) == "Heads up: served is unreachable — no key."
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
