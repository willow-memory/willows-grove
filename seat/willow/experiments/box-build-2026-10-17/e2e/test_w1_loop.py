"""W1 end-to-end: the deterministic prediction loop across repos (J1 + J2 + J3).

    peaks.distribution(world) -> api.forecast -> human seals tip -> StorySession
    on the SHA-256 stream to the first decision beat -> path from the rolls ->
    api.seal_outcome -> api.seal_tip -> api.reconcile -> Brier / log score.

Run:  /home/user/tools/venv/bin/python -m pytest -q /home/user/sandbox/box-build/e2e

Nothing under sandbox/repos is edited; every box lives in tmp_path. Every seed
is derived from a fixed label by SHA-256, so every run is the same run.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

import pytest

REPOS = Path(os.environ.get("BOX_REPOS", "/home/user/sandbox/repos"))
TABLE = REPOS / "safe-app-store" / "apps" / "the-table"
ONESCRIPT = REPOS / "willow-bot" / "one-script"
for p in (str(TABLE), str(ONESCRIPT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from onescript import api, gate, record, reverse  # noqa: E402
from the_table import peaks  # noqa: E402
from the_table.dice_source import replay_roll  # noqa: E402
from the_table.story_session import StorySession  # noqa: E402
from the_table.stream import GeneratorMismatch, ReplayRefused  # noqa: E402
from the_table.worlds import load_world  # noqa: E402

HUMAN_KEY = b"a-throwaway-human-key-for-e2e"
CAP = 10**6
WORLDS = ("aetheris", "hasbeen", "ironworks")
N_SEEDS = 200

# Tolerance for "empirical frequency ~ exact p" over N_SEEDS runs (stated here,
# asserted below). Per path: |freq - p| <= Z * sqrt(p(1-p)/N) + 1/N, Z = 4.5
# (two-sided ~7e-6 per path, ~6e-4 across the 243 paths of the three worlds).
# Overall: total-variation distance <= TV_SLACK x its sampling expectation
# E[TV] = 0.5 * sum sqrt(2 p (1-p) / (pi N)) (a fixed 0.2 cut would be wrong: with 81
# paths and N=200 the expected TV from sampling noise alone is ~0.2).
# Per beat marginal (strong/weak/miss): |freq - p| <= Z * sqrt(p(1-p)/N) + 1/N.
Z = 4.5
TV_SLACK = 1.5


def beacon_seed(label: str) -> str:
    """A beacon-like 64-hex string, fixed by its label (stands in for drand)."""
    return hashlib.sha256(label.encode()).hexdigest()


def world_path(name: str) -> Path:
    return TABLE / "worlds" / f"{name}.json"


# ── the box ──────────────────────────────────────────────────────────────────
def make_cfg(tmp: Path) -> api.Config:
    grove = tmp / "grove"
    (grove / "governance").mkdir(parents=True)
    (grove / "governance" / "CONSTITUTION.md").write_text("CONST-III CONST-VI")
    ci = grove / "ci.yml"
    ci.write_text("pip install ruff==0.16.7")
    keys = tmp / "keys" / "keys.json"
    keys.parent.mkdir(mode=0o700)
    keys.write_text(json.dumps({"desk": "aa" * 32, "human": HUMAN_KEY.hex()}))
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


def make_key_file(tmp: Path) -> Path:
    """The human's key, outside the box, 0600 (SPEC H4)."""
    f = tmp / "human" / "key.hex"
    f.parent.mkdir(mode=0o700)
    f.write_text(HUMAN_KEY.hex() + "\n")
    f.chmod(0o600)
    return f


def proof(subject: str) -> str:
    return gate.sign(HUMAN_KEY, "seal", subject)


def box_rows(cfg) -> list[dict]:
    return [json.loads(x) for x in (cfg.box / "record.jsonl").read_text().splitlines()]


def seal_tip(cfg, subject):
    return api.seal_tip(cfg, subject, proof=proof(subject))


def seal_out(cfg, wager, outcome):
    return api.seal_outcome(
        cfg, wager, outcome, proof=proof(reverse.outcome_subject(wager, outcome))
    )


def wager_row(rep, wid):
    return next(r for r in rep["wagers"]["rows"] if r["id"] == wid)


