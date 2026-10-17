"""W2 end-to-end: results as rows (J4) and the ai-game-master head (J9), across repos.

    forecast -> human seals tip -> play on the stream with the verdict sink
    (Tee'd into campaign.db) -> code proposes the outcome from verdict rows ->
    human seals it -> agm_head row -> human seals the tip over both ->
    reconcile (with the R3 basis) -> agm_head check.

SPEC rulings R3, R9, R10; SPEC-rival T4, T5, T7. Run:

    /home/user/tools/venv/bin/python -m pytest -q /home/user/sandbox/box-build/e2e

`BOX_REPOS` points at a directory holding `willow-bot` and `safe-app-store`
(default: the sandbox clones). Every box and campaign.db lives in tmp_path;
every seed comes from a fixed label by SHA-256.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

REPOS = Path(os.environ.get("BOX_REPOS", "/home/user/sandbox/repos"))
TABLE = REPOS / "safe-app-store" / "apps" / "the-table"
ONESCRIPT = REPOS / "willow-bot" / "one-script"
for p in (str(TABLE), str(ONESCRIPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from onescript import api, gate, record, reverse, table  # noqa: E402
from the_table import agm_head, peaks  # noqa: E402
from the_table import onescript_sink as osk  # noqa: E402
from the_table.dice_source import replay_roll  # noqa: E402
from the_table.ledger_sink import LedgerSink  # noqa: E402
from the_table.story_session import StorySession  # noqa: E402
from the_table.worlds import load_world  # noqa: E402
from beacon_e2e import FakeDrand, fired_round, table_forecast  # noqa: E402

HUMAN_KEY = b"a-throwaway-human-key-for-e2e-w2"
WORLDS = ("aetheris", "hasbeen", "ironworks")


def beacon_seed(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


def world_path(name: str) -> Path:
    return TABLE / "worlds" / f"{name}.json"


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
        beacon=FakeDrand(),  # W4 break 1: the operator's (stand-in) drand reader
    )


def make_key_file(tmp: Path) -> Path:
    f = tmp / "human" / "key.hex"
    f.parent.mkdir(mode=0o700)
    f.write_text(HUMAN_KEY.hex() + "\n")
    f.chmod(0o600)
    return f


def proof(subject: str) -> str:
    """The human's hand: the only place a proof is made in this file."""
    return gate.sign(HUMAN_KEY, "seal", subject)


def box_rows(cfg) -> list[dict]:
    return [json.loads(x) for x in (cfg.box / "record.jsonl").read_text().splitlines()]


