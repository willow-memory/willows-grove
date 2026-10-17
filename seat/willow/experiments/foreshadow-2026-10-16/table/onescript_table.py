"""onescript_table.py — the table's record as a real one-script record.

The hand-kept `record.md` becomes a one-script box (`box/record.jsonl`): a
check-in, then one `turn` per human line, the bite verbatim. The GM's proposals
and the facts the chat sealed don't go in yet. One-script refuses an idea with
no cites while nothing is served, and nothing is served before the human seals
a scope. So `migrate` stops at the scope card (`scope-card.json`), and the
proposals wait in `pending.jsonl`. After the human seals the card's subject,
`propose "<next line>"` serves the sealed scope, cites the served table, and
sends the proposals through the human's next turn. Each one is then a `pass`
awaiting its own `proposal:<hash>` seal, or whatever the door says.

Nothing here seals. The keys file holds the desk's key only; a seal is the
human's (HMAC proof or a Nestor pair), made with `python3 -m onescript seal`.

`wagers` turns the ledger's open predictions into one-script forecasts
(`python3 -m onescript forecast`, box build J1): each a binary wager, yes at
its stated confidence, by the desk. A forecast is committed only once the
human seals a tip that holds it, and counts only by the human's outcome seal.
f2 is held with p3/p4 (SPEC-documented C17): it rests on the agent's training.

Usage:
  python3 -I onescript_table.py migrate
  python3 -I onescript_table.py propose "<the human's next line>"
  python3 -I onescript_table.py wagers

Env: ONESCRIPT_DIR (willow-bot/one-script, beside this repo by default),
ONESCRIPT_PYTHON (a Python with pytest, for the tests gate), ONESCRIPT_VENV
(the venv whose ruff the toolchain gate checks), TABLE_KEYS (the desk's keys
file, outside the repo: ~/.willow/table-keys/keys.json by default).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_REPO = HERE.parents[4]
ONESCRIPT = Path(
    os.environ.get("ONESCRIPT_DIR", _REPO.parent / "willow-bot/one-script")
)
PYTHON = os.environ.get("ONESCRIPT_PYTHON", sys.executable)
VENV = os.environ.get("ONESCRIPT_VENV")
KEYS = Path(os.environ.get("TABLE_KEYS", "~/.willow/table-keys/keys.json")).expanduser()
BOX = HERE / "box"
CARD = HERE / "scope-card.json"
PENDING = HERE / "pending.jsonl"
MAX_CHARS = 20000

#: Ledger proposals and predictions left out: they rest on the agent's
#: training, not on anything the human said or served (handoff §4, Q7; the
#: experiment README :79-80 for f2; box build C17: held until Q5/Q7 are ruled).
HELD = {
    "p3": "rests on training (palantír), not on a served line; Q7",
    "p4": "rests on training (the Shire), not on a served line; Q7",
    "f2": "rests on training (hobbits), not on a served line; Q5/Q7 (C17)",
}


def _items(md: str, head: str) -> list[str]:
    """The `- ` lines of one `## ` section. Every line is read or refused:
    a line the pattern can't read stops the run, it is never skipped."""
    sec = md.replace("\r\n", "\n").split(f"\n## {head}\n", 1)[1].split("\n## ", 1)[0]
    return [x for x in sec.split("\n") if x.startswith("- ")]


def _read(line: str, pattern: str, head: str) -> re.Match:
    m = re.fullmatch(pattern, line)
    if m is None:
        sys.exit(f"record.md, {head}: can't read {line!r}; nothing migrated")
    return m


def human_lines(md: str) -> list[str]:
    """The `## Human lines (verbatim)` section, each line as written (JSON-quoted),
    numbered 1, 2, 3, ... with none missing."""
    head = "Human lines (verbatim)"
    got = [_read(x, r'- (\d+): (".*")', head) for x in _items(md, head)]
    if [int(m[1]) for m in got] != list(range(1, len(got) + 1)):
        sys.exit(f"record.md, {head}: lines are not numbered 1..{len(got)}")
    return [json.loads(m[2]) for m in got]


def sealed_facts(md: str) -> list[tuple[str, str, int]]:
    """(id, fact, line) from `## Sealed`, ordered by id."""
    pattern = r"- (s\d+): (.*) — line (\d+)"
    got = [_read(x, pattern, "Sealed") for x in _items(md, "Sealed")]
    return sorted((m[1], m[2], int(m[3])) for m in got)


def pending_rows(md: str, ledger: dict) -> list[dict]:
    """The proposals that go through the next served turn. `cites` is filled at
    serve time: served ids are keyed per check-in, so none can be written now."""
    rows = [
        {
            "path": f"world/{i}.md",
            "data": fact + "\n",
            "cites": [],
            "claim": f"sealed in chat by the human's line {n}; "
            "awaits the human's one-script seal",
        }
        for i, fact, n in sealed_facts(md)
    ]
    rows += [
        {
            "path": f"world/{p['id']}.md",
            "data": p["text"] + "\n",
            "cites": [],
            "claim": f"the GM's proposal from turn {p['from_turn']}; "
            "open, for the human to seal, fold or reject",
        }
        for p in ledger["proposals"]
        if p["state"] == "open" and p["id"] not in HELD
    ]
    return rows


