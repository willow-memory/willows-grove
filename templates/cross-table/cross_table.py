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
    cross_table.py drip NEW_MAP --source MAP [--source MAP ...] [--cells A1,B2] [--over 3]
                        [--after MAP ...] [--links CROSSWALK.json]
    cross_table.py measure MAP [DOC] [--root DIR] [--with OTHER_MAP ...]
                           [--snapshot NEW.json] [--against OLD.json]

`new` writes a blank map; with `--after`, its rows start after the earlier
grids' last row, so no address is used twice. `--with` makes `check` and
`fill` refuse a map that shares a row letter with another grid. `link`
writes a crosswalk between grids: every address is checked against the maps,
and labels are copied from them. `drip` lets the fat drip: each fat box's passage is cut into clauses, and
every clause gets its own box in a new grid, copied again from the source
and checked. `measure` reports how much of the grid's
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
import os
import re
import string
import sys
from pathlib import Path

MODES = ("para", "sent", "row", "head", "line", "clause")
STANDINGS = ("unattested", "witnessed", "sealed")
CAP = 420
SECTIONS = ("grid", "sources", "index")


# ── the map ──────────────────────────────────────────────────────────────────


def row_index(label: str) -> int:
    """A=0 … Z=25, AA=26, AB=27 …: rows run on past Z the way spreadsheet
    columns do, so an address still names one box across every grid."""
    if not re.fullmatch(r"[A-Z]+", label or ""):
        raise SystemExit(f"{label!r} is not a row label (A–Z, then AA, AB …)")
    n = 0
    for ch in label:
        n = n * 26 + string.ascii_uppercase.index(ch) + 1
    return n - 1


def row_label(i: int) -> str:
    out, n = "", i + 1
    while n:
        n, r = divmod(n - 1, 26)
        out = string.ascii_uppercase[r] + out
    return out


def split_cell(cell: str) -> tuple[str, int]:
    m = re.fullmatch(r"([A-Z]+)(\d+)", cell)
    if not m:
        raise SystemExit(f"{cell!r} is not a cell address (a row label, then a number)")
    return m[1], int(m[2])


def blank_map(rows: int, cols: int, title: str, start: str = "A") -> dict:
    """A blank grid. `start` is its first row label: a new grid starts where
    the last one stopped, so an address names one box across every grid."""
    first = row_index(start.upper())
    if rows < 1 or cols < 1:
        raise SystemExit("rows and cols must be at least 1")
    letters = [row_label(first + k) for k in range(rows)]
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
    cols = sorted({split_cell(c["cell"])[1] for c in m["cells"]})
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
    """The first row label after every earlier grid's last row (Z, then AA)."""
    used = set().union(*(rows_of(load_map(p)) for p in earlier)) if earlier else set()
    if not used:
        return "A"
    return row_label(max(row_index(r) for r in used) + 1)


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


_CLAUSE_END = re.compile(r"[.!?][\"”’'*)\]]*(?=\s|$)|\s\|(?=\s|$)")
_NOT_AN_END = re.compile(
    r"(?:^[-*>]?\s*\d+[a-z]?\.|\b(?:e\.g|i\.e|etc|vs|cf|no)\.)$", re.I
)


def clause_end(t: str) -> int:
    """Where the clause starting at t[0] ends: after its sentence's full stop
    (and any closing quote or emphasis), or before a table-cell boundary,
    whichever comes first. A list number ("6.") or an abbreviation ("e.g.")
    is not an end."""
    for m in _CLAUSE_END.finditer(t):
        if m.group(0).lstrip()[:1] == "|":
            return m.start()
        if not _NOT_AN_END.search(t[: m.start() + 1]):
            return m.end()
    return len(t)


def clauses(region: str) -> list[str]:
    """A passage cut into clauses by the same rule `clause` mode reads with."""
    out, t = [], region.strip().strip("|").strip()
    while t:
        end = clause_end(t)
        piece = t[:end].strip().strip("|").strip()
        if piece:
            out.append(piece)
        t = t[end:].lstrip(" |").strip()
    return out


