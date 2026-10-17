"""W4 end-to-end: the surface (R13), symbol cites (T-cbm-1), rules by phase (T-mai-2).

    forecast -> the human seals its tip -> play on the stream (verdict rows,
    campaign.db Tee'd) -> a decision beat is a proposal -> the human seals it ->
    code proposes the outcome, the human seals it -> agm_head row -> the human
    seals the tip -> reconcile, with the seat pointed at the box by config and
    reading it ONLY through api.needs / api.checkout at every stage.

SPEC rulings R13 (no new panel: a `wager` pattern in `seat_record.item_box`, the
seat pointed at the table box), R15 (T-cbm-1, T-mai-2), R18, R19, R20, R21;
SPEC-documented J8-table-panel; SPEC-rival section 7, T10 (the surface line);
SPEC-tools T-cbm-1, T-mai-2. Run:

    /home/user/tools/venv/bin/python -m pytest -q /home/user/sandbox/box-build/e2e

No model is reachable here; every model is a deterministic fake. Every box,
ledger and throwaway repo lives in tmp_path; every seed is a fixed label's
SHA-256. The seat never opens a record file: a test that reads one does it to
prove a secret is absent.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPOS = Path(os.environ.get("BOX_REPOS", "/home/user/sandbox/repos"))
TABLE = REPOS / "safe-app-store" / "apps" / "the-table"
ONESCRIPT = REPOS / "willow-bot" / "one-script"
GROVE = REPOS / "willows-grove"
for p in (str(TABLE), str(ONESCRIPT), str(GROVE)):
    if p not in sys.path:
        sys.path.insert(0, p)

from grove import seat_cli as sc  # noqa: E402
from grove import seat_say as say_mod  # noqa: E402
from grove import table_boxes as tb  # noqa: E402
from onescript import api, gate, graph, table  # noqa: E402
from the_table import agm_head, peaks  # noqa: E402
from the_table import onescript_sink as osk  # noqa: E402
from the_table.ledger_sink import LedgerSink  # noqa: E402
from the_table.story_session import StorySession  # noqa: E402
from the_table.worlds import load_world  # noqa: E402
from beacon_e2e import FakeDrand, fired_round, table_forecast  # noqa: E402

HUMAN_KEY = b"a-throwaway-human-key-for-e2e-w4"
SEED = hashlib.sha256(b"w4:surface").hexdigest()
CAP = 200_000


# ── the box, and the human's hand ───────────────────────────────────────────────
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


def tip(cfg) -> str:
    from onescript import record

    return record.tip_subject(box_rows(cfg)[-1])


# ── the seat, real bot, scripted keys, fake model ───────────────────────────────
def seat(cfg, *, key=None, db=None, say=None, doc=None):
    out: list[str] = []
    bot = sc.load_bot(sc.bot_root())
    st = sc.Seat(
        bot,
        cfg,
        say=say,
        read=lambda prompt: (_ for _ in ()).throw(EOFError()),
        write=out.append,
        color=False,
        clock=lambda: "09:14",
        human_key=key,
        read_head=sc.ledger_reader(str(db), TABLE) if db else None,
    )
    st.doc = doc
    return st, out


def view(cfg, key=None, db=None, ask="what's on the table") -> str:
    st, out = seat(cfg, key=key, db=db)
    st.status(ask)
    return "\n".join(out)


def card(text: str, label: str) -> list[str]:
    """The cards of `label` in a seat transcript, each as its lines."""
    cards, cur = [], None
    for ln in text.split("\n"):
        if ln[:2] in ("+-", "+.", "+!"):
            cur = [ln] if f"] {label} " in ln else None
            if cur is not None:
                cards.append(cur)
        elif cur is not None and ln[:1] in ("|", ":", "!"):
            cur.append(ln)
        else:
            cur = None
    return ["\n".join(c) for c in cards]


# ── the whole table box, stage by stage ─────────────────────────────────────────
@pytest.fixture
def loop(tmp_path):
    cfg, key = make_cfg(tmp_path), make_key_file(tmp_path)
    assert api.checkin(cfg)["code"] == 0
    world_file = TABLE / "worlds" / "hasbeen.json"
    world = load_world(world_file)
    L = dict(tmp=tmp_path, cfg=cfg, key=key, world=world, world_file=world_file)

    L["f"] = api.forecast(
        cfg,
        "f1",
        peaks.distribution(world),
        by="oracle",
        table=table_forecast(cfg, peaks.world_key(world), SEED),
    )
    assert L["f"]["code"] == 0
    return L


def stage_tip(L):
    assert api.seal_tip(L["cfg"], L["f"]["tip"], proof=proof(L["f"]["tip"]))["sealed"]


def stage_play(L):
    cfg = L["cfg"]
    L["ledger"] = LedgerSink(str(L["tmp"] / "campaign"))
    L["sink"] = osk.OneScriptSink(
        lambda r: table.verdict(cfg, r),
        check=lambda x: table.beat_seal(cfg, x),
        forecast=L["f"]["subject"],
        beacon_round=fired_round(cfg, L["f"]),
    )
    L["session"] = StorySession(L["world_file"])
    L["pending"] = osk.play_to_decision(
        L["session"],
        osk.suggested_policy(),
        osk.Tee(L["ledger"], L["sink"]),
        seed=SEED,
        session_id="hasbeen-1",
    )
    assert L["pending"] is not None
    L["beat"] = L["sink"].decision(
        L["pending"], lambda p, c: table.propose_beat(cfg, p, c)
    )


def stage_seal_beat(L):
    cfg = L["cfg"]
    assert api.seal_proposal(cfg, L["beat"], proof=proof(L["beat"]))["sealed"]
    L["sink"].apply_beat_seal(L["session"], L["pending"], L["beat"])


def stage_outcome(L):
    cfg = L["cfg"]
    po = table.outcome_from_verdicts(cfg, L["f"]["subject"], human_key=L["key"])
    assert po["state"] == "proposed", po
    assert api.seal_outcome(
        cfg, L["f"]["subject"], po["outcome"], proof=proof(po["subject"])
    )["sealed"]
    L["po"] = po


def stage_head(L):
    cfg = L["cfg"]
    L["ledger"].close()
    L["db"] = L["ledger"].db_path
    ah = table.agm_head(cfg, **agm_head.row(L["db"]))
    assert ah["code"] == 0, ah
    assert api.seal_tip(cfg, ah["tip"], proof=proof(ah["tip"]))["sealed"]


# ═══════════════════════════ R13: the seat at every stage ═══════════════════════
def test_the_seat_follows_the_box_from_forecast_to_head(loop):
    cfg, key = loop["cfg"], loop["key"]

    # 1. a forecast, nothing sealed: a wager box that escalates to the human
    t1 = view(cfg, key)
    (w,) = card(t1, "wager")
    assert "[needs you] wager" in w and "wager f1 escalate to human" in w
    assert "the grade is the human's" in w
    assert not card(t1, "verdict session") and not card(t1, "agm_head")

    # 2. the tip sealed, the table plays: a verdict session whose tip is not yet
    # the human's, a decision beat awaiting a seal, an agm_head with no anchor
    stage_tip(loop)
    stage_play(loop)
    t2 = view(cfg, key)
    (sess,) = card(t2, "verdict session")
    assert "[needs you]" in sess and "table verdict session hasbeen-1" in sess
    assert "forecast f1" in sess and "waiting on your tip seal" in sess
    (beat,) = card(t2, "proposal")
    assert "needs you" in beat and "own_idea: no" in beat
    (head,) = card(t2, "agm_head")  # no anchor: the empty arm, not a pass
    assert head.startswith("+.") and "no agm_head row on record" in head
    assert "wager f1 escalate to human" in t2

    # 3. the human seals the beat and the outcome, the head is anchored and the
    # tip sealed over everything: reconciled, covered, satisfied
    stage_seal_beat(loop)
    stage_outcome(loop)
    stage_head(loop)
    t3 = view(cfg, key, loop["db"])
    (w3,) = card(t3, "wager")
    assert "wager f1 reconciled" in w3 and "[needs you]" in w3
    assert "brier " in w3 and "log " in w3 and "grade is yours" in w3
    assert "by oracle (claimed)" in w3
    assert "happened: " + loop["po"]["outcome"]["path"] in w3
    (s3,) = card(t3, "verdict session")
    assert "[decided]" in s3 and "covered by your sealed tip" in s3
    (h3,) = card(t3, "agm_head")
    assert "[decided]" in h3 and "table agm_head satisfied" in h3
    assert not card(t3, "proposal")  # the beat was sealed: nothing awaits

    # the grade is the human's: code made a score and wrote no seal of its own
    rows = box_rows(cfg)
    assert all(r["who"] == "human" for r in rows if r["kind"] == "seal")
    assert [
        r["graded_by"] for r in api.reconcile(cfg, human_key=key)["wagers"]["rows"]
    ] == [None]


def test_the_seat_reads_the_box_only_through_the_api(loop):
    """The seat names no record file and opens no box path: what it shows is
    what api.needs and api.checkout hand it. Prove it on the source, and prove
    the screen follows the api by changing what the api says."""
    for name in ("seat_cli", "seat_record", "seat_boxes", "table_boxes"):
        src = (GROVE / "grove" / f"{name}.py").read_text()
        assert "record.jsonl" not in src and ".box /" not in src, name
    stage_tip(loop)
    stage_play(loop)
    real = sc.load_bot(sc.bot_root())

    class Said:
        def __getattr__(self, name):
            return getattr(real.api, name)

        def needs(self, c, **kw):
            return {
                "needs": ["wager zz escalate to human · said by the api"],
                "count": 1,
            }

    out: list[str] = []
    bot = sc.Bot(Said(), real.cut, real.subject, real.piece_chars, real.claims)
    sc.Seat(
        bot,
        loop["cfg"],
        write=out.append,
        color=False,
        read=lambda p: (_ for _ in ()).throw(EOFError()),
    ).status("what's on the table")
    text = "\n".join(out)
    assert "wager zz escalate to human" in text and "hasbeen-1" not in text


def test_pointed_at_the_box_by_config_not_by_path(loop, monkeypatch):
    """`GROVE_SEAT_BOX` / `GROVE_SEAT_KEYS` build the seat's Config."""
    bot = sc.load_bot(sc.bot_root())
    cfg = sc.config(
        bot,
        loop["tmp"],
        environ={
            "GROVE_SEAT_BOX": str(loop["cfg"].box),
            "GROVE_SEAT_KEYS": str(loop["cfg"].keys),
        },
    )
    assert cfg.box == loop["cfg"].box and cfg.keys == loop["cfg"].keys
    import dataclasses

    cfg = dataclasses.replace(cfg, no_tests=True, phone=True)
    assert "wager f1 escalate to human" in view(cfg, loop["key"])


