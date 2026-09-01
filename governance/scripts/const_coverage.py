#!/usr/bin/env python3
"""const_coverage.py — the generated coverage artifact Appendix A calls for.

Draft 0.8 removed Appendix A's hand-maintained enforcement table. This is what
replaces it: a report built by scanning trees for Trace-ID citations, rebuilt on
demand, never checked in as prose.

The one-direction rule it enforces
----------------------------------
The constitution names no artifact; artifacts name the constitution. So coverage
is discovered by looking for upward references (``CONST-*`` appearing in code,
tests, configs) and never by reading a list the constitution carries. A Trace ID
does not move when a file does, which is the whole point.

What this script will and will not claim
----------------------------------------
It reports two things it can actually see:

  * which clauses this document defines, parsed from the constitution itself;
  * which clauses are cited somewhere in the scanned trees, and where.

It does NOT decide the four verdicts. ``satisfied`` versus ``differently``
requires knowing whether the citing artifact enforces the clause *by the
mechanism the clause describes* — a judgment about meaning, not a fact about
text. Appendix B: *a gate that cannot check its subject is not a weaker gate; it
is no gate.* So verdicts are read from a declarations file a human maintains,
and any clause without a declaration is reported as ``undeclared`` rather than
guessed into one of the four.

Nor does it treat its own green as evidence. Appendix B again: *a gate's own
report about itself is not evidence about that gate.* This script reports what
it scanned and what it could not read; a clause with no citation found is
reported with the reason, never as a bare empty row (IV.5 / Casebook Case 10).

Usage
-----
    python3 governance/scripts/const_coverage.py [--root DIR ...] [--json]

Exit codes follow the house convention: 0 the report was produced, 1 the answer
is no (a clause is declared ``failing``), 2 the report could not be produced.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONSTITUTION = REPO_ROOT / "governance" / "CONSTITUTION.md"
DECLARATIONS = REPO_ROOT / "governance" / "compliance" / "coverage-declarations.json"

EXIT_OK, EXIT_ANSWER_IS_NO, EXIT_CANNOT = 0, 1, 2

VERDICTS = ("satisfied", "differently", "not applicable", "failing")

# A Trace ID: CONST-0, CONST-IV, CONST-0-3, CONST-IV-5, CONST-0-3-II.
TRACE_RE = re.compile(r"\bCONST-(?:0|[IVX]+)(?:-[0-9A-Za-z]+)*\b")

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache",
    ".mypy_cache", "dist", "build", ".ruff_cache",
}
TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".sh", ".sql", ".json", ".yaml", ".yml", ".toml",
    ".md", ".cfg", ".ini", ".txt",
}


def clauses_from_constitution(path: Path) -> tuple[list[str], str | None]:
    """Parse the Trace IDs this constitution defines.

    Returns (ids, unreadable_reason). The reason is non-None when the document
    could not be read at all — reported rather than silently yielding zero
    clauses, which would render as a vacuously clean sweep.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        return [], f"could not read {path}: {err}"
    # Definitions come from the headings and the clause markers, in document
    # order, de-duplicated. Anything the document merely mentions in prose is
    # still a definition here: this document is the only authority on which
    # clauses exist.
    seen: dict[str, None] = {}
    for match in TRACE_RE.finditer(text):
        seen.setdefault(match.group(0), None)
    return list(seen), None


def scan(roots: list[Path], skip: set[Path]) -> tuple[dict[str, list[str]], list[str]]:
    """Find upward Trace-ID citations. Returns (citations, unreadable)."""
    citations: dict[str, list[str]] = {}
    unreadable: list[str] = []
    for root in roots:
        if not root.exists():
            unreadable.append(f"{root}: not present")
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                fp = Path(dirpath) / name
                if fp.suffix not in TEXT_SUFFIXES or fp in skip:
                    continue
                try:
                    body = fp.read_text(encoding="utf-8", errors="strict")
                except (OSError, UnicodeDecodeError) as err:
                    unreadable.append(f"{fp}: {type(err).__name__}")
                    continue
                for match in set(TRACE_RE.findall(body)):
                    rel = str(fp.relative_to(REPO_ROOT)) if REPO_ROOT in fp.parents else str(fp)
                    citations.setdefault(match, []).append(rel)
    return citations, unreadable


