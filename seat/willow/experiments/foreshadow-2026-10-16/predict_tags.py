"""predict_tags.py — the outcome-tagging forecaster.

Ironworks showed the dice there change WHO KNOWS WHAT, not who appears. So this
forecaster tags every outcome by what it changes, then forecasts, from the
world file alone (no dice run), how often a run carries each kind of change
before the decision, and which beat is the pivot.

The tagger is a fixed keyword lexicon written from Hasbeen and Ironworks only
(2026-10-16), before any Aetheris outcome was read. It is the fallback the
grove seat uses when no model answers: no Ollama was reachable in this
container. A local model would replace tag_outcome(); the claims and the
grader stay the same.

Odds rotate seats the way StorySession does (turn t -> seat t % seats).

Usage: python3 -I predict_tags.py <world.json> <out.json>
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

BUCKETS = ("strong", "weak", "miss")

# What an outcome changes. Phrases, matched case-insensitively on word starts.
LEXICON = {
    "exposure": [
        r"heard",
        r"\bsound",
        r"echo",
        r"\bnoise",
        r"beacon",
        r"clatter",
        r"groan",
        r"rings? through",
        r"\bspotted",
        r"\bcaught\b",
        r"patrol",
        r"exposed",
        r"now knows",
        r"they heard",
        r"\bsaw\b",
        r"\bseen\b",
        r"alarm",
        r"gave away",
        r"carries",
    ],
    "injury": [
        r"bleed",
        r"blood",
        r"\bhurt",
        r"wound",
        r"injur",
        r"goes down",
        r"\bburn",
        r"\bpain",
        r"limp",
        r"bruis",
        r"\bknee\b",
    ],
    "insight": [
        r"\breads?\b",
        r"surfaces",
        r"citation",
        r"timestamp",
        r"\bmaps?\b",
        r"\bfinds?\b",
        r"\bfound\b",
        r"\blearns?",
        r"understand",
        r"\brecord",
        r"\bclue",
        r"realiz",
        r"names",
        r"follows",
    ],
    "setback": [
        r"\bloses?\b",
        r"\blost\b",
        r"chokes",
        r"salvage",
        r"malformed",
        r"\bdrops?\b",
        r"\bclosed?\b",
        r"insufficient",
        r"\bflag",
        r"resist",
        r"stiff",
        r"misjudg",
        r"panic",
        r"freezes",
    ],
    "trust": [
        r"together",
        r"respect",
        r"\bhelp",
        r"unasked",
        r"\btrust",
        r"\bagree",
        r"quietly",
        r"hands visible",
        r"\bally",
    ],
}


def tag_outcome(text: str) -> list[str]:
    low = text.lower()
    return sorted(
        t for t, pats in LEXICON.items() if any(re.search(p, low) for p in pats)
    )


def bucket_probs(stat: int) -> dict:
    c = dict.fromkeys(BUCKETS, 0)
    for a, b in itertools.product(range(1, 7), repeat=2):
        t = a + b + stat
        c["strong" if t >= 10 else "weak" if t >= 7 else "miss"] += 1
    return {k: v / 36 for k, v in c.items()}


def jaccard_distance(a: set, b: set) -> float:
    return 0.0 if not (a | b) else 1 - len(a & b) / len(a | b)


def main() -> None:
    world_path, out = Path(sys.argv[1]), Path(sys.argv[2])
    world = json.loads(world_path.read_text())
    seated = [c for c in world["characters"] if c["seat"]]
    sheets = [
        {s: c["stats"].get(s, world["base_stat"]) for s in world["stats"]}
        for c in seated
    ]

    playable = []
    for sc in world["scenes"]:
        for b in sc["beats"]:
            if b["kind"] == "decision":
                break
            playable.append(b)
        else:
            continue
        break

    tags = {
        b["id"]: {k: tag_outcome(b["outcomes"][k]) for k in BUCKETS} for b in playable
    }

    def odds(policy: str) -> dict:
        out = {}
        for t, b in enumerate(playable):
            sheet = sheets[t % len(sheets)]
            if policy == "suggested":
                out[b["id"]] = bucket_probs(sheet[b["suggests"]])
            else:
                acc = dict.fromkeys(BUCKETS, 0.0)
                for s in world["stats"]:
                    for k, v in bucket_probs(sheet[s]).items():
                        acc[k] += v / len(world["stats"])
                out[b["id"]] = acc
        return out

    claims = []
    for policy in ("suggested", "random"):
        p = odds(policy)
        carry = dict.fromkeys(LEXICON, 0.0)
        for combo in itertools.product(BUCKETS, repeat=len(playable)):
            pr = math.prod(p[b["id"]][k] for b, k in zip(playable, combo))
            have = set().union(
                *(set(tags[b["id"]][k]) for b, k in zip(playable, combo))
            )
            for t in have:
                carry[t] += pr
        for t, v in carry.items():
            claims.append(
                {
                    "id": f"C-{t}-{policy}",
                    "claim": f"{v:.1%} of runs ({policy}) carry at least one '{t}' outcome before the decision; measured within 0.07.",
                    "check": {
                        "kind": "carry",
                        "tag": t,
                        "policy": policy,
                        "p": round(v, 4),
                        "tol": 0.07,
                    },
                }
            )
        for b in playable:
            claims.append(
                {
                    "id": f"A-{b['id']}-{policy}",
                    "claim": f"Beat {b['id']} ({policy}) odds strong/weak/miss = "
                    + "/".join(f"{p[b['id']][k]:.3f}" for k in BUCKETS)
                    + "; measured within 0.05 each.",
                    "check": {
                        "kind": "beat_probs",
                        "beat": b["id"],
                        "policy": policy,
                        "p": p[b["id"]],
                        "tol": 0.05,
                    },
                }
            )

    # Pivot: the beat whose three outcomes differ most in what they change,
    # weighted by how uncertain the roll is (suggested approach).
    p = odds("suggested")
    score = {}
    for b in playable:
        sets = [set(tags[b["id"]][k]) for k in BUCKETS]
        div = (
            sum(jaccard_distance(x, y) for x, y in itertools.combinations(sets, 2)) / 3
        )
        ent = -sum(v * math.log2(v) for v in p[b["id"]].values() if v > 0)
        score[b["id"]] = round(div * ent, 4)
    pivot = max(score, key=score.get)
    claims.append(
        {
            "id": "P-pivot",
            "claim": f"The pivot is {pivot}: its outcomes differ most in what they change, weighted by roll uncertainty ({score}).",
            "check": {"kind": "pivot", "beat": pivot, "scores": score},
        }
    )

    for b in playable:
        for k in BUCKETS:
            claims.append(
                {
                    "id": f"T-{b['id']}-{k}",
                    "claim": f"{b['id']} {k} changes: {tags[b['id']][k] or ['nothing tagged']}.",
                    "check": {
                        "kind": "tags",
                        "beat": b["id"],
                        "bucket": k,
                        "tags": tags[b["id"]][k],
                    },
                }
            )

    doc = {
        "world": world["title"],
        "world_file": world_path.name,
        "world_sha256": hashlib.sha256(world_path.read_bytes()).hexdigest(),
        "written_at": datetime.now(timezone.utc).isoformat(),
        "tagger": "lexicon-v1 (Hasbeen + Ironworks vocabulary; no model reachable)",
        "lexicon": LEXICON,
        "playable_beats": [b["id"] for b in playable],
        "claims": claims,
    }
    body = json.dumps(doc, indent=1, sort_keys=True)
    out.write_text(body)
    print(hashlib.sha256(body.encode()).hexdigest(), out, f"{len(claims)} claims")


if __name__ == "__main__":
    main()