# ═══════════════════ the three states, never collapsed ══════════════════════════
def test_the_agm_head_card_has_four_states_and_the_session_two_more(loop):
    cfg, key = loop["cfg"], loop["key"]
    stage_tip(loop)
    stage_play(loop)
    stage_seal_beat(loop)
    stage_outcome(loop)
    stage_head(loop)
    db = loop["db"]

    # satisfied (above); unreachable: the reader has no db to read
    gone = loop["tmp"] / "nowhere" / "campaign.db"
    (h,) = card(view(cfg, key, gone), "agm_head")
    assert h.startswith("+!") and "unreachable" in h and "no campaign.db" in h

    # unreachable too: no ledger handed to the seat at all
    (h,) = card(view(cfg, key), "agm_head")
    assert h.startswith("+!") and "no ledger reader" in h

    # failing: a row of campaign.db edited after it was anchored
    con = sqlite3.connect(db)
    con.execute("UPDATE ledger SET note='forged' WHERE id=2")
    con.commit()
    con.close()
    (h,) = card(view(cfg, key, db), "agm_head")
    assert "[blocked]" in h and "table agm_head failing" in h and "broken" in h

    # no human key: the tip is "not checked here", an unreachable session card,
    # never a quiet pass and never "waiting"
    (s,) = card(view(cfg, None, db), "verdict session")
    assert s.startswith("+!") and "tip seal not checked here" in s
    (w,) = card(view(cfg, None, db), "wager")
    assert "escalate to human" in w  # without the key nothing counts