def load_declarations(path: Path) -> tuple[dict[str, dict], str | None]:
    if not path.exists():
        return {}, f"no declarations file at {path}"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        return {}, f"could not read {path}: {err}"
    decls = raw.get("clauses", {})
    for cid, entry in decls.items():
        verdict = entry.get("verdict")
        if verdict not in VERDICTS:
            return {}, f"{cid}: verdict {verdict!r} is not one of {VERDICTS}"
    return decls, None


def build_report(roots: list[Path]) -> dict:
    clauses, unreadable_const = clauses_from_constitution(CONSTITUTION)
    if unreadable_const:
        return {"error": unreadable_const}
    # This script's own Trace-ID mentions are regex examples and prose, not
    # enforcement. A gate's self-report is not evidence about that gate
    # (Appendix B; Casebook Case 7), so it excludes itself from its own scan.
    citations, unreadable = scan(roots, skip={CONSTITUTION, Path(__file__).resolve()})
    decls, decl_problem = load_declarations(DECLARATIONS)

    rows = []
    for cid in clauses:
        cites = sorted(set(citations.get(cid, [])))
        decl = decls.get(cid)
        if decl is not None:
            verdict = decl["verdict"]
            note = decl.get("note", "")
        else:
            verdict = "undeclared"
            # Say WHY, never a bare empty row. 'Nothing here' and 'nothing left
            # to do' are different claims (IV.5, Casebook Case 10).
            if decl_problem:
                note = "no verdict recorded — see the declarations line above"
            elif cites:
                note = "cited in the tree but no human verdict recorded"
            else:
                note = "no citation found in the scanned roots and no verdict recorded"
        rows.append({"clause": cid, "verdict": verdict, "citations": cites, "note": note})

    return {
        "clauses_defined": len(clauses),
        "roots_scanned": [str(r) for r in roots],
        "unreadable": unreadable,
        "declarations_problem": decl_problem,
        "rows": rows,
    }


def render(report: dict) -> str:
    if "error" in report:
        return f"const-coverage: cannot report — {report['error']}"
    out = [
        "const-coverage — generated, not tabled. This is evidence about a checkout",
        "at a moment; the constitution is the law. References point up.",
        "",
        f"clauses defined: {report['clauses_defined']}",
        f"roots scanned:   {', '.join(report['roots_scanned'])}",
    ]
    if report["declarations_problem"]:
        out.append(f"declarations:    {report['declarations_problem']}")
    if report["unreadable"]:
        out.append(f"unreadable:      {len(report['unreadable'])} path(s) — listed below")
    out.append("")
    counts: dict[str, int] = {}
    for row in report["rows"]:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    out.append("  " + " · ".join(f"{v}: {counts[v]}" for v in sorted(counts)))
    out.append("")
    width = max((len(r["clause"]) for r in report["rows"]), default=10)
    for row in report["rows"]:
        cites = ", ".join(row["citations"][:3]) or "—"
        if len(row["citations"]) > 3:
            cites += f" (+{len(row['citations']) - 3})"
        out.append(f"  {row['clause']:<{width}}  {row['verdict']:<14}  {cites}")
        if row["note"]:
            out.append(f"  {'':<{width}}  └─ {row['note']}")
    if report["unreadable"]:
        out.append("")
        out.append("unreadable paths:")
        out.extend(f"  {u}" for u in report["unreadable"])
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", action="append", default=None,
                    help="tree to scan for upward Trace-ID citations (repeatable)")
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = ap.parse_args()

    roots = [Path(r).resolve() for r in args.root] if args.root else [REPO_ROOT]
    report = build_report(roots)

    if "error" in report:
        print(render(report), file=sys.stderr)
        return EXIT_CANNOT

    print(json.dumps(report, indent=2) if args.json else render(report))
    failing = [r for r in report["rows"] if r["verdict"] == "failing"]
    return EXIT_ANSWER_IS_NO if failing else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
