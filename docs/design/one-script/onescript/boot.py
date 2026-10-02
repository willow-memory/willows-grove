"""1 boot — check-in. The record first, then state, then attack the gate, then egress.

Cites: CONST-I (identity is the manifest), CONST-V (reserved decisions need the
human key), CONST-III (the egress index), App. B (adversarial probes through the
real path: a gate's own report about itself is not evidence).

Any change without a recorded cause is a hard close: report, options, wait.
If any probe gets through, the box does not open at all.
"""

from __future__ import annotations

from . import gate, reverse

OPTIONS = [
    "put it back and continue",
    "keep it as a standing grant",
    "leave it, block it until you decide",
    "stop here",
]


class BoxWontOpen(Exception):
    """A probe got through the gate. Nothing runs until a human looks."""


def probes(keys: dict, law: dict) -> list[dict]:
    """The demo stories' attacks, every morning, through the real door."""
    out = []

    try:
        gate.verify({"who": "assistant", "family": "copied", "sig": "forged"}, keys)
        out.append({"probe": "unsigned identity", "held": False, "got": "verified"})
    except gate.Refused as e:
        out.append({"probe": "unsigned identity", "held": True, "got": str(e)})

    for name, change, must_not in (
        (
            "self-awarded seal",
            {"kind": "edit", "standing": "sealed", "cites": ["CONST-IV"]},
            "pass",
        ),
        ("write to the law", {"kind": "law", "none_because": "probe"}, "pass"),
        (
            "egress with no grant",
            {
                "kind": "egress",
                "who": "probe",
                "what": "probe",
                "where": "probe.invalid",
                "bytes": 1,
                "cites": ["CONST-III"],
            },
            "pass",
        ),
    ):
        d = gate.door(change, law)
        out.append({"probe": name, "held": d.verdict != must_not, "got": d.verdict})
    return out


def boot(rec, keys: dict, law: dict) -> dict:
    rows = rec.rows()
    lines: list[str] = []

    for b in rec.verify_chain():  # B1: the record holds?
        lines.append(f"record: {b}")
    for t in reverse.open_turns(rows):  # a crash left a row
        intent = next(
            r["intent"] for r in rows if r["kind"] == "turn_open" and r["turn"] == t
        )
        lines.append(f"turn {t} never closed; it was doing: {intent}")
    for i in reverse.three_way(rec.box, rec.pile(), rows):  # B2: state vs last close
        if i["verdict"] == "failing":
            lines.append(f"{i['where']}: {i['why']}")

    held = probes(keys, law)  # App. B, every morning
    broke = [p for p in held if not p["held"]]
    if broke:
        raise BoxWontOpen(f"probes got through: {[p['probe'] for p in broke]}")

    egress = sorted(f"{g['who']} -> {g['where']}" for g in law.get("grants", []))  # B3
    return {
        "hard_close": bool(lines),
        "lines": lines,
        "options": OPTIONS if lines else [],
        "probes": held,
        "egress": egress,
    }
