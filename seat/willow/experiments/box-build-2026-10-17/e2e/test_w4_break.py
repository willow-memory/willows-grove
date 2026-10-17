# ruff: noqa: E402  (sys.path setup must run before the sibling repos import)
"""W4 break: the full adversarial list, run end to end across the three repos.

    SPEC-rival.md §5 T1-T16, one test each (``test_T<k>_...``); every
    SPEC-documented "Break:" line not already in test_w1/w2/w3 (``test_J<k>_...``);
    the whole chain on one real box with a throwaway human key (``test_chain_...``);
    and the seams BETWEEN waves that no wave audit saw (``test_seam_...``).

Every test fails if its attack succeeds. An attack that succeeds today is kept
as ``xfail(strict=True)`` with the reproducer in its reason: it turns into a
failure (XPASS) the day the defect is fixed, so the marker must then go.

Nothing under sandbox/repos is edited. Every box, key and campaign.db lives in
tmp_path; every seed is SHA-256 of a fixed label, so every run is the same run.

    /home/user/tools/venv/bin/python -m pytest -q /home/user/sandbox/box-build/e2e
"""

from __future__ import annotations

import copy
import json
import os
import random
import sqlite3
import sys
from pathlib import Path

import pytest

REPOS = Path(os.environ.get("BOX_REPOS", "/home/user/sandbox/repos"))
TABLE = REPOS / "safe-app-store" / "apps" / "the-table"
ONESCRIPT = REPOS / "willow-bot" / "one-script"
GROVE = REPOS / "willows-grove"
PREDICTIONS = GROVE / "seat" / "willow" / "experiments" / "predictions-2026-10-17"
HERE = Path(__file__).resolve().parent
for p in (str(TABLE), str(ONESCRIPT), str(GROVE), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import test_w1_loop as w1
import test_w3_act as w3
from beacon_e2e import FakeDrand, table_forecast
from grove import table_boxes as tb
from onescript import api, gate, mai_shape, record, reverse, table
from the_table import agm_head, menu, peaks
from the_table import onescript_sink as osk
from the_table.dice_source import replay_roll, rolled_with
from the_table.ledger_sink import LedgerSink, _row_hash
from the_table.story_session import StorySession
from the_table.stream import (
    EngineMismatch,
    ReplayRefused,
    Stream,
    StreamRandom,
)
from the_table.worlds import load_world

HUMAN_KEY = b"a-throwaway-human-key-for-e2e-w4-break"
CAP = 400_000
beacon_seed = w1.beacon_seed
FakePick, honest_say, never = w3.FakePick, w3.honest_say, w3.never


def world_path(name: str = "hasbeen") -> Path:
    return TABLE / "worlds" / f"{name}.json"


# ── the box: a throwaway human key, a table key, nothing shared ─────────────
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
        beacon=FakeDrand(tmp / "box"),  # W4 break 1: the operator's (stand-in) reader
    )


def make_key_file(tmp: Path) -> Path:
    f = tmp / "human" / "key.hex"
    f.parent.mkdir(mode=0o700)
    f.write_text(HUMAN_KEY.hex() + "\n")
    f.chmod(0o600)
    return f


def proof(subject: str) -> str:
    """The human's hand: the only place this file makes a proof."""
    return gate.sign(HUMAN_KEY, "seal", subject)


def box_rows(cfg) -> list[dict]:
    return [json.loads(x) for x in (cfg.box / "record.jsonl").read_text().splitlines()]


def write_rows(cfg, rows: list[dict]) -> None:
    """The attacker's pen: rewrite record.jsonl, re-chained and re-numbered."""
    prev, out = record.GENESIS, []
    for i, r in enumerate(rows):
        r = dict(r, n=i, prev=prev)
        r.pop("hash", None)
        r["hash"] = record.h256(record.canon(r))
        prev = r["hash"]
        out.append(record.canon(r))
    (cfg.box / "record.jsonl").write_text("".join(x + "\n" for x in out))


def forge(cfg, kind: str, **fields) -> dict:
    """Append one well-chained row the attacker wrote by hand (A5): every
    stamp copied from the last row, ``who`` whatever the attacker says."""
    rows = box_rows(cfg)
    last = rows[-1]
    row = {k: last[k] for k in ("family", "standing", "version", "ts")}
    row.update(kind=kind, who="human", **fields)
    write_rows(cfg, [*rows, row])
    return box_rows(cfg)[-1]


def seal_tip(cfg, subject: str) -> dict:
    return api.seal_tip(cfg, subject, proof=proof(subject))


def last_tip(cfg) -> str:
    return record.tip_subject(box_rows(cfg)[-1])


def wager_of(rep: dict, wid: str = "f1") -> dict:
    return next(r for r in rep["wagers"]["rows"] if r["id"] == wid)


def bucket(total: int) -> str:
    """Own copy of the 2d6+stat read (never peaks.bucket: a shared bug cancels)."""
    return "strong" if total >= 10 else "weak" if total >= 7 else "miss"


def sheet_of(world: dict, seat: int) -> dict:
    return peaks.engine_view(peaks.raw_sheets_for(world)[seat])


def seal_tables(cfg, ids) -> None:
    run, _ = api._open(cfg, "needs", ("needs",))
    for sub in ids:
        run.rec.append(
            "seal",
            gate.human(sub, proof(sub), HUMAN_KEY),
            where=sub,
            subject=sub,
            proof=proof(sub),
        )


def serve_by(cfg, by=("what",), match=None, tables=True) -> dict:
    card = api.scope(cfg, by=by, match=match or {})
    assert card["code"] == 0, card
    if tables:
        seal_tables(cfg, card["ids"])
    assert api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))["sealed"]
    return api.serve(cfg, card["spec"], max_chars=CAP)["doc"]


def seal_lore(cfg, md: str = w3.WORLD_MD, path: str = "world/hasbeen.md") -> dict:
    """A world/*.md proposal the human seals; returns {subject, lore}."""
    card = api.scope(cfg, by=("who",), match={"who": "run"})
    assert api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))["sealed"]
    res = api.serve(cfg, card["spec"], max_chars=CAP)
    ids = [t["id"] for t in res["doc"]["tables"]]
    prop = json.dumps(
        {"path": path, "data": md, "cites": ids[:1], "claim": "the world"}
    )
    (p,) = api.take_proposals(cfg, [prop])["out"]["proposals"]
    assert api.seal_proposal(cfg, p["subject"], proof=proof(p["subject"]))["sealed"]
    return {"subject": p["subject"], "lore": api.lore(cfg, p["subject"])}


def forecast_table(cfg, world: dict, wid="f1", dist=None, by="oracle", *, seed):
    """A table forecast awaiting the next round, whose randomness is `seed`
    (fixed now, before any die: the stand-in drand's `commit`)."""
    f = api.forecast(
        cfg,
        wid,
        dist if dist is not None else peaks.distribution(world),
        by=by,
        table=table_forecast(cfg, peaks.world_key(world), seed),
    )
    assert f["code"] == 0, f
    return f


def play_table(
    cfg,
    wp: Path,
    seed,
    *,
    forecast=None,
    policy=None,
    session_id="s",
    write=None,
    ledger=None,
    pick=None,
):
    """Code plays to the first decision beat; every roll a verdict row."""
    write = write or (lambda r: table.verdict(cfg, r))
    rnd = (
        next(
            (
                r["table"]["beacon_round"]
                for r in box_rows(cfg)
                if r["kind"] == "wager" and r["hash"] == forecast
            ),
            None,
        )
        if forecast
        else None
    )
    if rnd is not None and FakeDrand.of(cfg) is not None:
        FakeDrand.of(cfg).fire(rnd)  # the session starts once its round is out (R23a)
    sink = osk.OneScriptSink(
        write,
        check=lambda x: table.beat_seal(cfg, x),
        forecast=forecast,
        beacon_round=rnd,
    )
    if pick is not None:
        policy = menu.menu_policy(pick, sink=sink)
    s = StorySession(wp)
    pending = osk.play_to_decision(
        s,
        policy or osk.suggested_policy(),
        osk.Tee(ledger, sink) if ledger else sink,
        seed=seed,
        session_id=session_id,
    )
    return s, sink, pending, policy


def table_loop(
    tmp: Path, seed, *, name="hasbeen", dist=None, play_seed=None, **play_kw
) -> dict:
    """forecast -> human tip -> code plays -> decision proposed. Stops before
    any outcome is proposed, so a test can attack what comes next."""
    cfg, key = make_cfg(tmp), make_key_file(tmp)
    assert api.checkin(cfg)["code"] == 0
    world = load_world(world_path(name))
    f = forecast_table(cfg, world, dist=dist, seed=seed)  # the round's randomness
    assert seal_tip(cfg, f["tip"])["sealed"]
    s, sink, pending, _policy = play_table(
        cfg, world_path(name), play_seed or seed, forecast=f["subject"], **play_kw
    )
    assert pending is not None
    sub = sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    return {
        "cfg": cfg,
        "key": key,
        "world": world,
        "f": f,
        "s": s,
        "sink": sink,
        "pending": pending,
        "beat": sub,
        "seed": seed,
    }


def close_loop(out: dict) -> dict:
    """code proposes the outcome; the human seals it and a tip over it; reconcile."""
    cfg, key, f = out["cfg"], out["key"], out["f"]
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    if po["state"] != "proposed":
        return {"po": po, "rep": None, "w": None}
    so = api.seal_outcome(cfg, f["subject"], po["outcome"], proof=proof(po["subject"]))
    assert so["sealed"]
    assert seal_tip(cfg, so["tip"])["sealed"]
    rep = api.reconcile(cfg, human_key=key)
    return {"po": po, "so": so, "rep": rep, "w": wager_of(rep)}


# ── replay a whole box's dice from the record and the beacon alone ──────────
def replay_box(rows: list[dict], seed: str, world: dict) -> list[str]:
    """Every way the box's verdict rows disagree with the dice the beacon
    fixes. Reads only the record and the seed: each roll replays from its own
    counter, totals and verdicts are re-derived, the path is re-joined, each
    session's counters run on from 0 without a gap, and every roll's seed_id
    is the one its `open` row named."""
    bad, opened, at, path = [], {}, {}, {}
    for r in rows:
        if r.get("kind") != "verdict":
            continue
        sid = r.get("session")
        if r.get("what") == "open":
            opened[sid], at[sid], path[sid] = r.get("seed_id"), 0, []
            continue
        if r.get("what") != "roll":
            continue
        roll = r.get("roll") or {}
        try:
            replay_roll(seed, roll, sheet=sheet_of(world, r["seat"]))
        except Exception as e:  # noqa: BLE001 - every refusal is a finding
            bad.append(f"row {r['n']}: replay refused: {type(e).__name__}: {e}")
        if roll.get("seed_id") != opened.get(sid):
            bad.append(
                f"row {r['n']}: seed_id {roll.get('seed_id')} is not the open "
                f"row's {opened.get(sid)}"
            )
        if roll.get("counter_before") != at.get(sid):
            bad.append(
                f"row {r['n']}: counter_before {roll.get('counter_before')} "
                f"!= {at.get(sid)}"
            )
        at[sid] = roll.get("counter")
        if r.get("total") != roll.get("result"):
            bad.append(
                f"row {r['n']}: total {r.get('total')} != dice {roll.get('result')}"
            )
        if r.get("verdict") != bucket(roll.get("result", -99)):
            bad.append(f"row {r['n']}: verdict {r.get('verdict')} is not the dice's")
        path.setdefault(sid, []).append(bucket(roll.get("result", -99)))
        if r.get("path") != "-".join(path[sid]):
            bad.append(f"row {r['n']}: path {r.get('path')!r} is not the dice's")
    return bad


