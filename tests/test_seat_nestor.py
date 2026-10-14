# b17: GRSNT ΔΣ=42
"""Tests for the seat's read-only Nestor reader (``grove/seat_nestor.py``).

The fixtures are built here with Nestor's real column names (``tm_pairs`` and
``tm_rejections`` in ``nestor/sqlite_store.py``); nothing imports Nestor.
"""

from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path

import pytest

from grove import seat_boxes, seat_nestor
from grove.seat_nestor import read_store

PAIRS = """CREATE TABLE tm_pairs (
    id TEXT PRIMARY KEY, source_text TEXT NOT NULL, source_norm TEXT NOT NULL,
    source_lang TEXT NOT NULL, target_text TEXT NOT NULL, target_lang TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft', verifier TEXT NOT NULL DEFAULT '',
    weight REAL NOT NULL DEFAULT 1.0, origin TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL, seal_sig TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '', superseded_by TEXT NOT NULL DEFAULT '',
    visibility TEXT NOT NULL DEFAULT 'internal')"""
REJS = """CREATE TABLE tm_rejections (
    id TEXT PRIMARY KEY, query_norm TEXT NOT NULL, source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL, pair_id TEXT NOT NULL DEFAULT '',
    target_text TEXT NOT NULL DEFAULT '', verifier TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL,
    reject_sig TEXT NOT NULL DEFAULT '', reopen_when TEXT NOT NULL DEFAULT '')"""
FIX = "fixture:test-box"
HER = "I settled it once so I stop looking at it."


def pair(
    n, src, tgt, status="sealed", who="ana", origin=FIX, reason="", sup="", at=None
):
    return (
        f"p{n}",
        src,
        src.lower(),
        "es",
        tgt,
        "en",
        status,
        who if status == "sealed" else "",
        origin,
        at or f"2026-01-{n:02d}T00:00:00",
        reason,
        sup,
    )


def make(path: Path, pairs=(), rejs=(), schema=(PAIRS, REJS)) -> Path:
    con = sqlite3.connect(path)
    for ddl in schema:
        con.execute(ddl)
    if "tm_pairs" in "".join(schema):
        con.executemany(
            "INSERT INTO tm_pairs (id, source_text, source_norm, source_lang, "
            "target_text, target_lang, status, verifier, origin, created_at, "
            "reason, superseded_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            pairs,
        )
    if "tm_rejections" in "".join(schema):
        con.executemany(
            "INSERT INTO tm_rejections (id, query_norm, source_lang, target_lang, "
            "target_text, verifier, reason, created_at, reopen_when) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            rejs,
        )
    con.commit()
    con.close()
    return path


def by_kind(r, kind):
    return [b for b in r.boxes if b.kind == kind and b.state == "populated"]


def test_unset_path_is_unreachable_not_empty():
    for p in (None, "", "   "):
        r = read_store(p)
        assert r.state == "unreachable" and "no Nestor store is configured" in r.reason
        assert [b.state for b in r.boxes] == ["unreachable"]


def test_missing_file_is_unreachable_with_the_path(tmp_path):
    r = read_store(tmp_path / "nope.db")
    assert r.state == "unreachable" and "nope.db" in r.reason
    assert r.boxes[0].state == "unreachable"


def test_not_a_sqlite_file_is_unreachable(tmp_path):
    p = tmp_path / "x.db"
    p.write_text("this is not a database, it is a long enough line of text " * 20)
    r = read_store(p)
    assert r.state == "unreachable" and "not a readable Nestor store" in r.reason


def test_sqlite_without_nestor_tables_is_unreachable(tmp_path):
    p = tmp_path / "other.db"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE notes (id TEXT)")
    con.commit()
    con.close()
    r = read_store(p)
    assert r.state == "unreachable" and "not a Nestor store" in r.reason


def test_pairs_table_missing_a_needed_column_is_unreachable(tmp_path):
    p = tmp_path / "a.db"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE tm_pairs (id TEXT, source_text TEXT)")
    con.commit()
    con.close()
    r = read_store(p)
    assert r.state == "unreachable" and "target_text" in r.reason


