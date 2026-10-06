#!/usr/bin/env python3
"""cross_table.py — a grid of addresses, filled by copying from sources.

The template behind docs/design/one-box/rules-cross-table-2026-10-06.md.
A map (JSON) names the grid: its rows, and for every cell a label, a
source file and a pattern that finds the source line. `fill` copies the
matching passage into the document, with file and line. Nothing is
composed: a cell whose pattern finds nothing says `not found`, and a cell
with no source says `source silent`. Same map and same files give the same
bytes. Stdlib only.

    cross_table.py new  MAP --rows 13 --cols 13 [--title T] [--after EARLIER_MAP ...]
    cross_table.py fill MAP DOC [--root DIR] [--with OTHER_MAP ...]
    cross_table.py check MAP [--root DIR] [--with OTHER_MAP ...]
    cross_table.py link LINKS DOC --map MAP [--map MAP ...]
    cross_table.py measure MAP [DOC] [--root DIR] [--with OTHER_MAP ...]
                           [--snapshot NEW.json] [--against OLD.json]

`new` writes a blank map; with `--after`, its rows start after the earlier
grids' last row, so no address is used twice. `--with` makes `check` and
`fill` refuse a map that shares a row letter with another grid. `link`
writes a crosswalk between grids: every address is checked against the maps,
and labels are copied from them. `measure` reports how much of the grid's
text each box holds, by percentage (with DOC, it writes that between
`<!-- cross-table:measure -->` markers); `fill --measure` also adds a Share
column to the index. `fill` writes the grid, the row sources and the
index into DOC between `<!-- cross-table:… -->` markers (creating DOC if it
does not exist) and leaves everything else in DOC alone. `check` prints
every cell's result and exits 1 if any cell is `not found`.

Standing (`unattested` / `witnessed` / `sealed`) lives in the map and is
copied as-is. The script never raises it. A cell may carry `span` (lines to
take in `line` mode) and `note` (why a cell with no source is silent).
"""

from __future__ import annotations

import argparse
import hashlib
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


def blank_map(rows: int, cols: int, title: str, start: str = "A") -> dict:
    """A blank grid. `start` is its first row letter: a new grid starts where
    the last one stopped, so an address names one box across every grid."""
    first = string.ascii_uppercase.find(start.upper()) if len(start) == 1 else -1
    if first < 0 or rows < 1 or first + rows > 26 or cols < 1:
        raise SystemExit(
            "rows must fit in A–Z from --start, and cols must be at least 1"
        )
    letters = string.ascii_uppercase[first : first + rows]
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


def rows_of(m: dict) -> set[str]:
    return {r["row"] for r in m["rows"]}


