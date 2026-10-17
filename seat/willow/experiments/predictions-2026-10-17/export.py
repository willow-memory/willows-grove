"""Export revealed rounds as one-script forecasts and proposed outcomes.

One JSON line per (forecaster, question) of a revealed round, in the shape
`python3 -m onescript forecast` takes (box build J1, SPEC-documented §6):

    {"id": "r001-3d6-human",
     "distribution": [{"path": "yes", "p": 0.12}, {"path": "no", "p": 0.88}],
     "by": "human", "committed": {"sha256", "beacon_then", "target"},
     "proposed_outcome": {"path": "no"}}

`by` is a role (human, desk, oracle, coin), never a name; the forecaster
`willow` is the desk. `committed` carries the round file's own fields
(`sha256`, `beacon_then`, `target`). The round file is the game's own
record, a plain rewritable JSON file, not a commitment: its `sha256` sits in
the clear beside the forecast it hashes, so anyone can edit both. What this
checks is narrower: an edit that forgets to re-hash is refused, and so is a
forecast whose own fields say it was made at or after its target
(`beacon_then >= target`, or `at >= target_at`). The one-script record's
commitment is the chain order under the human's sealed tip, made when the
rows are written, not here. Oracle and coin rows carry none: code worked
them out. The `proposed_outcome` is code's reading of the beacon, re-derived
here from the stored randomness with play.py's own deck; it is never a seal.
Only the human's proof over `reverse.outcome_subject` makes an outcome count.
The beacon's BLS signature is still not checked (the README's §4 limit; the
box build's T10): the stored randomness is taken as the beacon's.

This file sits beside `play.py` and imports it by path; `play.py` and the
round files are the game's record as played and are not edited.

    python3 -I export.py R        # one revealed round
    python3 -I export.py all      # every revealed round, in order
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLE = {"human": "human", "willow": "desk"}  # forecaster -> role


def _play():
    spec = importlib.util.spec_from_file_location("_play", HERE / "play.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


play = _play()


class Refused(Exception):
    """A round that can't be exported as it stands, and why."""


def answers_from_beacon(data: dict) -> dict[str, bool]:
    """Each question's answer, worked out again from the stored beacon."""
    seed = bytes.fromhex(data["reveal"]["beacon"]["randomness"])
    return {
        q: bool(play.DECK[q][1](play.Stream(seed + q.encode())))
        for q in data["questions"]
    }


def export(data: dict) -> list[dict]:
    """The rows of one round file, or Refused."""
    if "reveal" not in data:
        raise Refused(f"round {data.get('round')} is not revealed")
    rev = data["reveal"]
    got = answers_from_beacon(data)
    if got != rev["answers"]:
        raise Refused(f"round {data['round']}: the stored answers are not the beacon's")
    rows = {}
    for who, f in data["forecasts"].items():
        if who not in ROLE:
            raise Refused(f"round {data['round']}: no role for forecaster {who!r}")
        if hashlib.sha256(play.canon(f["p"]).encode()).hexdigest() != f["sha256"]:
            raise Refused(
                f"round {data['round']}: {who}'s forecast is not what was committed"
            )
        if f["beacon_then"] >= data["target"] or f["at"] >= data["target_at"]:
            raise Refused(
                f"round {data['round']}: {who}'s forecast says it was made at or "
                "after its target beacon"
            )
        rows[ROLE[who]] = (
            f["p"],
            {
                "sha256": f["sha256"],
                "beacon_then": f["beacon_then"],
                "target": data["target"],
            },
        )
    rows["oracle"] = (rev["oracle"], None)
    rows["coin"] = ({q: 0.5 for q in data["questions"]}, None)
    out = []
    for by, (ps, committed) in sorted(rows.items()):
        for q in sorted(data["questions"]):
            p = ps[q]
            out.append(
                {
                    "id": f"r{data['round']:03d}-{q}-{by}",
                    "distribution": [
                        {"path": "yes", "p": p},
                        {"path": "no", "p": 1 - p},
                    ],
                    "by": by,
                    "committed": committed,
                    "proposed_outcome": {"path": "yes" if got[q] else "no"},
                }
            )
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    paths = (
        sorted(play.ROUNDS.glob("*.json"))
        if argv[0] == "all"
        else [play.path(int(argv[0]))]
    )
    try:
        for p in paths:
            for row in export(json.loads(p.read_text())):
                print(json.dumps(row, sort_keys=True))
    except Refused as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