# ═══════════════════════ the whole chain, one real box ═══════════════════════
@pytest.fixture(scope="module")
def chain(tmp_path_factory):
    """forecast before dice -> seal tip -> play on a beacon-like seed, a fake
    model picking from the closed menu on set pieces -> verdict rows (Tee'd
    into campaign.db) -> decision beat sealed by proof -> code-proposed
    outcome -> human seals -> agm_head -> human seals the tip -> reconcile ->
    agm check -> served doc -> narration."""
    tmp = tmp_path_factory.mktemp("chain")
    cfg, key = make_cfg(tmp), make_key_file(tmp)
    seed = beacon_seed("w4:chain")
    seen: list = []  # every string a human or a model is shown along the way
    assert api.checkin(cfg)["code"] == 0
    lo = seal_lore(cfg)
    assert lo["lore"]["code"] == 0 and lo["lore"]["count"] == 2

    wp = w3.set_piece_world(tmp)
    world = load_world(wp)
    f = forecast_table(cfg, world, seed=seed)  # before any die
    seen.append(api.seal_tip(cfg, f["tip"])["covers"])  # asked without a proof
    t1 = seal_tip(cfg, f["tip"])
    assert t1["sealed"]

    ledger = LedgerSink(str(tmp / "campaign"))
    pick = FakePick("act:Weird", "act:Grit")  # the suggested stats
    s, sink, pending, policy = play_table(
        cfg, wp, seed, forecast=f["subject"], ledger=ledger, pick=pick
    )
    seen.append(pick.calls)
    assert pending is not None and policy.refusals == []

    sub = sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    with pytest.raises(osk.BeatNotSealed):
        sink.apply_beat_seal(s, pending, sub)
    assert api.seal_proposal(cfg, sub, proof=proof(sub))["sealed"]
    sink.apply_beat_seal(s, pending, sub)

    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] == "proposed", po
    so = api.seal_outcome(cfg, f["subject"], po["outcome"], proof=proof(po["subject"]))
    assert so["sealed"]
    ledger.close()
    ah = table.agm_head(cfg, **agm_head.row(ledger.db_path))
    assert ah["code"] == 0
    covers = api.seal_tip(cfg, ah["tip"])["covers"]
    seen.append(covers)
    assert seal_tip(cfg, ah["tip"])["sealed"]
    rep = api.reconcile(cfg, human_key=key)
    chk = table.agm_check(cfg, agm_head.reader(ledger.db_path), human_key=key)

    doc = serve_by(cfg)
    boxes = tb.served_boxes(doc)
    told = tb.narrate(boxes, "what happened on the floor?", say=honest_say)
    seen += [doc, told, tb.code_sentence(boxes)]
    obs = StorySession(wp).reset(seed)
    seen.append([obs.narration, obs.view])
    return {
        "cfg": cfg,
        "key": key,
        "seed": seed,
        "world": world,
        "wp": wp,
        "f": f,
        "po": po,
        "so": so,
        "rep": rep,
        "chk": chk,
        "doc": doc,
        "boxes": boxes,
        "told": told,
        "covers": covers,
        "seen": seen,
        "ledger": ledger,
        "sink": sink,
        "lore": lo,
    }


def test_chain_reconciles_anchors_serves_and_narrates(chain):
    w = wager_of(chain["rep"])
    assert w["state"] == "reconciled" and w["graded_by"] is None and "brier" in w
    assert (
        w["actual_path"]
        == chain["po"]["outcome"]["path"]
        == "-".join(chain["sink"].path)
    )
    assert chain["chk"]["state"] == "satisfied" and chain["chk"]["covered"] is True
    assert [c["what"] for c in chain["covers"]] == [
        "verdict session",
        "outcome",
        "agm_head",
    ]
    rows = box_rows(chain["cfg"])
    assert all(r["who"] == "human" for r in rows if r["kind"] == "seal")
    assert all(r["who"] == "table" for r in rows if r["kind"] == "verdict")
    told = chain["told"]
    assert told["source"] == "model" and told["checks"] == [True] * 6
    assert sorted(b.label for b in tb.facts(chain["boxes"])) == [
        "lore",
        "lore",
        "roll",
        "roll",
    ]
    rolls = [r for r in rows if r.get("what") == "roll"]
    for r in rolls:
        assert f"rolled {r['total']}" in told["sentence"]


def test_chain_seam_replays_every_verdict_row_from_record_and_beacon(chain):
    """Seam (j): the record and the beacon alone re-derive every verdict row."""
    rows = box_rows(chain["cfg"])
    assert [r for r in rows if r.get("what") == "roll"]
    assert replay_box(rows, chain["seed"], chain["world"]) == []
    assert replay_box(rows, beacon_seed("w4:not-the-beacon"), chain["world"]) != []


def test_chain_seam_beacon_seed_never_in_narration_menu_or_covers(chain):
    """Seam (i): the seed fixes every later die; no surface shows it, nor its
    first 16 hex, nor the hex upper-cased."""
    seed = chain["seed"]
    blob = json.dumps(chain["seen"], default=str)
    for needle in (seed, seed[:16], seed.upper(), seed[-16:]):
        assert needle not in blob
    # W4 break 1: the seed is the beacon round's randomness, public once the
    # round fires; the record holds it on the session's open row and nowhere else
    holding = [r for r in box_rows(chain["cfg"]) if seed in json.dumps(r)]
    assert [(r["kind"], r.get("what")) for r in holding] == [("verdict", "open")]


def test_chain_seam_model_sentence_citing_a_wager_row_is_struck(chain):
    """Seam (d): a wager row is the run's (`who: run`), so no scope serves it
    and no box is made of it; a model clause citing it by its id, its hash or
    its subject is struck, and the code sentence stands."""
    cfg, f = chain["cfg"], chain["f"]
    for by in (("who",), ("what",), ("where",)):
        doc = serve_by(cfg, by=by, tables=False)
        assert doc["state"] == "populated"
        assert not [
            r for t in doc["tables"] for r in t["rows"] if r.get("what") == "wager"
        ]
    boxes = chain["boxes"]
    good = tb.narrate(boxes, say=honest_say)
    assert good["source"] == "model"
    for cite in ("f1", f["subject"], f["subject"][:12]):
        bad = tb.narrate(
            boxes, say=lambda p, c=cite: honest_say(p) + f" Looks like weak [{c}]."
        )
        assert (
            bad["struck"] and bad["source"] == "code" and bad["checks"][0] is False
        ), cite


# ═════════════════════════════ T1-T16 (SPEC-rival §5) ════════════════════════
def test_T1_a_forged_human_seal_row_serves_nothing_and_grades_nothing(tmp_path):
    out = table_loop(tmp_path, beacon_seed("w4:t1"))
    cfg, key, f = out["cfg"], out["key"], out["f"]
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] == "proposed"
    # outcome: who human, the outcome on the row, no proof
    forge(
        cfg,
        "seal",
        where=po["subject"],
        subject=po["subject"],
        wager=f["subject"],
        outcome=po["outcome"],
    )
    # beat: who human over the proposal, no proof
    forge(cfg, "seal", where=out["beat"], subject=out["beat"])
    # scope: who human over a fresh scope card, no proof
    card = api.scope(cfg, by=("what",))
    forge(cfg, "seal", where=card["subject"], subject=card["subject"])
    assert seal_tip(cfg, last_tip(cfg))["sealed"]  # the human seals over all of it
    w = wager_of(api.reconcile(cfg, human_key=key))
    assert w["state"] == "escalate" and "brier" not in w
    assert table.beat_seal(cfg, out["beat"])["state"] == "unsealed"
    with pytest.raises(osk.BeatNotSealed):
        out["sink"].apply_beat_seal(out["s"], out["pending"], out["beat"])
    assert api.serve(cfg, card["spec"], max_chars=CAP)["doc"]["state"] != "populated"


def test_T2_the_humans_proof_copied_onto_another_outcome_leaves_the_first(tmp_path):
    out = table_loop(tmp_path, beacon_seed("w4:t2"))
    cfg, key, f = out["cfg"], out["key"], out["f"]
    closed = close_loop(out)
    path = closed["po"]["outcome"]["path"]
    other = next(
        e["path"] for e in peaks.distribution(out["world"]) if e["path"] != path
    )
    real = next(
        r
        for r in box_rows(cfg)
        if r["kind"] == "seal" and r.get("subject") == closed["po"]["subject"]
    )
    forge(
        cfg,
        "seal",
        where=real["subject"],
        subject=real["subject"],
        proof=real["proof"],
        wager=f["subject"],
        outcome={"path": other},
    )
    assert seal_tip(cfg, last_tip(cfg))["sealed"]
    w = wager_of(api.reconcile(cfg, human_key=key))
    assert w["state"] == "reconciled" and w["actual_path"] == path


def test_T3_an_outcome_sealed_over_the_bare_wager_hash_escalates(tmp_path):
    out = table_loop(tmp_path, beacon_seed("w4:t3"))
    cfg, key, f = out["cfg"], out["key"], out["f"]
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    bare = api.seal_outcome(cfg, f["subject"], po["outcome"], proof=proof(f["subject"]))
    assert not bare.get("sealed")
    forge(
        cfg,
        "seal",
        where=f["subject"],
        subject=f["subject"],
        proof=proof(f["subject"]),
        wager=f["subject"],
        outcome=po["outcome"],
    )
    assert seal_tip(cfg, last_tip(cfg))["sealed"]
    w = wager_of(api.reconcile(cfg, human_key=key))
    assert w["state"] == "escalate" and "brier" not in w


def test_T4_a_wager_appended_after_the_verdict_it_predicts_escalates(tmp_path):
    """Through the plain reconcile verb, not only the outcome proposer (W2)."""
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    world = load_world(world_path())
    _s, sink, pending, _ = play_table(cfg, world_path(), beacon_seed("w4:t4"))
    sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    path = "-".join(sink.path)
    f = forecast_table(cfg, world, seed=beacon_seed("w4:t4"))  # after the dice
    assert seal_tip(cfg, f["tip"])["sealed"]
    so = api.seal_outcome(
        cfg,
        f["subject"],
        {"path": path},
        proof=proof(reverse.outcome_subject(f["subject"], {"path": path})),
    )
    assert seal_tip(cfg, so["tip"])["sealed"]
    w = wager_of(api.reconcile(cfg, human_key=key))
    assert w["state"] == "escalate" and "brier" not in w


def test_T5_a_wager_inside_no_sealed_tip_when_the_verdicts_land_escalates(tmp_path):
    """The human never seals a tip before the outcome: nothing is graded."""
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    world = load_world(world_path())
    f = forecast_table(cfg, world, seed=beacon_seed("w4:t5"))
    _s, sink, pending, _ = play_table(
        cfg, world_path(), beacon_seed("w4:t5"), forecast=f["subject"]
    )
    sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] == "escalate" and "T5" in po["reason"]
    path = "-".join(sink.path)
    api.seal_outcome(
        cfg,
        f["subject"],
        {"path": path},
        proof=proof(reverse.outcome_subject(f["subject"], {"path": path})),
    )
    w = wager_of(api.reconcile(cfg, human_key=key))  # no tip sealed at all
    assert w["state"] == "escalate" and "brier" not in w


def test_T6_a_late_wager_the_human_seals_reconciles_visibly(tmp_path):
    """The trust root's own act reconciles; the row shows the beacon round
    beside the tip's ts so a reader can see it was late."""
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    committed = {
        "sha256": "ab" * 32,
        "beacon_then": 9,
        "target": 8,
    }  # made after its target
    f = api.forecast(
        cfg,
        "f1",
        [{"path": "yes", "p": 0.3}, {"path": "no", "p": 0.7}],
        by="human",
        committed=committed,
    )
    assert f["code"] == 0, f
    assert seal_tip(cfg, f["tip"])["sealed"]
    out = {"path": "no"}
    so = api.seal_outcome(
        cfg, f["subject"], out, proof=proof(reverse.outcome_subject(f["subject"], out))
    )
    assert seal_tip(cfg, so["tip"])["sealed"]
    w = wager_of(api.reconcile(cfg, human_key=key))
    assert w["state"] == "reconciled"
    assert w["beacon_then"] == 9 and w["tip_seal_ts"] and w["wager_ts"]


