"""Flowering step 0 aggregation — reads raw run rows, never writes them.

Per the ladder plan (governance/proposals/2026-09-02-mcp-jobs-ladder-test-plan.md):
aggregation is a second script over immutable rows. Per the protocol
(docs/design/forge-convergence-flowering-experiment.md §5-6) it produces:

  scores/checklist-<date>.json   machine-checkable class items, every tier
  scores/rubric-<date>.csv       T5 operator blind sheet (tier hidden, shuffled)
  scores/rubric-<date>.key.json  blind_id -> tier; open only after scoring

Scored text is the reply after the last '</think>' (whole reply when absent);
see manifest.json qwen3_thinking_template.scoring_rule.

Usage: python aggregate.py [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEX_ID = re.compile(r"\b(?=[0-9a-fA-F]*[0-9])(?=[0-9a-fA-F]*[a-fA-F])[0-9a-fA-F]{8,12}\b")


def answer_text(raw: str) -> str:
    if "</think>" in raw:
        raw = raw.rsplit("</think>", 1)[1]
    return raw.strip()


def tier_paths(manifest: dict) -> dict[str, str]:
    runner = manifest["host_runner"]
    tiers = {m: t["out_path"] for m, t in runner["layer_b_chain_serial_CTR0WBSE"]["tiers"].items()}
    tiers["qwen3:4b"] = runner["qwen3_step0_unit_CP0QFV7C"]["out_path"]
    order = manifest["thresholds_from_section_8"]["chain_tiers"]
    return {m: tiers[m] for m in order}


def cites_ok(answer: str, must: list[str]) -> bool:
    low = answer.lower()
    return all(c.lower() in low for c in must)


def check(fx: dict, answer: str) -> dict:
    exp, cls = fx["expected"], fx["class"]
    low = answer.lower()
    items: dict[str, bool] = {}
    if cls == "G1":
        items["names_target"] = exp["to_app"].lower() in low
        items["cites_excerpts"] = cites_ok(answer, exp["must_cite"])
    elif cls == "G2":
        items["within_max_chars"] = len(answer) <= exp["max_chars"]
        items["names_repo_and_leg"] = all(n.lower() in low for n in exp["must_name"])
    elif cls == "G3":
        items["cites_gap"] = cites_ok(answer, exp["must_cite"])
        allowed = {e["id"].lower().removeprefix("ex-") for e in fx["excerpts"]}
        allowed |= {t.lower() for e in fx["excerpts"] for t in HEX_ID.findall(e["text"])}
        stray = sorted({t for t in HEX_ID.findall(answer) if t.lower() not in allowed})
        items["no_unrelated_ids"] = not stray
        if stray:
            items["_stray_ids"] = stray  # type: ignore[assignment]
    elif cls == "G4":
        items["names_builder_seat"] = exp["builder_seat"].lower() in low
    elif cls == "G5":
        head = low[:200]
        says_no = bool(re.search(r"\b(no|cannot|can't|not)\b", head)) and not re.match(r"\W*yes\b", head)
        items["answer_matches"] = says_no if exp["answer"] == "no" else exp["answer"] in head
        items["cites_excerpt"] = cites_ok(answer, exp["must_cite"])
    checks = [v for k, v in items.items() if not k.startswith("_")]
    needs_rubric = cls in ("G1", "G3")
    return {
        "class": cls,
        "excluded_from_T": fx["excluded_from_T"],
        "items": items,
        "machine_pass": all(checks),
        "escalated": "escalate" in low,
        "needs_operator_rubric": needs_rubric,
        "rubric_min": 4 if cls == "G1" else 3 if cls == "G3" else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2026-09-25")
    args = ap.parse_args()

    manifest = json.loads((HERE / "manifest.json").read_text())
    fixtures = {
        fx["id"]: fx
        for fx in (json.loads(p.read_text()) for p in sorted(HERE.glob("S-growth-*.json")))
    }
    out = HERE / "scores"
    out.mkdir(exist_ok=True)

    checklist: dict = {"date": args.date, "tiers": {}, "summary": {}}
    blind_rows: list[dict] = []
    for model, path in tier_paths(manifest).items():
        rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
        per: dict = {}
        for row in rows:
            fx = fixtures[row["fixture_id"]]
            ans = answer_text(row.get("raw_reply") or "")
            res = check(fx, ans) if not row.get("error") else {"class": fx["class"], "error": row["error"], "machine_pass": False, "excluded_from_T": fx["excluded_from_T"]}
            res["latency_ms"] = row.get("latency_ms")
            per[row["fixture_id"]] = res
            blind_rows.append({"model": model, "fixture": fx, "answer": ans, "run_file": Path(path).name})
        counted = [r for r in per.values() if not r["excluded_from_T"]]
        checklist["tiers"][model] = {"run_file": Path(path).name, "fixtures": per}
        checklist["summary"][model] = {
            "rows": len(per),
            "counted_for_T": len(counted),
            "machine_pass_counted": sum(r["machine_pass"] for r in counted),
            "pending_operator_rubric": sum(1 for r in counted if r.get("needs_operator_rubric") and r["machine_pass"]),
        }
    (out / f"checklist-{args.date}.json").write_text(json.dumps(checklist, indent=2) + "\n")

    rng = random.Random(f"flowering-{args.date}")
    rng.shuffle(blind_rows)
    key = {}
    with (out / f"rubric-{args.date}.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["blind_id", "scenario_id", "class", "policy", "brief", "excerpts", "answer", "score_1_5", "cloud_needed_YN", "notes"])
        for i, br in enumerate(blind_rows, 1):
            bid = f"B{i:03d}"
            fx = br["fixture"]
            ex = " | ".join(f"[{e['id']}] {e['text']}" for e in fx["excerpts"])
            w.writerow([bid, fx["id"], fx["class"], "P-growth", fx["brief"], ex, br["answer"], "", "", ""])
            key[bid] = {"model": br["model"], "scenario_id": fx["id"], "run_file": br["run_file"]}
    (out / f"rubric-{args.date}.key.json").write_text(json.dumps(key, indent=2) + "\n")

    for model, s in checklist["summary"].items():
        print(f"{model:18} machine_pass {s['machine_pass_counted']}/{s['counted_for_T']}  awaiting rubric {s['pending_operator_rubric']}")
    print(f"blind rows: {len(blind_rows)}")


if __name__ == "__main__":
    main()