def test_an_unreachable_outcome_seal_is_an_unreachable_wager_card(loop):
    import dataclasses

    cfg = loop["cfg"]
    stage_tip(loop)
    stage_play(loop)
    stage_seal_beat(loop)
    stage_outcome(loop)
    stage_head(loop)
    keys = json.loads(cfg.keys.read_text())
    del keys["human"]  # this box can no longer check the outcome's proof
    k2 = loop["tmp"] / "k2" / "keys.json"
    k2.parent.mkdir(mode=0o700)
    k2.write_text(json.dumps(keys))
    k2.chmod(0o600)
    (w,) = card(view(dataclasses.replace(cfg, keys=k2)), "wager")
    assert w.startswith("+!") and "unreachable" in w and "wager f1 seal" in w


def test_a_broken_chain_is_said_in_the_wager_card_not_hidden(loop):
    stage_tip(loop)
    path = loop["cfg"].box / "record.jsonl"
    lines = path.read_text().splitlines()
    row = json.loads(lines[1])
    row["ts"] = "2000-01-01T00:00:00Z"  # an edit, not a re-chain
    lines[1] = json.dumps(row, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n")
    (w,) = card(view(loop["cfg"], loop["key"]), "wager")
    assert "the record is broken" in w


# ═════════════════ a surface line that would show a seed or key ═════════════════
def test_no_seed_and_no_key_reach_the_screen(loop):
    cfg, key = loop["cfg"], loop["key"]
    stage_tip(loop)
    stage_play(loop)
    stage_seal_beat(loop)
    stage_outcome(loop)
    stage_head(loop)
    st, out = seat(cfg, key=key, db=loop["db"])
    st.status("what's on the table")
    st.checkout()
    screen = "\n".join(out)
    assert "TABLE" in screen and "agm_head satisfied" in screen
    rec = (cfg.box / "record.jsonl").read_text()
    for secret in (SEED, HUMAN_KEY.hex(), HUMAN_KEY.decode(), SEED[:16]):
        assert secret not in screen
    for secret in (HUMAN_KEY.hex(), HUMAN_KEY.decode()):
        assert secret not in rec
    # W4 break 1: the seed is the beacon round's randomness, public once the
    # round fires; the record holds it on the session's open row only
    holding = [json.loads(x) for x in rec.splitlines() if SEED in x]
    assert [(r["kind"], r.get("what")) for r in holding] == [("verdict", "open")]


def test_a_poisoned_needs_line_is_scrubbed_before_it_is_a_box(loop):
    """A record whose text carries a key or seed (a reason a model wrote) is
    never put on the screen, even though the seat cannot tell it from a hash."""
    cfg, key = loop["cfg"], loop["key"]
    real = sc.load_bot(sc.bot_root())

    class Poisoned:
        def __getattr__(self, name):
            return getattr(real.api, name)

        def needs(self, c, **kw):
            got = real.api.needs(c, **kw)
            got["needs"].append(
                f"wager f1 escalate to human · seed: {SEED[:30]} key={HUMAN_KEY.hex()}"
            )
            return got

    out: list[str] = []
    bot = sc.Bot(Poisoned(), real.cut, real.subject, real.piece_chars, real.claims)
    st = sc.Seat(
        bot,
        cfg,
        read=lambda p: (_ for _ in ()).throw(EOFError()),
        write=out.append,
        color=False,
        human_key=key,
    )
    st.status("what's on the table")
    screen = "\n".join(out)
    assert SEED[:30] not in screen and HUMAN_KEY.hex() not in screen
    assert "[withheld]" in screen


# ═══════════ the narrator on the served table, with an injectable say ═══════════
def serve_verdicts(L) -> dict:
    cfg = L["cfg"]
    card_ = api.scope(cfg, by=("what",), match={"what": "verdict"})
    assert card_["code"] == 0
    for sub in card_["ids"]:  # the human seals each table's own hash: human-sealed
        run, _ = api._open(cfg, "needs", ("needs",))
        run.rec.append(
            "seal",
            gate.human(sub, proof(sub), HUMAN_KEY),
            where=sub,
            subject=sub,
            proof=proof(sub),
        )
    assert api.seal_scope(cfg, card_["subject"], proof=proof(card_["subject"]))[
        "sealed"
    ]
    doc = api.serve(cfg, card_["spec"], max_chars=CAP)["doc"]
    assert doc["state"] == "populated", doc
    return doc


def test_the_seat_narrates_the_served_table_and_strikes_an_invented_roll(loop):
    stage_tip(loop)
    stage_play(loop)
    doc = serve_verdicts(loop)
    boxes = tb.served_boxes(doc)
    rolls = [b for b in tb.facts(boxes) if b.label == "roll"]
    assert rolls
    good = tb.code_sentence(tb.facts(boxes))  # code's own sentence: a valid reply

    st, out = seat(loop["cfg"], say=lambda prompt: good, doc=doc)
    st.table_story("what happened at the table")
    text = "\n".join(out)
    assert "[struck]" not in text and "agent> " in text
    assert text.count("✓") == len(tb.TABLE_CHECK_NAMES)

    # a model that invents a number: struck, code stands, nothing is written
    n_rows = len(box_rows(loop["cfg"]))
    import re

    bad = re.sub(r"rolled \d+", "rolled 99", good, count=1)
    assert bad != good
    st, out = seat(loop["cfg"], say=lambda prompt: bad, doc=doc)
    st.table_story("what happened at the table")
    text = "\n".join(out)
    assert "[struck]" in text and "replaced by a code sentence" in text
    assert "rolled 99" not in text.split("[struck]")[1]
    assert len(box_rows(loop["cfg"])) == n_rows

    # the seals and the escalated picks in the doc are shown, never said
    no_model, out = seat(loop["cfg"], say=None, doc=doc)
    no_model.table_story("what happened at the table")
    assert "no model asked" in "\n".join(out)


# ═══════════════════ T-mai-2: rules by exact phase, in the same box ═════════════
RULES = (
    "@markdownai v1.0\n\n# Table rules\n\n"
    "@phase R-weak\nA weak hit (7-9)  lands, but it costs.\n\n"
    "@phase R-miss\nA miss (6-) gives the GM a move.\n"
)


def test_rules_by_phase_are_verbatim_only_when_sealed_and_exact(loop):
    cfg = loop["cfg"]
    stage_tip(loop)
    stage_play(loop)
    card_ = api.scope(cfg, by=("who",), match={"who": "table"})
    assert api.seal_scope(cfg, card_["subject"], proof=proof(card_["subject"]))[
        "sealed"
    ]
    ids = [
        t["id"] for t in api.serve(cfg, card_["spec"], max_chars=CAP)["doc"]["tables"]
    ]
    prop = json.dumps(
        {
            "path": "rules/table.md",
            "data": RULES,
            "cites": ids[:1],
            "claim": "the rules",
        }
    )
    (p,) = api.take_proposals(cfg, [prop])["out"]["proposals"]
    assert api.rules(cfg, p["subject"])["code"] == 1  # unsealed: no rows
    assert api.seal_proposal(cfg, p["subject"], proof=proof(p["subject"]))["sealed"]
    assert api.rules(cfg, p["subject"])["count"] == 2

    rc = api.scope(cfg, by=("what",), match={"what": "rules"})
    assert api.seal_scope(cfg, rc["subject"], proof=proof(rc["subject"]))["sealed"]
    served = api.serve(cfg, rc["spec"], max_chars=CAP)["doc"]

    def never(*a, **k):
        raise AssertionError("a model was asked")

    ok = api.escalate(cfg, "table.rules: @phase R-weak", rung=never)
    assert ok["d0"]["status"] == "verbatim"
    assert ok["pieces"][0]["rows"] == [
        {"status": "verbatim", "answer": "A weak hit (7-9)  lands, but it costs."}
    ]
    assert ok["pieces"][0]["cites"] == [served["tables"][0]["id"]]
    for task in (
        "table.rules: @phase r-weak",
        "table.rules: @phase  R-weak",
        "table.rules: @phase R-weak ",
        "table.rules: @phase R-missing",
    ):
        out = api.escalate(cfg, task, rung=never, piece_chars=10**6)
        if task.endswith("R-weak "):  # outer whitespace is the task's, not the name's
            assert out["d0"]["status"] == "verbatim"
        else:
            assert (
                out["d0"]["status"] == "escalate" and out["card"]["route"] == "willow"
            )


# ═══════════════ T-cbm-1: a code cite in a model sentence, real graph ═══════════
needs_cbm = pytest.mark.skipif(
    not os.access(graph.cbm_path(), os.X_OK), reason="cbm is not here"
)


def git(root, *args, date=None):
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    if date:
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = date
    subprocess.run(
        ["git", "-C", str(root), *args], check=True, env=env, capture_output=True
    )


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setenv("CBM_CACHE_DIR", str(tmp_path / "cbm-cache"))
    root = tmp_path / "graphrepo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    (root / "gate.py").write_text(
        "def check_claims(t):\n    return t\n\n\nclass Run:\n    pass\n"
    )
    git(root, "add", ".")
    git(root, "commit", "-qm", "one")
    return root


