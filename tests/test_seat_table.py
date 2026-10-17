# b17: GRSTB ΔΣ=42
"""R13: the seat shows the table through ``api.needs`` and ``api.checkout``.

SPEC.md ruling R13, SPEC-documented phase J8-table-panel, SPEC-rival section 7.
No new panel: ``seat_record.item_box`` has a ``wager`` pattern (and a ``table``
one for the verdict sessions and the agm_head check), the seat is pointed at the
table box by config, and ``table_boxes.narrate`` says the served table's fact
boxes through the seat's injectable ``say``. A fake one-script api stands in for
willow-bot's; the real api is exercised in box-build/e2e/test_w4_surface.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from grove import seat_boxes as bx
from grove import seat_cli as s
from grove import seat_record as rec
from grove import table_boxes as tb
from tests.test_seat_cli import FakeApi, seat, text

SEEN: set[str] = set()

WAGER_RECONCILED = (
    "wager f1 reconciled · band middle p 0.139 · happened: weak-strong · brier 0.099"
    " · log 1.97 · by oracle (claimed) · wager 2026-10-17T00:00:00Z · tip sealed"
    " 2026-10-17T00:00:01Z · grade is yours"
)
WAGER_ESCALATE = (
    "wager f1 escalate to human · no human seal covered by the sealed anchor tip"
    " names an outcome; the grade is the human's"
)
WAGER_UNREACHABLE = "wager f1 seal unreachable · no key to check the outcome proof by"
LINES = {
    "reconciled": WAGER_RECONCILED,
    "escalate": WAGER_ESCALATE,
    "unreachable": WAGER_UNREACHABLE,
}


def box(line: str) -> bx.Box:
    return rec.item_box(line, set())


# ── item_box: a wager box for each reconcile state ───────────────────────────────
def test_a_reconciled_wager_is_a_needs_you_box_with_the_score_apart():
    b = box(WAGER_RECONCILED)
    assert (b.kind, b.label, b.state) == ("you", "wager", "populated")
    assert b.value == "wager f1 reconciled"
    assert b.detail.split("\n") == [
        "band middle p 0.139",
        "happened: weak-strong",
        "brier 0.099",
        "log 1.97",
        "by oracle (claimed)",
        "wager 2026-10-17T00:00:00Z",
        "tip sealed 2026-10-17T00:00:01Z",
        "grade is yours",
    ]


def test_an_escalated_wager_is_a_needs_you_box_with_its_reason():
    b = box(WAGER_ESCALATE)
    assert (b.kind, b.label, b.state, b.value) == (
        "you",
        "wager",
        "populated",
        "wager f1 escalate to human",
    )
    assert "the grade is the human's" in b.detail


def test_an_unreachable_wager_seal_is_an_unreachable_box_not_an_escalation():
    b = box(WAGER_UNREACHABLE)
    assert (b.label, b.state) == ("wager", "unreachable")
    assert (
        b.value == "unreachable — wager f1 seal: no key to check the outcome proof by"
    )


def test_the_three_wager_states_are_three_different_cards():
    cards = {k: bx.render_box(box(v)) for k, v in LINES.items()}
    assert len({c.split("\n")[0].split("]")[0] for c in cards.values()}) == 2
    assert "[needs you]" in cards["reconciled"] and "[needs you]" in cards["escalate"]
    assert cards["unreachable"].startswith("+! [unreachable]")
    assert len(set(cards.values())) == 3


def test_a_wager_id_with_odd_characters_still_parses():
    b = box("wager f-1.a reconciled · winner yes · grade is yours")
    assert b.label == "wager" and b.value == "wager f-1.a reconciled"


# ── item_box: sessions and the agm_head check ────────────────────────────────────
@pytest.mark.parametrize(
    "tip, kind, state",
    [
        ("waiting on your tip seal", "you", "populated"),
        ("covered by your sealed tip", "dec", "populated"),
        ("tip seal not checked here (no human key)", "block", "unreachable"),
    ],
)
def test_a_verdict_session_box_says_where_its_tip_stands(tip, kind, state):
    b = box(f"table verdict session hasbeen-1 · 4 rows · forecast f1 · {tip}")
    assert (b.label, b.kind, b.state) == ("verdict session", kind, state)
    assert "hasbeen-1" in b.value
    if state == "populated":
        assert b.value == "table verdict session hasbeen-1"
        assert b.detail.split("\n") == ["4 rows", "forecast f1", tip]
    else:
        assert tip in b.value and "4 rows" in b.detail


@pytest.mark.parametrize(
    "line, kind, state",
    [
        (
            "table agm_head satisfied · ledger n 3 · covered by your sealed tip",
            "dec",
            "populated",
        ),
        (
            "table agm_head failing · the ledger is at (3, zz), anchored (3, ab)",
            "block",
            "populated",
        ),
        (
            "table agm_head unreachable · db absent · ledger n 3 · not covered by a sealed tip",
            "block",
            "unreachable",
        ),
        ("table agm_head unanchored · no agm_head row on record", "pass", "empty"),
    ],
)
def test_the_agm_head_check_has_four_cards(line, kind, state):
    b = box(line)
    assert (b.label, b.kind, b.state) == ("agm_head", kind, state)
    if state != "populated":
        assert b.value.startswith(state if state == "empty" else "unreachable")


def test_a_line_that_only_looks_like_a_table_line_stays_a_plain_record_box():
    for line in (
        "table agm_head fine · all well",
        "wager f1 won · nice",
        "table verdict session x",
        "a wager f1 reconciled · x",
    ):
        assert box(line).label == "record"


def test_counts_name_the_new_kinds():
    items = [
        box(WAGER_ESCALATE),
        box(WAGER_RECONCILED),
        box("table agm_head satisfied · x"),
    ]
    assert rec._counts(items) == "2 wagers, 1 agm_head"


# ── read_needs: asked as before, and scrubbed ────────────────────────────────────
class Needs:
    def __init__(self, lines):
        self.lines, self.calls = lines, []

    def needs(self, cfg, **kw):
        self.calls.append(kw)
        return {"needs": self.lines, "count": len(self.lines), "code": 0}


def test_read_needs_hands_the_key_and_reader_over_only_when_set():
    api = Needs([WAGER_ESCALATE])
    rec.read_needs(api, "cfg")
    assert api.calls == [{}]
    reader = lambda: {}  # noqa: E731
    rec.read_needs(api, "cfg", human_key="/k/key.hex", read_head=reader)
    assert api.calls[1] == {"human_key": "/k/key.hex", "read_head": reader}


def test_every_wager_state_reads_populated_with_its_box():
    got = rec.read_needs(Needs(list(LINES.values())), "cfg")
    assert got.state == "populated"
    wagers = [b for b in got.boxes if b.label == "wager"]
    assert [b.state for b in wagers] == ["populated", "populated", "unreachable"]
    assert got.boxes[0].value.startswith("3 waiting on you: 3 wagers")


KEY = "7f" * 32


@pytest.mark.parametrize(
    "line",
    [
        "wager f1 escalate to human · the seed: 9a8b7c6d5e4f3a2b was used",
        "wager f1 escalate to human · seed=0123456789abcdef0123456789abcdef",
        "wager f1 escalate to human · key: deadbeefcafe1234",
        f"wager f1 escalate to human · bad proof from {KEY}",
        "wager f1 escalate to human · signature " + "ab" * 64,
        "wager f1 escalate to human · a 33-byte key " + "cd" * 33,
    ],
)
def test_a_surface_line_that_would_show_a_seed_or_key_does_not(line):
    got = rec.read_needs(Needs([line]), "cfg", secrets=(KEY,))
    shown = "\n".join(bx.render_box(b) for b in got.boxes)
    for leak in (
        "9a8b7c6d5e4f3a2b",
        "0123456789abcdef",
        "deadbeefcafe1234",
        KEY,
        "ab" * 64,
        "cd" * 33,
    ):
        assert leak not in shown
    assert "[withheld]" in shown


def test_what_is_not_a_secret_stays_readable():
    sha = "e" * 40
    line = f"wager f1 escalate to human · no key for the proposal's author; commit {sha}; tip:3:{'a' * 64}"
    (_, b) = rec.read_needs(Needs([line]), "cfg").boxes
    assert "no key for the proposal's author" in b.detail and sha in b.detail
    assert "a" * 12 in bx.render_box(
        b
    )  # the 64-hex is shortened by render, not withheld


# ── the seat: pointed at the table box by config ─────────────────────────────────
def test_config_points_the_seat_at_a_table_box_by_environment(tmp_path):
    made = []

    class Api:
        def default_keyring(self):
            return None

        def default_nestor_db(self):
            return None

        def Config(self, **kw):  # noqa: N802
            made.append(kw)
            return kw

    b = s.Bot(Api(), None, None, 1)
    s.config(b, tmp_path, environ={})
    s.config(
        b,
        tmp_path,
        environ={"GROVE_SEAT_BOX": "/t/box", "GROVE_SEAT_KEYS": "/t/k.json"},
    )
    assert made[0]["box"] == tmp_path / ".flow" / "onescript"
    assert (
        Path(made[1]["box"]).as_posix() == "/t/box"
        and Path(made[1]["keys"]).as_posix() == "/t/k.json"
    )


def test_the_status_turn_shows_the_wagers_and_the_table_through_api_needs():
    lines = [
        WAGER_ESCALATE,
        "table verdict session hasbeen-1 · 4 rows · forecast f1 · waiting on your tip seal",
        "table agm_head satisfied · ledger n 3 · covered by your sealed tip",
        "proposal · own_idea: no · decisions/beat-3 · pass",
    ]
    api = FakeApi(needs=lambda cfg, **k: {"needs": lines, "count": 4, "code": 0})
    st, out = seat(api, ["what's on the table"])
    st.human_key, st.read_head = "/k/key.hex", lambda: {}
    st.status("what's on the table")
    said = text(out)
    for want in (
        "[needs you] wager",
        "wager f1 escalate to human",
        "verdict session",
        "[decided] agm_head",
        "[needs you] proposal",
    ):
        assert want in said, want
    assert api.calls[-1][2].keys() == {"human_key", "read_head"}
    assert [
        c for c in api.names() if c in ("checkin", "scope", "serve")
    ] == []  # a read only


def test_the_status_turn_without_a_key_asks_api_needs_as_before():
    api = FakeApi(
        needs=lambda cfg, **k: {"needs": [WAGER_ESCALATE], "count": 1, "code": 0}
    )
    st, out = seat(api, [])
    st.status("whats on the table")
    assert api.calls[-1] == ("needs", (), {})


def test_checkout_hands_the_key_and_reader_to_api_checkout_and_scrubs_the_screen():
    api = FakeApi(
        checkout={
            "screen": f"GRADES\n  · leaked {KEY}\nTABLE\n  · table agm_head satisfied · x"
        }
    )
    st, out = seat(api, [])
    st.human_key, st.read_head, st.secrets = "/k/key.hex", (lambda: {}), (KEY,)
    st.checkout()
    assert api.calls[0][0] == "checkout" and api.calls[0][2].keys() == {
        "human_key",
        "read_head",
    }
    shown = text(out)
    assert "TABLE" in shown and KEY not in shown and "[withheld]" in shown


def test_checkout_without_a_key_is_asked_as_before():
    api = FakeApi()
    st, out = seat(api, [])
    st.checkout()
    assert api.calls[0] == ("checkout", (), {})


def test_read_key_secrets_reads_text_and_hex_and_a_missing_file_yields_none(tmp_path):
    f = tmp_path / "k"
    f.write_text(KEY + "\n")
    assert KEY in s.read_key_secrets(f)
    assert (
        s.read_key_secrets(tmp_path / "nope") == () and s.read_key_secrets(None) == ()
    )


def test_the_ledger_reader_is_unreachable_when_the_table_is_not_there(tmp_path):
    read = s.ledger_reader(str(tmp_path / "campaign.db"), tmp_path / "no-the-table")
    with pytest.raises(OSError, match="the-table is not importable"):
        read()


# ── the narrator, wired ──────────────────────────────────────────────────────────
TID = "a" * 64
SERVED = {
    "state": "populated",
    "why": "",
    "tables": [
        {
            "id": TID,
            "trust": "human-sealed",
            "rows": [
                {
                    "what": "verdict",
                    "where": "s1",
                    "session": "s",
                    "turn": 0,
                    "total": 11,
                    "verdict": "strong",
                    "reason": "2d6+3 = 11: 10+",
                },
                {
                    "what": "verdict",
                    "where": "s1",
                    "session": "s",
                    "turn": 1,
                    "total": 9,
                    "verdict": "weak",
                    "reason": "2d6+2 = 9: 7-9",
                },
                {"what": "seal", "who": "human", "subject": "proposal:" + "ab" * 32},
            ],
        }
    ],
}
GOOD = f"You rolled 11 on turn 0, strong [{TID}_0], and 9 on turn 1, weak [{TID}_1]."


def story(say, doc=SERVED, color=False):
    api = FakeApi()
    st, out = seat(api, [], say=say)
    st.doc = doc
    st.table_story("what happened at the table")
    return text(out), st


def test_the_story_phrases_are_matched_whole():
    assert rec.story_kind("What happened at the table?")
    assert rec.story_kind("tell me the story, please")
    assert not rec.story_kind("what happened at the table in table 3 of the file")


def test_with_no_model_code_says_the_boxes_and_the_seal_is_shown_never_said():
    out, st = story(None)
    assert "agent> " in out and "no model asked" in out
    assert "rolled 11" in out and "[decided] seal" in out
    said = out.split("agent> ", 1)[1]
    assert "sealed" not in said.split("\n")[0]  # the seal box is shown, not said


def test_a_checked_model_sentence_stands_with_the_six_table_checks():
    out, _ = story(lambda prompt: GOOD)
    assert f"agent> {GOOD}" in out and "[struck]" not in out
    assert out.count("✓") == len(tb.TABLE_CHECK_NAMES)
    assert "each clause from its box" in out and "your words quoted exactly" not in out


def test_a_sentence_that_invents_a_roll_is_struck_and_code_stands():
    bad = f"You rolled 12 on turn 0, strong [{TID}_0], and 9 on turn 1, weak [{TID}_1]."
    out, _ = story(lambda prompt: bad)
    assert "[struck]" in out and "replaced by a code sentence" in out
    assert out.count("agent> ") == 2 and "rolled 11" in out.split("[struck]")[1]


def test_a_model_that_escalates_goes_to_the_human_card():
    out, _ = story(lambda prompt: "ESCALATE: I would have to guess")
    assert "[needs you] human card" in out and "the model escalated" in out
    assert "rolled 11" in out  # code still says the boxes


def test_a_model_that_is_unreachable_is_code_with_the_reason():
    def down(prompt):
        raise s.SayUnreachable("ollama is down")

    out, _ = story(down)
    assert "unreachable" in out and "ollama is down" in out and "rolled 11" in out


def test_no_served_table_is_a_state_card_not_a_story():
    out, _ = story(lambda p: pytest.fail("a model was asked"), doc=None)
    assert "[empty]" in out and "no served file" in out
    out, _ = story(
        lambda p: pytest.fail("a model was asked"),
        doc={"state": "unreachable", "why": "chain broken"},
    )
    assert "[unreachable]" in out and "chain broken" in out


def test_the_story_turn_is_reached_from_the_loop_without_the_chain():
    api = FakeApi(serve={"doc": SERVED, "state": "populated", "why": ""})
    st, out = seat(api, ["who", "", "what happened at the table", ""])
    st.run()
    assert "rolled 11" in text(out) and "escalate" not in api.names()


# ── T-cbm-1 in the seat: a code cite in a model sentence ─────────────────────────
from grove import seat_say as say_mod  # noqa: E402

GRAPH_OK = {
    "gate.py": {
        "state": "populated",
        "why": "",
        "stamp": {"head_sha": "abc123def4567"},
        "paths": ["one-script/onescript/gate.py"],
        "names": {"check_claims": [[437, 510]]},
    }
}


def fake_gate(sentence, facts):
    """gate.check_claims as far as the seat sees it: symbol rows from the facts."""
    out = []
    for word in sentence.split():
        file, _, name = word.strip(".,;").partition(".py:")
        e = facts.get("symbols", {}).get(file + ".py") if name else None
        if e is None:
            continue
        if e["state"] in ("stale", "unreachable"):
            v, why = "unchecked", f"graph {e['state']}: {e['why']}"
        elif e["state"] == "empty":
            v, why = "unverified", "not in the graph"
        else:
            ok = name in e["names"]
            v, why = ("verified", "") if ok else ("unverified", "not in the file")
        out.append(
            {"kind": "symbol", "claim": word.strip(".,;"), "verdict": v, "record": why}
        )
    return out


def with_graph(graph, name="check_claims"):
    api = FakeApi()
    box = bx.Box("b1", "you", "needs you", f"gate.py {name} needs a look")
    sentence = f"gate.py:{name} needs a look [b1]."
    st, out = seat(api, [], say=lambda prompt: sentence)
    st.bot = s.Bot(
        api, lambda d, q, n: [], lambda p: "", 6000, fake_gate, lambda text: graph
    )
    st.converse("k", [box], "check it")
    return text(out)


def test_a_cite_the_graph_holds_passes_the_cites_check():
    out = with_graph(GRAPH_OK)
    assert "agent> gate.py:check_claims needs a look [b1]." in out
    assert "[struck]" not in out and "note ·" not in out


def test_a_forged_symbol_cite_is_struck_by_every_cite_was_served():
    out = with_graph(GRAPH_OK, name="check_claimz")
    assert "[struck]" in out and "✗ every cite was served" in out
    assert "✓ nothing the boxes lack" in out  # the words were the boxes' own
    assert len(say_mod.CHECK_NAMES) == 4  # no fifth check


@pytest.mark.parametrize("state", ["stale", "unreachable"])
def test_a_stale_or_unreachable_graph_is_unchecked_and_says_so(state):
    graph = {
        "gate.py": {**GRAPH_OK["gate.py"], "state": state, "why": "re-index first"}
    }
    out = with_graph(graph, name="check_claimz")
    assert (
        "[struck]" not in out and "– every cite was served (code cite unchecked)" in out
    )
    assert (
        f"note · unchecked: gate.py:check_claimz (graph {state}: re-index first)" in out
    )


def test_an_empty_graph_strikes_the_cite():
    graph = {"gate.py": {"state": "empty", "why": "x", "paths": [], "names": {}}}
    assert "[struck]" in with_graph(graph)


def test_no_reader_makes_no_symbol_claim():
    assert say_mod.symbol_rows("gate.py:nope", fake_gate, None) == []
    assert say_mod.symbol_rows("gate.py:nope", None, lambda t: {}) == []
    assert say_mod.symbol_rows("no cite here", fake_gate, lambda t: GRAPH_OK) == []


def test_a_gate_that_cannot_answer_is_unchecked_never_verified():
    def boom(sentence, facts):
        raise RuntimeError("down")

    (r,) = say_mod.symbol_rows("gate.py:x", boom, lambda t: {})
    assert r["verdict"] == "unchecked" and "RuntimeError" in r["record"]
    assert say_mod.check_cites_served("x", [], symbols=[r]) is True


def test_the_graph_reader_is_off_unless_a_project_is_named():
    assert s.graph_reader({}) is None
    try:
        s.load_bot(s.bot_root())  # puts the one script on the path
    except s.SeatUnavailable:
        pytest.skip("willow-bot's one script is not beside this repo")
    assert callable(s.graph_reader({"GROVE_SEAT_GRAPH": "home-user-willow-bot"}))


def test_the_real_gate_and_graph_agree_with_the_seat():
    try:
        real = s.load_bot(s.bot_root())
        from onescript import graph
    except (s.SeatUnavailable, ImportError):
        pytest.skip("willow-bot's one script is not beside this repo")
    rows = say_mod.symbol_rows(
        "gate.py:check_claimz and gate.py:check_claims",
        real.claims,
        lambda t: {
            f: {
                "state": "populated",
                "why": "",
                "stamp": {},
                "paths": ["gate.py"],
                "names": {"check_claims": [[1, 2]]},
            }
            for f in ("gate.py",)
        },
    )
    assert [r["verdict"] for r in rows] == ["unverified", "verified"]
    assert graph.CITE.pattern  # the one pattern both sides use


# ── S4: every LEAK row of the audit's scrub probe (p3_scrub.py), and more ────────
import base64  # noqa: E402
import hashlib  # noqa: E402

K32 = hashlib.sha256(b"k").hexdigest()[:32]
K64 = hashlib.sha256(b"k").hexdigest()
K40 = hashlib.sha1(b"k").hexdigest()
SEED64 = hashlib.sha256(b"w4:surface").hexdigest()
B64 = base64.b64encode(hashlib.sha256(b"k").digest()).decode()
B64URL = base64.urlsafe_b64encode(hashlib.sha256(b"k").digest()).decode().rstrip("=")
W = "wager f1 escalate to human · "
LEAKS = {
    "32-hex bare": f"{W}{K32}",
    "64-hex bare": f"{W}{K64}",
    "64-hex seed bare": f"table verdict session s · 3 rows · seed {SEED64} · waiting on your tip seal",
    "40-hex bare": f"{W}{K40}",
    "seed: 64-hex": f"{W}seed: {SEED64}",
    "seed 64-hex, no colon": f"{W}seed {SEED64}",
    "key= base64": f"{W}key={B64}",
    "base64 bare": f"{W}{B64}",
    "base64url bare": f"{W}{B64URL}",
    "HUMAN_KEY=64hex": f"{W}GROVE_SEAT_HUMAN_KEY={K64}",
    "HUMAN_KEY=b64": f"{W}HUMAN_KEY={B64}",
    "key split across fields": f"{W}key · {K32[:16]} · {K32[16:]}",
    "hex split in 20s": f"{W}{K64[:20]} {K64[20:40]} {K64[40:]}",
    "key: with spaces inside": f"{W}key: {K32[:8]} {K32[8:16]} {K32[16:]}",
    "uppercase SEED=": f"{W}SEED={SEED64}",
    "passphrase in words": f"{W}passphrase: correct horse battery staple",
    "7-char key=": f"{W}key=abc1234",
    "secret in parentheses": f"{W}(secret) {K32}",
    "0x hex": f"{W}0x{K32}",
    "hex inside a word": f"{W}id{K32}x",
    "two 32s glued": f"{W}{K32}{K32}",
    "bare 64-hex in a cite bracket not served": f"{W}[{K64}_0]",
}
SECRETS = (K32, K64, K40, SEED64, B64, B64URL, "abc1234", "correct horse")


@pytest.mark.parametrize("label", list(LEAKS))
def test_S4_no_secret_shape_survives_the_scrub(label):
    out = rec.scrub(LEAKS[label])
    assert [x for x in SECRETS if x in LEAKS[label] and x in out] == [], out
    assert "[withheld]" in out
    # and through the whole path: a needs line becomes a box that shows none of it
    got = rec.read_needs(Needs([LEAKS[label]]), "cfg")
    shown = "\n".join(bx.render_box(b) + b.value + b.detail for b in got.boxes)
    assert [x for x in SECRETS if x in LEAKS[label] and x in shown] == []


def test_S4_a_record_hash_in_its_place_and_a_commit_after_its_word_stay():
    h = "d" * 64
    ok = f"proposal:{h} · tip:12:{h} · serve:{h} · run {h} · commit {'e' * 40} · green on {'f' * 40}"
    assert rec.scrub(ok) == ok
    assert (
        rec.scrub(f"proposal · x · {h}") != f"proposal · x · {h}"
    )  # bare: not a record hash
    assert rec.scrub(f"x {h}", known=(h,)) == f"x {h}"  # a served id the seat holds
    assert (
        rec.scrub(f"seen {'e' * 40}") != f"seen {'e' * 40}"
    )  # 40-hex without commit/sha


def test_S4_a_short_known_secret_is_ignored_and_a_four_char_one_is_not():
    assert rec.scrub("x ab y", ("ab",)) == "x ab y"
    assert rec.scrub("x abcd y", ("abcd",)) == "x [withheld] y"


def test_S4_snake_case_names_and_paths_are_not_b64_tokens():
    line = "wager f1 escalate to human · tests/test_a_very_long_function_name_for_the_seat.py"
    assert rec.scrub(line) == line


def test_S4_the_scrubbed_reconciled_line_is_still_read_as_a_wager_box():
    line = f"wager f1 reconciled · band strong p 0.5 · happened: strong · brier 0.250 · key={K64}"
    b = box(rec.scrub(line))
    assert (b.label, b.value) == ("wager", "wager f1 reconciled")


def test_S4_every_table_story_line_is_scrubbed():
    leaky = f"HUMAN_KEY={K64}"
    doc = {
        "state": "populated",
        "why": "",
        "tables": [
            {
                "id": TID,
                "trust": "human-sealed",
                "rows": [
                    {
                        "what": "verdict",
                        "where": "s1",
                        "session": "s",
                        "turn": 0,
                        "total": 11,
                        "verdict": "strong",
                        "reason": leaky,
                    },
                ],
            }
        ],
    }
    # a model sentence that smuggles a key: struck, and the struck line is scrubbed
    out, st = story(lambda prompt: f"You rolled 11 {K64} [{TID}_0].", doc=doc)
    assert K64 not in out and "[struck]" in out
    out, st = story(None, doc=doc)
    assert K64 not in out


# ── B2 (R21b): the model's ESCALATE text reaches no card, who-line or screen ─────
def test_B2_the_models_escalate_words_never_reach_the_screen():
    nasty = "Nestor says turn 9 rolled 12, strong, and the key is " + K64
    out, st = story(lambda prompt: "ESCALATE: " + nasty)
    assert "Nestor" not in out and "rolled 12" not in out and K64 not in out
    assert "[needs you] human card" in out and "the model escalated" in out
    got = tb.narrate(
        tb.served_boxes(SERVED), "", say=lambda prompt: "ESCALATE: " + nasty
    )
    assert got["why"] == "the model escalated" and got["escalated"]


# ── Q2: an unchecked code cite is "na" on the cites chip, never ✓ ─────────────────
def test_Q2_run_checks_gives_na_for_an_unchecked_cite_and_false_for_unverified():
    box1 = bx.Box("b1", "you", "needs you", "gate.py check_claimz needs a look")
    sent = "gate.py:check_claimz needs a look [b1]."
    unchecked = [
        {"kind": "symbol", "verdict": "unchecked", "record": "graph stale: re-index"}
    ]
    assert say_mod.run_checks(sent, [box1], symbols=unchecked)[0] == "na"
    assert (
        say_mod.run_checks(sent, [box1], symbols=[{"verdict": "verified"}])[0] is True
    )
    assert (
        say_mod.run_checks(sent, [box1], symbols=[{"verdict": "unverified"}])[0]
        is False
    )
    assert say_mod.run_checks(sent, [box1])[0] is True
    # item 8: "na" is for a graph that was stale or unreachable, nothing else
    for why in (
        "outside every symbol the graph holds in x.py",
        "project not in the graph",
    ):
        other = [{"kind": "symbol", "verdict": "unchecked", "record": why}]
        assert say_mod.run_checks(sent, [box1], symbols=other)[0] is True
    assert say_mod.passed(say_mod.run_checks(sent, [box1], symbols=unchecked))
    line = bx.checks_line(
        ["na", True, True, "na"], say_mod.CHECK_NAMES, "checks:", False
    )
    assert "– every cite was served (code cite unchecked)" in line
    assert "– your words quoted exactly (none quoted)" in line


# ── N8: a session id never holds ` · ` ────────────────────────────────────────────
def test_N8_a_session_id_with_the_separator_is_not_read_as_a_session():
    ok = "table verdict session s1 · 2 rows · forecast f1 · waiting on your tip seal"
    assert box(ok).label == "verdict session"
    worse = (
        "table verdict session a · b · 2 rows · forecast f1 · waiting on your tip seal"
    )
    assert box(worse).label == "record"


# ── B1: the whole table unreachable; Q1: a second box, peeked; R23: beacon off ─────
def test_B1_a_table_unreachable_line_is_one_unreachable_card():
    b = box("table unreachable · chain broken at row 7")
    assert (b.label, b.state) == ("table", "unreachable")
    assert b.value == "unreachable — table: chain broken at row 7"
    assert bx.render_box(b).startswith("+! [unreachable]")


def test_B1_the_no_sealed_tip_session_line_is_a_blocked_not_a_key_complaint():
    b = box(
        "table verdict session s1 · 2 rows · forecast f1 · no sealed tip on record that checks out"
    )
    assert (b.kind, b.state) == ("block", "unreachable")
    assert "no human key" not in b.value


class Peeker:
    """A fake api with a needs and a peek that remember what they were asked."""

    def __init__(self, own, watched):
        self.own, self.watched, self.calls = own, watched, []

    def needs(self, cfg, **kw):
        self.calls.append(("needs", cfg, kw))
        return {"needs": self.own, "count": len(self.own), "code": 0}

    def peek(self, cfg, **kw):
        self.calls.append(("peek", cfg, kw))
        return {"needs": self.watched, "count": len(self.watched), "code": 0}


def test_Q1_source_table_reads_by_peek_and_ids_its_boxes_apart():
    api = Peeker([], [WAGER_ESCALATE])
    got = rec.read_needs(api, "tcfg", source="table")
    assert [c[0] for c in api.calls] == ["peek"]
    ids = [b.id for b in got.boxes]
    assert all(i.startswith("t") for i in ids)
    same = rec.read_needs(Peeker([WAGER_ESCALATE], []), "cfg")
    assert not set(ids) & {b.id for b in same.boxes}
    assert got.boxes[0].label == "table" and "api.peek" in got.boxes[0].detail


def test_Q1_an_older_willow_bot_without_peek_is_unreachable_not_a_crash():
    class Old:
        pass

    got = rec.read_needs(Old(), "c", source="table")
    assert got.state == "unreachable" and "no peek read" in got.boxes[0].value


def test_Q1_the_status_turn_shows_both_boxes_and_asks_the_second_by_peek_only(tmp_path):
    api = Peeker(["proposal · own_idea: no · own/x · pass"], [WAGER_ESCALATE])
    st, out = seat(FakeApi(), [])
    st.api = api
    keys = tmp_path / "keys.json"
    keys.write_text("{}")
    watched = type("Cfg", (), {"keys": keys})()
    st.cfg, st.table_cfg = "own", watched
    st.status("what's on the table")
    said = text(out)
    assert "wager f1 escalate to human" in said and "[needs you] proposal" in said
    assert [(c[0], c[1]) for c in api.calls] == [("needs", "own"), ("peek", watched)]


def test_Q1_table_config_names_a_second_box_only_when_asked(tmp_path):
    made = []

    class Api:
        def default_keyring(self):
            return None

        def default_nestor_db(self):
            return None

        def Config(self, **kw):  # noqa: N802
            made.append(kw)
            return kw

    b = s.Bot(Api(), None, None, 1)
    assert s.table_config(b, tmp_path, environ={}) is None
    s.table_config(b, tmp_path, environ={"GROVE_SEAT_TABLE_BOX": "/t/box"})
    assert Path(made[0]["box"]).as_posix() == "/t/box"
    # item 7: the table box's OWN keys, beside it; never the seat's
    assert Path(made[0]["keys"]).as_posix() == "/t/keys/keys.json"
    s.table_config(
        b,
        tmp_path,
        environ={
            "GROVE_SEAT_TABLE_BOX": "/t/box",
            "GROVE_SEAT_TABLE_KEYS": "/k/x.json",
        },
    )
    assert Path(made[1]["keys"]).as_posix() == "/k/x.json"
    assert "beacon" not in made[0]


def test_R23_the_seat_says_the_beacon_reader_is_off_when_a_table_is_watched():
    class Cfg:
        beacon = None

    st, out = seat(FakeApi(needs=lambda c, **k: {"needs": [], "count": 0}), [])
    st.table_own = True
    st.cfg = Cfg()
    (note,) = st.beacon_note()
    assert note.state == "unreachable"
    assert note.value == "unreachable — beacon reader off: table outcomes unreachable"
    Cfg.beacon = staticmethod(lambda n: {})
    assert st.beacon_note() == []
    st.table_own = False
    Cfg.beacon = None
    assert st.beacon_note() == []  # no table watched: nothing to say


def test_R23_the_status_turn_carries_the_beacon_note():
    class Cfg:
        beacon = None

    api = FakeApi(needs=lambda c, **k: {"needs": [WAGER_ESCALATE], "count": 1})
    st, out = seat(api, [])
    st.cfg, st.table_own = Cfg(), True
    st.status("what's on the table")
    assert "beacon reader off: table outcomes unreachable" in text(out)


def test_item7_a_table_box_without_its_own_keys_is_unreachable_never_the_seats():
    api = Peeker([], [WAGER_ESCALATE])
    st, out = seat(FakeApi(), ["", "", ""])
    st.api = api
    st.cfg = "own"
    st.table_cfg = type("Cfg", (), {"keys": "/nowhere/keys/keys.json"})()
    st.status("what's on the table")
    said = text(out)
    assert (
        "[unreachable]" in said
        and "own keys are not at /nowhere/keys/keys.json" in said
    )
    assert [c[0] for c in api.calls] == ["needs"]  # no peek was made on any keys


# ── items 9, 10, 11: the public record values survive, a split key does not ──────
def test_item9_the_agm_head_line_keeps_the_ledger_heads():
    h1, h2 = "a1" * 32, "b2" * 32
    line = f"table agm_head failing · the ledger is at (4, {h1}), anchored (3, {h2})"
    assert rec.scrub(line) == line
    assert rec.scrub(f"seed_id {'c3' * 8} · subject {h1} · head {h2}") == (
        f"seed_id {'c3' * 8} · subject {h1} · head {h2}"
    )
    assert rec.scrub(f"merged {'e' * 40}") == f"merged {'e' * 40}"
    assert rec.scrub(f"table {h1}", known=(h1,)) == f"table {h1}"  # a served table id
    assert rec.scrub(f"seed {h1}") != f"seed {h1}"  # a seed is still not a seed_id


def test_item9_the_status_turn_passes_the_served_ids_it_holds_as_known():
    h = "d4" * 32
    api = FakeApi(
        needs=lambda c, **k: {
            "needs": [f"wager f1 escalate to human · table {h}"],
            "count": 1,
        }
    )
    st, out = seat(api, [])
    st.doc = {"tables": [{"id": h}]}
    st.status("what's on the table")
    assert h[:12] in text(out) and "[withheld]" not in text(out)
    st.doc = {"tables": []}
    st.turns.clear()
    st.status("what's on the table")
    assert "[withheld]" in text(out)


def test_item11_a_human_key_split_by_separators_or_pieces_is_withheld():
    k = hashlib.sha256(b"w4b:k").hexdigest()
    for line in (
        ",".join(k[i : i + 8] for i in range(0, 64, 8)),
        "-".join(k[i : i + 8] for i in range(0, 64, 8)),
        "/".join(k[i : i + 16] for i in range(0, 64, 16)),
        ":".join(k[i : i + 2] for i in range(0, 64, 2)),
        " ".join(k[i : i + 6] for i in range(0, 64, 6)),
        " · ".join(k[i : i + 4] for i in range(0, 64, 4)),
    ):
        out = rec.scrub("got " + line, (k,))
        assert out == "got [withheld]", (line, out)
