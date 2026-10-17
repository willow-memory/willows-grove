"""Predict random things: forecasts first, a public beacon after, code grades.

Each round names a drand beacon round that has not happened yet. Forecasts
(a probability that each question comes out "yes") are written while that
round is still in the future; the script refuses one written after. Once the
beacon publishes, its randomness seeds the data, code works out each answer,
and grades every forecaster by Brier score beside two baselines: a coin flip
(0.5 on everything) and the oracle (the exact probability, worked out by code
and shown only at reveal).

    python3 -I play.py open [--ahead N]          # a round N beacon rounds ahead
    python3 -I play.py forecast R WHO q1=0.5 ...  # before the beacon round
    python3 -I play.py reveal R                   # after it
    python3 -I play.py board                      # every graded round

Standard library only. drand: https://api.drand.sh (the "default" chain).
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
import urllib.request
from fractions import Fraction
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUNDS = HERE / "rounds"
DRAND = "https://api.drand.sh"
CHAIN = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
GENESIS, PERIOD = 1595431050, 30
PER_ROUND = 4


# ── the beacon ───────────────────────────────────────────────────────────────
def beacon(rnd: int | str = "latest") -> dict:
    url = f"{DRAND}/{CHAIN}/public/{rnd}"
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read())


def round_now() -> int:
    """The beacon round current by the clock (drand's own formula)."""
    return (int(time.time()) - GENESIS) // PERIOD + 1


def round_time(rnd: int) -> int:
    return GENESIS + (rnd - 1) * PERIOD


# ── a stream of numbers from a seed, the same on every Python ────────────────
class Stream:
    def __init__(self, seed: bytes):
        self.seed, self.n = seed, 0

    def u32(self) -> int:
        d = hashlib.sha256(self.seed + self.n.to_bytes(8, "big")).digest()
        self.n += 1
        return int.from_bytes(d[:4], "big")

    def below(self, k: int) -> int:
        """Uniform in 0..k-1, by rejection: no modulo bias."""
        cap = (1 << 32) - (1 << 32) % k
        while (x := self.u32()) >= cap:
            pass
        return x % k

    def die(self, sides: int) -> int:
        return self.below(sides) + 1

    def shuffle(self, xs: list) -> list:
        xs = list(xs)
        for i in range(len(xs) - 1, 0, -1):
            j = self.below(i + 1)
            xs[i], xs[j] = xs[j], xs[i]
        return xs


# ── the deck: each question, how its data is drawn, and its exact odds ───────
def _dice_odds(n: int, sides: int, test) -> Fraction:
    hits = sum(1 for r in product(range(1, sides + 1), repeat=n) if test(r))
    return Fraction(hits, sides**n)


def _no_run(n: int, k: int) -> int:
    """How many n-flip sequences have no run of k heads."""
    ways = [0] * k  # ways[j]: sequences ending in exactly j heads
    ways[0] = 1
    for _ in range(n):
        new = [0] * k
        new[0] = sum(ways)
        for j in range(1, k):
            new[j] = ways[j - 1]
        ways = new
    return sum(ways)


def _longest(seq) -> int:
    best = run = 0
    for x in seq:
        run = run + 1 if x else 0
        best = max(best, run)
    return best


def _birthday(n: int, days: int) -> Fraction:
    p = Fraction(1)
    for i in range(n):
        p *= Fraction(days - i, days)
    return 1 - p


def _derangements(n: int) -> int:
    d = [1, 0]
    for i in range(2, n + 1):
        d.append((i - 1) * (d[-1] + d[-2]))
    return d[n]


DECK = {
    "birthday": (
        "23 people, birthdays drawn from 365 days: do any two share one?",
        lambda s: len({s.die(365) for _ in range(23)}) < 23,
        lambda: _birthday(23, 365),
    ),
    "3d6": (
        "Roll 3d6: is the sum 13 or more?",
        lambda s: sum(s.die(6) for _ in range(3)) >= 13,
        lambda: _dice_odds(3, 6, lambda r: sum(r) >= 13),
    ),
    "streak": (
        "Flip 20 coins: is there a run of 4 or more heads?",
        lambda s: _longest(s.below(2) for _ in range(20)) >= 4,
        lambda: 1 - Fraction(_no_run(20, 4), 2**20),
    ),
    "pair": (
        "Deal 5 cards from a shuffled deck: do two share a rank?",
        lambda s: len({c // 4 for c in s.shuffle(range(52))[:5]}) < 5,
        lambda: 1 - Fraction(math.comb(13, 5) * 4**5, math.comb(52, 5)),
    ),
    "ten": (
        "Roll 10d10: does a 10 come up?",
        lambda s: any(s.die(10) == 10 for _ in range(10)),
        lambda: 1 - Fraction(9, 10) ** 10,
    ),
    "fixed": (
        "Shuffle 8 numbered cards: is any card in its own place?",
        lambda s: any(c == i for i, c in enumerate(s.shuffle(range(8)))),
        lambda: 1 - Fraction(_derangements(8), math.factorial(8)),
    ),
    "2d20": (
        "Roll 2d20: is the sum over 25?",
        lambda s: s.die(20) + s.die(20) > 25,
        lambda: _dice_odds(2, 20, lambda r: sum(r) > 25),
    ),
    "six": (
        "Flip 12 coins: exactly 6 heads?",
        lambda s: sum(s.below(2) for _ in range(12)) == 6,
        lambda: Fraction(math.comb(12, 6), 2**12),
    ),
    "distinct": (
        "Roll 6d6: are all six faces different?",
        lambda s: len({s.die(6) for _ in range(6)}) == 6,
        lambda: Fraction(math.factorial(6), 6**6),
    ),
    "d100": (
        "Roll a d100: 37 or under?",
        lambda s: s.die(100) <= 37,
        lambda: Fraction(37, 100),
    ),
    "gap": (
        "Roll 2d6 twice: do the two sums differ by 3 or more?",
        lambda s: abs(
            (s.die(6) + s.die(6)) - (s.die(6) + s.die(6))
        )
        >= 3,
        lambda: _dice_odds(4, 6, lambda r: abs(r[0] + r[1] - r[2] - r[3]) >= 3),
    ),
    "max": (
        "Draw 5 numbers from 1–100: is the largest 90 or more?",
        lambda s: max(s.die(100) for _ in range(5)) >= 90,
        lambda: 1 - Fraction(89, 100) ** 5,
    ),
}


# ── the round files ──────────────────────────────────────────────────────────
def path(r: int) -> Path:
    return ROUNDS / f"{r:03d}.json"


def load(r: int) -> dict:
    return json.loads(path(r).read_text())


def save(r: int, data: dict) -> None:
    ROUNDS.mkdir(exist_ok=True)
    path(r).write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def cmd_open(ahead: int = 6) -> int:
    latest = beacon()
    n = max((int(p.stem) for p in ROUNDS.glob("*.json")), default=0) + 1
    # the questions are picked by a beacon round already public: no one chose them
    pick = Stream(bytes.fromhex(latest["randomness"]) + b"pick").shuffle(sorted(DECK))
    target = latest["round"] + ahead
    save(
        n,
        {
            "round": n,
            "opened_by_beacon": latest["round"],
            "target": target,
            "target_at": round_time(target),
            "questions": {q: DECK[q][0] for q in sorted(pick[:PER_ROUND])},
            "forecasts": {},
        },
    )
    t = time.strftime("%H:%M:%S UTC", time.gmtime(round_time(target)))
    print(f"round {n}: forecasts close at beacon {target} ({t})")
    for q, text in load(n)["questions"].items():
        print(f"  {q:9} {text}")
    return 0


def cmd_forecast(r: int, who: str, pairs: list[str]) -> int:
    data = load(r)
    if "reveal" in data:
        print(f"round {r} is already revealed", file=sys.stderr)
        return 1
    now = max(round_now(), beacon()["round"])
    if now >= data["target"]:
        print(f"too late: beacon round {data['target']} is out", file=sys.stderr)
        return 1
    got = {}
    for p in pairs:
        q, _, v = p.partition("=")
        if q not in data["questions"]:
            print(f"no question {q!r} in round {r}", file=sys.stderr)
            return 1
        x = float(v.rstrip("%")) / (100 if v.endswith("%") else 1)
        if not 0 <= x <= 1:
            print(f"{q}: {v} is not a probability", file=sys.stderr)
            return 1
        got[q] = x
    if set(got) != set(data["questions"]):
        missing = sorted(set(data["questions"]) - set(got))
        print(f"every question needs a forecast; missing {missing}", file=sys.stderr)
        return 1
    if who in data["forecasts"]:
        print(f"{who} already forecast round {r}; a forecast stands", file=sys.stderr)
        return 1
    data["forecasts"][who] = {
        "p": got,
        "at": int(time.time()),
        "beacon_then": now,
        "sha256": hashlib.sha256(canon(got).encode()).hexdigest(),
    }
    save(r, data)
    print(f"{who}: forecast for round {r} kept, {data['target'] - now} beacon rounds early")
    return 0


def brier(p: float, yes: bool) -> float:
    return (p - (1.0 if yes else 0.0)) ** 2


def cmd_reveal(r: int) -> int:
    data = load(r)
    if "reveal" not in data:
        wait = round_time(data["target"]) - time.time()
        if wait > 0:
            print(f"beacon {data['target']} is {wait:.0f}s away", file=sys.stderr)
            return 1
        b = beacon(data["target"])
        seed = bytes.fromhex(b["randomness"])
        answers, oracle = {}, {}
        for q in data["questions"]:
            _, draw, odds = DECK[q]
            answers[q] = bool(draw(Stream(seed + q.encode())))
            oracle[q] = float(odds())
        data["reveal"] = {"beacon": b, "answers": answers, "oracle": oracle}
        save(r, data)
    rev = data["reveal"]
    rows = dict(data["forecasts"])
    rows["coin flip"] = {"p": {q: 0.5 for q in data["questions"]}}
    rows["oracle"] = {"p": rev["oracle"]}
    print(f"round {r}, beacon {data['target']}")
    print(f"  {'question':9} {'answer':6} " + " ".join(f"{w[:10]:>10}" for w in rows))
    for q in data["questions"]:
        a = "yes" if rev["answers"][q] else "no"
        cells = " ".join(f"{rows[w]['p'][q]:>10.0%}" for w in rows)
        print(f"  {q:9} {a:6} {cells}")
    scores = " ".join(f"{score(rows[w], rev):>10.3f}" for w in rows)
    print(f"  {'Brier':9} {'':6} {scores}   (lower is better)")
    return 0


def score(row: dict, rev: dict) -> float:
    qs = rev["answers"]
    return sum(brier(row["p"][q], qs[q]) for q in qs) / len(qs)


def cmd_board() -> int:
    total: dict[str, list[float]] = {}
    for p in sorted(ROUNDS.glob("*.json")):
        d = json.loads(p.read_text())
        if "reveal" not in d:
            continue
        rows = dict(d["forecasts"])
        rows["coin flip"] = {"p": {q: 0.5 for q in d["questions"]}}
        rows["oracle"] = {"p": d["reveal"]["oracle"]}
        for w, row in rows.items():
            for q in d["questions"]:
                total.setdefault(w, []).append(brier(row["p"][q], d["reveal"]["answers"][q]))
    if not total:
        print("no graded round yet")
        return 0
    print(f"  {'who':12} {'questions':>9} {'mean Brier':>11}")
    for w, xs in sorted(total.items(), key=lambda kv: sum(kv[1]) / len(kv[1])):
        print(f"  {w:12} {len(xs):>9} {sum(xs) / len(xs):>11.3f}")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "open":
        ahead = int(rest[1]) if rest[:1] == ["--ahead"] else 6
        return cmd_open(ahead)
    if cmd == "forecast" and len(rest) >= 3:
        return cmd_forecast(int(rest[0]), rest[1], rest[2:])
    if cmd == "reveal" and len(rest) == 1:
        return cmd_reveal(int(rest[0]))
    if cmd == "board":
        return cmd_board()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