# ── the table ────────────────────────────────────────────────────────────────
def bucket(total: int) -> str:
    """Own copy of the PbtA read (10+ strong, 7-9 weak, 6- miss): the test must
    not borrow peaks.bucket, or a shared bug would cancel out."""
    return "strong" if total >= 10 else "weak" if total >= 7 else "miss"


def play_to_decision(world_file: Path, seed: str):
    """Play on the stream to the first decision beat, always taking the beat's
    own suggested stat (peaks' 'suggested' policy). Returns (session, path,
    rolls) where rolls = [(seat, last_roll_record)]."""
    s = StorySession(world_file)
    s.reset(seed)
    buckets, rolls = [], []
    while not s.is_terminal() and s.pending_seal() is None:
        seat = s.current_seat()
        stat = s.observe(seat).view["suggests"]
        s.step(seat, ("act", stat))
        buckets.append(bucket(s.last_roll["result"]))
        rolls.append((seat, dict(s.last_roll)))
    return s, "-".join(buckets), rolls


def expected_brier(dist: list[dict], idx: int) -> float:
    """The pairing rule in reverse.wager_pairs, restated: two paths -> one pair
    (p0, idx==0); else one pair per path, mean over n of
    [(1-p_actual)^2 + sum(p_other^2)]. (n = len(dist); the mean, not the sum.)"""
    ps = [e["p"] for e in dist]
    if len(ps) == 2:
        return (ps[0] - (1.0 if idx == 0 else 0.0)) ** 2
    return (
        (1 - ps[idx]) ** 2 + sum(p * p for i, p in enumerate(ps) if i != idx)
    ) / len(ps)


def run_loop(tmp: Path, name: str, seed: str, wid: str = "f1", dist=None) -> dict:
    """Steps 1-4 of the brief on a fresh box. Returns everything a test asserts."""
    cfg, key_file = make_cfg(tmp), make_key_file(tmp)
    world = load_world(world_path(name))
    dist = dist if dist is not None else peaks.distribution(world)
    assert api.checkin(cfg)["code"] == 0
    # 1. forecast BEFORE any dice (the stream is not yet built)
    f = api.forecast(cfg, wid, dist, by="oracle")
    assert f["code"] == 0, f
    n_forecast = f["row"]["n"]
    # 2. the human seals the tip covering it
    t1 = seal_tip(cfg, f["tip"])
    assert t1["sealed"] and [c["id"] for c in t1["covers"]] == [wid]
    # 3. dice
    s, path, rolls = play_to_decision(world_path(name), seed)
    # 4. outcome: the FULL path string
    so = seal_out(cfg, f["subject"], {"path": path})
    assert so["sealed"], so
    t2 = seal_tip(cfg, so["tip"])
    assert t2["sealed"], t2
    rep = api.reconcile(cfg, human_key=key_file)
    return dict(
        cfg=cfg,
        key_file=key_file,
        dist=dist,
        path=path,
        rolls=rolls,
        session=s,
        f=f,
        so=so,
        rep=rep,
        row=wager_row(rep, wid),
        n_forecast=n_forecast,
    )


# ═════════════════════════════════ 1-4: one loop ═════════════════════════════
@pytest.mark.parametrize("name", WORLDS)
def test_full_loop_reconciles_with_exact_brier(tmp_path, name):
    seed = beacon_seed(f"loop:{name}")
    out = run_loop(tmp_path, name, seed)
    row, dist, path = out["row"], out["dist"], out["path"]

    # order on the chain: wager < tip seal < outcome seal < second tip seal
    kinds = [
        (r["n"], r["kind"])
        for r in box_rows(out["cfg"])
        if r["kind"] in ("wager", "seal")
    ]
    assert [k for _, k in kinds] == ["wager", "seal", "seal", "seal"]

    assert row["state"] == "reconciled" and row["graded_by"] is None
    idx = [e["path"] for e in dist].index(path)
    assert row["path_index"] == idx and row["actual_path"] == path
    assert row["predicted_p"] == dist[idx]["p"]
    assert math.isclose(
        row["brier"], expected_brier(dist, idx), rel_tol=0, abs_tol=1e-12
    )
    assert math.isfinite(row["log_score"])
    assert math.isclose(row["log_score"], -math.log(dist[idx]["p"]), abs_tol=1e-12)
    assert row["committed_under"]["tip"] >= out["n_forecast"]
    assert row["by_claimed"] == "oracle" and row["by_vouched"] is False
    assert out["rep"]["wagers"]["escalate"] == []
    assert reverse_chain_ok(out["cfg"])