def wager_rows(ledger: dict) -> tuple[list[dict], list[dict]]:
    """(forecasts, held): each open prediction as a binary wager, yes at its
    stated confidence, by the desk; a held one is listed with why, not sent."""
    out, held = [], []
    for f in ledger.get("predictions", []):
        if f["state"] != "open":
            continue
        if f["id"] in HELD:
            held.append({"id": f["id"], "why": HELD[f["id"]]})
            continue
        c = f["confidence"]
        out.append(
            {
                "id": f["id"],
                "distribution": [{"path": "yes", "p": c}, {"path": "no", "p": 1 - c}],
                "by": "desk",
            }
        )
    return out, held


def onescript(*args: str) -> subprocess.CompletedProcess:
    cmd = [PYTHON, "-m", "onescript", "--box", str(BOX), "--keys", str(KEYS)]
    if VENV:
        cmd += ["--venv", VENV]
    return subprocess.run(
        [*cmd, *args], cwd=ONESCRIPT, capture_output=True, text=True, check=False
    )


def must(res: subprocess.CompletedProcess, what: str) -> str:
    if res.returncode != 0:
        sys.exit(f"{what}: exit {res.returncode}\n{res.stdout}{res.stderr}")
    return res.stdout


def migrate() -> None:
    if (BOX / "record.jsonl").exists():
        sys.exit(f"{BOX}/record.jsonl exists; the record is append-only, not rebuilt")
    md = (HERE / "record.md").read_text(encoding="utf-8")
    ledger = json.loads((HERE / "ledger.json").read_text(encoding="utf-8"))
    print(must(onescript("checkin"), "checkin"))
    for line in human_lines(md):
        must(onescript("turn", "--", line), "turn")
    card = json.loads(
        must(onescript("scope", "--by", "who", "--match", "who=desk"), "scope")
    )
    CARD.write_text(json.dumps(card, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PENDING.write_text(
        "".join(
            json.dumps(r, ensure_ascii=False) + "\n" for r in pending_rows(md, ledger)
        ),
        encoding="utf-8",
    )
    print(f"seal next (the human): {card['subject']}")


def propose(bite: str) -> None:
    spec = json.loads(CARD.read_text(encoding="utf-8"))["spec"]
    args = ["serve", "--by", ",".join(spec["by"]), "--upto", str(spec["upto"])]
    args += [f"--match={k}={v}" for k, v in spec["match"].items()]
    must(onescript(*args, "--max-chars", str(MAX_CHARS)), "serve")
    doc = json.loads((BOX / "served.json").read_text(encoding="utf-8"))
    if doc["state"] != "populated" or len(doc["tables"]) != 1:
        hint = (
            " (a new container: run `onescript checkin` first)"
            if "serve key" in doc["why"]
            else ""
        )
        sys.exit(f"serve: {doc['state']}: {doc['why'] or 'expected one table'}{hint}")
    cite = doc["tables"][0]["id"]
    rows = [
        json.loads(x) for x in PENDING.read_text(encoding="utf-8").splitlines() if x
    ]
    out = BOX.parent / "pending.cited.jsonl"
    out.write_text(
        "".join(
            json.dumps({**r, "cites": [cite]}, ensure_ascii=False) + "\n" for r in rows
        ),
        encoding="utf-8",
    )
    try:
        print(must(onescript("turn", "--proposal", str(out), "--", bite), "turn"))
    finally:
        out.unlink()  # its cite is this check-in's id; the record holds the rows


def wagers() -> None:
    """Each forecast through `onescript forecast`; the human seals the tip it
    prints to commit it. Held predictions are named, never sent."""
    ledger = json.loads((HERE / "ledger.json").read_text(encoding="utf-8"))
    rows, held = wager_rows(ledger)
    for h in held:
        print(f"held {h['id']}: {h['why']}")
    for w in rows:
        dist = BOX.parent / f"forecast-{w['id']}.json"
        dist.write_text(json.dumps(w["distribution"]), encoding="utf-8")
        try:
            out = must(
                onescript("forecast", w["id"], "--dist", str(dist), "--by", w["by"]),
                f"forecast {w['id']}",
            )
        finally:
            dist.unlink()
        print(f"{w['id']}: {out.strip()}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["migrate"] and len(sys.argv) == 2:
        migrate()
    elif sys.argv[1:2] == ["wagers"] and len(sys.argv) == 2:
        wagers()
    elif sys.argv[1:2] == ["propose"] and len(sys.argv) == 3:
        propose(sys.argv[2])
    else:
        sys.exit(__doc__)