def test_empty_store_is_empty_not_unreachable(tmp_path):
    r = read_store(make(tmp_path / "e.db"))
    assert r.state == "empty" and "no pairs" in r.reason
    assert [b.state for b in r.boxes] == ["empty"]
    assert seat_boxes.plain_line(r.boxes[0]).startswith("Nestor store is empty")


def test_three_states_render_distinctly(tmp_path):
    full = make(tmp_path / "f.db", [pair(1, "Hola", "Hello")])
    cards = [
        seat_boxes.render_box(read_store(x).boxes[0])
        for x in (None, make(tmp_path / "e.db"), full)
    ]
    assert [c.split()[0] for c in cards] == ["+!", "+.", "+-"]


def test_sealed_pair_is_decided_with_her_reason_exact(tmp_path):
    p = make(tmp_path / "s.db", [pair(1, "Hola", "Hello", reason=HER)])
    r = read_store(p)
    (dec,) = by_kind(r, "dec")
    assert dec.value == "Hola → Hello"
    assert f'reason: "{HER}"' in dec.detail and "sealed by ana" in dec.detail
    assert r.counts["sealed"] == r.counts["live_sealed"] == 1


def test_fixture_tag_is_kept_on_every_pair_box(tmp_path):
    rows = [
        pair(1, "Hola", "Hello", reason="r"),
        pair(2, "Adios", "Bye", status="draft", reason="r"),
        pair(3, "Uno", "One", reason="r", sup="p4"),
        pair(4, "Uno", "1", reason="r"),
    ]
    r = read_store(make(tmp_path / "f.db", rows))
    for b in r.boxes:
        text = f"{b.label}\n{b.detail}"
        assert FIX in text or "fixture" in text, b
    pairs_only = [b for b in r.boxes if b.kind in ("dec", "pr")]
    assert all(FIX in b.detail and "(fixture)" in b.label for b in pairs_only)
    assert r.fixtures == [FIX]


def test_real_origin_is_not_tagged_as_fixture(tmp_path):
    r = read_store(make(tmp_path / "r.db", [pair(1, "Hola", "Hello", origin="")]))
    assert r.fixtures == []
    assert all("fixture" not in f"{b.label}{b.detail}{b.value}" for b in r.boxes)


def test_rejections_carry_the_fixture_store_tag(tmp_path):
    rej = ("r1", "hola", "es", "en", "Howdy", "ana", "No.", "2026-02-01", "")
    r = read_store(make(tmp_path / "j.db", [pair(1, "Hola", "Hello")], [rej]))
    (blk,) = by_kind(r, "block")
    assert "fixture" in blk.label and "origin not recorded" in blk.detail


def test_draft_is_never_said_as_fact(tmp_path):
    rows = [pair(1, "Adios", "Bye", status="draft", reason="not sure")]
    r = read_store(make(tmp_path / "d.db", rows))
    (d,) = [b for b in r.boxes if "draft" in b.label]
    assert d.kind == "pr" and d.value == "Adios (draft)"
    assert "nobody has confirmed it" in d.detail and "Bye" in d.detail
    assert d.value.endswith("(draft)") and "→" not in d.value
    say = seat_boxes.compose(r.boxes)
    assert "adios (draft)" in say.lower() and "→" not in say.split(";")[0]
    assert not by_kind(r, "dec")


def test_drafts_can_be_raised_to_needs_you_by_the_caller(tmp_path):
    p = make(tmp_path / "y.db", [pair(1, "Adios", "Bye", status="draft")])
    assert [b.kind for b in read_store(p).boxes if "draft" in b.label] == ["pr"]
    r = read_store(p, drafts_as="you")
    assert [b.kind for b in r.boxes if "draft" in b.label] == ["you"]


