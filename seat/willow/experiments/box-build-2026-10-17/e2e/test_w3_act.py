"""W3b end-to-end: the act (R12, R20, R21, R22), across repos.

    sealed lore -> code rolls (GameSession.step on the stream) while a fake
    model picks a move id from legal_moves through the closed menu, on the
    set-piece beats only -> every roll a verdict row -> the human seals a scope
    and the served rows become boxes -> code narrates, the fake model rewrites
    under seat_say.run_checks and the table checks -> the decision beat is a
    proposal the human seals -> the D0 `table.*` classes close a table act in
    code and, when they cannot, go straight to the human -> the adversarial
    fakes (off-menu, lying, misattributing, inventing, unserved cite, quoting,
    ESCALATE, unreachable) are refused or fall back.

SPEC rulings R10, R11, R12, R20-R22; SPEC-documented C13-C16; SPEC-rival T12,
T13; W3b audit B1-B5, S1-S6, the M/N/S probes. Run:

    /home/user/tools/venv/bin/python -m pytest -q /home/user/sandbox/box-build/e2e

No model is reachable here; every model is a deterministic fake. Every box
lives in tmp_path; every seed comes from a fixed label by SHA-256.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

REPOS = Path(os.environ.get("BOX_REPOS", "/home/user/sandbox/repos"))
TABLE = REPOS / "safe-app-store" / "apps" / "the-table"
ONESCRIPT = REPOS / "willow-bot" / "one-script"
GROVE = REPOS / "willows-grove"
for p in (str(TABLE), str(ONESCRIPT), str(GROVE)):
    if p not in sys.path:
        sys.path.insert(0, p)

from grove import table_boxes as tb  # noqa: E402
from grove.seat_say import build_prompt  # noqa: E402
from onescript import api, gate, lore, table  # noqa: E402
from the_table import menu, peaks  # noqa: E402
from the_table import onescript_sink as osk  # noqa: E402
from the_table.dice_source import replay_roll  # noqa: E402
from the_table.story_session import StorySession  # noqa: E402
from the_table.worlds import load_world  # noqa: E402

HUMAN_KEY = b"a-throwaway-human-key-for-e2e-w3"
WORLD_MD = (
    "# The Floor\n"
    "- Hasbeen does not pay overtime for hope.\n"
    "- rule: weak 7-9 the beat holds but a flag stays lit\n"
)
CAP = 200_000
MENU = ["act:Grit", "act:Weird", "act:Cute", "act:Cool"]


def beacon_seed(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def world_path(name: str = "hasbeen") -> Path:
    return TABLE / "worlds" / f"{name}.json"


def set_piece_world(tmp: Path, flags=(True, True), name: str = "sp") -> Path:
    """hasbeen with ``set_piece`` on its two action beats as given (C15)."""
    w = copy.deepcopy(load_world(world_path()))
    for beat, flag in zip(w["scenes"][0]["beats"], flags):
        if flag is not None:
            beat["set_piece"] = flag
    p = tmp / f"{name}.json"
    p.write_text(json.dumps(w))
    return p


def make_cfg(tmp: Path) -> api.Config:
    grove = tmp / "grove"
    (grove / "governance").mkdir(parents=True)
    (grove / "governance" / "CONSTITUTION.md").write_text("CONST-III CONST-VI")
    ci = grove / "ci.yml"
    ci.write_text("pip install ruff==0.16.7")
    keys = tmp / "keys" / "keys.json"
    keys.parent.mkdir(mode=0o700)
    keys.write_text(
        json.dumps({"desk": "aa" * 32, "table": "bb" * 32, "human": HUMAN_KEY.hex()})
    )
    keys.chmod(0o600)
    return api.Config(
        box=tmp / "box",
        keys=keys,
        constitution=grove / "governance" / "CONSTITUTION.md",
        ci=ci,
        root=tmp / "no-clone-here",
        grove=grove,
        venv=tmp / "no-venv",
        now="2026-10-17T00:00:00Z",
        no_tests=True,
        phone=True,
    )


def proof(subject: str) -> str:
    """The human's hand: the only place a proof is made in this file."""
    return gate.sign(HUMAN_KEY, "seal", subject)


