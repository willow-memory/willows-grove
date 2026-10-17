"""setup_pass.py — the setup tag: does an outcome set up the decision beat?

Detector (code, no model): an outcome carries 'setup' when it shares a two-word
phrase with the decision beat (its prompt, its proposed fact, its scene title)
that has at least one content word (5+ letters) the player has not already
read (setting, openings and prompts so far). Fitted after reading all three
worlds — descriptive, not a blind forecast.

  predict  <world> <out>                  record the detector's tags + forecast
  grade    <pred> <reference> <peaks>     grade against a reading and a run
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from harness import STOP  # noqa: E402

BUCKETS = ("strong", "weak", "miss")


def phrases(text: str) -> set[str]:
    w = re.findall(r"[a-z']+", text.lower())
    return {
        f"{a} {b}"
        for a, b in zip(w, w[1:])
        if any(len(x) >= 5 and x not in STOP for x in (a, b))
    }


def bucket_probs(stat: int) -> dict:
    c = dict.fromkeys(BUCKETS, 0)
    for a, b in itertools.product(range(1, 7), repeat=2):
        t = a + b + stat
        c["strong" if t >= 10 else "weak" if t >= 7 else "miss"] += 1
    return {k: v / 36 for k, v in c.items()}


def predict(world_path: Path, out: Path) -> None:
    w = json.loads(world_path.read_text())
    flat = [(si, b) for si, sc in enumerate(w["scenes"]) for b in sc["beats"]]
    di = next(i for i, (_, b) in enumerate(flat) if b["kind"] == "decision")
    dsi, dec = flat[di]
    target = phrases(
        " ".join([dec["prompt"], dec["proposes"]["fact"], w["scenes"][dsi]["title"]])
    )
    playable = [b for _, b in flat[:di]]
    tags, evidence = {}, {}
    for i, (si, b) in enumerate(flat[:di]):
        seen = phrases(
            " ".join(
                [w["setting"]]
                + [line for j in range(si + 1) for line in w["scenes"][j]["opening"]]
                + [x["prompt"] for _, x in flat[: i + 1]]
            )
        )
        for k in BUCKETS:
            hit = sorted((phrases(b["outcomes"][k]) & target) - seen)
            tags[f"{b['id']}-{k}"] = bool(hit)
            if hit:
                evidence[f"{b['id']}-{k}"] = hit
    seated = [c for c in w["characters"] if c["seat"]]
    sheets = [
        {s: c["stats"].get(s, w["base_stat"]) for s in w["stats"]} for c in seated
    ]
    fc = {}
    for policy in ("suggested", "random"):
        p = {}
        for t, b in enumerate(playable):
            sh = sheets[t % len(sheets)]
            if policy == "suggested":
                p[b["id"]] = bucket_probs(sh[b["suggests"]])
            else:
                p[b["id"]] = {
                    k: sum(bucket_probs(sh[s])[k] for s in w["stats"]) / len(w["stats"])
                    for k in BUCKETS
                }
        none = sum(
            math.prod(p[b["id"]][k] for b, k in zip(playable, combo))
            for combo in itertools.product(BUCKETS, repeat=len(playable))
            if not any(tags[f"{b['id']}-{k}"] for b, k in zip(playable, combo))
        )
        fc[policy] = round(1 - none, 4)
    doc = {
        "world": w["title"],
        "world_sha256": hashlib.sha256(world_path.read_bytes()).hexdigest(),
        "written_at": datetime.now(timezone.utc).isoformat(),
        "decision": dec["id"],
        "playable_beats": [b["id"] for b in playable],
        "tags": tags,
        "evidence": evidence,
        "p_any_setup": fc,
    }
    body = json.dumps(doc, indent=1, sort_keys=True)
    out.write_text(body)
    print(hashlib.sha256(body.encode()).hexdigest(), out)


def grade(pred_path: Path, ref_path: Path, peaks_path: Path) -> None:
    pred = json.loads(pred_path.read_text())
    run = json.loads(peaks_path.read_text())
    if pred["written_at"] >= run["run_at"]:
        sys.exit("refused: predictions were written after the run")
    ref = set(json.loads(ref_path.read_text())["setup"][pred["world"]])
    got = {k for k, v in pred["tags"].items() if v}
    tp, fp, fn = len(got & ref), len(got - ref), len(ref - got)
    beats = pred["playable_beats"]
    out = {
        "world": pred["world"],
        "detector": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(tp / (tp + fp), 3) if tp + fp else None,
            "recall": round(tp / (tp + fn), 3) if tp + fn else None,
            "found": sorted(got),
            "reference": sorted(ref),
        },
        "setup_by_bucket": {
            b: sum(1 for r in ref if r.endswith("-" + b)) for b in BUCKETS
        },
        "policies": {},
    }
    for policy, d in run["policies"].items():
        n = run["n"]

        def has(path, tagset):
            return any(f"{b}-{k}" in tagset for b, k in zip(beats, path.split("-")))

        actual = sum(p["runs"] for p in d["paths"] if has(p["path"], ref)) / n
        exact_ref = sum(p["p"] for p in d["paths"] if has(p["path"], ref))
        miss_only = (
            sum(
                p["runs"]
                for p in d["paths"]
                if has(p["path"], {r for r in ref if r.endswith("-miss")})
                and not has(p["path"], {r for r in ref if not r.endswith("-miss")})
            )
            / n
        )
        out["policies"][policy] = {
            "forecast_p_any_setup": pred["p_any_setup"][policy],
            "measured_p_any_setup": round(actual, 4),
            "exact_p_any_setup": round(exact_ref, 4),
            "hit_within_0.07": abs(actual - pred["p_any_setup"][policy]) <= 0.07,
            "measured_reach_decision_with_no_setup": round(1 - actual, 4),
            "measured_setup_only_via_a_miss": round(miss_only, 4),
        }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "predict":
        predict(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        grade(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
