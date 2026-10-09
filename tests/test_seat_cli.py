# b17: GRSET ΔΣ=42
"""Tests for grove.seat_cli — the desk's command-line seat.

A fake one-script api stands in for willow-bot's, so no box, no model and no
network: each test scripts the human's keystrokes and reads what the seat
printed and which api calls it made.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import pytest

from grove import seat_cli as s

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


def seat(api, keys, *, pieces=(), flower=None, deposit=None):
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
    assert "MORNING SCREEN" in out
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
    assert "  refused: no law" in out


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
        ["who", "", "the task", "y", ""],
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
    assert "  subject: serve:abc" in out
    assert "serve" in api.names()


def test_an_empty_scope_is_said_and_nothing_is_served():
    api = FakeApi(scope={"spec": {}, "subject": None, "ids": [], "stack": []})
    st, out = seat(api, ["who"])
    st.run()
    assert "serve" not in api.names()
    assert any(o.startswith("  empty") for o in out)


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
    assert "  served: empty — over the cap" in out


def test_a_scope_with_no_past_seal_is_the_honest_empty_not_a_mint():
    why = "the scope has no human seal over this exact set"
    api = FakeApi(serve={"doc": {}, "state": "empty", "why": why})
    st, out = seat(api, ["who", "", ""])
    st.run()
    assert f"  served: empty — {why}" in out
    assert not [n for n in api.names() if n.startswith("seal")]


# --- the chain and flowering ------------------------------------------------------------


def test_local_answers_are_shown_pooled_and_not_sealed():
    api = FakeApi(escalate=chain_result(piece("local", "answered", rows=[ROW])))
    st, out = seat(api, ["who", "", "the task", ""])
    st.run()
    assert "    pooled: proposal:notes/a.md" in out
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
    assert "    pooled: proposal:x" in out
    assert "  [onescript] rung=openrouter" in out


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
    assert any("unreachable — the piece isn't in the served file" in o for o in out)


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
    assert "  link_fail: a cite is not in the served file" in out
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
    assert out.index("MORNING SCREEN") < out.index(
        "  deposit: populated — 2 in Nestor as drafts"
    )
    assert f"    {SUBJ}  proposed" in out
    assert "    proposal:bad  ERROR: empty_claim" in out  # an error pair, verbatim
    offers = [o for o in out if o.startswith("  seal ↗")]
    assert len(offers) == 1 and s.NESTOR_UI in offers[0]
    assert not [n for n in api.names() if n.startswith("seal")]


def test_checkout_deposits_even_when_the_run_ended_early():
    dep = FakeDeposit(DEPOSITED)
    st, _out = seat(FakeApi(pooled=POOL), ["who"], deposit=dep)  # EOF at served
    st.run()
    assert len(dep.pools) == 1


def test_an_empty_pool_is_said_empty_and_offers_no_seal():
    st, out = seat(FakeApi(), ["who", "", ""])
    st.run()
    assert "  deposit: empty — the pool is empty" in out
    assert not any("seal ↗" in o for o in out)


def test_an_unavailable_deposit_is_unreachable_not_empty_and_lists_the_pool():
    gone = {"state": "unreachable", "reason": s.NO_DEPOSIT}
    st, out = seat(FakeApi(pooled=POOL), ["who", "", ""], deposit=FakeDeposit(gone))
    st.run()
    assert f"  deposit: unreachable — {s.NO_DEPOSIT}" in out
    assert f"    pooled, not deposited: {SUBJ}" in out
    assert not any(o.startswith("  deposit: empty") for o in out)
    assert not any("seal ↗" in o for o in out)


def test_a_deposit_that_raises_is_unreachable_and_never_ends_the_close_out():
    dep = FakeDeposit(RuntimeError("db down"))
    st, out = seat(FakeApi(pooled=POOL), ["who", "", ""], deposit=dep)
    assert st.run() == 0
    assert "  deposit: unreachable — RuntimeError: db down" in out
    assert f"    pooled, not deposited: {SUBJ}" in out


def test_a_refused_pool_read_is_unreachable_and_deposits_nothing():
    dep = FakeDeposit(DEPOSITED)
    api = FakeApi(pooled={"refused": "box won't open", "code": 2})
    st, out = seat(api, ["who", "", ""], deposit=dep)
    st.run()
    assert "  pool: unreachable — box won't open" in out
    assert dep.pools == []


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
