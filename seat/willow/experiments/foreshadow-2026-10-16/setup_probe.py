"""Print every candidate setup link (outcome -> later beat) so the rule can be chosen by looking."""

import json
import re
import sys

sys.path.insert(0, ".")
from harness import STOP  # noqa: E402


def stems(text):
    return [
        w.strip("'-")[:6]
        for w in re.findall(r"[a-z][a-z'\-]+", text.lower())
        if len(w.strip("'-")) >= 5 and w.strip("'-") not in STOP
    ]


def bigrams(text):
    s = stems(text)
    return {(a, b) for a, b in zip(s, s[1:])}


def low_phr(text):  # 2-word phrases incl. short words, for things like "who decides"
    w = re.findall(r"[a-z']+", text.lower())
    return {f"{a} {b}" for a, b in zip(w, w[1:]) if not (a in STOP and b in STOP)}


for wp in sys.argv[1:]:
    w = json.load(open(wp))
    print("\n#####", w["title"])
    flat = [(si, b) for si, sc in enumerate(w["scenes"]) for b in sc["beats"]]
    for i, (si, b) in enumerate(flat):
        if b["kind"] == "decision":
            break
        seen = " ".join(
            [w["setting"]]
            + [
                w["scenes"][j]["opening"][k]
                for j in range(si + 1)
                for k in range(len(w["scenes"][j]["opening"]))
            ]
            + [x["prompt"] for _, x in flat[: i + 1]]
            + [w["scenes"][j]["title"] for j in range(si + 1)]
        )
        later_parts = [
            x["prompt"] + " " + x.get("proposes", {}).get("fact", "")
            for _, x in flat[i + 1 :]
        ] + [
            w["scenes"][j]["title"] + " " + " ".join(w["scenes"][j]["opening"])
            for j in range(si + 1, len(w["scenes"]))
        ]
        later = " ".join(later_parts)
        uni = set(stems(later)) - set(stems(seen))
        bi = bigrams(later) - bigrams(seen)
        ph = low_phr(later) - low_phr(seen)
        for k, txt in b["outcomes"].items():
            hu = sorted(set(stems(txt)) & uni)
            hb = sorted(bigrams(txt) & bi)
            hp = sorted(low_phr(txt) & ph)
            print(f"{b['id']}-{k:6} uni={hu} bi={hb} phrase={hp}")
