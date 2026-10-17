"""grade_tags.py — grade the tagging forecast against a reference reading and a run.

Truth for a run = the measured path counts (peaks.py, real StorySession) with the
reference tags. Refuses predictions written after the run or naming a different
world file. The reference is a DRAFT reading; the grade is only as good as it.

Usage: python3 -I grade_tags.py <predictions.json> <reference.json> <peaks.json> <world.json>
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

BUCKETS = ("strong", "weak", "miss")


def main() -> None:
    pred = json.loads(Path(sys.argv[1]).read_text())
    ref = json.loads(Path(sys.argv[2]).read_text())["tags"]
    run = json.loads(Path(sys.argv[3]).read_text())
    world_path = Path(sys.argv[4])
    if pred["written_at"] >= run["run_at"]:
        sys.exit("refused: predictions were written after the run")
    if pred["world_sha256"] != hashlib.sha256(world_path.read_bytes()).hexdigest():
        sys.exit("refused: predictions name a different world file")
    beats = pred["playable_beats"]
    n = run["n"]
    results = []
    tp = fp = fn = 0
    per_tag = {t: [0, 0, 0] for t in pred["lexicon"]}
    for c in pred["claims"]:
        ck, k = c["check"], c["check"]["kind"]
        if k == "tags":
            want = set(ref[ck["beat"]][ck["bucket"]])
            got = set(ck["tags"])
            for t in per_tag:
                per_tag[t][0] += t in got and t in want
                per_tag[t][1] += t in got and t not in want
                per_tag[t][2] += t in want and t not in got
            tp += len(got & want)
            fp += len(got - want)
            fn += len(want - got)
            results.append({**c, "hit": got == want, "measured": sorted(want)})
        elif k == "carry":
            paths = run["policies"][ck["policy"]]["paths"]
            frac = (
                sum(
                    p["runs"]
                    for p in paths
                    if ck["tag"]
                    in set().union(
                        *(set(ref[b][x]) for b, x in zip(beats, p["path"].split("-")))
                    )
                )
                / n
            )
            results.append(
                {
                    **c,
                    "hit": abs(frac - ck["p"]) <= ck["tol"],
                    "measured": round(frac, 4),
                }
            )
        elif k == "beat_probs":
            m = run["policies"][ck["policy"]]["measured_bucket_rates"][ck["beat"]]
            gaps = {b: round(abs(m[b] - ck["p"][b]), 4) for b in BUCKETS}
            results.append(
                {**c, "hit": all(g <= ck["tol"] for g in gaps.values()), "measured": m}
            )
        elif k == "pivot":
            sw = run["policies"]["suggested"]["swing"]
            score = {}
            for b in beats:
                sets = [set(ref[b][x]) for x in BUCKETS]
                div = (
                    sum(
                        1 - (len(x & y) / len(x | y) if x | y else 1)
                        for x, y in itertools.combinations(sets, 2)
                    )
                    / 3
                )
                score[b] = round(div * sw[b]["entropy_bits"], 4)
            top = max(score.values())
            winners = [b for b, s in score.items() if abs(s - top) < 1e-9]
            fc_top = max(ck["scores"].values())
            fc_tied = [b for b, s in ck["scores"].items() if abs(s - fc_top) < 1e-9]
            results.append(
                {
                    **c,
                    "hit": winners == [ck["beat"]] and len(fc_tied) == 1,
                    "measured": {
                        "reference_scores": score,
                        "reference_pivot": winners,
                        "forecast_tied": fc_tied,
                    },
                }
            )
    groups = {}
    for r in results:
        g = r["id"].split("-")[0]
        h, t = groups.get(g, (0, 0))
        groups[g] = (h + bool(r["hit"]), t + 1)
    prec = tp / (tp + fp) if tp + fp else 0
    rec = tp / (tp + fn) if tp + fn else 0
    print(
        json.dumps(
            {
                "score": {g: f"{h}/{t}" for g, (h, t) in groups.items()},
                "tagger": {
                    "precision": round(prec, 3),
                    "recall": round(rec, 3),
                    "per_tag_tp_fp_fn": per_tag,
                },
                "results": results,
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