def test_T7_cut_rows_on_a_table_box_caught_under_a_tip_ungraded_without(tmp_path):
    out = table_loop(tmp_path, beacon_seed("w4:t7"))
    cfg, key = out["cfg"], out["key"]
    closed = close_loop(out)
    assert closed["w"]["state"] == "reconciled"
    good = box_rows(cfg)
    # (a) inside the sealed tip: cut back past the outcome seal
    cut = good[: closed["so"]["row"]["n"]]
    (cfg.box / "record.jsonl").write_text("".join(record.canon(r) + "\n" for r in cut))
    run, _ = api._open(cfg, "needs", ("needs",))
    assert reverse.covered_through(run.rec, HUMAN_KEY) is None
    w = wager_of(api.reconcile(cfg, human_key=key))
    assert w["state"] != "reconciled" and "brier" not in w
    # (b) a fresh box with no tip after the verdicts: cut the tail, nothing graded
    out2 = table_loop(tmp_path / "b", beacon_seed("w4:t7b"))
    rows = box_rows(out2["cfg"])
    cut = rows[: next(r["n"] for r in rows if r.get("what") == "decision")]
    (out2["cfg"].box / "record.jsonl").write_text(
        "".join(record.canon(r) + "\n" for r in cut)
    )
    po = table.outcome_from_verdicts(
        out2["cfg"], out2["f"]["subject"], human_key=out2["key"]
    )
    assert po["state"] == "escalate" and "A7" in po["reason"]


def _rolls_of(seed: str, interfere: bool) -> list[dict]:
    """Two live sessions stepped in turn, a third party calling random.seed
    between every step when ``interfere``. Returns session A's roll records."""
    got = {"A": [], "B": []}
    sessions = {}
    for k, sd in (("A", seed), ("B", beacon_seed("w4:t8:other"))):
        s = StorySession(world_path())
        s.reset(sd)
        sessions[k] = s
    live = True
    while live:
        live = False
        for k, s in sessions.items():
            if s.is_terminal() or s.pending_seal() is not None:
                continue
            live = True
            if interfere:
                random.seed(1234)
                random.random()
            seat = s.current_seat()
            s.step(seat, ("act", s.observe(seat).view["suggests"]))
            got[k].append(dict(s.last_roll))
    return got["A"]


def test_T8_a_reseed_of_global_random_between_two_live_sessions_changes_nothing():
    seed = beacon_seed("w4:t8")
    solo = []
    s = StorySession(world_path())
    s.reset(seed)
    while not s.is_terminal() and s.pending_seal() is None:
        seat = s.current_seat()
        s.step(seat, ("act", s.observe(seat).view["suggests"]))
        solo.append(dict(s.last_roll))
    assert solo and _rolls_of(seed, interfere=True) == solo == _rolls_of(seed, False)


def test_T9_a_replay_that_skips_a_creator_roll_diverges_and_is_refused():
    """Engine.roll draws two dice before its is_creator branch returns
    (engine_v1_7.py:57-58): the row's counter_before carries those draws."""
    from the_table.dice_source import _engine_class
    from the_table.dice_source import roll as droll

    Engine = _engine_class()

    def creator_then_roll(seed):
        rng = StreamRandom.from_seed(seed)
        eng = Engine()
        eng.stats = {"Integrity": 1}
        with rolled_with(rng, eng):
            eng.roll("Grit", is_creator=True)  # draws two dice, uses none
        after = rng.counter
        _, _, rec = droll(eng, "Grit", rng, 1)
        first = StreamRandom.from_seed(seed)  # what a skipping replay would draw
        skipped_sum = first.randint(1, 6) + first.randint(1, 6) + 1
        return after, rec, skipped_sum

    # the first label whose creator dice sum differs from the real roll's (a
    # replay cannot tell two draws apart that give one sum, by construction)
    seed, (after_creator, rec, _skipped_sum) = next(
        (sd, got)
        for sd in (beacon_seed(f"w4:t9:{i}") for i in range(50))
        if (got := creator_then_roll(sd))[2] != got[1]["result"]
    )
    assert after_creator > 0
    assert rec["counter_before"] == after_creator
    replay_roll(seed, rec, sheet={"Integrity": 1})  # with the draws: it replays
    skipped = dict(rec, counter_before=0, counter=rec["counter"] - after_creator)
    with pytest.raises(ReplayRefused):
        replay_roll(seed, skipped, sheet={"Integrity": 1})


def test_T10_a_round_whose_randomness_is_not_its_beacons_is_refused():
    spec = __import__("importlib.util").util.spec_from_file_location(
        "_w4_export", PREDICTIONS / "export.py"
    )
    ex = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(ex)
    rounds = sorted((PREDICTIONS / "rounds").glob("*.json"))
    revealed = [json.loads(p.read_text()) for p in rounds]
    revealed = [d for d in revealed if "reveal" in d]
    assert revealed
    data = copy.deepcopy(revealed[0])
    assert ex.export(data)  # as stored: exports
    r = data["reveal"]["beacon"]["randomness"]
    flipped = None
    for i in range(len(r)):  # flip hex until an answer moves
        cand = r[:i] + ("0" if r[i] != "0" else "1") + r[i + 1 :]
        data["reveal"]["beacon"]["randomness"] = cand
        if ex.answers_from_beacon(data) != data["reveal"]["answers"]:
            flipped = cand
            break
    assert flipped is not None
    with pytest.raises(ex.Refused, match="not the beacon's"):
        ex.export(data)
    # BLS stays unverified, and the file says so (predictions README §4)
    assert "BLS signature is still not checked" in ex.__doc__


def test_T11_an_outcome_seal_moves_the_scope_and_serves_empty_until_resealed(tmp_path):
    out = table_loop(tmp_path, beacon_seed("w4:t11"))
    cfg = out["cfg"]
    doc = serve_by(cfg, by=("who",), match={"who": "human"}, tables=False)
    assert doc["state"] == "populated"
    old = {t["id"] for t in doc["tables"]}
    closed = close_loop(out)
    assert "rescope" in closed["so"] and closed["so"]["rescope"]["steps"]
    card = api.scope(cfg, by=("who",), match={"who": "human"})
    assert api.serve(cfg, card["spec"], max_chars=CAP)["doc"]["state"] == "empty"
    assert api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))["sealed"]
    new = api.serve(cfg, card["spec"], max_chars=CAP)["doc"]
    assert new["state"] == "populated" and not ({t["id"] for t in new["tables"]} & old)
    # a model row citing the moved (old) table is refused
    stale = json.dumps(
        {"path": "notes/x.md", "data": "x", "cites": sorted(old)[:1], "claim": "x"}
    )
    took = api.take_proposals(cfg, [stale])
    assert not [
        p
        for p in took.get("out", {}).get("proposals", [])
        if p.get("verdict") == "pass"
    ], took


@pytest.mark.parametrize(
    "got",
    [
        "act:Integrity",  # the engine's own stat name: the engine takes it, the menu does not
        "act:Synthesis",
        "decide:s1::b3",  # a decision move id
        "act:Grit;act:Cool",
        {"path": "act:Efficiency", "claim": "x", "cites": []},
    ],
)
def test_T12_a_move_the_engine_knows_but_legal_moves_does_not_is_refused(tmp_path, got):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    _s, _sink, _pending, policy = play_table(
        cfg,
        w3.set_piece_world(tmp_path),
        beacon_seed("w4:t12"),
        pick=FakePick(got, "act:Cute"),
    )
    (ref,) = policy.refusals
    assert ref["reason"] == "off_menu" and ref["took"] == "act:Weird"
    rolls = [r for r in box_rows(cfg) if r.get("what") == "roll"]
    assert [r["move"] for r in rolls] == [["act", "Weird"], ["act", "Cute"]]
    assert (
        next(r for r in box_rows(cfg) if r.get("what") == "escalate")["to"] == "human"
    )


def test_T13_a_narrator_word_or_number_no_box_holds_is_struck(chain):
    boxes = chain["boxes"]
    good = honest_say(tb.build_prompt(tb.facts(boxes), ""))
    assert tb.narrate(boxes, say=lambda p: good)["source"] == "model"
    rolls = [r for r in box_rows(chain["cfg"]) if r.get("what") == "roll"]
    t0 = rolls[0]
    words = {
        9: "nine",
        10: "ten",
        11: "eleven",
        12: "twelve",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        4: "four",
        3: "three",
        2: "two",
    }
    lies = [
        good.replace(f"rolled {t0['total']}", f"rolled {t0['total']} luckily"),  # word
        good.replace(f"rolled {t0['total']}", f"rolled {t0['total'] + 1}"),  # number
        good.replace(f"rolled {t0['total']}", f"rolled {words.get(t0['total'], 'x')}"),
        good.replace(f"rolled {t0['total']}", f"rolled 0{t0['total']}"),  # 09
        good.replace(f", {t0['verdict']}", f", {t0['verdict']}ed"),  # stemming
    ]
    for lie in lies:
        assert lie != good
        r = tb.narrate(boxes, say=lambda p, lie=lie: lie)
        assert r["struck"] and r["sentence"] == r["code"], lie


def test_T14_a_world_file_that_is_not_lore_rows_is_not_served(tmp_path):
    """The human seals a world/*.md proposal (so the file is written) but no
    lore rows are made: nothing of it is served, and naming it is struck."""
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    md = "# The Vault\n- the vault door hums at midnight\n"
    card = api.scope(cfg, by=("who",), match={"who": "run"})
    api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))
    ids = [
        t["id"] for t in api.serve(cfg, card["spec"], max_chars=CAP)["doc"]["tables"]
    ]
    (p,) = api.take_proposals(
        cfg,
        [
            json.dumps(
                {"path": "world/vault.md", "data": md, "cites": ids[:1], "claim": "x"}
            )
        ],
    )["out"]["proposals"]
    assert api.seal_proposal(cfg, p["subject"], proof=proof(p["subject"]))["sealed"]
    assert any(
        r["kind"] == "write" and r.get("path") == "world/vault.md"
        for r in box_rows(cfg)
    )
    play_table(
        cfg,
        w3.set_piece_world(tmp_path),
        beacon_seed("w4:t14"),
        pick=FakePick("act:Weird", "act:Grit"),
    )
    doc = serve_by(cfg)
    assert "hums" not in json.dumps(doc)
    boxes = tb.served_boxes(doc)
    assert not [b for b in boxes if b.label == "lore"]
    r = tb.narrate(
        boxes, say=lambda q: honest_say(q) + " the vault door hums at midnight."
    )
    assert r["struck"] and r["source"] == "code"


def test_T15_shim_shuffle_in_place_equals_the_stream_copy():
    seed = beacon_seed("w4:t15")
    for n in (2, 17, 52):
        xs = list(range(n))
        a = StreamRandom.from_seed(seed)
        a.shuffle(xs)
        b = Stream.from_seed(seed)
        assert xs == b.shuffle(list(range(n))) and a.counter == b.n


def test_T15_the_dice_library_shuffles_on_the_stream_not_global_random():
    """R6 limit (W4 break 6): the third-party `dice` library's keep operators
    ignore `random=` (dice/elements.py:409-418, 625), so the-table's seam
    (aetheris5e.dice5e) rolls keep forms itself, on the stream, and refuses any
    library roll that touches the global random while a stream is injected."""
    from aetheris5e import dice5e

    seed = beacon_seed("w4:t15")
    got = []
    for g in (0, 1):
        random.seed(g)
        before = random.getstate()
        got.append(dice5e.total("6d6l4", StreamRandom.from_seed(seed)))
        assert random.getstate() == before  # a stream roll never touches global random
    assert got[0] == got[1]
    random.seed(0)
    before = random.getstate()
    with pytest.raises(dice5e.GlobalRandomUsed, match="R6 limit"):
        dice5e.total("4d6l3+1", StreamRandom.from_seed(seed))  # the library's keep form
    assert random.getstate() == before  # put back before the refusal


def test_T16_a_roll_from_another_engine_hash_is_refused_and_named():
    seed = beacon_seed("w4:t16")
    _s, _path, rolls = w1.play_to_decision(world_path(), seed)
    seat, rec = rolls[0]
    world = load_world(world_path())
    forged = dict(rec, engine_hash="ee" * 32)
    with pytest.raises(EngineMismatch, match="ee" * 32):
        replay_roll(seed, forged, sheet=sheet_of(world, seat))