def extract(
    lines: list[str], pattern: str, mode: str, span: int = 1, raw: bool = False
) -> tuple[int, str] | None:
    """(line number, copied text) for the first match, or None. `line` takes
    `span` lines from the match, with comment markers stripped (for code).
    `clause` takes one clause from the match: to its full stop, or to the
    table-cell boundary. With `raw`, a `row` or `head` match returns its
    source text uncombined (the row with its pipes, the heading's body), for
    `drip` to cut."""
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
        if mode == "clause":
            fm = rx.search(text)
            if not fm:
                continue
            t = text[fm.start() :]
            return line_no, t[: clause_end(t)].strip().strip("|").strip()
        if raw and mode == "row":
            return line_no, flat(bl[0])
        if raw and mode == "head":
            return line_no, flat("\n".join(blks[idx + 1][1])) if idx + 1 < len(
                blks
            ) else ""
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
        mine = {c: v for c, v in sizes.items() if split_cell(c)[0] == r["row"]}
        row_total = sum(mine.values())
        big = (
            max(mine, key=lambda c: (mine[c], -split_cell(c)[1])) if row_total else "—"
        )
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


def label_of(piece: str, words: int = 5) -> str:
    w = re.sub(r"[*`#]", "", piece).split()
    return " ".join(w[:words]) + (" …" if len(w) > words else "")


def pattern_for(
    lines: list[str], piece: str, lo: int, hi: int
) -> tuple[str, int] | None:
    """The shortest prefix pattern that finds exactly this clause again, at
    its own place (between lines lo and hi), when read from the top of the
    file the way `fill` reads it. None if it can't be pinned there."""
    for k in (60, 120, len(piece)):
        pat = re.escape(piece[:k]).replace("\\ ", " ")
        got = extract(lines, pat, "clause")
        if got and got[1] == piece and lo <= got[0] <= hi:
            return pat, got[0]
    return None


def bounds(lines: list[str], line_no: int, next_block: bool = False) -> tuple[int, int]:
    """First and last line of the block holding line_no (or the block after)."""
    blks = blocks(lines)
    for i, (start, bl) in enumerate(blks):
        if start <= line_no < start + len(bl):
            if next_block and i + 1 < len(blks):
                start, bl = blks[i + 1]
            return start, start + len(bl) - 1
    return line_no, line_no