def run_loop(tmp: Path, name: str, seed: str) -> dict:
    cfg, key = make_cfg(tmp), make_key_file(tmp)
    assert api.checkin(cfg)["code"] == 0
    world = load_world(world_path(name))
    dist = peaks.distribution(world)

    # 1. forecast, and the human seals the tip that holds it, before any dice
    f = api.forecast(
        cfg,
        "f1",
        dist,
        by="oracle",
        table=table_forecast(cfg, peaks.world_key(world), seed),
    )
    assert f["code"] == 0, f
    assert api.seal_tip(cfg, f["tip"], proof=proof(f["tip"]))["sealed"]

    # 2. play on the stream; every roll a verdict row, Tee'd into campaign.db
    ledger = LedgerSink(str(tmp / "campaign"))
    sink = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r),
        check=lambda x: table.beat_seal(cfg, x),
        forecast=f["subject"],
        beacon_round=fired_round(cfg, f),
    )
    s = StorySession(world_path(name))
    pending = osk.play_to_decision(
        s,
        osk.suggested_policy(),
        osk.Tee(ledger, sink),
        seed=seed,
        session_id=f"{name}-1",
    )
    assert pending is not None

    # 3. the decision beat: a proposal; only the human's proof moves the story
    sub = sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    with pytest.raises(osk.BeatNotSealed):
        sink.apply_beat_seal(s, pending, sub)
    assert api.seal_proposal(cfg, sub, proof=proof(sub))["sealed"]
    sink.apply_beat_seal(s, pending, sub)
    assert s.pending_seal() is None

    # 4. code proposes the outcome from the verdict rows; it seals nothing
    seals_before = [r["n"] for r in box_rows(cfg) if r["kind"] == "seal"]
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] == "proposed", po
    assert [r["n"] for r in box_rows(cfg) if r["kind"] == "seal"] == seals_before

    # 5. the human seals that outcome
    so = api.seal_outcome(cfg, f["subject"], po["outcome"], proof=proof(po["subject"]))
    assert so["sealed"], so

    # 6. J9: the campaign.db head as one agm_head row; the human is shown what
    # the tip covers (S3) and then seals it
    ledger.close()
    ah = table.agm_head(cfg, **agm_head.row(ledger.db_path))
    assert ah["code"] == 0, ah
    shown = api.seal_tip(cfg, ah["tip"])["covers"]
    assert [c["what"] for c in shown] == ["verdict session", "outcome", "agm_head"]
    assert shown[0]["forecast"] == "f1" and shown[0]["who"] == ["table"]
    assert api.seal_tip(cfg, ah["tip"], proof=proof(ah["tip"]))["sealed"]

    # 7. reconcile (the R3 hook bound by the box itself, B1) and the head check
    rep = api.reconcile(cfg, human_key=key)
    chk = table.agm_check(cfg, agm_head.reader(ledger.db_path), human_key=key)
    return dict(
        cfg=cfg,
        key=key,
        dist=dist,
        f=f,
        po=po,
        so=so,
        ah=ah,
        rep=rep,
        chk=chk,
        ledger=ledger,
        session=s,
        sink=sink,
        world=world,
        seed=seed,
    )


def wager(rep) -> dict:
    return next(r for r in rep["wagers"]["rows"] if r["id"] == "f1")


# ═══════════════════════════════ the full loop ═══════════════════════════════
@pytest.mark.parametrize("name", WORLDS)
def test_full_loop_rows_to_reconcile_to_head(tmp_path, name):
    out = run_loop(tmp_path, name, beacon_seed(f"w2:{name}"))
    w, rows = wager(out["rep"]), box_rows(out["cfg"])
    assert w["state"] == "reconciled" and w["graded_by"] is None and "brier" in w
    assert (
        w["actual_path"] == out["po"]["outcome"]["path"] == "-".join(out["sink"].path)
    )
    assert out["chk"]["state"] == "satisfied" and out["chk"]["covered"] is True
    assert out["chk"]["db_sha"] == "matches"
    assert (
        table.reconcile_table(out["cfg"], human_key=out["key"])["wagers"]["rows"][0][
            "state"
        ]
        == "reconciled"
    )

    # chain order: wager < tip seal < every verdict < outcome seal < agm_head < tip seal
    n = {
        k: next(r["n"] for r in rows if pred(r))
        for k, pred in {
            "wager": lambda r: r["kind"] == "wager",
            "verdict": lambda r: r["kind"] == "verdict",
            "agm": lambda r: r.get("what") == "agm_head",
        }.items()
    }
    tip1 = out["po"]["under"]["tip_seal"]
    assert n["wager"] < tip1 < n["verdict"] < out["so"]["row"]["n"] < n["agm"]
    last_tip = [
        r["n"]
        for r in rows
        if r["kind"] == "seal" and str(r.get("subject", "")).startswith("tip:")
    ][-1]
    assert n["agm"] < last_tip

    # no verdict row is a seal; every seal row the code path wrote is the human's
    assert all(r["who"] == "human" for r in rows if r["kind"] == "seal")
    assert all(r["standing"] == "unattested" for r in rows if r["kind"] == "verdict")
    # the seed is the beacon round's public randomness: on the open row only
    # (W4 break 1), never on a roll row
    holding = [r for r in rows if out["seed"] in json.dumps(r)]
    assert [(r["kind"], r.get("what")) for r in holding] == [("verdict", "open")]
    assert holding[0]["randomness"] == out["seed"]