def reverse_chain_ok(cfg) -> bool:
    rec = record.Record(cfg.box, lambda: "t", "v", object())
    return not rec.verify_chain()


def test_the_2d6_sums_come_from_the_session_not_the_test(tmp_path):
    """The path is derived from `last_roll` results; check them against the
    stream itself (independent of StorySession's bucketing)."""
    from the_table.stream import StreamRandom

    seed = beacon_seed("loop:hasbeen")
    s, path, rolls = play_to_decision(world_path("hasbeen"), seed)
    rng = StreamRandom.from_seed(seed)
    world = load_world(world_path("hasbeen"))
    sheets = peaks.sheets_for(world)
    beats = peaks.action_beats(world)
    want = []
    for t, b in enumerate(beats):
        eng = peaks.engine_view(peaks.raw_sheets_for(world)[t % len(sheets)])
        a, c = rng.randint(1, 6), rng.randint(1, 6)
        want.append(
            bucket(
                a + c + eng[peaks._ENGINE_STAT_MAP.get(b["suggests"], b["suggests"])]
            )
        )
    assert path == "-".join(want)


# ═════════════════════════════════ 5: replay ═════════════════════════════════
@pytest.mark.parametrize("name", WORLDS)
def test_same_seed_same_path_and_last_roll_replays(name):
    seed = beacon_seed(f"replay:{name}")
    world = load_world(world_path(name))
    _, p1, r1 = play_to_decision(world_path(name), seed)
    s2, p2, r2 = play_to_decision(world_path(name), seed)
    assert p1 == p2 and [x for _, x in r1] == [x for _, x in r2]
    # replay_roll on the session's last roll, with the sheet of the seat that rolled
    seat, last = r2[-1]
    assert last == s2.last_roll
    sheet = peaks.engine_view(peaks.raw_sheets_for(world)[seat])
    rng = replay_roll(seed, last, sheet=sheet)
    assert rng.counter == last["counter"]
    # every roll of the run verifies, not just the last
    for seat, rec in r1:
        replay_roll(
            seed, rec, sheet=peaks.engine_view(peaks.raw_sheets_for(world)[seat])
        )
    # the record names the seed by id only
    assert seed not in json.dumps(last) and last["seed_id"] != seed


def test_replay_refuses_a_wrong_seed_and_a_row_without_a_sheet():
    seed = beacon_seed("replay:wrong")
    world = load_world(world_path("hasbeen"))
    _, _, rolls = play_to_decision(world_path("hasbeen"), seed)
    seat, last = rolls[-1]
    sheet = peaks.engine_view(peaks.raw_sheets_for(world)[seat])
    with pytest.raises(GeneratorMismatch):
        replay_roll(beacon_seed("replay:other"), last, sheet=sheet)
    with pytest.raises(ReplayRefused):
        replay_roll(seed, last)  # stat_value is self-declared: refused without a sheet
    forged = dict(last, result=last["result"] + 1)
    with pytest.raises(ReplayRefused):
        replay_roll(seed, forged, sheet=sheet)


def test_a_different_seed_gives_a_different_path_for_some_of_20():
    for name in WORLDS:
        base = play_to_decision(world_path(name), beacon_seed(f"diff:{name}:0"))[1]
        others = {
            play_to_decision(world_path(name), beacon_seed(f"diff:{name}:{i}"))[1]
            for i in range(1, 20)
        }
        assert others - {base}, f"{name}: 20 seeds all gave {base!r}"


# ═════════════════ 6: 200 seeds x 3 worlds, frequencies and Brier ════════════
@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """For each world: 200 full loops (fresh box each). Cached for the module."""
    out = {}
    for name in WORLDS:
        recs = []
        for i in range(N_SEEDS):
            tmp = tmp_path_factory.mktemp(f"{name}{i}")
            o = run_loop(tmp, name, beacon_seed(f"mass:{name}:{i}"))
            recs.append({"path": o["path"], "row": o["row"], "dist": o["dist"]})
        out[name] = recs
    return out