# ═════════════════ SPEC-documented "Break:" lines not yet in e2e ═════════════
def test_J1_a_beacon_outcome_without_the_humans_proof_counts_for_nothing(tmp_path):
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    a = api.forecast(
        cfg, "a", [{"path": "yes", "p": 0.4}, {"path": "no", "p": 0.6}], by="oracle"
    )
    assert seal_tip(cfg, a["tip"])["sealed"]
    out = {"path": "yes"}
    forge(
        cfg,
        "seal",
        where=a["subject"],
        subject=reverse.outcome_subject(a["subject"], out),
        wager=a["subject"],
        outcome=out,
        proposed_outcome=out,
    )
    assert seal_tip(cfg, last_tip(cfg))["sealed"]
    w = wager_of(api.reconcile(cfg, human_key=key), "a")
    assert w["state"] == "escalate" and "brier" not in w


def test_J1_an_outcome_proof_moved_to_another_wager_counts_for_nothing(tmp_path):
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    dist = [{"path": "yes", "p": 0.4}, {"path": "no", "p": 0.6}]
    a = api.forecast(cfg, "a", dist, by="oracle")
    b = api.forecast(cfg, "b", dist, by="oracle")
    assert seal_tip(cfg, b["tip"])["sealed"]
    out = {"path": "yes"}
    sub_a = reverse.outcome_subject(a["subject"], out)
    assert api.seal_outcome(cfg, a["subject"], out, proof=proof(sub_a))["sealed"]
    real = next(
        r for r in box_rows(cfg) if r["kind"] == "seal" and r.get("subject") == sub_a
    )
    forge(
        cfg,
        "seal",
        where=b["subject"],
        subject=sub_a,
        proof=real["proof"],
        wager=b["subject"],
        outcome=out,
    )
    assert seal_tip(cfg, last_tip(cfg))["sealed"]
    rep = api.reconcile(cfg, human_key=key)
    assert wager_of(rep, "a")["state"] == "reconciled"
    assert wager_of(rep, "b")["state"] == "escalate" and "brier" not in wager_of(
        rep, "b"
    )


def test_J1_forecast_refuses_bad_mass_duplicate_path_and_reused_id(tmp_path):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    assert api.forecast(cfg, "ok", [{"path": "x", "p": 1.0}])["code"] == 0
    for wid, dist in (
        ("m", [{"path": "x", "p": 0.6}, {"path": "y", "p": 0.5}]),
        ("d", [{"path": "x", "p": 0.5}, {"path": "x", "p": 0.5}]),
        ("ok", [{"path": "z", "p": 1.0}]),
        ("n", [{"path": "x", "p": -0.1}, {"path": "y", "p": 1.1}]),
        ("e", []),
    ):
        before = len(box_rows(cfg))
        res = api.forecast(cfg, wid, dist)
        assert res["code"] != 0, (wid, res)
        added = box_rows(cfg)[before:]
        assert [r["kind"] for r in added if r["kind"] not in ("invocation",)] == [
            "refused"
        ]


def test_J1_reconcile_refuses_a_human_key_inside_the_box_or_world_readable(tmp_path):
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    inside = cfg.box / "human.hex"
    inside.write_text(HUMAN_KEY.hex())
    inside.chmod(0o600)
    assert "refused" in api.reconcile(cfg, human_key=inside) or api.reconcile(
        cfg, human_key=inside
    ).get("code") not in (0, None)
    key.chmod(0o644)
    res = api.reconcile(cfg, human_key=key)
    assert res.get("code") not in (0, None) and "wagers" not in res


def test_J2_engine_random_restored_after_a_raise_and_below_zero_refused():
    from the_table.dice_source import _engine_class

    Engine = _engine_class()
    g = Engine.roll.__globals__
    before = g["random"]

    class Boom:
        def randint(self, a, b):
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"), rolled_with(Boom(), Engine()):
        Engine().roll("Grit")
    assert g["random"] is before
    s = Stream.from_seed(beacon_seed("w4:j2"))
    for k in (0, -1):
        with pytest.raises(ValueError):
            s.below(k)


def test_J2_a_story_on_the_stream_leaves_engine_state_json_untouched():
    state = REPOS / "safe-app-store" / "apps" / "game" / "engine_state.json"
    before = state.read_bytes() if state.exists() else None
    w1.play_to_decision(world_path(), beacon_seed("w4:j2state"))
    assert (state.read_bytes() if state.exists() else None) == before


def test_J3_a_world_opening_on_a_decision_is_no_forecast(tmp_path):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    w = copy.deepcopy(load_world(world_path()))
    beats = w["scenes"][0]["beats"]
    w["scenes"][0]["beats"] = [b for b in beats if b["kind"] != "action"] or beats[-1:]
    assert not peaks.action_beats(w)
    with pytest.raises(ValueError):
        peaks.distribution(w)
    before = len(box_rows(cfg))
    assert (
        api.forecast(cfg, "f", [{"path": "", "p": 1.0}], table=peaks.world_key(w))[
            "code"
        ]
        != 0
    )
    assert not [r for r in box_rows(cfg)[before:] if r["kind"] == "wager"]


def test_J4_a_hand_written_seal_row_never_advances_the_story(tmp_path):
    out = table_loop(tmp_path, beacon_seed("w4:j4"))
    cfg = out["cfg"]
    forge(cfg, "seal", where=out["beat"], subject=out["beat"], proof="human")
    assert table.beat_seal(cfg, out["beat"])["state"] == "unsealed"
    with pytest.raises(osk.BeatNotSealed):
        out["sink"].apply_beat_seal(out["s"], out["pending"], out["beat"])
    assert out["s"].pending_seal() == out["pending"]


def test_J4_a_verdict_row_carries_no_person_and_refuses_an_unverified_table(tmp_path):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    w = copy.deepcopy(load_world(world_path()))
    names = []
    for c in w["characters"]:
        if c.get("seat"):
            c["name"] = f"Sean Player{len(names)}"
            names.append(c["name"])
    wp = tmp_path / "named.json"
    wp.write_text(json.dumps(w))
    play_table(cfg, wp, beacon_seed("w4:j4n"))
    text = json.dumps([r for r in box_rows(cfg) if r["kind"] == "verdict"])
    assert names and not any(n.split()[0] in text or n in text for n in names)
    bad = table.verdict(
        cfg,
        {"what": "roll", "session": "x", "turn": 0},
        identity={"who": "table", "family": "python", "sig": "00" * 32},
    )
    assert bad["code"] == 1 and "refused" in bad
    keys = json.loads(cfg.keys.read_text())
    keys.pop("table")
    cfg.keys.write_text(json.dumps(keys))
    assert table.verdict(cfg, {"what": "roll", "session": "x", "turn": 0})["code"] == 1


def test_J5_forged_or_edited_lore_proposals_serve_no_lore_and_training_lore_is_struck(
    tmp_path,
):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    # (a) a forged seal over a world proposal: no lore
    card = api.scope(cfg, by=("who",), match={"who": "run"})
    api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))
    ids = [
        t["id"] for t in api.serve(cfg, card["spec"], max_chars=CAP)["doc"]["tables"]
    ]
    (p,) = api.take_proposals(
        cfg,
        [
            json.dumps(
                {
                    "path": "world/forged.md",
                    "data": "- the moon is a lamp\n",
                    "cites": ids[:1],
                    "claim": "x",
                }
            )
        ],
    )["out"]["proposals"]
    forge(cfg, "seal", where=p["subject"], subject=p["subject"])
    assert api.lore(cfg, p["subject"])["code"] != 0
    # (b) a real seal, lore made, then the proposal data edited and re-chained
    lo = seal_lore(cfg)
    assert lo["lore"]["code"] == 0
    doc = serve_by(cfg, by=("what",), match={"what": "lore"}, tables=False)
    assert doc["state"] == "populated" and "overtime" in json.dumps(doc)
    rows = box_rows(cfg)
    for r in rows:
        if r["kind"] == "proposal" and r.get("subject") == lo["subject"]:
            r["data"] = r["data"].replace("overtime", "salary")
    write_rows(cfg, rows)
    card = api.scope(cfg, by=("what",), match={"what": "lore"})
    api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))
    doc = api.serve(cfg, card["spec"], max_chars=CAP)["doc"]
    assert "overtime" not in json.dumps(doc) and "salary" not in json.dumps(doc)
    # (c) training lore over boxes without it: struck
    out = table_loop(tmp_path / "c", beacon_seed("w4:j5"))
    boxes = tb.served_boxes(serve_by(out["cfg"]))
    r = tb.narrate(boxes, say=lambda q: honest_say(q) + " the palantír glows.")
    assert r["struck"] and r["source"] == "code"


def test_J6_two_verdicts_for_one_turn_are_conflicting(tmp_path):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    play_table(
        cfg,
        w3.set_piece_world(tmp_path),
        beacon_seed("w4:j6"),
        session_id="s",
        pick=FakePick("act:Weird", "act:Grit"),
    )
    r0 = next(r for r in box_rows(cfg) if r.get("what") == "roll")
    other = 12 if r0["total"] != 12 else 3
    table.verdict(
        cfg,
        {
            "what": "roll",
            "session": "s",
            "turn": r0["turn"],
            "total": other,
            "verdict": bucket(other),
            "path": bucket(other),
            "seat": r0["seat"],
        },
    )
    serve_by(cfg, by=("what",), match={"what": "verdict"}, tables=False)
    res = api.escalate(cfg, f"table.roll: turn {r0['turn']}", rung=never)
    assert res["d0"] == {"status": "escalate", "reason": "conflicting_field"}
    assert res["card"]["route"] == "willow"


def _cut_ledger(db: str, k: int) -> None:
    con = sqlite3.connect(db)
    ids = [
        x[0]
        for x in con.execute("SELECT id FROM ledger ORDER BY id DESC LIMIT ?", (k,))
    ]
    con.executemany("DELETE FROM ledger WHERE id=?", [(i,) for i in ids])
    con.commit()
    con.close()


def _rehash_ledger(db: str, row_id: int, note: str) -> None:
    con = sqlite3.connect(db)
    con.execute("UPDATE ledger SET note=? WHERE id=?", (note, row_id))
    prev = "genesis"
    for rid, ts, sess, kind, nt, st in con.execute(
        "SELECT id, ts, session, kind, note, state FROM ledger ORDER BY id"
    ).fetchall():
        h = _row_hash(rid, ts, sess, kind, nt, st, prev)
        con.execute("UPDATE ledger SET prev_hash=?, hash=? WHERE id=?", (prev, h, rid))
        prev = h
    con.commit()
    con.close()


@pytest.fixture
def anchored(tmp_path):
    """A table box whose campaign.db head is anchored and sealed under a tip."""
    ledger = LedgerSink(str(tmp_path / "campaign"))
    out = table_loop(tmp_path, beacon_seed("w4:j9"), ledger=ledger)
    closed = close_loop(out)
    assert closed["w"]["state"] == "reconciled"
    ledger.close()
    ah = table.agm_head(out["cfg"], **agm_head.row(ledger.db_path))
    assert seal_tip(out["cfg"], ah["tip"])["sealed"]
    out["db"] = ledger.db_path
    assert (
        table.agm_check(out["cfg"], agm_head.reader(out["db"]), human_key=out["key"])[
            "state"
        ]
        == "satisfied"
    )
    return out


def test_J9_cut_ledger_rows_are_failing_fewer_than_anchored(anchored):
    _cut_ledger(anchored["db"], 2)
    chk = table.agm_check(
        anchored["cfg"], agm_head.reader(anchored["db"]), human_key=anchored["key"]
    )
    assert chk["state"] == "failing" and "fewer rows than anchored" in chk["why"]


def test_J9_a_rewritten_ledger_row_rehashed_forward_is_failing(anchored):
    _rehash_ledger(anchored["db"], 2, "forged and re-hashed")
    chk = table.agm_check(
        anchored["cfg"], agm_head.reader(anchored["db"]), human_key=anchored["key"]
    )
    assert chk["state"] == "failing"


