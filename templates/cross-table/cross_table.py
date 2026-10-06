#!/usr/bin/env python3
"""cross_table.py — a grid of addresses, filled by copying from sources.

The template behind docs/design/one-box/rules-cross-table-2026-10-06.md.
A map (JSON) names the grid: its rows, and for every cell a label, a
source file and a pattern that finds the source line. `fill` copies the
matching passage into the document, with file and line. Nothing is
composed: a cell whose pattern finds nothing says `not found`, and a cell
with no source says `source silent`. Same map and same files give the same
bytes. Stdlib only.

    cross_table.py new  MAP --rows 13 --cols 13 [--title T]
    cross_table.py fill MAP DOC [--root DIR]
    cross_table.py check MAP [--root DIR]

`new` writes a blank map. `fill` writes the grid, the row sources and the
index into DOC between `<!-- cross-table:… -->` markers (creating DOC if it
does not exist) and leaves everything else in DOC alone. `check` prints
every cell's result and exits 1 if any cell is `not found`.

Standing (`unattested` / `witnessed` / `sealed`) lives in the map and is
copied as-is. The script never raises it. A cell may carry `span` (lines to
take in `line` mode) and `note` (why a cell with no source is silent).
"""

from __future__ import annotations

import argparse
import json
import re
import string
import sys
from pathlib import Path

MODES = ("para", "sent", "row", "head", "line")
STANDINGS = ("unattested", "witnessed", "sealed")
CAP = 420
SECTIONS = ("grid", "sources", "index")


# ── the map ──────────────────────────────────────────────────────────────────


def blank_map(rows: int, cols: int, title: str) -> dict:
    if not 1 <= rows <= 26 or cols < 1:
        raise SystemExit("rows must be 1–26 (lettered A–Z) and cols at least 1")
    letters = string.ascii_uppercase[:rows]
    return {
        "title": title,
        "root": ".",
        "rows": [{"row": r, "title": "", "source": ""} for r in letters],
        "cells": [
            {
                "cell": f"{r}{c}",
                "label": "",
                "file": "",
                "pattern": "",
                "mode": "para",
                "standing": "unattested",
            }
            for r in letters
            for c in range(1, cols + 1)
        ],
    }


def load_map(path: Path) -> dict:
    m = json.loads(path.read_text(encoding="utf-8"))
    rows = [r["row"] for r in m["rows"]]
    cols = sorted({int(c["cell"][1:]) for c in m["cells"]})
    want = {f"{r}{c}" for r in rows for c in cols}
    have = [c["cell"] for c in m["cells"]]
    if len(have) != len(set(have)) or set(have) != want:
        raise SystemExit(f"{path}: cells must be exactly rows × columns, each once")
    for c in m["cells"]:
        if c.get("mode", "para") not in MODES:
            raise SystemExit(f"{c['cell']}: mode must be one of {MODES}")
        if c.get("standing", "unattested") not in STANDINGS:
            raise SystemExit(f"{c['cell']}: standing must be one of {STANDINGS}")
    m["_cols"] = cols
    return m


# ── reading a source ─────────────────────────────────────────────────────────

_LIST = re.compile(r"(- |\* |\d+[a-z]?\. |>)")


def blocks(lines: list[str]) -> list[tuple[int, list[str]]]:
    """Headings, table rows and list items each start a block; other lines
    continue the current one; a blank line ends it."""
    out: list[tuple[int, list[str]]] = []
    cur = None
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            cur = None
            continue
        starts = (
            s.startswith(("#", "|"))
            or _LIST.match(s)
            or (cur and cur[1][-1].strip().startswith("|"))
        )
        if cur is None or starts:
            cur = (i, [])
            out.append(cur)
        cur[1].append(line)
    return out


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract(
    lines: list[str], pattern: str, mode: str, span: int = 1
) -> tuple[int, str] | None:
    """(line number, copied text) for the first match, or None. `line` takes
    `span` lines from the match, with comment markers stripped (for code)."""
    if mode == "line":
        rx = re.compile(pattern)
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                got = [
                    ln.strip().lstrip("#").strip() for ln in lines[i - 1 : i - 1 + span]
                ]
                return i, flat(" ".join(g for g in got if g))
        return None
    blks = blocks(lines)
    rx = re.compile(pattern.replace(" ", r"\s+"), re.M)
    for idx, (start, bl) in enumerate(blks):
        joined = "\n".join(bl)
        m = rx.search(joined)
        if not m:
            continue
        line_no = start + joined[: m.start()].count("\n")
        text = flat(joined)
        if mode == "row":
            cells = [c.strip() for c in bl[0].strip().strip("|").split("|")]
            return line_no, " — ".join(c for c in cells if c)
        if mode == "head":
            body = flat("\n".join(blks[idx + 1][1])) if idx + 1 < len(blks) else ""
            head = flat(bl[0]).lstrip("#").strip()
            return line_no, f"{head}: {body}" if body else head
        if mode == "sent":
            sents = re.split(r"(?<=[.!?]\*\*)\s+|(?<=[.!?])\s+(?=[A-Z*\"“(`])", text)
            srx = re.compile(pattern.lstrip("^"))
            hit = [s for s in sents if srx.search(s)]
            return line_no, " ".join(hit) if hit else text
        return line_no, text
    return None


