"""predict.py — forecast a world's peaks and valleys from its world file alone.

Runs no dice and imports nothing from the-table. Two forecasters:

  heuristic  rules carried over from the Hasbeen pass (2026-10-16), applied to a
             world they were not built on. This is the transfer test.
  arithmetic 2d6 + stat enumerated per beat. A control: it should grade near
             perfect, and if it does not, the harness is wrong, not the world.

Writes predictions.json and prints its sha256. Run this BEFORE peaks.py;
grade.py refuses a prediction file written after the run it grades.

Usage: python3 -I predict.py <world.json> <out.json>
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def bucket_probs(stat: int) -> dict:
    c = {"strong": 0, "weak": 0, "miss": 0}
    for a, b in itertools.product(range(1, 7), repeat=2):
        t = a + b + stat
        c["strong" if t >= 10 else "weak" if t >= 7 else "miss"] += 1
    return {k: v / 36 for k, v in c.items()}


def main() -> None:
    world_path, out = Path(sys.argv[1]), Path(sys.argv[2])
    world = json.loads(world_path.read_text())
    seat = next(c for c in world["characters"] if c["seat"])
    stats = {s: seat["stats"].get(s, world["base_stat"]) for s in world["stats"]}

    flat = [(si, b) for si, sc in enumerate(world["scenes"]) for b in sc["beats"]]
    dec_i = next((i for i, (_, b) in enumerate(flat) if b["kind"] == "decision"), None)
    playable = [b for _, b in flat[: dec_i if dec_i is not None else len(flat)]]
    last_scene = flat[-1][0]
    dec_scene = flat[dec_i][0] if dec_i is not None else None
    proposer = flat[dec_i][1]["proposes"]["proposed_by"] if dec_i is not None else None

    claims = []

    def claim(cid, forecaster, text, check):
        claims.append(
            {"id": cid, "forecaster": forecaster, "claim": text, "check": check}
        )

    # --- heuristic forecaster: Hasbeen lessons, stated as checkable rules ----
    if playable:
        claim(
            "H1",
            "heuristic",
            "The last action beat before the decision is the biggest swing (highest outcome entropy).",
            {"kind": "max_entropy_beat", "beat": playable[-1]["id"]},
        )
        claim(
            "H2",
            "heuristic",
            "The first action beat is the cast gate: its strong outcome introduces more new characters than any other single outcome.",
            {"kind": "cast_gate", "beat": playable[0]["id"], "bucket": "strong"},
        )
    if proposer:
        claim(
            "H3",
            "heuristic",
            "No path before the decision introduces the decision's proposer by name.",
            {"kind": "proposer_unintroduced", "proposer": proposer},
        )
    claim(
        "H4",
        "heuristic",
        "At least one character is met only on a path that contains a miss (the valley holds unique content).",
        {"kind": "valley_unique"},
    )
    claim(
        "H5",
        "heuristic",
        "The night 'holds together' (strong >= miss) on 85-92% of runs under the suggested approach.",
        {"kind": "held_range", "lo": 0.85, "hi": 0.92, "policy": "suggested"},
    )
    claim(
        "H6",
        "heuristic",
        "20-45% of runs (suggested approach) reach the decision without meeting at least one unseated character who is met on some other path.",
        {"kind": "missing_cast_range", "lo": 0.20, "hi": 0.45, "policy": "suggested"},
    )
    claim(
        "H7",
        "heuristic",
        "A decision beat stops every run before the final scene: the last scene is unreachable without a human seal.",
        {
            "kind": "seal_gates_last_scene",
            "expected": dec_scene is not None and dec_scene < last_scene,
        },
    )

    # --- arithmetic forecaster: the control ----------------------------------
    for b in playable:
        p = bucket_probs(stats[b["suggests"]])
        claim(
            f"A-{b['id']}",
            "arithmetic",
            f"Beat {b['id']} under the suggested approach ({b['suggests']}): strong {p['strong']:.3f}, weak {p['weak']:.3f}, miss {p['miss']:.3f}; measured within 0.05 each.",
            {
                "kind": "beat_probs",
                "beat": b["id"],
                "p": p,
                "tol": 0.05,
                "policy": "suggested",
            },
        )

    doc = {
        "world": world["title"],
        "world_file": world_path.name,
        "world_sha256": hashlib.sha256(world_path.read_bytes()).hexdigest(),
        "written_at": datetime.now(timezone.utc).isoformat(),
        "playable_beats": [b["id"] for b in playable],
        "claims": claims,
    }
    body = json.dumps(doc, indent=1, sort_keys=True)
    out.write_text(body)
    print(hashlib.sha256(body.encode()).hexdigest(), out)
    for c in claims:
        print(f"  {c['id']:7} [{c['forecaster']}] {c['claim']}")


if __name__ == "__main__":
    main()