def test_J9_cut_onescript_rows_after_a_sealed_tip_is_seen_on_the_morning_screen(
    anchored,
):
    cfg, key = anchored["cfg"], anchored["key"]
    rows = box_rows(cfg)
    agm = next(r["n"] for r in rows if r.get("what") == "agm_head")
    (cfg.box / "record.jsonl").write_text(
        "".join(record.canon(r) + "\n" for r in rows[:agm])
    )
    run, _ = api._open(cfg, "needs", ("needs",))
    assert reverse.covered_through(run.rec, HUMAN_KEY) is None
    co = api.checkout(cfg, human_key=key)
    assert "wager f1 escalate to human · the record is broken" in co["screen"]


def test_J9_a_cut_with_no_tip_after_it_is_still_unseen_A7_pinned(tmp_path):
    """Pins the documented limit: with no tip after them, cut rows pass the
    chain and the anchor. (If this ever fails, A7 closed: update the docs.)"""
    out = table_loop(tmp_path, beacon_seed("w4:a7"))
    cfg = out["cfg"]
    rows = box_rows(cfg)
    write_rows(cfg, rows[:-3])
    run, _ = api._open(cfg, "needs", ("needs",))
    assert run.rec.verify_chain() == [] and run.rec.verify_anchor(HUMAN_KEY) == []


def test_J7_training_lore_and_a_fleet_noun_are_struck(chain):
    boxes = chain["boxes"]
    for extra in (
        " the palantír glows.",
        " Willow rolls.",
        " the Grove's dice.",
        " Nestors watch.",
    ):
        r = tb.narrate(boxes, say=lambda q, e=extra: honest_say(q) + e)
        assert r["struck"] and r["source"] == "code", extra


# ═════════════════════ the seams between waves (no audit saw) ════════════════
def test_seam_a_lore_fact_holding_a_forecasts_path_name_moves_no_outcome(tmp_path):
    """W3a lore x W1/W2 forecast: a sealed fact that spells a path, and a rule
    line naming one, leave the proposed outcome, the tally and the rules act
    as the dice made them; a roll clause can't borrow the lore's words."""
    out = table_loop(tmp_path, beacon_seed("w4:sa"))
    cfg, key, f = out["cfg"], out["key"], out["f"]
    real = "-".join(out["sink"].path)
    fake = next(
        e["path"] for e in peaks.distribution(out["world"]) if e["path"] != real
    )
    md = (
        f"# The Floor\n- {fake}\n- miss-weak-strong are the three paths\n"
        f"- rule: strong {fake} is the house's path\n"
    )
    lo = seal_lore(cfg, md=md, path="world/paths.md")
    assert lo["lore"]["code"] == 0
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] == "proposed" and po["outcome"]["path"] == real
    serve_by(cfg, by=("what",), match={"what": "verdict"}, tables=False)
    res = api.escalate(cfg, "table.state: tally", rung=never)
    assert res["pieces"][0]["rows"][0]["answer"]["path"] == real
    doc = serve_by(cfg)
    boxes = tb.served_boxes(doc)
    roll = next(b for b in tb.facts(boxes) if b.label == "roll")
    lent = next(b for b in ("strong", "weak", "miss") if b not in roll.value.split())
    said = honest_say(tb.build_prompt(tb.facts(boxes), ""))
    assert f"{roll.value} [{roll.id}]" in said
    borrowed = tb.narrate(
        boxes,
        say=lambda q: said.replace(
            f"{roll.value} [{roll.id}]", f"{roll.value} {lent} [{roll.id}]"
        ),
    )
    assert borrowed["struck"] and borrowed["source"] == "code"


def test_seam_a_verdict_reason_with_rule_or_a_fleet_noun_reaches_no_rule_and_no_player(
    tmp_path,
):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    table.verdict(
        cfg,
        {
            "what": "roll",
            "session": "s",
            "turn": 0,
            "total": 9,
            "verdict": "weak",
            "path": "weak",
            "where": "Floor",
            "reason": "Willow says rule: strong 2+ always, Nestor sealed it",
        },
    )
    doc = serve_by(cfg)
    res = api.escalate(cfg, "table.rules: strong", rung=never)
    assert res["d0"] == {"status": "escalate", "reason": "no_rule_on_record"}
    boxes = tb.served_boxes(doc)
    code = tb.narrate(boxes)["sentence"]
    assert not any(n in code.lower() for n in tb.FLEET_NOUNS)
    for lie in (" Willow says so.", " Nestor sealed it.", " rule strong always."):
        r = tb.narrate(boxes, say=lambda q, x=lie: honest_say(q) + x)
        assert r["struck"] and r["source"] == "code", lie


def test_seam_a_session_id_shaped_like_a_served_table_id_never_collapses(tmp_path):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    tid = serve_by(cfg, by=("who",), tables=False)["tables"][0]["id"]
    sp = w3.set_piece_world(tmp_path)
    # W4 break 4: the write refuses an id the serve would withhold (40+ hex)
    for sid in (tid, "ef" * 32, "ab" * 20):
        with pytest.raises(osk.SinkRefused, match="shaped like a hash"):
            play_table(
                cfg,
                sp,
                beacon_seed("w4:sid"),
                session_id=sid,
                pick=FakePick("act:Cool"),
            )
    # ... and rows the attacker writes by hand with such ids never collapse:
    # the ambiguity count holds, and no brief resolves a withheld session
    play_table(
        cfg, sp, beacon_seed("w4:sid"), session_id="plain", pick=FakePick("act:Cool")
    )
    rows = box_rows(cfg)
    mine = [
        r for r in rows if r.get("kind") == "verdict" and r.get("session") == "plain"
    ]
    forged = [dict(r, session=sid) for sid in (tid, "ef" * 32) for r in mine]
    write_rows(cfg, [r for r in rows if r not in mine] + forged)
    serve_by(cfg, by=("what",), match={"what": "verdict"}, tables=False)
    for task in ("table.state: tally", "table.roll: turn 0"):
        res = api.escalate(cfg, task, rung=never)
        assert res["d0"] == {"status": "escalate", "reason": "ambiguous_session"}, (
            task,
            res["d0"],
        )
    res = api.escalate(cfg, f"table.state: tally session {tid}", rung=never)
    assert res["d0"]["status"] == "escalate"


def test_seam_reseeding_mid_session_gets_no_outcome(tmp_path):
    seed_b = beacon_seed("w4:reseed:B")

    class Reseed:
        n = 0

        def __call__(self, game, seat):
            if self.n == 1:
                game._rng = StreamRandom.from_seed(seed_b)
            self.n += 1
            return ("act", game.observe(seat).view["suggests"])

    out = table_loop(tmp_path, beacon_seed("w4:reseed:A"), policy=Reseed())
    assert (
        replay_box(box_rows(out["cfg"]), out["seed"], out["world"]) != []
    )  # the record shows it
    po = table.outcome_from_verdicts(
        out["cfg"], out["f"]["subject"], human_key=out["key"]
    )
    assert po["state"] != "proposed", po


def test_seam_a_seed_ground_after_the_forecast_scores_nothing(tmp_path):
    world = load_world(world_path())
    exact = peaks.distribution(world)
    rare = min(exact, key=lambda e: e["p"])["path"]
    sharp = [
        {
            "path": e["path"],
            "p": 0.9 if e["path"] == rare else 0.1 / (len(exact) - 1),
            "band": "likely",
        }
        for e in exact
    ]
    ground = next(
        beacon_seed(f"w4:grind:{i}")
        for i in range(5000)
        if w1.play_to_decision(world_path(), beacon_seed(f"w4:grind:{i}"))[1] == rare
    )
    # the round's randomness is fixed when the forecast is made; the grinder
    # then plays the seed it found offline instead (W4 break 1)
    out = table_loop(
        tmp_path, beacon_seed("w4:grind:the-round"), dist=sharp, play_seed=ground
    )
    closed = close_loop(out)
    assert closed["w"] is None or closed["w"]["state"] != "reconciled", closed["w"]
    assert closed["po"]["state"] == "escalate" and "not round" in closed["po"]["reason"]


def test_seam_verdict_labels_that_disagree_with_their_own_dice_get_no_outcome(tmp_path):
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)

    def lying(row):
        if row.get("what") == "roll":
            n = len(row["path"].split("-"))
            row = dict(row, total=12, verdict="strong", path="-".join(["strong"] * n))
        return table.verdict(cfg, row)

    api.checkin(cfg)
    world = load_world(world_path())
    f = forecast_table(cfg, world, seed=beacon_seed("w4:lie:1"))
    assert seal_tip(cfg, f["tip"])["sealed"]
    _s, sink, pending, _ = play_table(
        cfg, world_path(), beacon_seed("w4:lie:1"), forecast=f["subject"], write=lying
    )
    sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    rows = box_rows(cfg)
    assert any(
        r.get("total") != r["roll"]["result"] for r in rows if r.get("what") == "roll"
    )
    po = table.outcome_from_verdicts(cfg, f["subject"], human_key=key)
    assert po["state"] != "proposed", po


def test_seam_a_forecast_survives_a_lore_change_after_sealing_and_rules_conflict(
    tmp_path,
):
    """W3a lore x W1 forecast: lore re-sealed with another rule after the tip
    neither moves the outcome nor silently picks a rule; an edited world file
    (another stat sheet) supplies no outcome (S2)."""
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    seal_lore(cfg)
    world = load_world(world_path())
    f = forecast_table(cfg, world, seed=beacon_seed("w4:lorechg"))
    assert seal_tip(cfg, f["tip"])["sealed"]
    seal_lore(
        cfg,
        md="# The Floor\n- rule: weak 7-9 the floor gives way\n",
        path="world/hasbeen-v2.md",
    )
    _s, sink, pending, _ = play_table(
        cfg, world_path(), beacon_seed("w4:lorechg"), forecast=f["subject"]
    )
    sink.decision(pending, lambda p, c: table.propose_beat(cfg, p, c))
    out = close_loop({"cfg": cfg, "key": key, "f": f})
    assert out["w"]["state"] == "reconciled"
    serve_by(cfg, by=("what",), match={"what": "lore"}, tables=False)
    res = api.escalate(cfg, "table.rules: weak", rung=never)
    assert res["d0"] == {"status": "escalate", "reason": "conflicting_field"}
    # the world's stat sheets edited after the forecast: no outcome from it
    w2 = copy.deepcopy(world)
    for c in w2["characters"]:
        if c.get("seat") and isinstance(c.get("stats"), dict):
            c["stats"] = {k: v + 1 for k, v in c["stats"].items()}
            break
    else:
        w2["base_stat"] = {k: v + 1 for k, v in w2["base_stat"].items()}
    assert peaks.world_key(w2) != peaks.world_key(world)
    wp2 = tmp_path / "hasbeen-edited.json"
    wp2.write_text(json.dumps(w2))
    cfg2, key2 = make_cfg(tmp_path / "e"), make_key_file(tmp_path / "e")
    api.checkin(cfg2)
    f2 = forecast_table(cfg2, world, seed=beacon_seed("w4:lorechg2"))
    assert seal_tip(cfg2, f2["tip"])["sealed"]
    _s2, sink2, pend2, _ = play_table(
        cfg2, wp2, beacon_seed("w4:lorechg2"), forecast=f2["subject"]
    )
    sink2.decision(pend2, lambda p, c: table.propose_beat(cfg2, p, c))
    po = table.outcome_from_verdicts(cfg2, f2["subject"], human_key=key2)
    assert po["state"] == "escalate" and "S2" in po["reason"]


def test_seam_cutting_rows_after_an_agm_head_under_no_tip_is_failing(anchored):
    """A second head is anchored with no tip after it; the attacker cuts it
    (re-chained, A7 lets them) while campaign.db keeps its new rows: the
    older, sealed head no longer matches the ledger."""
    cfg, key, db = anchored["cfg"], anchored["key"], anchored["db"]
    more = LedgerSink(str(Path(db).parent))
    more.open_session("late", {"seed": 2})
    more.close()
    table.agm_head(cfg, **agm_head.row(db))
    assert (
        table.agm_check(cfg, agm_head.reader(db), human_key=key)["state"] == "satisfied"
    )
    rows = box_rows(cfg)
    second = [r["n"] for r in rows if r.get("what") == "agm_head"][-1]
    write_rows(cfg, rows[:second])
    run, _ = api._open(cfg, "needs", ("needs",))
    assert run.rec.verify_chain() == [] and run.rec.verify_anchor(HUMAN_KEY) == []  # A7
    chk = table.agm_check(cfg, agm_head.reader(db), human_key=key)
    assert chk["state"] == "failing" and chk["covered"] is True