def sentence_seat(cfg, symbols):
    real = sc.load_bot(sc.bot_root())
    out: list[str] = []
    bot = sc.Bot(
        real.api, real.cut, real.subject, real.piece_chars, real.claims, symbols
    )
    box = sc.Box("b1", "you", "needs you", "gate.py check_claimz needs a look")
    forged = "gate.py:check_claimz needs a look [b1]."
    honest = "gate.py:check_claims needs a look [b1]."
    st = sc.Seat(
        bot,
        cfg,
        say=lambda prompt: forged if st.which == "forged" else honest,
        read=lambda p: (_ for _ in ()).throw(EOFError()),
        write=out.append,
        color=False,
    )
    st.which = "forged"
    return st, out, box


@needs_cbm
def test_a_forged_symbol_cite_is_struck_a_stale_graph_is_unchecked(loop, repo):
    assert graph.reindex(repo)["state"] == "populated"
    project = next(
        p["name"]
        for p in json.loads(
            subprocess.run(
                [graph.cbm_path(), "list_projects", "{}"],
                capture_output=True,
                text=True,
            ).stdout
        )["projects"]
        if p["root_path"] == str(repo)
    )
    reader = lambda s_: graph.symbols_for(s_, project)  # noqa: E731

    st, out, box = sentence_seat(loop["cfg"], reader)
    st.converse("forged", [box], "check it")
    text = "\n".join(out)
    assert "[struck]" in text and "✗ every cite was served" in text
    assert len(say_mod.CHECK_NAMES) == 4

    st, out, box = sentence_seat(loop["cfg"], reader)
    st.which = "honest"
    box.value = "gate.py check_claims needs a look"
    st.converse("honest", [box], "check it")
    text = "\n".join(out)
    assert "[struck]" not in text and "note ·" not in text

    # the checkout moves after the index was made: stale -> unchecked, said
    (repo / "gate.py").write_text("def check_claims(t):\n    return 2\n")
    git(
        repo,
        "commit",
        "-qam",
        "two",
        date=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 3600)),
    )
    st, out, box = sentence_seat(loop["cfg"], reader)
    st.converse("stale", [box], "check it")
    text = "\n".join(out)
    assert "[struck]" not in text and "note · unchecked: gate.py:check_claimz" in text
    assert "graph stale" in text

    # cbm gone: unchecked and says so, never a pass and never empty
    def gone(s_):
        return graph.symbols_for(
            s_, project, runner=graph.cbm_runner("/nonexistent/cbm")
        )

    st, out, box = sentence_seat(loop["cfg"], gone)
    st.converse("gone", [box], "check it")
    text = "\n".join(out)
    assert "[struck]" not in text and "graph unreachable" in text