def test_every_verdict_roll_replays_from_the_seed(tmp_path):
    out = run_loop(tmp_path, "hasbeen", beacon_seed("w2:replay"))
    rolls = [r for r in box_rows(out["cfg"]) if r.get("what") == "roll"]
    assert rolls
    for r in rolls:
        sheet = peaks.engine_view(peaks.raw_sheets_for(out["world"])[r["seat"]])
        replay_roll(out["seed"], r["roll"], sheet=sheet)


# ═══════════════════════════ the head: tamper and loss ═══════════════════════
def test_a_tampered_campaign_db_differs(tmp_path):
    out = run_loop(tmp_path, "hasbeen", beacon_seed("w2:tamper"))
    db = out["ledger"].db_path
    con = sqlite3.connect(db)
    con.execute("UPDATE ledger SET note='forged' WHERE id=2")
    con.commit()
    con.close()
    chk = table.agm_check(out["cfg"], agm_head.reader(db), human_key=out["key"])
    assert chk["state"] == "failing" and "broken" in chk["why"]


def test_a_campaign_db_grown_after_the_anchor_differs_until_reanchored(tmp_path):
    out = run_loop(tmp_path, "hasbeen", beacon_seed("w2:grow"))
    db = out["ledger"].db_path
    more = LedgerSink(str(Path(db).parent))
    more.open_session("late", {"seed": 2})
    more.close()
    chk = table.agm_check(out["cfg"], agm_head.reader(db), human_key=out["key"])
    assert chk["state"] == "failing"
    table.agm_head(out["cfg"], **agm_head.row(db))
    chk = table.agm_check(out["cfg"], agm_head.reader(db), human_key=out["key"])
    assert (
        chk["state"] == "satisfied" and chk["covered"] is False
    )  # until the human seals a tip


def test_a_missing_campaign_db_is_unreachable(tmp_path):
    out = run_loop(tmp_path, "hasbeen", beacon_seed("w2:missing"))
    shutil.rmtree(Path(out["ledger"].db_path).parent)
    chk = table.agm_check(
        out["cfg"], agm_head.reader(out["ledger"].db_path), human_key=out["key"]
    )
    assert chk["state"] == "unreachable"


# ═══════════════════════════ adversarial across the seam ═════════════════════
def test_T5_play_before_the_human_sealed_the_tip_counts_for_nothing(tmp_path):
    """The forecast is on record, but the dice ran before the human sealed a tip
    holding it. The human then seals everything at once: R3 escalates."""
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    hw = load_world(world_path("hasbeen"))
    f = api.forecast(
        cfg,
        "f1",
        peaks.distribution(hw),
        by="oracle",
        table=table_forecast(cfg, peaks.world_key(hw), beacon_seed("w2:t5")),
    )
    sink = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r),
        forecast=f["subject"],
        beacon_round=fired_round(cfg, f),
    )
    pending = osk.play_to_decision(
        StorySession(world_path("hasbeen")),
        osk.suggested_policy(),
        sink,
        seed=beacon_seed("w2:t5"),
        session_id="s",
    )
    sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    tip = record.tip_subject(box_rows(cfg)[-1])
    assert api.seal_tip(cfg, tip, proof=proof(tip))["sealed"]
    path = "-".join(sink.path)
    so = api.seal_outcome(
        cfg,
        f["subject"],
        {"path": path},
        proof=proof(reverse.outcome_subject(f["subject"], {"path": path})),
    )
    assert api.seal_tip(cfg, so["tip"], proof=proof(so["tip"]))["sealed"]
    w = wager(api.reconcile(cfg, human_key=key))  # the plain verb: one door (B1)
    assert w["state"] == "escalate" and "T5" in w["reason"] and "brier" not in w
    co = api.checkout(cfg, human_key=key)
    assert "wager f1 escalate to human · R3:" in co["screen"]