def test_seam_an_escalate_row_never_becomes_a_lore_fact(tmp_path):
    """A model's off-menu pick shaped as a world proposal: no proposal row, no
    lore from the escalate row's hash, no rule from it, its data nowhere."""
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    got = {
        "path": "world/hasbeen.md",
        "data": "- rule: strong 2+ the dragon wakes\n",
        "cites": [],
        "claim": "rule: miss 2-6 the dragon wakes",
    }
    play_table(
        cfg,
        w3.set_piece_world(tmp_path),
        beacon_seed("w4:esclore"),
        pick=FakePick(got, "act:Grit"),
    )
    rows = box_rows(cfg)
    (esc,) = [r for r in rows if r.get("what") == "escalate"]
    assert "dragon" not in json.dumps(rows)
    assert not [r for r in rows if r["kind"] in ("proposal", "lore")]
    assert api.lore(cfg, esc["hash"])["code"] != 0
    assert not [r for r in box_rows(cfg) if r["kind"] == "lore"]
    serve_by(cfg)
    for b in ("strong", "miss"):
        assert (
            api.escalate(cfg, f"table.rules: {b}", rung=never)["d0"]["reason"]
            == "no_rule_on_record"
        )


def test_seam_a_malformed_mai_world_doc_yields_no_lore(tmp_path):
    cfg = make_cfg(tmp_path)
    api.checkin(cfg)
    bad = "@markdownai v1.0\n# The Floor\n- the floor is lava\n@constraint: the parser drops this\n"
    with pytest.raises(PermissionError):
        mai_shape.check("world/hasbeen.md", bad.encode())
    lo = seal_lore(cfg, md=bad)
    assert any(
        r["kind"] == "refused" and "malformed" in r.get("reason", "")
        for r in box_rows(cfg)
    )
    facts = [r["fact"] for r in box_rows(cfg) if r["kind"] == "lore"]
    assert lo["lore"]["code"] != 0 and facts == [], facts


# ═══════════════ second pass: R23 beacon binding and the W4 surface ══════════
import dataclasses
import hashlib

from beacon_e2e import NOW
from onescript import beacon


def _fresh(tmp: Path):
    cfg, key = make_cfg(tmp), make_key_file(tmp)
    assert api.checkin(cfg)["code"] == 0
    return cfg, key


def _sharp(dist: list[dict], on: str) -> list[dict]:
    return [
        {
            "path": e["path"],
            "p": 0.9 if e["path"] == on else 0.1 / (len(dist) - 1),
            "band": "likely",
        }
        for e in dist
    ]


def _play_and_propose(cfg, key, f, seed, **kw):
    _s, sink, pend, _ = play_table(cfg, world_path(), seed, forecast=f["subject"], **kw)
    sink.decision(pend, lambda p, c: table.propose_beat(cfg, p, c))
    return sink, table.outcome_from_verdicts(cfg, f["subject"], human_key=key)


def _human_seals(cfg, f, path):
    sub = reverse.outcome_subject(f["subject"], {"path": path})
    so = api.seal_outcome(cfg, f["subject"], {"path": path}, proof=proof(sub))
    assert so["sealed"]
    assert seal_tip(cfg, so["tip"])["sealed"]


def test_R23_a_round_already_out_at_forecast_time_is_refused(tmp_path):
    cfg, _ = _fresh(tmp_path)
    world = load_world(world_path())
    now = beacon.round_at(NOW)
    for rnd in (now - 5, now, 0, -1, True, "6558900"):
        before = len(box_rows(cfg))
        res = api.forecast(
            cfg,
            f"f{rnd}",
            peaks.distribution(world),
            table={**peaks.world_key(world), "beacon_round": rnd},
        )
        assert res["code"] != 0, rnd
        assert not [r for r in box_rows(cfg)[before:] if r["kind"] == "wager"]


def test_R23_a_round_that_fires_before_the_tip_seal_gets_no_outcome(tmp_path):
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    seed = beacon_seed("w4b:early")
    rnd = beacon.round_at(NOW) + 2  # fires 60 s after the forecast
    cfg.beacon.rounds[rnd] = seed
    f = api.forecast(
        cfg,
        "f1",
        peaks.distribution(world),
        table={**peaks.world_key(world), "beacon_round": rnd},
    )
    assert f["code"] == 0
    late = dataclasses.replace(
        cfg, now="2026-10-17T00:05:00Z"
    )  # the human seals 5 min on
    assert seal_tip(late, f["tip"])["sealed"]
    _, po = _play_and_propose(late, key, f, seed)
    assert po["state"] == "escalate" and "not after the tip seal" in po["reason"]


def test_R23_a_skewed_box_clock_cannot_forecast_a_round_already_fired(tmp_path):
    cfg, key = _fresh(tmp_path)
    skew = dataclasses.replace(cfg, now="2026-01-01T00:00:00Z")
    world = load_world(world_path())
    dist = peaks.distribution(world)
    rare = min(dist, key=lambda e: e["p"])["path"]
    start = beacon.round_at("2026-01-01T00:00:00Z") + 1
    history = (
        (r, hashlib.sha256(f"drand:{r}".encode()).hexdigest())
        for r in range(start, start + 20000)
    )  # rounds the real drand has fired
    rnd, rr = next(
        (r, x) for r, x in history if w1.play_to_decision(world_path(), x)[1] == rare
    )
    assert beacon.round_time(rnd) < beacon.epoch(NOW)  # out months before today
    skew.beacon.rounds[rnd] = rr  # the reader can read it now
    f = api.forecast(
        skew,
        "f1",
        _sharp(dist, rare),
        table={**peaks.world_key(world), "beacon_round": rnd},
    )
    if f["code"] != 0:
        return  # refused at the door: held
    assert seal_tip(skew, f["tip"])["sealed"]
    _, po = _play_and_propose(skew, key, f, rr)
    if po["state"] == "proposed":
        _human_seals(skew, f, po["outcome"]["path"])
    w = wager_of(api.reconcile(skew, human_key=key))
    assert w["state"] != "reconciled", w


def test_R23_two_forecasts_on_one_round_are_both_graded(tmp_path):
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    dist = peaks.distribution(world)
    seed = beacon_seed("w4b:two")
    played = w1.play_to_decision(world_path(), seed)[1]
    other = next(e["path"] for e in dist if e["path"] != played)
    rnd = cfg.beacon.commit(seed)
    tk = {**peaks.world_key(world), "beacon_round": rnd}
    fa = api.forecast(cfg, "fa", _sharp(dist, played), table=tk)
    fb = api.forecast(cfg, "fb", _sharp(dist, other), table=tk)
    if fb["code"] != 0:
        return  # one forecast per round: held
    assert seal_tip(cfg, fb["tip"])["sealed"]
    _, po = _play_and_propose(cfg, key, fa, seed)
    assert po["state"] == "proposed" and po["outcome"]["path"] == played
    _human_seals(cfg, fa, played)
    _human_seals(cfg, fb, played)  # the human seals what the round's dice did
    rep = api.reconcile(cfg, human_key=key)
    assert wager_of(rep, "fa")["state"] == "reconciled"
    assert wager_of(rep, "fb")["state"] == "reconciled", wager_of(rep, "fb")


def test_R23_a_round_that_never_fires_is_unreachable_never_graded(tmp_path):
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    rnd = beacon.round_at(NOW) + 10**6
    f = api.forecast(
        cfg,
        "f1",
        peaks.distribution(world),
        table={**peaks.world_key(world), "beacon_round": rnd},
    )
    assert f["code"] == 0 and seal_tip(cfg, f["tip"])["sealed"]
    sink, po = _play_and_propose(cfg, key, f, beacon_seed("w4b:never"))
    assert po["state"] == "unreachable"
    _human_seals(cfg, f, "-".join(sink.path))
    w = wager_of(api.reconcile(cfg, human_key=key))
    assert w["state"] != "reconciled" and "brier" not in w


def test_R23_the_right_round_with_another_rounds_randomness_escalates(tmp_path):
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    r1 = cfg.beacon.commit(beacon_seed("w4b:r1"))
    cfg.beacon.commit(beacon_seed("w4b:r2"))
    f = api.forecast(
        cfg,
        "f1",
        peaks.distribution(world),
        table={**peaks.world_key(world), "beacon_round": r1},
    )
    assert seal_tip(cfg, f["tip"])["sealed"]
    _, po = _play_and_propose(cfg, key, f, beacon_seed("w4b:r2"))
    assert po["state"] == "escalate" and f"not round {r1}'s" in po["reason"]


def test_R23_a_lying_reader_in_the_operators_config_is_said_on_the_proposal(tmp_path):
    """The reader is the operator's (R23): a lying one wins by design, and every
    proposal says BLS was not checked (T10)."""
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    f = forecast_table(cfg, world, seed=beacon_seed("w4b:honest"))
    assert seal_tip(cfg, f["tip"])["sealed"]
    ground = beacon_seed("w4b:ground")
    lying = dataclasses.replace(cfg, beacon=lambda r: {"randomness": ground})
    _, po = _play_and_propose(lying, key, f, ground)
    assert po["state"] == "proposed"
    assert po["beacon"]["bls"] == beacon.BLS_UNVERIFIED
    _, honest = (None, table.outcome_from_verdicts(cfg, f["subject"], human_key=key))
    assert honest["state"] == "escalate"


def test_R23_a_caller_cannot_replace_the_beacon_check(tmp_path):
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    f = forecast_table(cfg, world, seed=beacon_seed("w4b:hook"))
    assert seal_tip(cfg, f["tip"])["sealed"]
    ground = beacon_seed("w4b:hook:ground")
    sink, po = _play_and_propose(cfg, key, f, ground)
    assert po["state"] == "escalate"
    _human_seals(cfg, f, "-".join(sink.path))
    assert wager_of(api.reconcile(cfg, human_key=key))["state"] == "escalate"
    kb = HUMAN_KEY
    for basis in (
        lambda w, r, o: None,
        table.basis(kb, lambda r: {"randomness": ground}),
    ):
        assert (
            wager_of(api.reconcile(cfg, human_key=key, basis=basis))["state"]
            != "reconciled"
        )
        lines = api.peek(cfg, human_key=key, basis=basis)["needs"]
        assert not [x for x in lines if x.startswith("wager f1 reconciled")]


def _forged_session(tmp_path, tamper, label):
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    seed = beacon_seed(label)
    f = forecast_table(cfg, world, seed=seed)
    assert seal_tip(cfg, f["tip"])["sealed"]
    st = {"at": 0, "k": 0}

    def write(row):
        if row.get("what") == "roll":
            row = tamper(row, st)
        return table.verdict(cfg, row)

    _, po = _play_and_propose(cfg, key, f, seed, write=write)
    return cfg, seed, world, po


def test_R23_a_counter_gap_hidden_by_a_forged_roll_record_gets_no_outcome(tmp_path):
    def forge_second(row, st):
        st["k"] += 1
        roll = dict(row["roll"])
        if st["k"] == 2:
            roll.update(result=12, counter_before=st["at"], counter=st["at"] + 2)
            head = row["path"].split("-")[:-1]
            row = dict(
                row,
                roll=roll,
                total=12,
                verdict="strong",
                path="-".join([*head, "strong"]),
            )
        st["at"] = roll["counter"]
        return row

    cfg, seed, world, po = _forged_session(tmp_path, forge_second, "w4b:gap")
    assert replay_box(box_rows(cfg), seed, world) != []  # the beacon shows it
    assert po["state"] != "proposed", po


def test_R23_legacy_generator_rows_get_no_outcome(tmp_path):
    cfg, seed, world, po = _forged_session(
        tmp_path,
        lambda row, st: dict(row, roll=dict(row["roll"], generator_id="random/global")),
        "w4b:legacy",
    )
    assert replay_box(box_rows(cfg), seed, world) != []
    assert po["state"] != "proposed", po


