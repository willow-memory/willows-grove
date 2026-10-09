# b17: GRSET ΔΣ=42
"""Tests for grove.seat_cli — the desk's command-line seat.

A fake one-script api stands in for willow-bot's, so no box, no model and no
network: each test scripts the human's keystrokes and reads what the seat
printed and which api calls it made.
"""

from __future__ import annotations

import json
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
            "seal_scope": {"sealed": True},
            "serve": {"doc": DOC, "state": "populated", "why": ""},
            "escalate": {
                "task": "the task",
                "pieces": [],
                "answered": 0,
                "escalated": 0,
            },
            "take_proposals": {"out": {"proposals": []}},
            "seal_proposal": {"sealed": True},
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


def seat(api, keys, *, pieces=(), flower=None):
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
    st, out = seat(api, ["who", "s", "", "the task", ""])
    assert st.run() == 0
    assert api.names() == [
        "checkin",
        "scope",
        "seal_scope",
        "serve",
        "escalate",
        "checkout",
    ]
    assert "MORNING SCREEN" in out
    prompts = [o for o in out if "▶" in o]
    assert [p.split(" ▶")[0] for p in prompts] == [
        "scope",
        "seal",
        "served",
        "chain",
        "chain",
    ]


def test_eof_mid_run_still_checks_out():
    api = FakeApi()
    st, _out = seat(api, ["who"])  # EOF at the seal prompt
    assert st.run() == 0
    assert api.names()[-1] == "checkout"


def test_ctrl_c_mid_run_still_checks_out():
    api = FakeApi(serve=lambda *a, **k: (_ for _ in ()).throw(KeyboardInterrupt))
    st, _out = seat(api, ["who", "s", ""])
    assert st.run() == 0
    assert api.names()[-1] == "checkout"


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


def test_declining_the_scope_seal_serves_nothing():
    api = FakeApi()
    st, out = seat(api, ["who", "n"])
    st.run()
    assert "serve" not in api.names() and "  scope left unsealed" in out


def test_a_proof_is_passed_through_never_made_here():
    api = FakeApi()
    st, _out = seat(api, ["who", "p deadbeef", ""])
    st.run()
    seal = next(c for c in api.calls if c[0] == "seal_scope")
    assert seal[1] == ("serve:abc",) and seal[2] == {"proof": "deadbeef"}


def test_a_failed_seal_says_why_and_asks_again():
    results = iter(
        [
            {"sealed": False, "row": {"reason": "no sealed Nestor pair"}},
            {"sealed": True},
        ]
    )
    api = FakeApi(seal_scope=lambda *a, **k: next(results))
    st, out = seat(api, ["who", "s", "s", ""])
    st.run()
    assert "  not sealed: no sealed Nestor pair" in out
    assert "serve" in api.names()


def test_an_empty_scope_is_said_and_nothing_is_sealed():
    api = FakeApi(scope={"spec": {}, "subject": None, "ids": [], "stack": []})
    st, out = seat(api, ["who"])
    st.run()
    assert "seal_scope" not in api.names()
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
    st, out = seat(api, ["who", "s", "", ""])
    st.run()
    assert "  served: empty — over the cap" in out


# --- the chain and flowering ------------------------------------------------------------


def test_local_answers_become_proposals_to_seal():
    api = FakeApi(escalate=chain_result(piece("local", "answered", rows=[ROW])))
    st, _out = seat(api, ["who", "s", "", "the task", "s", ""])
    st.run()
    sealed = next(c for c in api.calls if c[0] == "seal_proposal")
    assert sealed[1] == ("proposal:notes/a.md",)


def test_a_d0_answer_is_not_a_proposal():
    api = FakeApi(escalate=chain_result(piece("d0", "answered", rows=[{"answer": 1}])))
    st, _out = seat(api, ["who", "s", "", "the task", ""])
    st.run()
    assert "seal_proposal" not in api.names()


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
        ["who", "s", "", "the task", "y", "s", ""],
        pieces=cut,
        flower=lambda p, q: sent.append((p, q)) or flow,
    )
    st.run()
    assert sent == [({"tables": ["the piece"]}, "the task")]
    take = next(c for c in api.calls if c[0] == "take_proposals")
    assert take[1] == ([ROW],) and take[2] == {"bite": "flowering"}
    seal = next(c for c in api.calls if c[0] == "seal_proposal")
    assert seal[1] == ("proposal:x",)
    assert "  [onescript] rung=openrouter" in out


def test_no_yes_no_cloud_turn():
    api = FakeApi(escalate=chain_result(piece("local")))
    st, _out = seat(
        api,
        ["who", "s", "", "the task", "", ""],
        pieces=[{"hash": "h" * 64, "piece": {}}],
    )
    st.run()  # the default flower fails the test if it runs
    assert "take_proposals" not in api.names()


@pytest.mark.parametrize("reason", sorted(s.NO_FLOWER))
def test_what_code_decided_never_reaches_a_model(reason):
    api = FakeApi(escalate=chain_result(piece("local", reason=reason)))
    st, out = seat(
        api, ["who", "s", "", "the task", ""], pieces=[{"hash": "h" * 64, "piece": {}}]
    )
    st.run()
    assert any("code decided" in o for o in out)
    assert not any(o.startswith("flowering ▶") for o in out)


def test_a_d0_escalation_flowers_over_the_whole_served_file():
    sent = []
    api = FakeApi(escalate=chain_result(piece("d0", reason="d0_escalate")))
    st, _out = seat(
        api,
        ["who", "s", "", "the task", "y", ""],
        flower=lambda p, q: sent.append(p) or {"code": 0, "summary": "", "rows": []},
    )
    st.run()
    assert sent == [DOC]


def test_a_piece_missing_from_the_served_file_is_unreachable_not_guessed():
    api = FakeApi(escalate=chain_result(piece("local")))
    st, out = seat(api, ["who", "s", "", "the task", ""], pieces=[])
    st.run()
    assert any("unreachable — the piece isn't in the served file" in o for o in out)


def test_a_cloud_escalate_row_is_never_a_proposal():
    esc = {"path": "ESCALATE", "data": "", "cites": [], "claim": "can't"}
    api = FakeApi(escalate=chain_result(piece("local")))
    st, out = seat(
        api,
        ["who", "s", "", "the task", "y", ""],
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
        ["who", "s", "", "the task", "y", ""],
        pieces=[{"hash": "h" * 64, "piece": {}}],
        flower=lambda p, q: {"code": 0, "summary": "", "rows": [ROW]},
    )
    st.run()
    assert "  link_fail: a cite is not in the served file" in out
    assert "seal_proposal" not in api.names()


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