def resolve(m: dict, root: Path) -> list[dict]:
    """One result per cell: cell, label, rule, source, standing."""
    cache: dict[str, list[str] | None] = {}
    out = []
    for c in m["cells"]:
        res = {
            "cell": c["cell"],
            "label": c.get("label", ""),
            "standing": c.get("standing", "unattested"),
        }
        f, pat = c.get("file", ""), c.get("pattern", "")
        if not f or not pat:
            note = c.get("note", "")
            res.update(
                rule=f"*source silent{': ' + note if note else ''}*",
                source="—",
                state="silent",
            )
            out.append(res)
            continue
        if f not in cache:
            p = root / f
            cache[f] = (
                p.read_text(encoding="utf-8").splitlines() if p.is_file() else None
            )
        if cache[f] is None:
            res.update(
                rule="*unreachable: file not found*",
                source=f"`{f}`",
                state="unreachable",
            )
            out.append(res)
            continue
        got = extract(cache[f], pat, c.get("mode", "para"), int(c.get("span", 1)))
        if got is None:
            res.update(rule="*not found*", source=f"`{f}`", state="not_found")
        else:
            line_no, text = got
            if len(text) > CAP:
                text = text[:CAP].rsplit(" ", 1)[0] + " …"
            res.update(rule=text, source=f"`{f}`:{line_no}", state="found")
        out.append(res)
    return out


# ── writing the document ─────────────────────────────────────────────────────


def esc(s: str) -> str:
    return s.replace("|", "\\|")


def render(m: dict, results: list[dict]) -> dict[str, str]:
    cols = m["_cols"]
    by = {r["cell"]: r for r in results}
    grid = ["| | " + " | ".join(map(str, cols)) + " |", "|---" * (len(cols) + 1) + "|"]
    for r in m["rows"]:
        head = f"**{r['row']}** {r['title']}".strip()
        grid.append(
            f"| {esc(head)} | "
            + " | ".join(esc(by[f"{r['row']}{c}"]["label"]) for c in cols)
            + " |"
        )
    src = ["| Row | What it holds | Source |", "|---|---|---|"]
    src += [
        f"| {r['row']} | {esc(r['title'])} | {esc(r['source'])} |" for r in m["rows"]
    ]
    idx = ["| Cell | Rule | Source | Standing |", "|---|---|---|---|"]
    idx += [
        f"| {r['cell']} | {esc(r['rule'])} | {esc(r['source'])} | {r['standing']} |"
        for r in results
    ]
    return {"grid": "\n".join(grid), "sources": "\n".join(src), "index": "\n".join(idx)}


def splice(doc: str, parts: dict[str, str]) -> str:
    for name in SECTIONS:
        start, end = f"<!-- cross-table:{name} -->", f"<!-- /cross-table:{name} -->"
        block = f"{start}\n{parts[name]}\n{end}"
        if start in doc and end in doc:
            doc = doc[: doc.index(start)] + block + doc[doc.index(end) + len(end) :]
        else:
            doc = doc.rstrip("\n") + f"\n\n## {name.capitalize()}\n\n{block}\n"
    return doc


# ── commands ─────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("map", type=Path)
    n.add_argument("--rows", type=int, default=13)
    n.add_argument("--cols", type=int, default=13)
    n.add_argument("--title", default="")
    f = sub.add_parser("fill")
    f.add_argument("map", type=Path)
    f.add_argument("doc", type=Path)
    f.add_argument("--root", type=Path)
    c = sub.add_parser("check")
    c.add_argument("map", type=Path)
    c.add_argument("--root", type=Path)
    a = ap.parse_args(argv)

    if a.cmd == "new":
        if a.map.exists():
            raise SystemExit(f"{a.map} exists; a map is never overwritten")
        a.map.write_text(
            json.dumps(blank_map(a.rows, a.cols, a.title), indent=1, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {a.map}: {a.rows} × {a.cols}")
        return 0

    m = load_map(a.map)
    root = a.root or (a.map.parent / m.get("root", ".")).resolve()
    results = resolve(m, root)
    counts = {
        s: sum(r["state"] == s for r in results)
        for s in ("found", "silent", "unreachable", "not_found")
    }
    if a.cmd == "check":
        for r in results:
            print(
                f"{r['cell']:>4} | {r['state']:<11} | {r['source']} | {r['rule'][:120]}"
            )
        print(json.dumps(counts))
        return 1 if counts["not_found"] or counts["unreachable"] else 0

    doc = (
        a.doc.read_text(encoding="utf-8")
        if a.doc.exists()
        else f"# {m.get('title') or 'Cross table'}\n"
    )
    a.doc.write_text(splice(doc, render(m, results)), encoding="utf-8")
    print(f"filled {a.doc}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