def test_replaced_row_is_changed_with_both_reasons_exact(tmp_path):
    rows = [
        pair(1, "Me hago cargo", "I will handle it", reason="First reading.", sup="p2"),
        pair(2, "Me hago cargo", "I understand", reason="It was her mother."),
    ]
    r = read_store(make(tmp_path / "c.db", rows))
    (ch,) = [b for b in by_kind(r, "pr") if b.label.startswith("changed")]
    assert ch.value == 'Me hago cargo: "I will handle it" was replaced'
    assert 'reason then: "First reading."' in ch.detail
    assert 'reason now: "It was her mother."' in ch.detail
    assert 'now: "I understand"' in ch.detail
    assert [c["live_sealed"] for c in [r.counts]] == [1] and r.counts["replaced"] == 1


def test_rejection_is_blocked_verbatim_and_not_yet_keeps_her_condition(tmp_path):
    rejs = [
        ("r1", "hola", "es", "en", "Howdy", "ana", "Too American.", "2026-02-01", ""),
        (
            "r2",
            "casa",
            "es",
            "en",
            "the house",
            "ana",
            "A guess.",
            "2026-02-02",
            "if I find the photo",
        ),
    ]
    r = read_store(make(tmp_path / "b.db", rejs=rejs))
    no, yet = by_kind(r, "block")
    assert no.value == '"Howdy" for hola' and 'reason: "Too American."' in no.detail
    assert no.label.startswith("a no")
    assert yet.label.startswith("not yet")
    assert 'reopen when: "if I find the photo"' in yet.detail
    assert r.counts["rejected"] == 2 and r.counts["not_yet"] == 1


def test_retired_baseline_is_history_not_a_draft_waiting(tmp_path):
    row = pair(1, "200", "200", status="draft", origin="unsealed:ana:superseded by 250")
    row = row[:7] + ("ana",) + row[8:]
    r = read_store(make(tmp_path / "t.db", [row]))
    assert r.counts["retired"] == 1 and r.counts["waiting"] == 0
    (b,) = [b for b in r.boxes if "retired" in b.label]
    assert b.value == "200 (retired)" and "unsealed:ana" in b.detail


def test_order_is_stable_and_ranked(tmp_path):
    rows = [
        pair(3, "C", "c", reason="r3"),
        pair(1, "A", "a", reason="r1"),
        pair(2, "B", "b", status="draft"),
    ]
    rej = ("r1", "q", "es", "en", "x", "ana", "n", "2026-03-01", "")
    p = make(tmp_path / "o.db", rows, [rej])
    r = read_store(p)
    assert [b.kind for b in r.boxes] == ["block", "dec", "dec", "pr", "pass"]
    assert [b.value for b in by_kind(r, "dec")] == ["A → a", "C → c"]
    assert [b.id for b in read_store(p).boxes] == [b.id for b in r.boxes]


def test_ids_are_short_stable_and_unique(tmp_path):
    rows = [pair(n, f"w{n}", f"t{n}") for n in range(1, 4)]
    p = make(tmp_path / "i.db", rows)
    ids = [b.id for b in read_store(p).boxes]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("n") and len(i) <= 8 for i in ids)
    assert ids == [b.id for b in read_store(p).boxes]


def test_cap_counts_the_rest_and_prefers_reasoned_rows(tmp_path):
    rows = [pair(n, f"w{n}", f"t{n}", reason=f"r{n}") for n in range(1, 8)]
    rows.append(pair(9, "bare", "bare", reason=""))  # newest, no reason
    r = read_store(make(tmp_path / "k.db", rows))
    dec = by_kind(r, "dec")
    cap = seat_nestor.CAPS["dec"]
    assert len(dec) == cap + 1 and r.omitted == {"dec": 8 - cap}
    assert dec[-1].value == f"{8 - cap} more sealed"
    assert "bare → bare" not in [b.value for b in dec]
    assert f"{r.counts['live_sealed']} sealed" in r.boxes[-1].value