@needs_cbm
def test_a_bare_name_is_never_a_symbol_cite(loop, repo):
    assert graph.reindex(repo)["state"] == "populated"
    got = say_mod.symbol_rows(
        "`check_claimz` and `Run`",
        sc.load_bot(sc.bot_root()).claims,
        lambda s_: graph.symbols_for(s_, "x"),
    )
    assert got == []


# ═════════════ B1 and Q1: a broken chain, and a box that is only watched ═════════
def snapshot(cfg):
    return {
        str(p): p.read_bytes()
        for d in (cfg.box, cfg.keys.parent)
        for p in sorted(d.rglob("*"))
        if p.is_file()
    }


def test_B1_a_forged_session_breaks_the_chain_and_the_seat_shows_the_table_unreachable(
    loop,
):
    cfg, key = loop["cfg"], loop["key"]
    stage_tip(loop)
    stage_play(loop)
    stage_seal_beat(loop)
    stage_outcome(loop)
    stage_head(loop)
    assert card(view(cfg, key, loop["db"]), "agm_head")[0].count(
        "satisfied"
    )  # sound first
    path = cfg.box / "record.jsonl"
    lines = path.read_text().splitlines()
    for i, ln in enumerate(lines):
        r = json.loads(ln)
        if r["kind"] == "verdict" and r.get("who") == "table" and r.get("session"):
            r["session"] = "FORGED-SESSION"
            lines[i] = json.dumps(r, separators=(",", ":"))
            break
    path.write_text("\n".join(lines) + "\n")
    t = view(cfg, key, loop["db"])
    (g,) = card(t, "table")
    assert g.startswith("+!") and "unreachable — table: chain broken at row" in g
    assert not card(t, "verdict session") and not card(t, "agm_head")
    assert "[decided]" not in t and "satisfied" not in t
    assert "covered by your sealed tip" not in t
    for k in (None, key):  # with or without the key the table is not decided
        assert card(view(cfg, k, loop["db"]), "table")


