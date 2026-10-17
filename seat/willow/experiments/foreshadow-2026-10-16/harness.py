"""foreshadow harness — does the player see the next beat coming?

Plays an authored the-table world through the real StorySession (real 2d6
dice via apps/game Engine.roll), and at each approach point — just before a
beat arrives — measures three things:

  1. one-script predict (willow-bot/one-script/onescript/predict.py): the
     backward-counting forecaster, fed the beat kinds seen so far, graded
     with its own predict.grade against the beat that actually comes.
  2. authored foreshadow: of the next beat's anchors (its characters, and its
     content words new since the opening), how many the player has already
     seen in the text the dice actually delivered.
  3. code foreshadow: the same coverage after a deterministic hint line,
     built only from the world file, is added to the outcome narration.

Decision beats are never sealed here: the harness stops at pending_seal().
Only a named human seals; a test does not play one.

Usage: python3 -I harness.py <world.json> [N]
"""

from __future__ import annotations

import json
import os
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
sys.path.insert(0, str(ONESCRIPT))

from the_table.story_session import StorySession  # noqa: E402
from onescript import predict  # noqa: E402

STOP = set(
    """a an the and or but of to in on at by for with from as is are was were be been
it its it's this that these those he she they them his her their there here not no nor so than
then just only into out up down over under again once what who whom which when where why how
all any each few more most other some such own same too very can will would should could has
have had do does did doing i you we our your one two three before after while about against
between through during above below off still even back away anything nothing something someone
everyone nobody isn't doesn't don't won't can't couldn't wasn't aren't""".split()
)


