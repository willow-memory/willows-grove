"""6 view — the morning screen, drawn from the record and the reverse report.

Cites: CONST-VI (the view never overrides the record), CONST-IV.5 (standing and
ground are reported separately, never one as the other).

Order is fixed: NEEDS YOU, DISAGREEMENTS, AGREED NOT SEALED, GRADES, QUIET.
Outliers first; nothing smoothed. No model text; same report, same bytes.
"""

from __future__ import annotations

import json


def morning(report: dict, boot: dict | None = None) -> str:
    L: list[str] = []
    needs: list[str] = []
    if boot and boot["hard_close"]:
        needs += [f"HARD CLOSE · {x}" for x in boot["lines"]]
    needs += [
        f"turn {t} never closed"
        for t in report["open_turns"]
        if not any(
            x.startswith(f"turn {t} never closed")
            for x in (boot or {}).get("lines", [])
        )
    ]
    needs += [f"{i['where']} · {i['why']}" for i in report["pile"]["failing"]]
    for a in report["awaiting"]:
        card = json.dumps(a.get("card", {}), sort_keys=True)
        needs.append(f"{a['verdict']} · {a.get('reason', '')} · {card}")
    needs += [
        f"seen {o['seen']}x · {o['procedure']} · {o['offer']}" for o in report["offers"]
    ]
    needs += [
        f"re-check row {s['row']} ({s['kind']}) · {s['why']}"
        for s in report["surfaced"]
    ]
    L.append("NEEDS YOU")
    L += [f"  · {x}" for x in needs] or ["  · nothing"]
    if boot and boot["hard_close"]:
        L.append("  options: " + " · ".join(boot["options"]))

    L.append("DISAGREEMENTS")
    split = report["witness"]["split"]
    L += [
        f"  · {s['q']} · "
        + " | ".join(f"{a}: {', '.join(f)}" for a, f in s["by_answer"].items())
        + (
            f" · torn inside: {', '.join(s['torn_within_family'])}"
            if s["torn_within_family"]
            else ""
        )
        for s in split
    ] or ["  · none"]

    L.append("AGREED, NOT SEALED")
    L += [
        f"  · {a['q']} · {a['answer']} · {len(a['families'])} families · {a['standing']}"
        for a in report["witness"]["agreed"]
    ] or ["  · none"]

    L.append("GRADES")
    L += [
        f"  · {p['likely']} predicted, {p['actual']} happened"
        + (" · unforeseen" if p["unforeseen"] else "")
        for p in report["predictions"]
    ]
    L += [
        f"  · {m}: floor {g['floor']} on {g['floor_task']} · {json.dumps(g['by_task'], sort_keys=True)}"
        for m, g in report["grades"].items()
    ]
    if not report["predictions"] and not report["grades"]:
        L.append("  · nothing graded yet")

    c = report["pile"]["counts"]
    L.append("QUIET")
    L.append(
        f"  · pile {json.dumps(c, sort_keys=True)} · {report['chain_rows']} rows"
        f" · run {report['version']}"
    )
    if boot:
        held = sum(p["held"] for p in boot["probes"])
        L.append(
            f"  · probes held: {held}/{len(boot['probes'])}"
            f" · egress: {', '.join(boot['egress']) or 'none'}"
        )
    return "\n".join(L) + "\n"