def test_Q1_a_second_box_is_watched_by_peek_and_not_a_byte_changes(loop):
    import dataclasses

    cfg, key = loop["cfg"], loop["key"]
    stage_tip(loop)
    stage_play(loop)
    stage_seal_beat(loop)
    stage_outcome(loop)
    stage_head(loop)
    # the seat's own box is something else; the table box is only watched
    own_dir = loop["tmp"] / "own"
    own_dir.mkdir()
    own = make_cfg(own_dir)
    assert api.checkin(own)["code"] == 0
    before = snapshot(cfg)
    bot = sc.load_bot(sc.bot_root())

    def watch(table_cfg):
        out: list[str] = []
        st = sc.Seat(
            bot,
            own,
            read=lambda p: "",
            write=out.append,
            color=False,
            human_key=key,
            read_head=sc.ledger_reader(str(loop["db"]), TABLE),
            table_cfg=table_cfg,
        )
        st.status("what's on the table")
        st.status("where are we")
        return "\n".join(out)

    on = watch(cfg)  # a beacon reader is configured on the table box's Config
    assert snapshot(cfg) == before  # not a byte of the table box or its keys moved
    assert "wager f1 reconciled" in card(on, "wager")[0]
    assert card(on, "verdict session") and card(on, "agm_head")
    assert not card(on, "beacon")
    # R23: the CLI is offline unless asked; the seat says so, and no outcome is shown real
    off = watch(dataclasses.replace(cfg, beacon=None))
    assert snapshot(cfg) == before
    b = card(off, "beacon")[0]
    assert "beacon reader off: table outcomes unreachable" in b and b.startswith("+!")
    assert "wager f1 reconciled" not in "".join(card(off, "wager"))
    # the same box read by api.needs is NOT byte-stable: it writes its invocation row
    api.needs(cfg, human_key=key)
    assert snapshot(cfg) != before