def box_rows(cfg) -> list[dict]:
    return [json.loads(x) for x in (cfg.box / "record.jsonl").read_text().splitlines()]


def never(*a, **k):
    raise AssertionError("a model was called where only code may act")


class FakePick:
    """A fake move-picking model: answers in order, the last repeated."""

    def __init__(self, *answers):
        self.answers, self.calls = list(answers), []

    def __call__(self, menu_ids):
        self.calls.append(list(menu_ids))
        a = self.answers[min(len(self.calls) - 1, len(self.answers) - 1)]
        if isinstance(a, Exception):
            raise a
        return a


def seal_lore(cfg) -> list[dict]:
    """A world/*.md proposal, sealed by the human, turned into lore rows (R11)."""
    card = api.scope(cfg, by=("who",), match={"who": "run"})
    assert api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))["sealed"]
    res = api.serve(cfg, card["spec"], max_chars=CAP)
    ids = [t["id"] for t in res["doc"]["tables"]]
    prop = json.dumps(
        {
            "path": "world/hasbeen.md",
            "data": WORLD_MD,
            "cites": ids[:1],
            "claim": "the floor",
        }
    )
    (p,) = api.take_proposals(cfg, [prop])["out"]["proposals"]
    assert api.lore(cfg, p["subject"])["code"] == 1  # unsealed: no lore
    assert api.seal_proposal(cfg, p["subject"], proof=proof(p["subject"]))["sealed"]
    out = api.lore(cfg, p["subject"])
    assert out["code"] == 0 and out["count"] == 2
    return out["lore"]


def play(cfg, pick, seed: str, world, session_id: str = "hasbeen-1", **kw):
    sink = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r), check=lambda x: table.beat_seal(cfg, x)
    )
    s = StorySession(world)
    policy = menu.menu_policy(pick, sink=sink, **kw)
    pending = osk.play_to_decision(s, policy, sink, seed=seed, session_id=session_id)
    return s, sink, policy, pending


def seal_tables(cfg, ids: list[str]) -> None:
    """The human seals each table's own hash, so it serves as `human-sealed`
    (serve.py: the label is read from the record); the only way a table's
    rows become fact boxes (NIT-3)."""
    run, _ = api._open(cfg, "needs", ("needs",))
    for sub in ids:
        run.rec.append(
            "seal",
            gate.human(sub, proof(sub), HUMAN_KEY),
            where=sub,
            subject=sub,
            proof=proof(sub),
        )


def serve_all(cfg) -> dict:
    """The human seals a scope over every pile by kind, and each table's own
    hash, and it is served."""
    card = api.scope(cfg, by=("what",))
    assert card["code"] == 0
    seal_tables(cfg, card["ids"])
    assert api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))["sealed"]
    doc = api.serve(cfg, card["spec"], max_chars=CAP)["doc"]
    assert doc["state"] == "populated", doc
    return doc


def served_verdicts(cfg) -> dict:
    card = api.scope(cfg, by=("what",), match={"what": "verdict"})
    assert card["code"] == 0
    assert api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))["sealed"]
    doc = api.serve(cfg, card["spec"], max_chars=CAP)["doc"]
    assert doc["state"] == "populated", doc
    return doc


def honest_say(prompt: str) -> str:
    """A fake narrator that rewrites the code sentence honestly: a roll's
    own line from the prompt glued with the free words, a lore line word
    for word (R21b: a lore clause is the box's exact value or nothing)."""
    out = []
    for ln in (ln for ln in prompt.splitlines() if ln.startswith("[")):
        tag, rest = ln.split("] ", 1)
        fact = rest.split(": ", 1)[1].split(" (")[0]
        if fact.startswith("turn "):
            out.append(f"Looks like {fact} {tag}].")
        else:
            out.append(f"{fact.rstrip('.')} {tag}].")
    return " ".join(out)