def test_R23_a_creator_roll_mid_session_is_a_counter_gap(tmp_path):
    from the_table.dice_source import _engine_class

    class Creator:
        n = 0

        def __call__(self, game, seat):
            if self.n == 1:
                e = _engine_class()()
                e.stats = {}
                with rolled_with(game._rng, e):
                    e.roll("Grit", is_creator=True)  # draws, writes no row
            self.n += 1
            return ("act", game.observe(seat).view["suggests"])

    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    seed = beacon_seed("w4b:creator")
    f = forecast_table(cfg, world, seed=seed)
    assert seal_tip(cfg, f["tip"])["sealed"]
    _, po = _play_and_propose(cfg, key, f, seed, policy=Creator())
    assert po["state"] == "escalate" and "gap" in po["reason"]


def _snapshot(root: Path) -> dict:
    return {
        str(p): (
            p.is_dir(),
            p.stat().st_mtime_ns,
            hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None,
        )
        for p in sorted(root.rglob("*"))
    }


def test_peek_writes_nothing_and_shows_only_what_the_record_holds(tmp_path):
    out = table_loop(tmp_path / "a", beacon_seed("w4b:peek"))
    cfg, key = out["cfg"], out["key"]
    close_loop(out)
    states = []
    for kw in ({"human_key": key}, {}):
        before = _snapshot(tmp_path)
        states.append(api.peek(cfg, **kw))
        assert _snapshot(tmp_path) == before
    assert any(x.startswith("wager f1 reconciled") for x in states[0]["needs"])
    assert not any(
        x.startswith("wager f1 reconciled") for x in states[1]["needs"]
    )  # no key
    rows = box_rows(cfg)
    rows[5]["bite"] = "edited"
    (cfg.box / "record.jsonl").write_text("".join(record.canon(r) + "\n" for r in rows))
    before = _snapshot(tmp_path)
    lines = api.peek(cfg, human_key=key)["needs"]
    assert _snapshot(tmp_path) == before
    assert any(x.startswith("table unreachable") for x in lines)
    assert not any("reconciled" in x for x in lines)
    inside = cfg.box / "k.hex"
    inside.write_text(key.read_text())
    inside.chmod(0o600)
    before = _snapshot(tmp_path)
    assert api.peek(cfg, human_key=inside)["code"] == 2
    assert _snapshot(tmp_path) == before
    empty = make_cfg(tmp_path / "e")
    before = _snapshot(tmp_path)
    assert api.peek(empty).get("empty") is True
    assert _snapshot(tmp_path) == before


def test_peek_with_no_keys_file_writes_nothing(tmp_path):
    out = table_loop(tmp_path, beacon_seed("w4b:peek:keys"))
    cfg = out["cfg"]
    os.remove(cfg.keys)
    before = _snapshot(tmp_path)
    api.peek(cfg)
    assert _snapshot(tmp_path) == before and not cfg.keys.exists()


def test_peek_of_an_honest_table_box_on_the_default_seat_keys_raises_no_alarm(tmp_path):
    table_box = table_loop(tmp_path / "t", beacon_seed("w4b:tb"))
    close_loop(table_box)
    seat = table_loop(tmp_path / "s", beacon_seed("w4b:seat"))
    close_loop(seat)
    sys.path.insert(0, str(GROVE))
    from grove import seat_cli

    class _Bot:
        api = api

    try:
        tcfg = seat_cli.table_config(
            _Bot,
            tmp_path / "root",
            environ={"GROVE_SEAT_TABLE_BOX": str(table_box["cfg"].box)},
        )
    except Exception:  # noqa: BLE001 - the seat's own config path may need more
        tcfg = None
    if tcfg is not None:
        assert (
            tcfg.keys != seat["cfg"].keys
        )  # the default is the table's OWN, never the seat's
    assert tcfg is not None and tcfg.keys == table_box["cfg"].keys  # its OWN keys
    lines = api.peek(tcfg, human_key=table_box["key"])["needs"]
    assert not [
        x for x in lines if "rewritten" in x or x.startswith("table unreachable")
    ], lines


def test_scrub_keeps_the_honest_hashes_the_table_prints(tmp_path):
    sys.path.insert(0, str(GROVE))
    from grove.seat_record import scrub

    ledger = LedgerSink(str(tmp_path / "campaign"))
    out = table_loop(tmp_path, beacon_seed("w4b:scrub"), ledger=ledger)
    close_loop(out)
    ledger.close()
    cfg, key = out["cfg"], out["key"]
    ah = table.agm_head(cfg, **agm_head.row(ledger.db_path))
    assert seal_tip(cfg, ah["tip"])["sealed"]
    more = LedgerSink(str(Path(ledger.db_path).parent))
    more.open_session("late", {"seed": 2})
    more.close()
    rd = agm_head.reader(ledger.db_path)
    lines = api.needs(cfg, read_head=rd)["needs"]
    (agm,) = [x for x in lines if x.startswith("table agm_head failing")]
    heads = [h for h in __import__("re").findall(r"[0-9a-f]{64}", agm)]
    assert len(heads) == 2
    secrets = (key.read_text().strip(),)
    shown = scrub(" ".join(agm.split()), secrets)
    assert all(h in shown for h in heads), shown
    # the record's own subjects survive where they are named as such
    t = last_tip(cfg)
    assert scrub(t, secrets) == t and scrub(
        f"forecast {out['f']['subject']}", secrets
    ).endswith(out["f"]["subject"])


def test_scrub_withholds_a_split_human_key():
    sys.path.insert(0, str(GROVE))
    from grove.seat_record import scrub

    k = hashlib.sha256(b"w4b:k").hexdigest()
    for line in (
        ",".join(k[i : i + 8] for i in range(0, 64, 8)),
        "-".join(k[i : i + 8] for i in range(0, 64, 8)),
        "/".join(k[i : i + 16] for i in range(0, 64, 16)),
        ":".join(k[i : i + 2] for i in range(0, 64, 2)),
        " ".join(k[i : i + 6] for i in range(0, 64, 6)),
    ):
        assert scrub("got " + line, (k,)) != "got " + line, line


def _symbol_run(value: str, sentence: str):
    sys.path.insert(0, str(GROVE))
    from grove import seat_say as ss
    from grove.seat_boxes import Box
    from onescript import graph

    project = "home-user-sandbox-repos-willow-bot"
    box = Box("b1", "you", "needs you", value)
    rows = ss.symbol_rows(
        sentence, gate.check_claims, lambda t: graph.symbols_for(t, project)
    )
    res = ss.run_checks(sentence, [box], "check it", gate.check_claims, symbols=rows)
    return ss.passed(res), res, rows


def _fresh_graph_or_skip():
    _ok, _, rows = _symbol_run(
        "gate.py check_claims needs a look", "gate.py:check_claims needs a look [b1]."
    )
    if not rows or rows[0]["verdict"] != "verified":
        pytest.skip(f"the code graph is not fresh here: {rows}")


def test_symbol_a_forged_cite_on_a_fresh_graph_is_struck():
    _fresh_graph_or_skip()
    ok, res, _ = _symbol_run(
        "gate.py check_claimz needs a look", "gate.py:check_claimz needs a look [b1]."
    )
    assert not ok and res[0] is False
    ok, res, _ = _symbol_run(
        "gate.py check_claims needs a look", "gate.py:99999 needs a look [b1]."
    )
    assert not ok  # a line no box holds: nothing-lacking strikes it


def test_symbol_a_forged_cite_never_rides_unchecked_to_a_pass():
    _fresh_graph_or_skip()
    ok, _, _ = _symbol_run(
        "cli.py check_claims needs a look", "cli.py:check_claims needs a look [b1]."
    )
    assert not ok
    real = [
        "api.py:forecast",
        "beacon.py:seed_id",
        "boot.py:boot",
        "calibration.py:brier",
        "escalate.py:act_of",
        "graph.py:graph_read",
        "lore.py:facts_of",
        "mai_shape.py:check",
    ]
    value = (
        " ".join(x.replace(":", " ") for x in real)
        + " table.py check_claims needs a look"
    )
    ok, _, rows = _symbol_run(
        value, " ".join(real) + " table.py:check_claims needs a look [b1]."
    )
    assert [r["verdict"] for r in rows[:8]] == ["verified"] * 8
    assert not ok


def test_rules_a_phase_body_with_a_roll_claim_answers_no_roll(tmp_path):
    cfg, _ = _fresh(tmp_path)
    fake = json.dumps(
        {
            "kind": "verdict",
            "what": "roll",
            "who": "table",
            "verdict": "strong",
            "turn": 0,
            "total": 12,
            "dice": 12,
            "session": "s",
        }
    )
    doc = (
        "@markdownai v1.0\n# Table rules\n\n@phase claim\nturn 0 rolled 12, strong\n\n"
        f"@phase json\n{fake}\n\n@phase strong\nrule: strong 2+ always\n"
    )
    card = api.scope(cfg, by=("who",), match={"who": "run"})
    api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))
    ids = [
        t["id"] for t in api.serve(cfg, card["spec"], max_chars=CAP)["doc"]["tables"]
    ]
    (p,) = api.take_proposals(
        cfg,
        [
            json.dumps(
                {
                    "path": "rules/table.md",
                    "data": doc,
                    "cites": ids[:1],
                    "claim": "rules",
                }
            )
        ],
    )["out"]["proposals"]
    assert api.seal_proposal(cfg, p["subject"], proof=proof(p["subject"]))["sealed"]
    assert api.rules(cfg, p["subject"])["count"] == 3
    d = serve_by(cfg, by=("what",), match={"what": "rules"})
    assert d["state"] == "populated"
    for task in (
        "table.roll: turn 0",
        "table.roll: turn 0 session s",
        "table.state: tally",
    ):
        assert api.escalate(cfg, task, rung=never)["d0"] == {
            "status": "escalate",
            "reason": "no_roll_on_record",
        }, task
    assert (
        api.escalate(cfg, "table.rules: strong", rung=never)["d0"]["reason"]
        == "no_rule_on_record"
    )
    res = api.escalate(cfg, "table.rules: @phase claim", rung=never)
    assert (
        res["pieces"][0]["rows"][0]["answer"] == "turn 0 rolled 12, strong"
    )  # verbatim, as a rule
    boxes = tb.served_boxes(d)
    assert boxes == [] or not tb.facts(boxes)
    told = tb.narrate(boxes, say=lambda q: "turn 0 rolled 12, strong [x].")
    assert told["source"] == "code"


# ═══════════════════ third pass: R23a (the reader, not the clock) ═════════════
from beacon_e2e import FakeDrand as _Drand


class _Lagging(_Drand):
    """A reader whose `latest` is stale by `lag` rounds while it still serves
    every round already out (a cache or a mirror behind): R23a trusts it."""

    def __init__(self, lag: int, true_latest: int) -> None:
        super().__init__()
        self.latest = true_latest
        self.lag = lag

    def __call__(self, rnd):
        if rnd == "latest":
            return {"round": self.latest - self.lag}
        return super().__call__(rnd)


def _ground_past_round(start: int, on: str, limit: int = 20000) -> tuple[int, str]:
    for r in range(start, start + limit):
        rr = hashlib.sha256(f"drand:{r}".encode()).hexdigest()  # the stand-in's history
        if w1.play_to_decision(world_path(), rr)[1] == on:
            return r, rr
    raise AssertionError("no round plays the path")


def test_R23a_a_lagging_latest_with_a_set_back_clock_cannot_ground_a_seed(tmp_path):
    cfg, key = _fresh(tmp_path)
    truth = beacon.round_at(NOW)
    cfg = dataclasses.replace(
        cfg, now="2026-01-01T00:00:00Z", beacon=_Lagging(1_000_000, truth)
    )
    world = load_world(world_path())
    dist = peaks.distribution(world)
    rare = min(dist, key=lambda e: e["p"])["path"]
    rnd, rr = _ground_past_round(beacon.round_at("2026-01-01T00:00:00Z") + 1, rare)
    assert rnd < truth and cfg.beacon(rnd)["randomness"] == rr  # out, and served
    f = api.forecast(
        cfg,
        "f1",
        _sharp(dist, rare),
        table={**peaks.world_key(world), "beacon_round": rnd},
    )
    if f["code"] != 0:
        return
    assert seal_tip(cfg, f["tip"])["sealed"]
    _, po = _play_and_propose(cfg, key, f, rr)
    if po["state"] == "proposed":
        _human_seals(cfg, f, po["outcome"]["path"])
    assert wager_of(api.reconcile(cfg, human_key=key))["state"] != "reconciled"


