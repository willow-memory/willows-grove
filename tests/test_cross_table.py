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