def test_older_schema_without_lineage_columns_is_tolerated(tmp_path):
    old = (
        "CREATE TABLE tm_pairs (id TEXT PRIMARY KEY, source_text TEXT, "
        "target_text TEXT, status TEXT, created_at TEXT)",
    )
    p = tmp_path / "old.db"
    con = sqlite3.connect(p)
    con.execute(old[0])
    con.execute(
        "INSERT INTO tm_pairs VALUES ('a','Hola','Hello','sealed','2025-01-01')"
    )
    con.execute("INSERT INTO tm_pairs VALUES ('b','Adios','Bye','draft','2025-01-02')")
    con.commit()
    con.close()
    r = read_store(p)  # no rejections table, no reason/origin/verifier columns
    assert r.state == "populated" and r.counts["live_sealed"] == 1
    assert by_kind(r, "dec")[0].value == "Hola → Hello"
    assert "reason: none recorded" in by_kind(r, "dec")[0].detail
    assert r.fixtures == []


def test_rejections_only_store_is_populated(tmp_path):
    rej = ("r1", "q", "es", "en", "x", "ana", "n", "2026-03-01", "")
    p = make(tmp_path / "ro.db", rejs=[rej], schema=(REJS,))
    assert read_store(p).state == "populated"


def test_control_characters_in_a_stored_reason_are_dropped(tmp_path):
    p = make(tmp_path / "x.db", [pair(1, "Hola", "Hello", reason="ok\x1b[31mred")])
    detail = by_kind(read_store(p), "dec")[0].detail
    assert "\x1b" not in detail and 'reason: "ok[31mred"' in detail


def test_read_only_file_unchanged_and_a_write_fails(tmp_path):
    p = make(tmp_path / "ro.db", [pair(1, "Hola", "Hello", reason=HER)])
    before, mtime = p.read_bytes(), p.stat().st_mtime_ns
    time.sleep(0.02)
    read_store(p)
    read_store(p, drafts_as="you")
    assert p.read_bytes() == before and p.stat().st_mtime_ns == mtime
    assert not list(tmp_path.glob("ro.db-*"))  # no journal / wal left behind
    # the connection the reader opens is read-only: a write through the same
    # URI fails, so the reader could not have written even by mistake
    con = sqlite3.connect(f"{p.resolve().as_uri()}?mode=ro", uri=True)
    with pytest.raises(sqlite3.OperationalError):
        con.execute("DELETE FROM tm_pairs")
    con.close()


def test_reader_connects_read_only_and_query_only(tmp_path, monkeypatch):
    p = make(tmp_path / "m.db", [pair(1, "Hola", "Hello")])
    seen = {}
    real = sqlite3.connect

    def spy(target, *a, **kw):
        seen["target"], seen["uri"] = target, kw.get("uri")
        return real(target, *a, **kw)

    monkeypatch.setattr(seat_nestor.sqlite3, "connect", spy)
    read_store(p)
    assert seen["uri"] is True and seen["target"].endswith("?mode=ro")


def test_unreadable_directory_is_unreachable(tmp_path):
    r = read_store(tmp_path)  # a directory, not a file
    assert r.state == "unreachable"


SHOEBOX = Path("/tmp/claude-0/demobox/shoebox/nestor.db")


@pytest.mark.skipif(
    not SHOEBOX.exists(),
    reason="demo check only: needs the kept Nestor shoebox "
    "(demo/shoebox.py --keep /tmp/claude-0/demobox/shoebox); not a gate",
)
def test_kept_shoebox_demo_store_reads_sensibly():
    before = SHOEBOX.stat().st_mtime_ns
    r = read_store(SHOEBOX)
    assert r.state == "populated"
    assert r.counts["sealed"] == 15 and r.counts["draft"] == 4
    assert r.counts["rejected"] == 2 and r.counts["not_yet"] == 1
    assert r.fixtures == ["fixture:consuelo-shoebox"]
    assert len(by_kind(r, "block")) == 2
    assert seat_boxes.compose(r.boxes, first=True)
    assert SHOEBOX.stat().st_mtime_ns == before
    assert os.access(SHOEBOX, os.R_OK)