def words(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z][a-z'\-]+", text.lower()):
        w = w.strip("'-")
        if len(w) > 3 and w not in STOP:
            out.add(w[:6])  # crude stem: "verified"/"verify" -> "verifi"/"verify"
    return out


def aliases(char: dict) -> set[str]:
    name = char["name"].lower()
    bare = re.sub(r"^the\s+", "", name)
    return {name, bare, bare.split()[0], char["id"].lower()}


def beat_text(beat: dict) -> str:
    parts = [beat["prompt"]]
    if "proposes" in beat:
        parts.append(beat["proposes"]["fact"])
    return " ".join(parts)


def beat_entities(world: dict, beat: dict) -> set[str]:
    text = beat_text(beat).lower()
    found = {
        c["id"]
        for c in world["characters"]
        if any(re.search(rf"\b{re.escape(a)}\b", text) for a in aliases(c))
    }
    if "proposes" in beat:
        found.add(beat["proposes"]["proposed_by"])
    return found


def seen_entities(world: dict, seen: str) -> set[str]:
    low = seen.lower()
    return {
        c["id"]
        for c in world["characters"]
        if any(re.search(rf"\b{re.escape(a)}\b", low) for a in aliases(c))
    }


def hint_for(world: dict, beat: dict) -> str:
    """The code foreshadow: one line, from the world file only, no model."""
    chars = {c["id"]: c for c in world["characters"]}
    ents = sorted(beat_entities(world, beat))
    bits = [
        f"{chars[e]['name']} ({chars[e]['role'].split(';')[0]})"
        for e in ents
        if not chars[e]["seat"]
    ]
    line = (
        "Somewhere at the edge of things: "
        + (", ".join(bits) if bits else "nothing named yet")
        + "."
    )
    if beat["kind"] == "decision":
        who = chars[beat["proposes"]["proposed_by"]]["name"]
        line += f" And a claim {who} made once, that nobody has checked since."
    return line


def play(world_path: Path, seed: int, policy: str) -> list[dict]:
    """One run to the first pending seal (or terminal). Returns one record per
    approach point: what the player had seen, and the beat that came next."""
    s = StorySession(world_path)
    world = s.world
    obs = s.reset(seed)
    seen = " ".join(obs.narration)
    history: list[dict] = []
    points = []
    while not s.is_terminal():
        beat = (
            s._current_beat()
        )  # read-only peek: the harness grades, it does not steer
        rows = [{"kind": "bite", "bite": h["kind"]} for h in history]
        pred = predict.declare(rows)
        if history:  # an approach point needs something already played
            prior = history[-1]
            ents_next = beat_entities(world, beat)
            new_anchor = words(beat_text(beat)) - words(
                " ".join([world["setting"]] + world["scenes"][0]["opening"])
            )
            hinted = seen + " " + hint_for(world, beat)
            points.append(
                {
                    "beat": beat["id"],
                    "kind": beat["kind"],
                    "path": "-".join(h["bucket"] for h in history),
                    "predict": predict.grade(pred, beat["kind"]),
                    "ent_need": sorted(ents_next),
                    "ent_authored": sorted(ents_next & seen_entities(world, seen)),
                    "ent_coded": sorted(ents_next & seen_entities(world, hinted)),
                    "word_need": len(new_anchor),
                    "word_authored": len(new_anchor & words(seen)),
                    "word_coded": len(new_anchor & words(hinted)),
                    "prior_beat": prior["id"],
                }
            )
        if beat["kind"] == "decision":
            break  # pending_seal(): a named human's, not ours
        stat = beat.get("suggests") if policy == "suggested" else None
        if stat is None:
            import random as _r

            stat = _r.Random(seed * 7919 + len(history)).choice(world["stats"])
        o = s.step(s.current_seat(), ("act", stat))
        bucket = s._tally and next(
            b for b, txt in beat["outcomes"].items() if txt == o.narration[0]
        )
        history.append({"id": beat["id"], "kind": beat["kind"], "bucket": bucket})
        seen += " " + " ".join(o.narration)
    return points


def main() -> None:
    world_path = Path(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    report: dict = {"world": world_path.name, "n": n, "policies": {}}
    for policy in ("suggested", "random"):
        agg: dict = {}
        paths: Counter = Counter()
        for seed in range(n):
            for p in play(world_path, seed, policy):
                a = agg.setdefault(
                    p["beat"],
                    {
                        "kind": p["kind"],
                        "n": 0,
                        "predict_hit": 0,
                        "predict_unforeseen": 0,
                        "ent_need": p["ent_need"],
                        "ent_authored_full": 0,
                        "ent_coded_full": 0,
                        "ent_authored_sum": 0,
                        "ent_coded_sum": 0,
                        "word_need": p["word_need"],
                        "word_authored_sum": 0,
                        "word_coded_sum": 0,
                        "by_path": {},
                    },
                )
                a["n"] += 1
                a["predict_hit"] += p["predict"]["hit"]
                a["predict_unforeseen"] += p["predict"]["unforeseen"]
                need = len(p["ent_need"]) or 1
                a["ent_authored_sum"] += len(p["ent_authored"]) / need
                a["ent_coded_sum"] += len(p["ent_coded"]) / need
                a["ent_authored_full"] += set(p["ent_authored"]) == set(p["ent_need"])
                a["ent_coded_full"] += set(p["ent_coded"]) == set(p["ent_need"])
                a["word_authored_sum"] += p["word_authored"] / (p["word_need"] or 1)
                a["word_coded_sum"] += p["word_coded"] / (p["word_need"] or 1)
                bp = a["by_path"].setdefault(
                    p["path"],
                    {
                        "n": 0,
                        "ent_authored": p["ent_authored"],
                        "word_authored": p["word_authored"],
                    },
                )
                bp["n"] += 1
                paths[p["path"]] += 1
        for a in agg.values():
            k = a["n"]
            for key in (
                "predict_hit",
                "predict_unforeseen",
                "ent_authored_full",
                "ent_coded_full",
            ):
                a[key] = round(a[key] / k, 3)
            for key in (
                "ent_authored_sum",
                "ent_coded_sum",
                "word_authored_sum",
                "word_coded_sum",
            ):
                a[key.replace("_sum", "_mean")] = round(a.pop(key) / k, 3)
        report["policies"][policy] = agg
    world = json.loads(world_path.read_text())
    report["hints"] = {
        b["id"]: hint_for(world, b) for sc in world["scenes"] for b in sc["beats"]
    }
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