@pytest.mark.parametrize("name", WORLDS)
def test_every_loop_reconciled_and_matches_the_pairing_rule(runs, name):
    for r in runs[name]:
        idx = [e["path"] for e in r["dist"]].index(r["path"])
        assert r["row"]["state"] == "reconciled" and r["row"]["graded_by"] is None
        assert math.isclose(
            r["row"]["brier"], expected_brier(r["dist"], idx), abs_tol=1e-12
        )
        assert math.isfinite(r["row"]["log_score"])


@pytest.mark.parametrize("name", WORLDS)
def test_empirical_path_frequencies_sit_within_tolerance_of_exact_p(runs, name):
    dist = runs[name][0]["dist"]
    counts = {e["path"]: 0 for e in dist}
    for r in runs[name]:
        counts[r["path"]] += 1
    assert sum(counts.values()) == N_SEEDS
    tv = 0.0
    for e in dist:
        p, f = e["p"], counts[e["path"]] / N_SEEDS
        tol = Z * math.sqrt(p * (1 - p) / N_SEEDS) + 1 / N_SEEDS
        assert abs(f - p) <= tol, (name, e["path"], p, f, tol)
        tv += abs(f - p) / 2
    etv = 0.5 * sum(
        math.sqrt(2 * e["p"] * (1 - e["p"]) / (math.pi * N_SEEDS)) for e in dist
    )
    assert tv <= TV_SLACK * etv, (name, tv, etv)
    # per-beat marginals: the same odds, read one beat at a time
    for b in range(len(dist[0]["path"].split("-"))):
        for k in ("strong", "weak", "miss"):
            p = sum(e["p"] for e in dist if e["path"].split("-")[b] == k)
            f = sum(1 for r in runs[name] if r["path"].split("-")[b] == k) / N_SEEDS
            assert abs(f - p) <= Z * math.sqrt(p * (1 - p) / N_SEEDS) + 1 / N_SEEDS, (
                name,
                b,
                k,
                p,
                f,
            )
    # the modal path is among the likely ones often enough to matter
    top = max(counts, key=counts.get)
    assert counts[top] > 0


def test_exact_odds_beat_the_coin_on_mean_brier(runs, record_property):
    summary = {}
    for name in WORLDS:
        exact_b, coin_b, exact_l, coin_l = [], [], [], []
        for r in runs[name]:
            idx = [e["path"] for e in r["dist"]].index(r["path"])
            n = len(r["dist"])
            coin = [
                {"path": e["path"], "p": 1.0 / n, "band": "likely"} for e in r["dist"]
            ]
            sc = reverse.score({"distribution": coin}, idx)
            exact_b.append(r["row"]["brier"])
            exact_l.append(r["row"]["log_score"])
            coin_b.append(sc["brier"])
            coin_l.append(sc["log_score"])
        me, mc = sum(exact_b) / len(exact_b), sum(coin_b) / len(coin_b)
        le, lc = sum(exact_l) / len(exact_l), sum(coin_l) / len(coin_l)
        summary[name] = dict(brier_exact=me, brier_coin=mc, log_exact=le, log_coin=lc)
        assert me < mc, (name, me, mc)
        # log_score here is the (negative) log of p, lower magnitude is better
        assert le < lc, (name, le, lc)
    record_property("summary", json.dumps(summary))
    (Path(__file__).parent / "w1_numbers.json").write_text(
        json.dumps(summary, indent=1)
    )


# ═════════════════════ 7: adversarial across the seam ════════════════════════
def test_forecast_written_after_the_dice_gets_no_score(tmp_path):
    """The dice are played and the path known; only then is the 'forecast' written
    (a perfect one). The only tip the human sealed came before it, so no tip holds
    the wager before the outcome seal: escalate, no Brier."""
    cfg, key_file = make_cfg(tmp_path), make_key_file(tmp_path)
    api.checkin(cfg)
    seal_tip(cfg, record.tip_subject(box_rows(cfg)[-1]))  # tip first: holds nothing
    seed = beacon_seed("late:hasbeen")
    _, path, _ = play_to_decision(world_path("hasbeen"), seed)  # dice
    world = load_world(world_path("hasbeen"))
    cheat = [
        {
            "path": e["path"],
            "p": 0.96 if e["path"] == path else 0.04 / 8,
            "band": "likely",
        }
        for e in peaks.distribution(world)
    ]
    f = api.forecast(cfg, "late", cheat, by="oracle")
    assert f["code"] == 0
    so = seal_out(cfg, f["subject"], {"path": path})
    assert so["sealed"]
    assert seal_tip(cfg, so["tip"])["sealed"]  # one tip over wager and outcome together
    w = wager_row(api.reconcile(cfg, human_key=key_file), "late")
    assert w["state"] == "escalate" and "brier" not in w and "log_score" not in w
    assert "wager.n <= tip.n" in w["reason"]