def drip(
    sources: list[tuple[dict, Path]],
    start: str,
    cells: list[str] | None = None,
    over: float = FAT,
    cols: int = 13,
) -> tuple[dict, list[dict], list[str]]:
    """Let the fat drip: cut each chosen box's passage into clauses and give
    every clause its own box in a new grid, one row per parent, rows from
    `start`. Each clause is copied again from the source by its own pattern
    and checked; one that can't be found on its own is silent and says so.
    Returns the new map, crosswalk links from each row to its parent, and
    any parents left out for want of row letters."""
    found: dict[str, tuple[dict, dict, Path]] = {}
    sizes: list[tuple[int, str]] = []
    for m, root in sources:
        results = resolve(m, root)
        even = sum(r.get("size", 0) for r in results) / len(results)
        cfg = {c["cell"]: c for c in m["cells"]}
        for r in results:
            if r["state"] == "found":
                found[r["cell"]] = (r, cfg[r["cell"]], root)
                if cells is None and r["size"] >= over * even:
                    sizes.append((r["size"], r["cell"]))
    if cells is None:
        cells = [c for _, c in sorted(sizes, key=lambda x: (-x[0], x[1]))]
    missing = [c for c in cells if c not in found]
    if missing:
        raise SystemExit(f"{', '.join(missing)}: not a found box in the source grids")
    letters = [row_label(row_index(start) + k) for k in range(len(cells))]
    chosen, left = cells, []
    if not chosen:
        raise SystemExit("nothing to drip")

    rows, plans = [], []
    for letter, parent in zip(letters, chosen):
        r, c, root = found[parent]
        lines = (root / c["file"]).read_text(encoding="utf-8").splitlines()
        region = extract(
            lines, c["pattern"], c.get("mode", "para"), int(c.get("span", 1)), raw=True
        )
        pieces = clauses(region[1]) if region else []
        span = bounds(lines, region[0], c.get("mode") == "head") if region else (0, 0)
        plans.append((letter, parent, c, lines, pieces, span))
    width = min(cols, max(len(p[4]) for p in plans))

    new_cells, links = [], []
    for letter, parent, c, lines, pieces, (lo, hi) in plans:
        kept = pieces[:width]
        note = f", the first {width} kept" if len(pieces) > width else ""
        rows.append(
            {
                "row": letter,
                "title": f"{parent} {c.get('label', '')}".strip(),
                "source": f"{parent}'s passage (`{c['file']}`), cut into {len(pieces)} clause(s){note}",
            }
        )
        for i in range(width):
            cell = {
                "cell": f"{letter}{i + 1}",
                "label": "",
                "file": c["file"],
                "pattern": "",
                "mode": "clause",
                "standing": "unattested",
            }
            if i < len(kept):
                hit = pattern_for(lines, kept[i], lo, hi)
                cell["label"] = label_of(kept[i])
                if hit:
                    cell["pattern"] = hit[0]
                else:
                    cell.update(
                        file="", note="this clause can't be found again on its own"
                    )
            else:
                cell.update(file="", note=f"{parent}'s passage has no more clauses")
            new_cells.append(cell)
        links.append(
            {
                "from": letter,
                "to": [parent],
                "why": f"Dripped from {parent}: its passage cut into clauses, each copied again from the source.",
                "standing": "unattested",
            }
        )
    return {"title": "", "root": ".", "rows": rows, "cells": new_cells}, links, left


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
    d = sub.add_parser("drip")
    d.add_argument("map", type=Path, help="the new grid's map (never overwritten)")
    d.add_argument("--source", type=Path, action="append", required=True)
    d.add_argument("--after", type=Path, action="append", default=[])
    d.add_argument(
        "--cells", help="comma-separated boxes to drip (default: the fat ones)"
    )
    d.add_argument(
        "--over", type=float, default=FAT, help="fat threshold, × an even share"
    )
    d.add_argument("--title", default="")
    d.add_argument(
        "--links", type=Path, help="a crosswalk JSON to add the parent links to"
    )
    k = sub.add_parser("link")
    k.add_argument("links", type=Path)
    k.add_argument("doc", type=Path)
    k.add_argument("--map", dest="maps", type=Path, action="append", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "drip":
        if a.map.exists():
            raise SystemExit(f"{a.map} exists; a map is never overwritten")
        srcs = [
            (load_map(p), (p.parent / load_map(p).get("root", ".")).resolve())
            for p in a.source
        ]
        roots = {r for _, r in srcs}
        if len(roots) != 1:
            raise SystemExit("the source grids must share one root")
        (root,) = roots
        cells = [c.strip() for c in a.cells.split(",")] if a.cells else None
        new, links, left = drip(srcs, next_row(a.source + a.after), cells, a.over)
        new["title"] = a.title
        new["root"] = os.path.relpath(root, a.map.parent.resolve())
        a.map.write_text(
            json.dumps(new, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        if a.links:
            have = (
                json.loads(a.links.read_text(encoding="utf-8"))
                if a.links.exists()
                else {"links": []}
            )
            known = {ln["from"] for ln in have["links"]}
            have["links"] += [ln for ln in links if ln["from"] not in known]
            a.links.write_text(
                json.dumps(have, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
            )
        rows = ", ".join(
            f"{r['row']}←{ln['to'][0]}" for r, ln in zip(new["rows"], links)
        )
        print(
            f"dripped into {a.map}: {rows}"
            + (f"; no row letters left for {', '.join(left)}" if left else "")
        )
        return 0

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
