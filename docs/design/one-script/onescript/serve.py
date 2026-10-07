"""serve — only the tables in scope, to one file the model reads.

Cites: the security core and "Where the reading lands" (README.md); the four
pieces join (../one-box/four-pieces-join.md, "What one-box adds to serve").

The model is served only the tables in its scope, by ids it can't guess, and
nothing else: a table out of scope isn't named, counted or marked. The one
served file is the model's only reference (Miller), and holding it is the
permission. Code fills out every field here; the model never sees a box.

  scope   a human seal over the exact set of table hashes (Janus: the seal binds
          to one hash, never to an attempt or a session). A seal over a
          different set covers nothing.
  ids     keyed (HMAC with the run's serve key), never the plain content hash,
          so a low-entropy table can't be reversed by enumeration.
  trust   `human-sealed` when the record holds the human's seal over that
          table's hash, else `untrusted`, always with the table's source
          receipt. The label is read from the record, never from the table.
  fails   closed and loud. No sealed scope, a seal that covers nothing, a table
          without a receipt: nothing is served, and the file says why. A sealed
          table the run can't find is `unreachable`, not `empty`.

  stack   the scope is a stack of piles (the operator, 2026-10-07: "yes to the
          stack"). A pile is one who/what/when/where group of record rows,
          its receipt the group key plus each row's number and hash, checked
          against the chain before anything is served. Code proposes the
          stack; the human seals its one hash.

Not here yet: the mosaic rule (judging scope on the combination), and the home.
D2 (sealed) puts serve inside willow-bot; it sits beside the skeleton until the
operator moves it.
"""

from __future__ import annotations

import hmac

from . import gate
from .record import Record, canon, h256

OUT = "served.json"
WS = ("who", "what", "when", "where")


def w_of(row: dict, w: str) -> str | None:
    """The four W's code can know without judging. Only write rows say where."""
    if w == "who":
        return row.get("who")
    if w == "what":
        return row.get("kind")
    if w == "when":
        return (row.get("ts") or "")[:10] or None  # the day
    if w == "where":
        return row.get("where") or row.get("path")
    raise ValueError(f"not a W: {w!r}")


def piles(rows: list[dict], *ws: str) -> list[dict]:
    """Group the record by the given W's: a GROUP BY, exact, nothing judged.
    A row missing any of them isn't in a pile; code doesn't guess it."""
    if not ws or any(w not in WS for w in ws):
        raise ValueError(f"group by one or more of {WS}, got {ws}")
    groups: dict[tuple, list[dict]] = {}
    for r in rows:
        key = tuple(w_of(r, w) for w in ws)
        if None not in key:
            groups.setdefault(key, []).append(r)
    return [
        {
            "rows": grp,
            "source": {
                "group": dict(zip(ws, key)),
                "rows": [[r["n"], r["hash"]] for r in grp],
            },
        }
        for key, grp in sorted(groups.items())
    ]


def name(pile: dict) -> str:
    """What the human reads on the card. The model never sees it."""
    src = pile["source"]
    group = src.get("group", {}) if isinstance(src, dict) else {}
    return " · ".join(f"{k}={v}" for k, v in group.items()) or str(src)


def propose(stack: list[dict], **match: str) -> dict:
    """Code proposes the stack: every pile whose group matches. The card is for
    the human; sealing `subject` is the only thing that makes it a scope."""
    chosen = [
        p
        for p in stack
        if isinstance(p["source"], dict)
        and all(p["source"]["group"].get(k) == v for k, v in match.items())
    ]
    ids = [table_id(p) for p in chosen]
    return {
        "subject": scope_subject(ids) if ids else None,
        "ids": ids,
        "stack": [
            {"name": name(p), "id": i, "rows": len(p["rows"])}
            for p, i in zip(chosen, ids)
        ],
    }


def table_id(table: dict) -> str:
    """A table's content hash: its rows and its source receipt, canonically."""
    return h256(canon({"rows": table["rows"], "source": table["source"]}))


def scope_subject(ids) -> str:
    """What the human seals: one hash over the exact, sorted set of table ids."""
    return "serve:" + h256(canon(sorted(set(ids))))


def served_id(serve_key: bytes, tid: str) -> str:
    return gate.sign(serve_key, "served", tid)


def _sealed(rows: list[dict]) -> set[str]:
    return {r["subject"] for r in rows if r["kind"] == "seal" and r["who"] == "human"}


def serve(
    rec: Record,
    tables: list[dict],
    scope: list[str] | None,
    serve_key: bytes,
    out: str = OUT,
) -> dict:
    """Write the served file and record it. Returns the served document."""
    try:
        doc = _serve(rec.rows(), tables, scope, serve_key)
    except gate.Refused as e:
        doc = _nothing("empty", str(e))
    except Exception as e:  # serve that can't think clearly serves nothing
        doc = _nothing("empty", f"serve error, failing closed: {type(e).__name__}: {e}")
    data = (canon(doc) + "\n").encode()
    untrusted = any(t["trust"] == "untrusted" for t in doc["tables"])
    rec.write_file(
        gate.system(),
        out,
        data,
        provenance="third-party" if untrusted else "authored",
    )
    rec.append(
        "serve",
        gate.system(),
        where=out,
        state=doc["state"],
        why=doc["why"],
        scope=scope_subject(scope) if scope else None,
        served=[t["id"] for t in doc["tables"]],
        sha=h256(data),
    )
    return doc


def _nothing(state: str, why: str) -> dict:
    return {"state": state, "why": why, "tables": []}


def _serve(rows, tables, scope, serve_key) -> dict:
    if not scope:
        return _nothing("empty", "no scope given; nothing is served without one")
    sealed = _sealed(rows)
    if scope_subject(scope) not in sealed:
        return _nothing(
            "empty", "the scope has no human seal over this exact set; nothing served"
        )
    by_id = {}
    for t in tables:
        _receipt(t, rows)
        by_id[table_id(t)] = t
    missing = sorted(set(scope) - set(by_id))
    if missing:  # in scope, so naming them is no leak
        return _nothing("unreachable", f"sealed tables not found: {missing}")
    served = [
        {
            "id": served_id(serve_key, tid),
            "trust": "human-sealed" if tid in sealed else "untrusted",
            "source": by_id[tid]["source"],
            "rows": by_id[tid]["rows"],
        }
        for tid in sorted(set(scope))
    ]
    served.sort(key=lambda t: t["id"])
    return {"state": "populated", "why": "", "tables": served}


def _receipt(table: dict, rows: list[dict]) -> None:
    """A pile's receipt is checked against the chain; a string receipt names an
    outside source, and is served as untrusted like everything unsealed."""
    src = table.get("source")
    if isinstance(src, str) and src.strip():
        return
    if not isinstance(src, dict) or not src.get("rows"):
        raise gate.Refused("a table without a source receipt is never served")
    at = {r["n"]: r for r in rows}
    cited = [at.get(n) for n, _ in src["rows"]]
    if (
        any(r is None or r["hash"] != h for r, (_, h) in zip(cited, src["rows"]))
        or cited != table["rows"]
    ):
        raise gate.Refused("a pile's receipt doesn't match the record; nothing served")


def check_cites(doc: dict, cited: list[str]) -> list[dict]:
    """A cite outside what was served is `link_fail`: a name the model can't
    have known. Caught here and escalated, never accepted as an answer."""
    known = {t["id"] for t in doc.get("tables", [])}
    return [
        {"cite": c, "verdict": "link_fail", "why": "not in the served file"}
        for c in cited
        if not any(hmac.compare_digest(c, k) for k in known)
    ]
