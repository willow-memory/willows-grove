"""run — the gate is the script. Check-in, each turn, check-out, reconcile.

The sequencer only. No logic of its own lives here: every decision is made by one
of the seven parts, and this file only calls them in order.

  check-in  = boot -> predict
  each turn = verify -> open -> predict -> door -> (resolve) -> record -> grade -> close
  check-out = reverse -> view
  night     = resolve.night_pool inside a budget, yielding to presence
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from . import boot, gate, predict, record, resolve, reverse, view
from .record import h16

PKG = Path(__file__).resolve().parent


class Run:
    def __init__(
        self, box: Path, keys: dict[str, bytes], law: dict, clock: Callable[[], str]
    ):
        self.keys, self.law = keys, law
        self.version = record.version_of(PKG)
        self.rec = record.Record(box, clock, self.version, gate.token())
        self.sys = gate.system()
        self.answers: list[dict] = []
        self.graded: list[dict] = []

    def checkin(self) -> dict:
        report = boot.boot(self.rec, self.keys, self.law)
        self.rec.append(
            "boot", self.sys, hard_close=report["hard_close"], lines=report["lines"]
        )
        return report

    def turn(
        self,
        identity: dict,
        bite: str,
        change: dict | None = None,
        question: str = "",
        sources=(),
        models=(),
        budget: resolve.Budget | None = None,
    ) -> dict:
        try:
            who = gate.verify(identity, self.keys)
        except gate.Refused as e:
            return self.rec.append(
                "refused",
                self.sys,
                at="identity",
                reason=str(e),
                claimed=identity.get("who"),
            )
        n = 1 + sum(r["kind"] == "turn_open" for r in self.rec.rows())
        self.rec.open_turn(who, n, bite)
        pred = predict.declare(self.rec.rows())
        self.rec.append("predict", self.sys, turn=n, prediction=pred)

        out: dict = {"turn": n}
        if change is not None:
            change = {**change, "who": who.who}
            d = gate.door(change, self.law, self._script_index())
            row = self.rec.append(
                "door",
                who,
                turn=n,
                verdict=d.verdict,
                reason=d.reason,
                card=d.card,
                cites=change.get("cites", []),
            )
            out["door"] = row
            if change["kind"] == "script" and d.match:
                self._record_script(who, n, d.match)
            if d.verdict == "pass" and change.get("path") is not None:
                out["write"] = self.rec.write_file(
                    who,
                    change["path"],
                    change["data"],
                    live=change.get("live", False),
                    expect_vanish=change.get("expect_vanish", False),
                    cites=change.get("cites", []),
                )
        if question:
            a = resolve.answer(
                question,
                list(sources),
                list(models),
                budget or resolve.Budget(0),
                self.law,
                who.who,
            )
            out["answer"] = self.rec.append("answer", who, turn=n, **a)

        self.rec.append("bite", self.sys, turn=n, bite=bite)
        if pred["likely"]:
            g = predict.grade(pred, bite)
            self.graded.append(g)
            self.rec.append("grade", self.sys, turn=n, **g)
        self.rec.close_turn(who, n)
        return out

    def seal(self, subject: str, proof: str, human_key: bytes) -> dict:
        try:
            hum = gate.human(subject, proof, human_key)
        except gate.Refused as e:
            return self.rec.append(
                "refused", self.sys, at="seal", reason=str(e), subject=subject
            )
        return self.rec.append("seal", hum, subject=subject)

    def night(self, questions, models, budget: resolve.Budget, present) -> str:
        got, how = resolve.night_pool(list(questions), list(models), budget, present)
        for a in got:
            self.answers.append(a)
            self.rec.append("night_answer", self.sys, **a)
        self.rec.append(
            "night", self.sys, status=how, spent=budget.spent, units=budget.units
        )
        return how

    def checkout(
        self,
        *,
        changed_law=frozenset(),
        sealed=None,
        task_of=None,
        boot_report: dict | None = None,
    ) -> tuple[dict, str]:
        rep = reverse.reconcile(
            self.rec.box,
            self.rec.pile(),
            self.rec.rows(),
            self.version,
            changed_law=changed_law,
            answers=self.answers,
            sealed=sealed,
            task_of=task_of,
            predictions=self.graded,
        )
        screen = view.morning(rep, boot_report)
        self.rec.append("reconcile", self.sys, report_hash=h16(screen))
        return rep, screen

    # ── the script index lives in the record, not in memory ──────────────────
    def _script_index(self) -> list[dict]:
        return [
            {
                "label": f"row {r['n']}",
                "name": r.get("name"),
                "sha": r["sha"],
                "shape": r["shape"],
                "features": frozenset(r["features"]),
            }
            for r in self.rec.rows()
            if r["kind"] == "script"
        ]

    def _record_script(self, who, n: int, m: dict) -> None:
        rows = [r for r in self.rec.rows() if r["kind"] == "script"]
        root = rows[m["of"]]["family_root"] if m.get("of") is not None else m["sha"]
        self.rec.append(
            "script",
            who,
            turn=n,
            name=m.get("name"),
            sha=m["sha"],
            shape=m.get("shape", ""),
            features=sorted(m.get("features", ())),
            verdict=m["verdict"],
            family_root=root,
        )