def test_T4_a_session_begun_before_the_forecast_counts_for_nothing(tmp_path):
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    table.verdict(
        cfg, {"what": "roll", "session": "s", "verdict": "strong", "path": "strong"}
    )
    hw = load_world(world_path("hasbeen"))
    f = api.forecast(
        cfg,
        "f1",
        peaks.distribution(hw),
        by="oracle",
        table=table_forecast(cfg, peaks.world_key(hw), beacon_seed("w2:t4")),
    )
    assert api.seal_tip(cfg, f["tip"], proof=proof(f["tip"]))["sealed"]
    sink = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r),
        forecast=f["subject"],
        beacon_round=fired_round(cfg, f),
    )
    osk.play_to_decision(
        StorySession(world_path("hasbeen")),
        osk.suggested_policy(),
        sink,
        seed=beacon_seed("w2:t4"),
        session_id="s",
    )
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] == "escalate" and "T4" in po["reason"]


def test_T7_cut_verdict_rows_after_the_last_tip_are_said(tmp_path):
    """No tip after the verdict rows: cutting the tail passes the chain and the
    anchor (A7, the documented limit), and the proposal says it is incomplete."""
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    hw = load_world(world_path("hasbeen"))
    f = api.forecast(
        cfg,
        "f1",
        peaks.distribution(hw),
        by="oracle",
        table=table_forecast(cfg, peaks.world_key(hw), beacon_seed("w2:t7")),
    )
    assert api.seal_tip(cfg, f["tip"], proof=proof(f["tip"]))["sealed"]
    sink = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r),
        forecast=f["subject"],
        beacon_round=fired_round(cfg, f),
    )
    pending = osk.play_to_decision(
        StorySession(world_path("hasbeen")),
        osk.suggested_policy(),
        sink,
        seed=beacon_seed("w2:t7"),
        session_id="s",
    )
    sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    rows = box_rows(cfg)
    cut = rows[: next(r["n"] for r in rows if r.get("what") == "decision")]
    (cfg.box / "record.jsonl").write_text("".join(record.canon(r) + "\n" for r in cut))
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] == "escalate" and "A7" in po["reason"]


def test_a_forged_verdict_seal_and_a_named_beat_seal_move_nothing(tmp_path):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    res = table.verdict(
        cfg,
        {"kind": "seal", "what": "open", "session": "s", "proof": proof("tip:0:00")},
    )
    assert res["code"] == 1
    sink = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r), check=lambda x: table.beat_seal(cfg, x)
    )
    s = StorySession(world_path("hasbeen"))
    pending = osk.play_to_decision(
        s, osk.suggested_policy(), sink, seed=beacon_seed("w2:named"), session_id="s"
    )
    sub = sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    assert not api.seal_proposal(cfg, sub, proof="Sean")["sealed"]
    with pytest.raises(osk.BeatNotSealed):
        sink.apply_beat_seal(s, pending, sub)
    assert s.pending_seal() == pending


def test_B2_a_sealed_beat_from_another_world_moves_nothing(tmp_path):
    """P2: world A's beat sealed for real; world B's same-box session handed
    A's subject. The real checker answers sealed, the sink refuses it."""
    out = run_loop(tmp_path, "aetheris", beacon_seed("w2:b2"))
    cfg = out["cfg"]
    sub_a = next(r["subject"] for r in box_rows(cfg) if r["kind"] == "proposal")
    sink = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r), check=lambda x: table.beat_seal(cfg, x)
    )
    s_b = StorySession(world_path("hasbeen"))
    pending_b = osk.play_to_decision(
        s_b,
        osk.suggested_policy(),
        sink,
        seed=beacon_seed("w2:b2b"),
        session_id="hasbeen-1",
    )
    sink.decision(pending_b, lambda p, c: table.propose_beat(cfg, p, c))
    assert table.beat_seal(cfg, sub_a)["state"] == "sealed"
    with pytest.raises(osk.BeatNotSealed, match="not this beat"):
        sink.apply_beat_seal(s_b, pending_b, sub_a)
    assert s_b.pending_seal() == pending_b


