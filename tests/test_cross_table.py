"""templates/cross-table/cross_table.py: copy, never compose; four states, never collapsed."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cross_table", ROOT / "templates/cross-table/cross_table.py"
)
ct = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ct)


def _map(tmp_path, cells, rows=None):
    m = {
        "title": "T",
        "root": ".",
        "rows": rows or [{"row": "A", "title": "Row A", "source": "src.md"}],
        "cells": cells,
    }
    p = tmp_path / "map.json"
    p.write_text(json.dumps(m))
    return p


def _cell(cell, **kw):
    return {
        "cell": cell,
        "label": kw.pop("label", cell),
        "file": "",
        "pattern": "",
        "mode": "para",
        "standing": "unattested",
        **kw,
    }


def test_new_writes_a_blank_grid_and_never_overwrites(tmp_path):
    p = tmp_path / "m.json"
    assert ct.main(["new", str(p), "--rows", "3", "--cols", "4"]) == 0
    m = json.loads(p.read_text())
    assert [c["cell"] for c in m["cells"]][:5] == ["A1", "A2", "A3", "A4", "B1"]
    assert len(m["cells"]) == 12 and all(
        c["standing"] == "unattested" for c in m["cells"]
    )
    with pytest.raises(SystemExit):
        ct.main(["new", str(p)])


def test_a_map_that_is_not_rows_by_columns_is_refused(tmp_path):
    p = _map(tmp_path, [_cell("A1"), _cell("A1")])
    with pytest.raises(SystemExit):
        ct.load_map(p)


def test_four_states_are_never_collapsed(tmp_path):
    (tmp_path / "src.md").write_text("# Head\n\n- **Rule one.** It holds.\n- Other.\n")
    p = _map(
        tmp_path,
        [
            _cell("A1", file="src.md", pattern=r"\*\*Rule one"),
            _cell("A2", note="why"),
            _cell("A3", file="missing.md", pattern="x"),
            _cell("A4", file="src.md", pattern="nowhere"),
        ],
    )
    res = {r["cell"]: r for r in ct.resolve(ct.load_map(p), tmp_path)}
    assert res["A1"]["state"] == "found"
    assert (
        res["A1"]["rule"] == "- **Rule one.** It holds."
        and res["A1"]["source"] == "`src.md`:3"
    )
    assert (
        res["A2"]["state"] == "silent" and res["A2"]["rule"] == "*source silent: why*"
    )
    assert res["A3"]["state"] == "unreachable"
    assert res["A4"]["state"] == "not_found"
    assert ct.main(["check", str(p), "--root", str(tmp_path)]) == 1


def test_modes_copy_and_never_compose(tmp_path):
    lines = [
        "## Rule 2",
        "",
        "Not a cron. The PR is when it happens.",
        "",
        "| 6 | One policy | at the soil |",
        "",
        "x = 1  # keep",
        "# a comment",
        "# continued",
    ]
    assert ct.extract(lines, r"is when", "sent") == (3, "The PR is when it happens.")
    assert ct.extract(lines, r"^\| 6 \|", "row") == (5, "6 — One policy — at the soil")
    assert ct.extract(lines, r"^## Rule 2", "head") == (
        1,
        "Rule 2: Not a cron. The PR is when it happens.",
    )
    assert ct.extract(lines, r"a comment", "line", span=2) == (8, "a comment continued")


def test_fill_writes_between_markers_and_is_deterministic(tmp_path):
    (tmp_path / "src.md").write_text("- **Rule one.** It holds.\n")
    p = _map(
        tmp_path,
        [_cell("A1", label="One", file="src.md", pattern="Rule one"), _cell("A2")],
    )
    doc = tmp_path / "out.md"
    doc.write_text("# Mine\n\nKeep this.\n")
    ct.main(["fill", str(p), str(doc)])
    expected = (
        "# Mine\n\nKeep this.\n\n"
        "## Grid\n\n<!-- cross-table:grid -->\n"
        "| | 1 | 2 |\n|---|---|---|\n| **A** Row A | One | A2 |\n"
        "<!-- /cross-table:grid -->\n\n"
        "## Sources\n\n<!-- cross-table:sources -->\n"
        "| Row | What it holds | Source |\n|---|---|---|\n| A | Row A | src.md |\n"
        "<!-- /cross-table:sources -->\n\n"
        "## Index\n\n<!-- cross-table:index -->\n"
        "| Cell | Rule | Source | Standing |\n|---|---|---|---|\n"
        "| A1 | - **Rule one.** It holds. | `src.md`:1 | unattested |\n"
        "| A2 | *source silent* | — | unattested |\n"
        "<!-- /cross-table:index -->\n"
    )
    assert doc.read_text() == expected
    ct.main(["fill", str(p), str(doc)])
    assert doc.read_text() == expected


def test_the_script_never_raises_standing(tmp_path):
    (tmp_path / "src.md").write_text("- Rule.\n")
    p = _map(
        tmp_path, [_cell("A1", file="src.md", pattern="Rule", standing="witnessed")]
    )
    (r,) = ct.resolve(ct.load_map(p), tmp_path)
    assert r["standing"] == "witnessed"
    bad = _map(tmp_path, [_cell("A1", standing="true")])
    with pytest.raises(SystemExit):
        ct.load_map(bad)


def test_a_new_grid_starts_where_the_last_one_stopped(tmp_path):
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    ct.main(["new", str(first), "--rows", "13", "--cols", "2"])
    ct.main(["new", str(second), "--rows", "4", "--cols", "2", "--after", str(first)])
    assert [r["row"] for r in json.loads(second.read_text())["rows"]] == [
        "N",
        "O",
        "P",
        "Q",
    ]


def test_two_grids_never_share_a_row_letter(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    ct.main(["new", str(a), "--rows", "2", "--cols", "1"])
    ct.main(["new", str(b), "--rows", "2", "--cols", "1"])
    with pytest.raises(SystemExit):
        ct.main(["check", str(b), "--with", str(a), "--root", str(tmp_path)])


def test_link_checks_every_address_and_copies_labels(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    ct.main(["new", str(a), "--rows", "1", "--cols", "2"])
    ct.main(["new", str(b), "--rows", "1", "--cols", "1", "--after", str(a)])
    m = json.loads(a.read_text())
    m["rows"][0]["title"] = "Rules"
    m["cells"][1]["label"] = "Two"
    a.write_text(json.dumps(m))
    links = tmp_path / "links.json"
    links.write_text(
        json.dumps({"links": [{"from": "B1", "to": ["A", "A2"], "why": "w"}]})
    )
    doc = tmp_path / "x.md"
    ct.main(["link", str(links), str(doc), "--map", str(a), "--map", str(b)])
    assert doc.read_text() == (
        "# Crosswalk\n\n## Links\n\n<!-- cross-table:links -->\n"
        "| From | To | Where they touch | Standing |\n|---|---|---|---|\n"
        "| B1 | A row: Rules · A2 Two | w | unattested |\n"
        "<!-- /cross-table:links -->\n"
    )
    links.write_text(json.dumps({"links": [{"from": "B1", "to": ["Z9"]}]}))
    with pytest.raises(SystemExit):
        ct.main(["link", str(links), str(doc), "--map", str(a), "--map", str(b)])


def test_measure_counts_the_full_passage_by_percentage(tmp_path):
    (tmp_path / "src.md").write_text("- " + "x" * 498 + "\n- yy\n")
    p = _map(
        tmp_path,
        [
            _cell("A1", file="src.md", pattern="^- x"),
            _cell("A2", file="src.md", pattern="^- yy"),
            _cell("A3"),
        ],
    )
    m = ct.load_map(p)
    results = ct.resolve(m, tmp_path)
    assert [r["size"] if "size" in r else 0 for r in results] == [500, 4, 0]
    report = ct.measure(m, results)
    assert report.splitlines()[:3] == [
        "- **Cells:** 3, of which 2 found (66.7%).",
        "- **Text:** 504 characters. An even share would be 33.33% per cell.",
        "- **Trim:** 1 cell(s) cut at 420 characters; the index keeps 84.1% of the source text.",
    ]
    assert "- **Holding nothing:** A3." in report.splitlines()
    assert ct.measure(m, results) == report
    index = ct.render(m, results, share=True)["index"].splitlines()
    assert index[0] == "| Cell | Rule | Source | Share | Standing |"
    assert index[3] == "| A2 | - yy | `src.md`:2 | 0.79% | unattested |"


def test_gini_is_zero_when_even_and_rises_when_one_box_holds_it_all():
    assert ct.gini([5, 5, 5, 5]) == 0
    assert ct.gini([0, 0, 0, 0]) == 0
    assert ct.gini([0, 0, 0, 12]) == 0.75


def test_measure_flags_fat_and_thin_and_covers_sources(tmp_path):
    (tmp_path / "src.md").write_text(
        "- " + "x" * 98 + "\n- y\n- zz\n- ww\n\n"
        "<!-- cross-table:grid -->\nnot counted\n<!-- /cross-table:grid -->\n"
    )
    p = _map(
        tmp_path,
        [
            _cell(f"A{i}", file="src.md", pattern=pat)
            for i, pat in enumerate(["^- x", "^- y", "^- zz", "^- ww"], 1)
        ],
    )
    m = ct.load_map(p)
    report = ct.measure(m, ct.resolve(m, tmp_path), tmp_path).splitlines()
    assert (
        "- **Fat** (at least 3× an even share; often several rules in one box, a candidate to split): A1."
        in report
    )
    assert (
        "- **Thin** (at most 0.25× an even share; a label with a line behind it): A2, A3, A4."
        in report
    )
    assert "| `src.md` | 4 | 111 | 114 | 97.4% |" in report


def test_a_snapshot_names_exactly_which_boxes_changed(tmp_path):
    src = tmp_path / "src.md"
    src.write_text("- one\n- two\n")
    p = _map(
        tmp_path,
        [
            _cell("A1", file="src.md", pattern="^- one"),
            _cell("A2", file="src.md", pattern="^- two"),
            _cell("A3", file="src.md", pattern="^- three"),
        ],
    )
    snap = tmp_path / "snap.json"
    ct.main(["measure", str(p), "--snapshot", str(snap)])
    with pytest.raises(SystemExit):
        ct.main(["measure", str(p), "--snapshot", str(snap)])
    src.write_text("- one, longer\n- three\n")
    m = ct.load_map(p)
    then = json.loads(snap.read_text())
    report = ct.measure(m, ct.resolve(m, tmp_path), against=then).splitlines()
    assert report[-3:] == [
        "- **Changed:** A1 (+8).",
        "- **Newly found:** A3.",
        "- **No longer found:** A2.",
    ]


def test_clauses_end_at_full_stops_and_cell_boundaries_not_list_numbers():
    assert ct.clauses(
        '6. **Bold rule.** It holds (e.g. here). "Quoted." | D10 | next cell'
    ) == ["6. **Bold rule.**", "It holds (e.g. here).", '"Quoted."', "D10", "next cell"]


def test_drip_cuts_a_fat_box_into_clauses_pinned_to_their_own_place(tmp_path):
    (tmp_path / "src.md").write_text(
        "- Phase 7 comes early.\n\n- **Big.** One clause here. Phase 7\n\n- small\n"
    )
    p = _map(
        tmp_path,
        [
            _cell("A1", file="src.md", pattern=r"\*\*Big"),
            _cell("A2", file="src.md", pattern="^- small"),
        ],
    )
    new, links, left = ct.drip([(ct.load_map(p), tmp_path)], "B", over=1.5)
    assert [r["row"] for r in new["rows"]] == ["B"] and left == []
    cells = {c["cell"]: c for c in new["cells"]}
    assert [cells[f"B{i}"]["label"] for i in (1, 2, 3)] == [
        "- Big.",
        "One clause here.",
        "Phase 7",
    ]
    assert cells["B3"]["note"] == "this clause can't be found again on its own"
    assert links == [
        {
            "from": "B",
            "to": ["A1"],
            "why": "Dripped from A1: its passage cut into clauses, each copied again from the source.",
            "standing": "unattested",
        }
    ]
    new["root"] = "."
    out = tmp_path / "drip.json"
    out.write_text(json.dumps(new))
    res = {r["cell"]: r for r in ct.resolve(ct.load_map(out), tmp_path)}
    assert (
        res["B2"]["rule"] == "One clause here." and res["B2"]["source"] == "`src.md`:3"
    )
    assert res["B3"]["state"] == "silent"


def test_rows_run_on_past_z_like_spreadsheet_columns(tmp_path):
    assert [ct.row_label(i) for i in (0, 25, 26, 51, 52, 701, 702)] == [
        "A",
        "Z",
        "AA",
        "AZ",
        "BA",
        "ZZ",
        "AAA",
    ]
    assert all(ct.row_index(ct.row_label(i)) == i for i in range(800))
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    ct.main(["new", str(a), "--rows", "26", "--cols", "1"])
    ct.main(["new", str(b), "--rows", "2", "--cols", "12", "--after", str(a)])
    m = ct.load_map(b)
    assert [r["row"] for r in m["rows"]] == ["AA", "AB"] and m["_cols"][-1] == 12
