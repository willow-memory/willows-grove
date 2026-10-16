"""peaks.py — the peak and valley pass over an authored the-table world.

The method from Nestor's life simulation (audits/2026-08-19-capability-probe/
lives/): run the world at volume, then read the edges of the distribution
rather than its mean. For each beat: how hard does it swing, and does the roll
change what the player meets next? For each path: how likely, and what only
exists down it?

Two sources that must agree:
  exact     — 2d6 + stat enumerated (36 outcomes), the same 10+/7-9/6- read
              StorySession uses
  measured  — N seeded runs through the real StorySession (real Engine.roll)

Decision beats are never sealed: a run stops at pending_seal().

Usage: python3 -I peaks.py <world.json> [N]
"""

from __future__ import annotations

import itertools
import json
import math
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path

# Sibling checkouts, beside this repo by default; override with env.
_REPO = Path(__file__).resolve().parents[4]
THE_TABLE = Path(
    os.environ.get("THE_TABLE_DIR", _REPO.parent / "safe-app-store/apps/the-table")
)
ONESCRIPT = Path(
    os.environ.get("ONESCRIPT_DIR", _REPO.parent / "willow-bot/one-script")
)
sys.path.insert(0, str(THE_TABLE))
from the_table.story_session import StorySession  # noqa: E402

BUCKETS = ("strong", "weak", "miss")
VALENCE = {"strong": 1, "weak": 0, "miss": -1}


def bucket_probs(stat: int) -> dict:
    c = Counter()
    for a, b in itertools.product(range(1, 7), repeat=2):
        t = a + b + stat
        c["strong" if t >= 10 else "weak" if t >= 7 else "miss"] += 1
    return {k: c[k] / 36 for k in BUCKETS}


def entropy(p: dict) -> float:
    return -sum(v * math.log2(v) for v in p.values() if v > 0)


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


def action_beats(world: dict) -> list[dict]:
    """The beats a run can play before the first decision, each tagged with its
    scene index (a copy; the world dict is not mutated)."""
    out = []
    for si, sc in enumerate(world["scenes"]):
        for b in sc["beats"]:
            if b["kind"] == "decision":
                return out
            out.append({**b, "_scene": si})
    return out


def first_decision(world: dict) -> dict | None:
    for sc in world["scenes"]:
        for b in sc["beats"]:
            if b["kind"] == "decision":
                return b
    return None


def exact(world: dict, sheets: list[dict], policy: str) -> dict:
    """sheets: one stat sheet per seated character; the beat at turn t is
    rolled by seat t % len(sheets), as StorySession rotates."""
    beats = action_beats(world)
    per_beat = {}
    for t, b in enumerate(beats):
        seat_stats = sheets[t % len(sheets)]
        if policy == "suggested":
            p = bucket_probs(seat_stats[b["suggests"]])
        else:  # uniform over the world's stats
            p = {k: 0.0 for k in BUCKETS}
            for s in world["stats"]:
                for k, v in bucket_probs(seat_stats[s]).items():
                    p[k] += v / len(world["stats"])
        per_beat[b["id"]] = p
    opening = " ".join([world["setting"]] + world["scenes"][0]["opening"])
    known0 = mentions(world, opening)
    paths = []
    for combo in itertools.product(BUCKETS, repeat=len(beats)):
        prob = math.prod(per_beat[b["id"]][k] for b, k in zip(beats, combo))
        curve, level, known, firsts = [], 0, set(known0), []
        scene_at = 0
        for b, k in zip(beats, combo):
            if (
                b["_scene"] != scene_at
            ):  # crossing into a new scene: its opening is seen
                scene_at = b["_scene"]
                known |= mentions(world, " ".join(world["scenes"][scene_at]["opening"]))
            level += VALENCE[k]
            curve.append(level)
            new = mentions(world, b["outcomes"][k]) - known
            known |= new
            if new:
                firsts.append({"beat": b["id"], "bucket": k, "introduces": sorted(new)})
        paths.append(
            {
                "path": "-".join(combo),
                "p": prob,
                "curve": curve,
                "firsts": firsts,
                "met": sorted(known),
                "held": combo.count("strong") >= combo.count("miss"),
            }
        )
    paths.sort(key=lambda x: -x["p"])
    return {"per_beat": per_beat, "paths": paths}


def measured(
    world_path: Path, world: dict, n: int, policy: str
) -> tuple[Counter, Counter]:
    paths, scenes = Counter(), Counter()
    for seed in range(n):
        s = StorySession(world_path)
        s.reset(seed)
        rng = random.Random(seed * 104729)
        combo = []
        while not s.is_terminal() and s.pending_seal() is None:
            beat = s._current_beat()
            stat = (
                beat["suggests"]
                if policy == "suggested"
                else rng.choice(world["stats"])
            )
            before = dict(s._tally)
            s.step(s.current_seat(), ("act", stat))
            combo.append(next(k for k in BUCKETS if s._tally[k] != before[k]))
        paths["-".join(combo)] += 1
        scenes[s._scene_idx] += 1  # read-only: where the run stopped
    return paths, scenes


def swing(world: dict, beat: dict, p: dict) -> dict:
    """How much the roll at this beat changes what comes after it."""
    intro = {k: sorted(mentions(world, beat["outcomes"][k])) for k in BUCKETS}
    distinct_casts = len({tuple(v) for v in intro.values()})
    return {
        "entropy_bits": round(entropy(p), 3),
        "max_bits": round(math.log2(3), 3),
        "outcome_casts": intro,
        "cast_diverges": distinct_casts > 1,
        "p_strong": round(p["strong"], 3),
        "p_weak": round(p["weak"], 3),
        "p_miss": round(p["miss"], 3),
    }


def main() -> None:
    world_path = Path(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    world = json.loads(world_path.read_text())
    seated = [c for c in world["characters"] if c["seat"]]
    sheets = [
        {s: c["stats"].get(s, world["base_stat"]) for s in world["stats"]}
        for c in seated
    ]
    from datetime import datetime, timezone

    report = {
        "world": world["title"],
        "seats": [c["name"] for c in seated],
        "stats": sheets,
        "n": n,
        "policies": {},
        "run_at": datetime.now(timezone.utc).isoformat(),
        "scenes": len(world["scenes"]),
    }
    dec = first_decision(world)
    report["decision"] = (
        {"beat": dec["id"], "proposed_by": dec["proposes"]["proposed_by"]}
        if dec
        else None
    )
    for policy in ("suggested", "random"):
        ex = exact(world, sheets, policy)
        me, stopped = measured(world_path, world, n, policy)
        rows = []
        for pth in ex["paths"]:
            got = me.get(pth["path"], 0)
            rows.append(
                {
                    **pth,
                    "p": round(pth["p"], 4),
                    "measured": round(got / n, 4),
                    "runs": got,
                }
            )
        beats = action_beats(world)
        report["policies"][policy] = {
            "swing": {
                b["id"]: {
                    **swing(world, b, ex["per_beat"][b["id"]]),
                    "scene": b["_scene"],
                }
                for b in beats
            },
            "paths": rows,
            "held_p": round(sum(r["p"] for r in rows if r["held"]), 4),
            "max_abs_gap": round(max(abs(r["p"] - r["measured"]) for r in rows), 4),
            "stopped_in_scene": {str(k): v for k, v in sorted(stopped.items())},
            "measured_bucket_rates": {
                b["id"]: {
                    k: round(
                        sum(r["runs"] for r in rows if r["path"].split("-")[i] == k)
                        / n,
                        4,
                    )
                    for k in BUCKETS
                }
                for i, b in enumerate(beats)
            },
        }
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