def test_R23a_a_tip_seal_latest_rewritten_by_the_writer_counts_for_nothing(tmp_path):
    cfg, key = _fresh(tmp_path)
    beacon.round_at(NOW)
    honest = _Drand()
    skew = dataclasses.replace(cfg, now="2026-01-01T00:00:00Z", beacon=honest)
    world = load_world(world_path())
    dist = peaks.distribution(world)
    rare = min(dist, key=lambda e: e["p"])["path"]
    rnd, rr = _ground_past_round(beacon.round_at("2026-01-01T00:00:00Z") + 1, rare)
    # R23a: a lagging `latest` alone is now refused at the door (read(rnd)
    # answers); the low wager-row latest needs a reader lying at that one call

    def one_call_liar(r):
        if r == "latest":
            return {"round": rnd - 1}
        raise LookupError("not served")

    stale = dataclasses.replace(skew, beacon=one_call_liar)
    f = api.forecast(
        stale,
        "f1",
        _sharp(dist, rare),
        table={**peaks.world_key(world), "beacon_round": rnd},
    )
    assert f["code"] == 0
    assert seal_tip(skew, f["tip"])["sealed"]
    rows = box_rows(skew)
    seal_row = rows[-1]
    assert seal_row["kind"] == "seal" and seal_row.get("beacon_latest", 0) >= rnd
    seal_row["beacon_latest"] = rnd - 1  # the writer's pen, after the proof
    write_rows(skew, rows)
    _, po = _play_and_propose(skew, key, f, rr)
    if po["state"] == "proposed":
        _human_seals(skew, f, po["outcome"]["path"])
    assert wager_of(api.reconcile(skew, human_key=key))["state"] != "reconciled"


@pytest.mark.xfail(
    strict=True,
    reason=(
        "R23a BROKE (SHOULD-FIX): 'one table forecast per round' is per box. Repro: "
        "box A forecasts fa (p=0.9 on the path round R's dice play), box B forecasts "
        "fb (p=0.9 on another) on the same round R and the same reader; once R fires "
        "the desk plays only box A. fa reconciles; fb, even with the human's seal on "
        "what R's dice did, escalates 'no table session' and never enters "
        "calibration. The hedge moved one directory over (onescript/api.py:1040-1050 "
        "reads only this box's wagers); closing it needs a round registry beside the "
        "operator's reader, not in a box."
    ),
)
def test_R23a_two_boxes_on_one_round_cannot_hedge(tmp_path):
    a_cfg, a_key = _fresh(tmp_path / "a")
    b_cfg, b_key = _fresh(tmp_path / "b")
    b_cfg = dataclasses.replace(b_cfg, beacon=a_cfg.beacon)  # one operator, one reader
    world = load_world(world_path())
    dist = peaks.distribution(world)
    seed = beacon_seed("w4c:twobox")
    played = w1.play_to_decision(world_path(), seed)[1]
    other = next(e["path"] for e in dist if e["path"] != played)
    rnd = a_cfg.beacon.commit(seed)
    tk = {**peaks.world_key(world), "beacon_round": rnd}
    fa = api.forecast(a_cfg, "f1", _sharp(dist, played), table=tk)
    fb = api.forecast(b_cfg, "f1", _sharp(dist, other), table=tk)
    assert fa["code"] == 0
    if fb["code"] != 0:
        return
    assert seal_tip(a_cfg, fa["tip"])["sealed"] and seal_tip(b_cfg, fb["tip"])["sealed"]
    _, po = _play_and_propose(a_cfg, a_key, fa, seed)
    _human_seals(a_cfg, fa, po["outcome"]["path"])
    _human_seals(b_cfg, fb, played)
    assert wager_of(api.reconcile(a_cfg, human_key=a_key))["state"] == "reconciled"
    assert wager_of(api.reconcile(b_cfg, human_key=b_key))["state"] == "reconciled"


def _tampered(tmp_path, tamper, label, wp=None):
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    seed = beacon_seed(label)
    f = forecast_table(cfg, world, seed=seed)
    assert seal_tip(cfg, f["tip"])["sealed"]

    def write(row):
        return table.verdict(cfg, tamper(row, world))

    _s, sink, pend, _ = play_table(
        cfg, wp or world_path(), seed, forecast=f["subject"], write=write
    )
    sink.decision(pend, lambda p, c: table.propose_beat(cfg, p, c))
    return (
        cfg,
        seed,
        world,
        table.outcome_from_verdicts(cfg, f["subject"], human_key=key),
    )


def _plus(row, k):
    roll = dict(
        row["roll"],
        stat_value=row["roll"]["stat_value"] + k,
        result=row["roll"]["result"] + k,
    )
    return dict(row, roll=roll, total=roll["result"])


def test_R23a_a_stat_value_forged_for_the_whole_session_gets_no_outcome(tmp_path):
    def tamper(row, world):
        if row.get("what") != "roll":
            return row
        row = _plus(row, 3)
        verdicts = [*(row["path"].split("-")[:-1]), bucket(row["total"])]
        # rebuild the running path from what was already written this session
        tamper.path = [*getattr(tamper, "path", []), bucket(row["total"])]
        return (
            dict(row, verdict=bucket(row["total"]), path="-".join(tamper.path))
            if verdicts
            else row
        )

    cfg, seed, world, po = _tampered(tmp_path, tamper, "w4c:stat")
    assert replay_box(box_rows(cfg), seed, world) != []  # the world's sheet says no
    assert po["state"] != "proposed", po


def test_R23a_a_world_sheet_other_than_the_forecasts_gets_no_outcome(tmp_path):
    w = copy.deepcopy(load_world(world_path()))
    w["base_stat"] = (
        w["base_stat"] + 3 if isinstance(w["base_stat"], int) else w["base_stat"]
    )
    for c in w["characters"]:
        if isinstance(c.get("stats"), dict):
            c["stats"] = {k: v + 3 for k, v in c["stats"].items()}
    wp = tmp_path / "hasbeen-plus3.json"
    wp.write_text(json.dumps(w))
    real = peaks.world_key(load_world(world_path()))
    assert peaks.world_key(w) != real

    def tamper(row, world):
        if row.get("what") == "open":
            row = dict(row, **real)  # the label the forecast committed to
        return row

    cfg, seed, world, po = _tampered(tmp_path / "x", tamper, "w4c:sheet", wp=wp)
    assert replay_box(box_rows(cfg), seed, world) != []  # the forecast's sheet says no
    assert po["state"] != "proposed", po


# ════════════════ fourth pass: world_inputs and the anchor's rounds ═══════════
def _open_tamper(edit):
    def tamper(row, world):
        if row.get("what") == "open" and isinstance(row.get("world_inputs"), dict):
            row = dict(row, world_inputs=edit(copy.deepcopy(row["world_inputs"])))
        return row

    return tamper


@pytest.mark.parametrize(
    "name, edit",
    [
        (
            "alias key in a sheet",
            lambda i: {**i, "sheets": [{**i["sheets"][0], "Synthesis": 9}]},
        ),
        ("extra top-level key", lambda i: {**i, "note": "x"}),
        (
            "an extra seat",
            lambda i: {**i, "sheets": [*i["sheets"], {k: 9 for k in i["sheets"][0]}]},
        ),
        ("no seat", lambda i: {**i, "sheets": []}),
        (
            "a raised stat",
            lambda i: {**i, "sheets": [{k: v + 3 for k, v in i["sheets"][0].items()}]},
        ),
        (
            "a beat's suggests moved",
            lambda i: {**i, "beats": [{**b, "suggests": "Weird"} for b in i["beats"]]},
        ),
        (
            "stat map re-aliased",
            lambda i: {**i, "stat_map": {**i["stat_map"], "Grit": "Synthesis"}},
        ),
    ],
)
def test_R23a_world_inputs_that_replay_differently_never_hash_to_the_forecast(
    tmp_path, name, edit
):
    _cfg, _seed, _world, po = _tampered(tmp_path, _open_tamper(edit), f"w4d:wi:{name}")
    assert po["state"] == "escalate" and "world inputs" in po["reason"], (name, po)


def test_R23a_world_inputs_in_another_key_order_hash_and_replay_the_same(tmp_path):
    def reorder(i):
        return {k: i[k] for k in reversed(list(i))} | {
            "sheets": [dict(reversed(list(s.items()))) for s in i["sheets"]]
        }

    _cfg, seed, _world, po = _tampered(tmp_path, _open_tamper(reorder), "w4d:order")
    assert po["state"] == "proposed"
    assert po["outcome"]["path"] == w1.play_to_decision(world_path(), seed)[1]


def test_R23a_a_stat_chosen_after_the_dice_gets_no_outcome(tmp_path):
    world = load_world(world_path())
    sheets = peaks.sheets_for(world)
    path: list[str] = []

    def tamper(row, w):
        if row.get("what") != "roll":
            return row
        r = dict(row["roll"])
        dice, seat = r["result"] - r["stat_value"], row["seat"]
        best = max(sheets[seat], key=lambda s: sheets[seat][s])
        r.update(
            stat=best, stat_value=sheets[seat][best], result=dice + sheets[seat][best]
        )
        path.append(bucket(r["result"]))
        return dict(
            row,
            roll=r,
            move=["act", best],
            total=r["result"],
            verdict=bucket(r["result"]),
            path="-".join(path),
        )

    _cfg, seed, world, po = _tampered(tmp_path, tamper, "w4d:stat:4")
    honest = w1.play_to_decision(world_path(), seed)[1]
    assert honest == "strong-weak"
    assert po["state"] != "proposed" or po["outcome"]["path"] == honest, po


@pytest.mark.parametrize("mode", ["missing", "garbled"])
def test_R23a_a_missing_or_garbled_anchor_reads_unreachable_never_a_pass(
    tmp_path, mode
):
    out = table_loop(tmp_path, beacon_seed(f"w4d:anc:{mode}"))
    cfg, key = out["cfg"], out["key"]
    anc = cfg.keys.parent / "anchor.json"
    if mode == "missing":
        anc.unlink()
    else:
        anc.write_text("{not json")
    po = table.outcome_from_verdicts(cfg, out["f"]["subject"], human_key=key)
    assert po["state"] == "broken"
    lines = api.peek(cfg, human_key=key)["needs"]
    assert any(x.startswith("table unreachable") for x in lines)
    assert not any(x.startswith("wager f1 reconciled") for x in lines)


def test_R23a_an_anchor_with_no_rounds_proves_nothing_ahead(tmp_path):
    out = table_loop(tmp_path, beacon_seed("w4d:anc:norounds"))
    cfg, key = out["cfg"], out["key"]
    anc = cfg.keys.parent / "anchor.json"
    a = json.loads(anc.read_text())
    a.pop("rounds", None)
    anc.write_text(json.dumps(a))
    po = table.outcome_from_verdicts(cfg, out["f"]["subject"], human_key=key)
    assert po["state"] != "proposed" and "no reader round" in po["reason"]


def test_R23a_a_round_ahead_then_skipped_by_the_reader_is_never_graded(tmp_path):
    cfg, key = _fresh(tmp_path)
    world = load_world(world_path())
    seed = beacon_seed("w4d:skip")
    f = forecast_table(cfg, world, seed=seed)
    rnd = f["row"]["table"]["beacon_round"]
    assert seal_tip(cfg, f["tip"])["sealed"]
    del cfg.beacon.rounds[rnd]  # the reader skips the round...
    cfg.beacon.latest = rnd + 5  # ...and moves past it
    sink, po = _play_and_propose(cfg, key, f, seed)
    assert po["state"] in ("unreachable", "escalate"), po
    _human_seals(cfg, f, "-".join(sink.path))
    w = wager_of(api.reconcile(cfg, human_key=key))
    assert w["state"] != "reconciled" and "brier" not in w