def test_forecast_distribution_edited_after_sealing_escalates(tmp_path):
    out = run_loop(tmp_path, "hasbeen", beacon_seed("edit:hasbeen"))
    cfg, key_file, path = out["cfg"], out["key_file"], out["path"]
    assert out["row"]["state"] == "reconciled"
    good = (cfg.box / "record.jsonl").read_text()
    p0 = out["dist"][0]["p"]

    # (a) in place: the chain breaks
    needle = f'"p":{json.dumps(p0)}'
    assert needle in good
    (cfg.box / "record.jsonl").write_text(good.replace(needle, '"p":0.97', 1))
    w = wager_row(api.reconcile(cfg, human_key=key_file), "f1")
    assert w["state"] == "escalate" and "brier" not in w
    (cfg.box / "record.jsonl").write_text(good)

    # (b) edited and the whole chain re-hashed: internally consistent, but the
    # human's sealed tip names the old hash
    prev, lines = record.GENESIS, []
    for r in box_rows(cfg):
        if r["kind"] == "wager":
            fat = [dict(e, p=0.0) for e in r["distribution"]]
            fat[[e["path"] for e in fat].index(path)]["p"] = 1.0
            r["distribution"] = fat
        r["prev"] = prev
        r["hash"] = record.h256(
            record.canon({k: v for k, v in r.items() if k != "hash"})
        )
        prev = r["hash"]
        lines.append(record.canon(r))
    (cfg.box / "record.jsonl").write_text("\n".join(lines) + "\n")
    w = wager_row(api.reconcile(cfg, human_key=key_file), "f1")
    assert w["state"] == "escalate" and "brier" not in w


def _walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from _walk(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            yield from _walk(v)
    else:
        yield o


def test_the_seed_hex_never_reaches_what_serve_hands_a_model(tmp_path):
    seed = beacon_seed("serve:hasbeen")
    cfg = make_cfg(tmp_path)
    world = load_world(world_path("hasbeen"))
    api.checkin(cfg)
    # the one place a seed-derived value may enter the box: the commitment
    committed = {
        "sha256": hashlib.sha256(seed.encode()).hexdigest(),
        "beacon_then": "round-1",
        "target": "round-2",
    }
    f = api.forecast(
        cfg, "f1", peaks.distribution(world), by="oracle", committed=committed
    )
    assert f["code"] == 0
    seal_tip(cfg, f["tip"])
    s, path, rolls = play_to_decision(world_path("hasbeen"), seed)
    so = seal_out(cfg, f["subject"], {"path": path})
    seal_tip(cfg, so["tip"])
    served = []
    for by, match in (
        (("who",), {}),
        (("who",), {"who": "human"}),
        (("kind",), {}),
        (("who",), {"who": "run"}),
    ):
        card = api.scope(cfg, by=by, match=match)
        if card.get("code") != 0:
            continue
        api.seal_scope(cfg, card["subject"], proof=proof(card["subject"]))
        res = api.serve(cfg, card["spec"], max_chars=CAP)
        served.append(res)
    assert served and any(r["state"] == "populated" for r in served), served
    blob = json.dumps(served, default=str)
    assert (
        seed not in blob
        and seed[:16] not in blob
        and s.last_roll["seed_id"] not in blob
    )
    assert seed not in (cfg.box / "record.jsonl").read_text()
    assert not any(isinstance(x, str) and seed in x for x in _walk(rolls))


# D1 (raw seed in reset narration) fixed in safe-app-store 647d8e0.
def test_seed_hex_is_absent_from_what_reset_narrates():
    seed = beacon_seed("narration:hasbeen")
    s = StorySession(world_path("hasbeen"))
    obs = s.reset(seed)
    assert seed not in json.dumps(obs.narration, default=str)
    assert seed not in json.dumps(obs.view, default=str)