# ═══════════════════════════════ the full turn ═══════════════════════════════
def test_full_table_turn_code_rolls_model_picks_code_narrates_human_seals(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    seed = beacon_seed("w3:act")

    # 1. sealed lore: rows, served only under the human's seal (R11)
    lore_rows = seal_lore(cfg)
    assert [r["where"] for r in lore_rows] == ["The Floor", "The Floor"]

    # 2. the act: on the set-piece beats a fake model picks move ids from the
    # closed menu (R22); code rolls
    pick = FakePick("act:Weird", {"path": "act:Grit", "claim": "grit", "cites": []})
    s, sink, policy, pending = play(cfg, pick, seed, set_piece_world(tmp_path))
    assert pick.calls[0] == MENU
    assert policy.refusals == [] and pending is not None
    rows = box_rows(cfg)
    rolls = [r for r in rows if r.get("what") == "roll"]
    assert [r["move"] for r in rolls] == [["act", "Weird"], ["act", "Grit"]]
    world = load_world(world_path())
    for (
        r
    ) in rolls:  # the dice are the stream's, replayable from the seed: no model rolled
        sheet = peaks.engine_view(peaks.raw_sheets_for(world)[r["seat"]])
        replay_roll(seed, r["roll"], sheet=sheet)
        assert r["who"] == "table" and r["total"] == r["roll"]["result"]

    # 3. raw record rows are code-only boxes (S3); the model narrates served boxes
    raw = tb.scene_boxes(rows)
    assert tb.facts(raw) == [] and [b.label for b in tb.sayable(raw)] == [
        "scene",
        "roll",
        "roll",
    ]
    assert not any(b.label == "lore" for b in raw)  # raw lore needs the host's servable
    run = api._open(cfg, "needs", ("needs",))[0]
    held, _ = run.held()
    idx = lore.Index(run.rec.rows())
    with_lore = tb.scene_boxes(rows, servable=lambda row: lore.servable(row, idx, held))
    assert [b.value for b in with_lore if b.label == "lore"] == [
        r["fact"] for r in lore_rows
    ]
    doc = serve_all(cfg)
    assert all(t["trust"] == "human-sealed" for t in doc["tables"])
    boxes = tb.served_boxes(doc)
    assert sorted(b.label for b in tb.facts(boxes)) == [
        "lore",
        "lore",
        "roll",
        "roll",
    ]  # tables sort by served id
    # NIT-3: the same document with its tables labelled untrusted yields no facts
    untrusted = json.loads(json.dumps(doc))
    for t in untrusted["tables"]:
        t["trust"] = "untrusted"
    assert tb.facts(tb.served_boxes(untrusted)) == []
    served_ids = {t["id"] for t in doc["tables"]}
    assert all(
        b.id.rsplit("_", 1)[0] in served_ids for b in boxes
    )  # every id a served id
    r = tb.narrate(boxes, "what happened on the floor?", say=honest_say)
    assert r["source"] == "model" and r["checks"] == [True] * 6
    assert "Looks like " in r["sentence"] and r["sentence"] != r["code"]
    for roll in rolls:
        assert f"rolled {roll['total']}" in r["sentence"]
    # T13: a lying rewrite (a number the boxes lack) is struck; code's stands
    lie = r["sentence"].replace(f"rolled {rolls[0]['total']}", "rolled 13")
    struck = tb.narrate(boxes, say=lambda p: lie)
    assert struck["struck"] and struck["sentence"] == struck["code"]
    assert struck["checks"][2] is False
    # B5: the same numbers on the wrong boxes are struck per clause
    a, b = (
        f"rolled {rolls[0]['total']}, {rolls[0]['verdict']}",
        f"rolled {rolls[1]['total']}, {rolls[1]['verdict']}",
    )
    if a != b:
        swapped = r["sentence"].replace(a, "@@").replace(b, a).replace("@@", b)
        sw = tb.narrate(boxes, say=lambda p: swapped)
        assert sw["struck"] and sw["checks"][4] is False
    # B5: a quote, even the human's exact words, is struck
    q = tb.narrate(
        boxes,
        "what happened on the floor?",
        say=lambda p: honest_say(p)[:-1] + ' and "on the floor".',
    )
    assert q["struck"] and q["checks"][3] is False

    # 4. the decision beat: a proposal; only the human's proof moves the story (R10)
    sub = sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    with pytest.raises(osk.BeatNotSealed):
        sink.apply_beat_seal(s, pending, sub)
    assert s.pending_seal() == pending
    assert api.seal_proposal(cfg, sub, proof=proof(sub))["sealed"]
    sink.apply_beat_seal(s, pending, sub)
    assert s.pending_seal() is None
    # C16: decision and seal rows are shown boxes; never served to the model,
    # and a model that narrates seal state is struck by the vocabulary
    doc = serve_all(cfg)
    boxes = tb.served_boxes(doc)
    kinds = {b.label: b.kind for b in tb.shown(boxes)}
    assert kinds["decision"] == "you" and kinds["seal"] == "dec"
    said = tb.narrate(
        boxes, say=lambda p: honest_say(p)[:-1] + ", and the fact is sealed."
    )
    assert said["struck"] and said["checks"][2] is False and said["source"] == "code"
    prompt = build_prompt(tb.facts(boxes), "")
    assert "seal" not in prompt.lower() and "decision" not in prompt.lower()

    # 5. no model rolled, chose a decision, or sealed
    rows = box_rows(cfg)
    assert all(r["who"] == "human" for r in rows if r["kind"] == "seal")
    assert all(r["who"] == "table" for r in rows if r["kind"] == "verdict")
    assert seed not in (cfg.box / "record.jsonl").read_text()


def test_R22_the_shipped_world_asks_no_model_and_code_takes_the_suggested_stat(
    tmp_path,
):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    pick = FakePick("act:Cool")
    _, _, policy, pending = play(cfg, pick, beacon_seed("w3:r22"), world_path())
    assert pick.calls == [] and policy.refusals == [] and pending is not None
    rolls = [r for r in box_rows(cfg) if r.get("what") == "roll"]
    assert [r["move"] for r in rolls] == [
        ["act", "Weird"],
        ["act", "Grit"],
    ]  # b1 suggests Weird, b2 Grit


# ═══════════════════════════════ D0: table.* ════════════════════════════════
def test_a_table_act_closes_in_code_and_G6_stays_classless(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    play(cfg, FakePick("act:Cool"), beacon_seed("w3:d0"), set_piece_world(tmp_path))
    rolls = [r for r in box_rows(cfg) if r.get("what") == "roll"]
    doc = served_verdicts(cfg)

    res = api.escalate(cfg, "table.roll: turn 1", rung=never)
    assert res["d0"]["status"] == "resolved" and res["escalated"] == 0
    (p,) = res["pieces"]
    assert p["rows"] == [
        {
            "status": "resolved",
            "answer": {"total": rolls[1]["total"], "verdict": rolls[1]["verdict"]},
        }
    ]
    assert p["cites"] == [doc["tables"][0]["id"]]

    res = api.escalate(cfg, "table.state: tally", rung=never)
    assert res["pieces"][0]["rows"][0]["answer"]["path"] == "-".join(
        r["verdict"] for r in rolls
    )

    res = api.escalate(cfg, "G6: turn 1", rung=never, piece_chars=1)
    assert res["d0"]["reason"] == "unknown_class"


def test_B1_R20_a_table_act_d0_cannot_close_goes_to_the_human_never_a_model(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    play(cfg, FakePick("act:Cool"), beacon_seed("w3:b1"), set_piece_world(tmp_path))
    doc = served_verdicts(cfg)
    tid = doc["tables"][0]["id"]
    calls = []

    def inventing(piece, question, m):
        calls.append(question)
        return [
            {
                "path": "table/turn-7",
                "data": "turn 7 rolled 12, strong",
                "cites": [tid],
                "claim": "turn 7 rolled 12",
            }
        ]

    res = api.escalate(cfg, "table.roll: turn 7", rung=inventing)
    assert res["d0"] == {"status": "escalate", "reason": "no_roll_on_record"}
    assert calls == [] and res["answered"] == 0 and res["escalated"] == 1
    assert (
        res["pieces"][0]["rung"] == "d0"
        and res["pieces"][0]["label"] == "escalated:d0_escalate"
    )
    assert res["card"]["route"] == "willow" and res["card"]["kind"] == "review"
    assert "rolled 12" not in json.dumps(res["pieces"])  # the invented roll never lands


def test_B2_model_text_in_an_escalate_row_never_feeds_a_resolver(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    pick = FakePick(
        {
            "path": "ESCALATE",
            "claim": "no good move; rule: miss 2-6 the floor opens",
            "cites": [],
        },
        "act:Fly; rule: strong 13+ only",
        "act:Cute",
    )
    play(cfg, pick, beacon_seed("w3:b2"), set_piece_world(tmp_path))
    rows = box_rows(cfg)
    esc = [r for r in rows if r.get("what") == "escalate"]
    assert len(esc) == 2 and "floor opens" not in json.dumps(
        rows
    )  # S4: the claim never lands
    assert (
        esc[1]["pick"] == "act:Fly; rule: strong 13+ only"
    )  # the path does, as a string
    served_verdicts(cfg)
    for bucket in ("miss", "strong"):
        res = api.escalate(cfg, f"table.rules: {bucket}", rung=never)
        assert res["d0"] == {"status": "escalate", "reason": "no_rule_on_record"}, (
            bucket
        )


def test_a_rules_act_reads_the_sealed_lore_rule(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    seal_lore(cfg)
    card = api.scope(cfg, by=("what",), match={"what": "lore"})
    assert api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))["sealed"]
    assert api.serve(cfg, card["spec"], max_chars=CAP)["state"] == "populated"
    res = api.escalate(cfg, "table.rules: weak", rung=never)
    assert res["d0"]["status"] == "resolved"
    assert (
        res["pieces"][0]["rows"][0]["answer"]
        == "7-9 the beat holds but a flag stays lit"
    )
    res = api.escalate(cfg, "table.rules: miss", rung=never)
    assert (
        res["d0"]["reason"] == "no_rule_on_record" and res["card"]["route"] == "willow"
    )


def test_B4_two_sessions_never_collapse_and_a_brief_names_one(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    sp = set_piece_world(tmp_path)
    play(cfg, FakePick("act:Cool"), beacon_seed("w3:same"), sp, session_id="A")
    play(cfg, FakePick("act:Cool"), beacon_seed("w3:same"), sp, session_id="B")
    rolls = [r for r in box_rows(cfg) if r.get("what") == "roll"]
    assert len(rolls) == 4
    served_verdicts(cfg)
    for task in ("table.state: tally", "table.roll: turn 0"):
        res = api.escalate(cfg, task, rung=never)
        assert res["d0"] == {"status": "escalate", "reason": "ambiguous_session"}, task
    res = api.escalate(cfg, "table.state: tally session B", rung=never)
    ans = res["pieces"][0]["rows"][0]["answer"]
    assert ans["turns"] == 2 and ans["session"] == "B"
    res = api.escalate(cfg, "table.roll: turn 1 session A", rung=never)
    assert res["pieces"][0]["rows"][0]["answer"]["total"] == rolls[1]["total"]


# ═══════════════════════════ adversarial: the menu ═══════════════════════════
@pytest.mark.parametrize(
    "got, reason",
    [
        ("act:Fly", "off_menu"),  # an invented move
        ("Grit", "off_menu"),  # a bare stat
        (7, "off_menu"),  # an index (N1)
        (["act", "Grit"], "off_menu"),  # a list (N1)
        ("act:Grіt", "off_menu"),  # a lookalike
        ({"path": "act:Fly", "claim": "x", "cites": []}, "off_menu"),
        ({"path": "ESCALATE", "claim": "no good move", "cites": []}, "escalate"),
        (TimeoutError("ollama down"), "unreachable"),
        (None, "unreachable"),
    ],
)
def test_T12_a_pick_outside_legal_moves_is_refused_and_recorded(tmp_path, got, reason):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    _, _, policy, pending = play(
        cfg, FakePick(got, "act:Cute"), beacon_seed("w3:t12"), set_piece_world(tmp_path)
    )
    (ref,) = policy.refusals
    assert (
        ref["reason"] == reason and ref["to"] == "human" and ref["took"] == "act:Weird"
    )
    rows = box_rows(cfg)
    (esc,) = [r for r in rows if r.get("what") == "escalate"]
    assert esc["kind"] == "verdict" and esc["who"] == "table" and esc["to"] == "human"
    assert esc["menu"] == MENU and "got" not in esc and "claim" not in esc
    assert "no good move" not in json.dumps(rows) and "ollama down" not in json.dumps(
        rows
    )
    rolls = [r for r in rows if r.get("what") == "roll"]
    assert [r["move"] for r in rolls] == [
        ["act", "Weird"],
        ["act", "Cute"],
    ]  # code's pick, then the honest one
    assert pending is not None
    boxes = tb.served_boxes(serve_all(cfg))
    (b,) = [x for x in boxes if x.label == "escalate"]
    assert b.kind == "block" and b.value == tb.REFUSED and not tb.is_fact(b)
    assert "Fly" not in b.value + b.detail


def test_S4_a_propose_rows_seal_fields_never_ride_into_the_record(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    got = {
        "path": "act:Fly",
        "claim": "x",
        "proof": "f" * 64,
        "subject": "proposal:" + "ab" * 32,
        "wager": "w1",
        "outcome": "win",
        "kind": "seal",
        "who": "human",
    }
    play(cfg, FakePick(got, "act:Cute"), beacon_seed("w3:x"), set_piece_world(tmp_path))
    rows = box_rows(cfg)
    (esc,) = [r for r in rows if r.get("what") == "escalate"]
    text = json.dumps(esc)
    assert (
        esc["kind"] == "verdict" and esc["who"] == "table" and esc["pick"] == "act:Fly"
    )
    assert "f" * 64 not in text and "ab" * 32 not in text and "w1" not in text


def test_a_decision_beat_never_reaches_the_model(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    w = copy.deepcopy(load_world(world_path()))
    for b in w["scenes"][0]["beats"]:
        b["set_piece"] = True  # even the decision beat flagged
    wp = tmp_path / "all-sp.json"
    wp.write_text(json.dumps(w))
    for sp in (True, False):
        pick = FakePick("act:Grit")
        s, _, policy, pending = play(
            cfg, pick, beacon_seed("w3:c14"), wp, session_id=f"d{sp}", set_piece_only=sp
        )
        assert pending is not None and len(pick.calls) == 2
        with pytest.raises(RuntimeError, match="never on the menu"):
            policy(s, s.current_seat())
        assert len(pick.calls) == 2


# ═══════════════════════════ the set piece (C15) ═════════════════════════════
def test_a_set_pieces_flowering_output_is_a_draft_never_a_fact(tmp_path):
    cfg = make_cfg(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    wp = set_piece_world(tmp_path, (None, True))
    flowered = []

    def flowering(prompt, fact_boxes):
        flowered.append(prompt)
        return [
            {
                "path": "draft/b2.md",
                "data": "Gerald slides a napkin under the grille.",
                "claim": "a set piece",
                "cites": [b.id for b in fact_boxes],
            }
        ]

    s = StorySession(wp)
    sink = osk.OneScriptSink(lambda r: table.verdict(cfg, r))
    s.reset(beacon_seed("w3:c15"))
    sink.open_session("sp", {"seed": beacon_seed("w3:c15"), "seats": s.seats})
    drafts = []
    turn = 0
    while s.pending_seal() is None and not s.is_terminal():
        seat = s.current_seat()
        view = s.observe(seat).view
        if view["set_piece"]:  # C15: flowering only here, and only for a draft
            drafts.append(
                tb.set_piece_draft(
                    flowering, tb.scene_boxes(box_rows(cfg)), view["prompt"]
                )
            )
        obs = s.step(seat, ("act", "Grit"))
        sink.snapshot(
            {
                "turn": turn,
                "seat": seat,
                "move": ("act", "Grit"),
                "view": obs.view,
                "roll": s.last_roll,
            },
            note=obs.narration[0],
        )
        turn += 1
    assert len(flowered) == 1 and len(drafts) == 1
    (d,) = drafts
    assert d.role == tb.DRAFT and not tb.is_fact(d)
    text = (cfg.box / "record.jsonl").read_text()
    assert "napkin" not in text  # no row depends on it: never a verdict, never lore
    boxes = [*tb.served_boxes(serve_all(cfg)), d]
    assert d not in tb.facts(boxes) and d in tb.shown(boxes)
    r = tb.narrate(
        boxes,
        say=lambda p: tb.code_sentence(boxes) + " Gerald slides a napkin [draft].",
    )
    assert r["struck"] and r["source"] == "code" and r["checks"][0] is False
