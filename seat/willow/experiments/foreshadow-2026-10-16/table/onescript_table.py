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

Usage:
  python3 -I onescript_table.py migrate
  python3 -I onescript_table.py propose "<the human's next line>"

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

#: Ledger proposals left out of pending: they rest on the agent's training,
#: not on anything the human said or served (handoff §4, Q7).
HELD = {
    "p3": "rests on training (palantír), not on a served line; Q7",
    "p4": "rests on training (the Shire), not on a served line; Q7",
}


def human_lines(md: str) -> list[str]:
    """The `## Human lines (verbatim)` section, each line as written (JSON-quoted)."""
    sec = md.split("## Human lines (verbatim)", 1)[1].split("\n## ", 1)[0]
    return [json.loads(m) for m in re.findall(r'^- \d+: (".*")$', sec, re.M)]


def sealed_facts(md: str) -> list[tuple[str, str, int]]:
    """(id, fact, line) from `## Sealed`, ordered by id."""
    sec = md.split("## Sealed", 1)[1].split("\n## ", 1)[0]
    got = re.findall(r"^- (s\d+): (.*) — line (\d+)$", sec, re.M)
    return sorted((i, t, int(n)) for i, t, n in got)


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
        must(onescript("turn", line), "turn")
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
        sys.exit(f"serve: {doc['state']}: {doc['why'] or 'expected one table'}")
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
        print(must(onescript("turn", bite, "--proposal", str(out)), "turn"))
    finally:
        out.unlink()  # its cite is this check-in's id; the record holds the rows


if __name__ == "__main__":
    if sys.argv[1:2] == ["migrate"] and len(sys.argv) == 2:
        migrate()
    elif sys.argv[1:2] == ["propose"] and len(sys.argv) == 3:
        propose(sys.argv[2])
    else:
        sys.exit(__doc__)