def next_row(earlier: list[Path]) -> str:
    """The first row letter after every earlier grid's last row."""
    used = set().union(*(rows_of(load_map(p)) for p in earlier)) if earlier else set()
    if not used:
        return "A"
    i = max(string.ascii_uppercase.index(r) for r in used) + 1
    if i >= 26:
        raise SystemExit("the earlier grids use every row letter A–Z")
    return string.ascii_uppercase[i]


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
            res["size"] = len(text)
            res["file"] = f
            res["sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if len(text) > CAP:
                text = text[:CAP].rsplit(" ", 1)[0] + " …"
            res.update(rule=text, source=f"`{f}`:{line_no}", state="found")
        out.append(res)
    return out


# ── writing the document ─────────────────────────────────────────────────────


def esc(s: str) -> str:
    return s.replace("|", "\\|")


FAT, THIN = 3.0, 0.25


def gini(values: list[int]) -> float:
    """0 when every box holds the same; towards 1 when one box holds it all."""
    xs, n = sorted(values), len(values)
    total = sum(xs)
    if not n or not total:
        return 0.0
    return 2 * sum(i * x for i, x in enumerate(xs, 1)) / (n * total) - (n + 1) / n


def snapshot(m: dict, results: list[dict]) -> dict:
    """What `measure --snapshot` saves: each cell's size and the sha256 of its
    full passage, so a later run can say exactly which boxes changed."""
    return {
        "title": m.get("title", ""),
        "cells": {
            r["cell"]: {"size": r.get("size", 0), "sha256": r.get("sha256", "")}
            for r in results
        },
    }


def measure(
    m: dict,
    results: list[dict],
    root: Path | None = None,
    others: list[tuple[str, list[dict]]] | None = None,
    against: dict | None = None,
) -> str:
    """How much of the grid's text each box holds, by percentage. A cell's
    size is its full copied passage in characters (whitespace collapsed,
    before the trim); a cell that isn't `found` is 0. Then: how evenly the
    text is spread, which boxes are fat or thin, how much of each source the
    grid draws on (with `root`), each grid's part of the whole (with
    `others`), and which boxes changed since a snapshot (with `against`).
    Same map, same files, same numbers."""
    sizes = {r["cell"]: r.get("size", 0) for r in results}
    total = sum(sizes.values())
    n, found = len(results), sum(r["state"] == "found" for r in results)
    pct = (lambda v: f"{v / total:.2%}") if total else (lambda v: "—")
    kept = sum(min(v, CAP) for v in sizes.values())
    trimmed = sum(v > CAP for v in sizes.values())
    out = [
        f"- **Cells:** {n}, of which {found} found ({found / n:.1%}).",
        f"- **Text:** {total} characters. An even share would be {1 / n:.2%} per cell.",
        f"- **Trim:** {trimmed} cell(s) cut at {CAP} characters; the index keeps "
        + (f"{kept / total:.1%}" if total else "—")
        + " of the source text.",
        "",
        "| Row | What it holds | Found | Characters | Share | Largest cell |",
        "|---|---|---|---|---|---|",
    ]
    for r in m["rows"]:
        mine = {c: v for c, v in sizes.items() if c[0] == r["row"]}
        row_total = sum(mine.values())
        big = max(mine, key=lambda c: (mine[c], -int(c[1:]))) if row_total else "—"
        hit = sum(by["state"] == "found" for by in results if by["cell"] in mine)
        out.append(
            f"| {r['row']} | {esc(r['title'])} | {hit}/{len(mine)} | {row_total} "
            f"| {pct(row_total)} | {big + ' ' + pct(mine[big]) if row_total else '—'} |"
        )
    order = sorted((c for c in sizes if sizes[c]), key=lambda c: (-sizes[c], c))
    if order:
        out += [
            "",
            "- **Largest:** "
            + ", ".join(f"{c} {pct(sizes[c])}" for c in order[:5])
            + ".",
            "- **Smallest:** "
            + ", ".join(f"{c} {pct(sizes[c])}" for c in order[::-1][:5])
            + ".",
        ]
    empty = [c for c in sizes if not sizes[c]]
    if empty:
        out.append("- **Holding nothing:** " + ", ".join(empty) + ".")

    even = total / n if n else 0
    fat = [c for c in sizes if even and sizes[c] >= FAT * even]
    thin = [c for c in sizes if even and 0 < sizes[c] <= THIN * even]
    out += [
        "",
        "**Evenness.** Gini "
        f"{gini(list(sizes.values())):.2f} (0 means every box holds the same, "
        "1 means one box holds everything).",
        f"- **Fat** (at least {FAT:g}× an even share; often several rules in one "
        "box, a candidate to split): " + (", ".join(fat) or "none") + ".",
        f"- **Thin** (at most {THIN:g}× an even share; a label with a line "
        "behind it): " + (", ".join(thin) or "none") + ".",
    ]

    if root is not None:
        drawn: dict[str, dict[str, int]] = {}
        cells: dict[str, int] = {}
        for r in results:
            if r["state"] == "found":
                drawn.setdefault(r["file"], {})[r["sha256"]] = r["size"]
                cells[r["file"]] = cells.get(r["file"], 0) + 1
        out += [
            "",
            "**Sources.** How much of each source file the grid draws on "
            "(distinct passages over the file's characters, whitespace collapsed, "
            "not counting any tables this script generated in it).",
            "",
            "| File | Cells | Drawn | File | Coverage |",
            "|---|---|---|---|---|",
        ]
        for f in sorted(drawn):
            text = (root / f).read_text(encoding="utf-8")
            # A document can be its own source; its generated tables aren't.
            text = re.sub(
                r"<!-- cross-table:(\w+) -->.*?<!-- /cross-table:\1 -->",
                "",
                text,
                flags=re.S,
            )
            size = len(flat(text))
            got = sum(drawn[f].values())
            out.append(
                f"| `{f}` | {cells[f]} | {got} | {size} | {got / size if size else 0:.1%} |"
            )

    if others:
        grids = [(m.get("title") or "this grid", results)] + others
        everything = sum(r.get("size", 0) for _, res in grids for r in res)
        out += [
            "",
            "**Across grids.** Each grid's part of all the text.",
            "",
            "| Grid | Cells | Characters | Share of all |",
            "|---|---|---|---|",
        ]
        for title, res in grids:
            chars = sum(r.get("size", 0) for r in res)
            share = f"{chars / everything:.1%}" if everything else "—"
            out.append(f"| {esc(title)} | {len(res)} | {chars} | {share} |")

    if against is not None:
        then = against.get("cells", {})
        now = snapshot(m, results)["cells"]
        changed = [
            c
            for c in now
            if c in then
            and then[c]["sha256"]
            and now[c]["sha256"]
            and then[c]["sha256"] != now[c]["sha256"]
        ]
        new = [c for c in now if now[c]["sha256"] and not then.get(c, {}).get("sha256")]
        gone = [
            c
            for c in then
            if then[c].get("sha256") and not now.get(c, {}).get("sha256")
        ]
        out += ["", "**Since the snapshot.** Compared by each passage's sha256."]
        if not (changed or new or gone):
            out.append("- No box changed.")
        if changed:
            out.append(
                "- **Changed:** "
                + ", ".join(
                    f"{c} ({now[c]['size'] - then[c]['size']:+d})" for c in changed
                )
                + "."
            )
        if new:
            out.append("- **Newly found:** " + ", ".join(new) + ".")
        if gone:
            out.append("- **No longer found:** " + ", ".join(gone) + ".")
    return "\n".join(out)


def render(m: dict, results: list[dict], share: bool = False) -> dict[str, str]:
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
    total = sum(r.get("size", 0) for r in results)
    if share:
        idx = ["| Cell | Rule | Source | Share | Standing |", "|---|---|---|---|---|"]
        idx += [
            f"| {r['cell']} | {esc(r['rule'])} | {esc(r['source'])} "
            f"| {(r.get('size', 0) / total if total else 0):.2%} | {r['standing']} |"
            for r in results
        ]
    else:
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


def render_links(links: dict, maps: list[dict]) -> str:
    """The crosswalk table. Every address must exist in exactly one of the
    grids; a bare row letter means the whole row. Labels are copied from the
    maps. The `why` is a reading, and its standing travels with it."""
    labels: dict[str, str] = {}
    for m in maps:
        for r in m["rows"]:
            if r["row"] in labels:
                raise SystemExit(
                    f"row {r['row']} is in two grids; an address must name one box"
                )
            labels[r["row"]] = f"row: {r['title']}"
        for c in m["cells"]:
            labels[c["cell"]] = c.get("label", "")

    def name(addr: str) -> str:
        if addr not in labels:
            raise SystemExit(f"{addr}: no such address in the grids given")
        return f"{addr} {labels[addr]}".strip()

    out = [
        "| From | To | Where they touch | Standing |",
        "|---|---|---|---|",
    ]
    for ln in links["links"]:
        standing = ln.get("standing", "unattested")
        if standing not in STANDINGS:
            raise SystemExit(f"{ln['from']}: standing must be one of {STANDINGS}")
        to = " · ".join(name(t) for t in ln.get("to", [])) or "—"
        out.append(
            f"| {esc(name(ln['from']))} | {esc(to)} | {esc(ln.get('why', ''))} | {standing} |"
        )
    return "\n".join(out)


def splice_one(doc: str, name: str, body: str) -> str:
    start, end = f"<!-- cross-table:{name} -->", f"<!-- /cross-table:{name} -->"
    block = f"{start}\n{body}\n{end}"
    if start in doc and end in doc:
        return doc[: doc.index(start)] + block + doc[doc.index(end) + len(end) :]
    return doc.rstrip("\n") + f"\n\n## {name.capitalize()}\n\n{block}\n"


# ── commands ─────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("map", type=Path)
    n.add_argument("--rows", type=int, default=13)
    n.add_argument("--cols", type=int, default=13)
    n.add_argument("--title", default="")
    n.add_argument(
        "--after",
        type=Path,
        action="append",
        default=[],
        help="an earlier grid's map; rows start after its last row",
    )
    f = sub.add_parser("fill")
    f.add_argument("map", type=Path)
    f.add_argument("doc", type=Path)
    f.add_argument("--root", type=Path)
    f.add_argument(
        "--with",
        dest="others",
        type=Path,
        action="append",
        default=[],
        help="another grid's map; refuse if any row letter is shared",
    )
    c = sub.add_parser("check")
    c.add_argument("map", type=Path)
    c.add_argument("--root", type=Path)
    c.add_argument(
        "--with",
        dest="others",
        type=Path,
        action="append",
        default=[],
        help="another grid's map; refuse if any row letter is shared",
    )
    f.add_argument(
        "--measure",
        action="store_true",
        help="add a Share column to the index and write the measure section",
    )
    me = sub.add_parser("measure")
    me.add_argument("map", type=Path)
    me.add_argument("doc", type=Path, nargs="?")
    me.add_argument("--root", type=Path)
    me.add_argument(
        "--with",
        dest="others",
        type=Path,
        action="append",
        default=[],
        help="another grid's map; adds each grid's part of all the text",
    )
    me.add_argument(
        "--snapshot", type=Path, help="save each box's size and sha256 here"
    )
    me.add_argument("--against", type=Path, help="an earlier snapshot to compare with")
    k = sub.add_parser("link")
    k.add_argument("links", type=Path)
    k.add_argument("doc", type=Path)
    k.add_argument("--map", dest="maps", type=Path, action="append", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "link":
        links = json.loads(a.links.read_text(encoding="utf-8"))
        table = render_links(links, [load_map(p) for p in a.maps])
        doc = (
            a.doc.read_text(encoding="utf-8")
            if a.doc.exists()
            else f"# {links.get('title') or 'Crosswalk'}\n"
        )
        a.doc.write_text(splice_one(doc, "links", table), encoding="utf-8")
        print(f"linked {a.doc}: {len(links['links'])} link(s)")
        return 0

    if a.cmd == "new":
        if a.map.exists():
            raise SystemExit(f"{a.map} exists; a map is never overwritten")
        a.map.write_text(
            json.dumps(
                blank_map(a.rows, a.cols, a.title, next_row(a.after)),
                indent=1,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {a.map}: {a.rows} × {a.cols}")
        return 0

    m = load_map(a.map)
    shared = sorted(
        rows_of(m)
        & set().union(*(rows_of(load_map(o)) for o in getattr(a, "others", [])))
    )
    if shared:
        raise SystemExit(
            f"rows {', '.join(shared)} are already used by another grid; "
            "an address must name one box across every grid"
        )
    root = a.root or (a.map.parent / m.get("root", ".")).resolve()
    results = resolve(m, root)
    counts = {
        s: sum(r["state"] == s for r in results)
        for s in ("found", "silent", "unreachable", "not_found")
    }
    others = [
        (
            mo.get("title") or o.stem,
            resolve(mo, (o.parent / mo.get("root", ".")).resolve()),
        )
        for o in getattr(a, "others", [])
        for mo in [load_map(o)]
    ]
    if a.cmd == "measure":
        against = (
            json.loads(a.against.read_text(encoding="utf-8")) if a.against else None
        )
        report = measure(m, results, root, others, against)
        if a.snapshot:
            if a.snapshot.exists():
                raise SystemExit(
                    f"{a.snapshot} exists; a snapshot is never overwritten"
                )
            a.snapshot.write_text(
                json.dumps(snapshot(m, results), indent=1, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        if a.doc:
            doc = (
                a.doc.read_text(encoding="utf-8")
                if a.doc.exists()
                else f"# {m.get('title') or 'Cross table'}\n"
            )
            a.doc.write_text(splice_one(doc, "measure", report), encoding="utf-8")
            print(f"measured {a.doc}")
        else:
            print(report)
        return 0
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
    doc = splice(doc, render(m, results, share=a.measure))
    if a.measure:
        doc = splice_one(doc, "measure", measure(m, results, root, others))
    a.doc.write_text(doc, encoding="utf-8")
    print(f"filled {a.doc}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
