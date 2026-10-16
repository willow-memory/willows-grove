"""grade.py — grade a recorded prediction file against a peaks.py run.

Refuses when the predictions were written after the run, or name a different
world file (sha256). Each claim grades hit / miss with the measured value
beside it; nothing is sealed — the verdict is a draft for a person to read.

Usage: python3 -I grade.py <predictions.json> <peaks.json> <world.json>
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


def aliases(char: dict) -> set[str]:
    name = char["name"].lower()
    bare = re.sub(r"^the\s+", "", name)
    return {name, bare, bare.split()[0], char["id"].lower()}


def mentions(world: dict, text: str) -> set[str]:
    low = text.lower()
    return {
        c["id"]
        for c in world["characters"]
        if any(re.search(rf"\b{re.escape(a)}\b", low) for a in aliases(c))
    }


def main() -> None:
    pred = json.loads(Path(sys.argv[1]).read_text())
    run = json.loads(Path(sys.argv[2]).read_text())
    world_path = Path(sys.argv[3])
    world = json.loads(world_path.read_text())
    if pred["written_at"] >= run["run_at"]:
        sys.exit("refused: predictions were written after the run")
    if pred["world_sha256"] != hashlib.sha256(world_path.read_bytes()).hexdigest():
        sys.exit("refused: predictions name a different world file")

    sug = run["policies"]["suggested"]
    unseated = {c["id"] for c in world["characters"] if not c["seat"]}
    met_somewhere = set().union(*(set(p["met"]) for p in sug["paths"])) & unseated
    results = []
    for c in pred["claims"]:
        ck, hit, got = c["check"], None, None
        k = ck["kind"]
        if k == "max_entropy_beat":
            ent = {b: s["entropy_bits"] for b, s in sug["swing"].items()}
            top = max(ent.values())
            winners = sorted(b for b, e in ent.items() if abs(e - top) < 1e-9)
            got = {"entropy": ent, "top": winners}
            hit = ck["beat"] in winners and len(winners) == 1
            if ck["beat"] in winners and len(winners) > 1:
                hit, got["note"] = (
                    False,
                    "tied: the beat is not uniquely the biggest swing",
                )
        elif k == "cast_gate":
            intro = {}
            for p in sug["paths"]:
                for f in p["firsts"]:
                    key = f"{f['beat']}:{f['bucket']}"
                    intro[key] = max(intro.get(key, 0), len(f["introduces"]))
            top = max(intro.values()) if intro else 0
            leaders = sorted(x for x, v in intro.items() if v == top)
            got = {"new_cast_by_outcome": intro, "leaders": leaders}
            hit = leaders == [f"{ck['beat']}:{ck['bucket']}"]
        elif k == "proposer_unintroduced":
            seen_on = [p["path"] for p in sug["paths"] if ck["proposer"] in p["met"]]
            got = {"paths_meeting_proposer": seen_on}
            hit = not seen_on
        elif k == "valley_unique":
            only_miss = []
            for ch in met_somewhere:
                paths_with = [p for p in sug["paths"] if ch in p["met"]]
                if paths_with and all("miss" in p["path"] for p in paths_with):
                    only_miss.append(ch)
            got = {"met_only_on_miss_paths": sorted(only_miss)}
            hit = bool(only_miss)
        elif k == "held_range":
            got = run["policies"][ck["policy"]]["held_p"]
            hit = ck["lo"] <= got <= ck["hi"]
        elif k == "missing_cast_range":
            frac = sum(
                p["measured"]
                for p in sug["paths"]
                if not met_somewhere <= set(p["met"])
            )
            got = {
                "measured_fraction": round(frac, 4),
                "unseated_met_somewhere": sorted(met_somewhere),
            }
            hit = ck["lo"] <= frac <= ck["hi"]
        elif k == "seal_gates_last_scene":
            last = str(run["scenes"] - 1)
            stopped = sug["stopped_in_scene"]
            got = {"stopped_in_scene": stopped}
            hit = last not in stopped
        elif k == "beat_probs":
            m = run["policies"][ck["policy"]]["measured_bucket_rates"][ck["beat"]]
            gaps = {b: round(abs(m[b] - ck["p"][b]), 4) for b in m}
            got = {"measured": m, "gaps": gaps}
            hit = all(g <= ck["tol"] for g in gaps.values())
        results.append(
            {
                "id": c["id"],
                "forecaster": c["forecaster"],
                "hit": hit,
                "claim": c["claim"],
                "measured": got,
            }
        )

    by = {}
    for r in results:
        h, t = by.get(r["forecaster"], (0, 0))
        by[r["forecaster"]] = (h + bool(r["hit"]), t + 1)
    print(
        json.dumps(
            {
                "world": pred["world"],
                "n": run["n"],
                "score": {f: f"{h}/{t}" for f, (h, t) in by.items()},
                "results": results,
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