@pytest.mark.parametrize("played", [w for w in WORLDS if w != "hasbeen"])
def test_S2_a_session_on_another_world_supplies_no_outcome(tmp_path, played):
    """P3: the forecast is about hasbeen; the session played another world."""
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    hw = load_world(world_path("hasbeen"))
    f = api.forecast(
        cfg,
        "f1",
        peaks.distribution(hw),
        by="oracle",
        table=table_forecast(cfg, peaks.world_key(hw), beacon_seed("w2:s2" + played)),
    )
    assert api.seal_tip(cfg, f["tip"], proof=proof(f["tip"]))["sealed"]
    sink = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r),
        forecast=f["subject"],
        beacon_round=fired_round(cfg, f),
    )
    pending = osk.play_to_decision(
        StorySession(world_path(played)),
        osk.suggested_policy(),
        sink,
        seed=beacon_seed("w2:s2" + played),
        session_id="s",
    )
    sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] == "escalate" and "S2" in po["reason"]


def test_onescript_beacon_restatements_equal_the_tables_and_play_pys():
    """onescript.beacon restates the-table's StreamRandom.seed_id and play.py's
    round arithmetic (onescript imports neither); pinned equal here."""
    import importlib.util

    from onescript import beacon
    from the_table.stream import StreamRandom

    for label in ("a", "w2:pin", "w4:grind:the-round"):
        seed = beacon_seed(label)
        assert beacon.seed_id(seed) == StreamRandom.from_seed(seed).seed_id
    play_py = (
        REPOS
        / "willows-grove"
        / "seat"
        / "willow"
        / "experiments"
        / "predictions-2026-10-17"
        / "play.py"
    )
    spec = importlib.util.spec_from_file_location("_play_pin", play_py)
    play = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(play)
    assert (beacon.GENESIS, beacon.PERIOD, beacon.CHAIN) == (
        play.GENESIS,
        play.PERIOD,
        play.CHAIN,
    )
    for r in (1, 6558806, 7000000):
        assert beacon.round_time(r) == play.round_time(r)


def test_onescript_dice_replay_equals_the_tables_stream():
    """R23a: onescript.beacon restates the-table's SHA-256 stream to REPLAY a
    roll from the open row's randomness; pinned equal here, roll for roll."""
    from onescript import beacon
    from the_table.stream import GENERATOR_ID, StreamRandom

    assert beacon.GENERATOR_ID == GENERATOR_ID
    for i in range(300):
        seed = beacon_seed(f"w2:replay-pin:{i}")
        at = i % 11
        rng = StreamRandom.from_seed(seed)
        rng.stream.n = at
        a, b = rng.randint(1, 6), rng.randint(1, 6)
        assert beacon.roll_2d6(seed, at) == (a, b, rng.counter)


@pytest.mark.parametrize("name", WORLDS)
def test_onescript_rehash_of_world_inputs_equals_peaks_world_key(name):
    """R23a: the open row carries peaks.world_inputs; onescript re-hashes them
    (table.world_problem) and must get peaks.world_key's sheets_sha, and the
    sheets it reads modifiers from are peaks.sheets_for (engine aliases)."""
    world = load_world(world_path(name))
    key = peaks.world_key(world)
    inputs = json.loads(json.dumps(peaks.world_inputs(world)))  # as the record holds it
    sheets, why = table.world_problem({"world_inputs": inputs}, {"table": key})
    assert why is None and sheets == peaks.sheets_for(world)
