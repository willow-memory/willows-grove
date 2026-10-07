"""The one script, run on this box.

    cd docs/design/one-script
    python3 -m onescript checkin            # boot: record, probes, the four gates
    python3 -m onescript turn "the bite"    # one turn as the desk
    python3 -m onescript checkout           # reverse, then the morning screen

The box defaults to the repo's `.flow/onescript/` (excluded from git). The
record persists there between commands, so check-in, turns and check-out are
one run across several invocations.

Every command first writes an `invocation` row: the argv, the root, the box,
and the hash of every input it read. A replay reads that row back; when the
bytes differ, the row names which input moved.

Honest about itself: the keys are the skeleton's HMAC secrets, kept beside the
box in `.flow/onescript-keys/` (0600), not passkeys, and still inside what the
sandbox can see. The desk signs its own identity with a key it can read,
so a turn proves the record's chain, not who sat at the keyboard.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import boot, gate, record
from .run import PKG, Run

ROOT = PKG.parents[3]  # onescript -> one-script -> design -> docs -> repo
CONSTITUTION = ROOT / "governance" / "CONSTITUTION.md"
CI = ROOT / ".github" / "workflows" / "tests.yml"
DESK = ("desk", "claude")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _keys(path: Path) -> dict[str, bytes]:
    """The signing secrets live beside the box, never in it: the record's own
    three-way check flags any file in the box the run didn't write."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump({DESK[0]: secrets.token_hex(32)}, f)
    return {k: bytes.fromhex(v) for k, v in json.loads(path.read_text()).items()}


def _law(text: str) -> dict:
    ids = sorted(set(re.findall(r"CONST-[IVXL]+(?:\.\d+)?", text)))
    return {"trace_ids": ids, "grants": []}


def _in_venv(venv: Path):
    """The toolchain gate reads the bot's venv, where the one script's tools
    live (D2), never whatever happens to be first on PATH."""

    def version_of(tool: str) -> str | None:
        exe = venv / "bin" / tool
        if not exe.exists():
            return None
        _, last = boot._run([str(exe), "--version"], ".", timeout=30)
        m = re.search(r"\d+\.\d+(?:\.\d+)?", last)
        return m.group(0) if m else last

    return version_of


def _gate_cfg(no_tests: bool, ci_text: str, venv: Path) -> dict:
    pin = re.search(r"ruff==([\d.]+)", ci_text)
    cfg: dict = {
        "pins": {"tools": {"ruff": pin.group(1)}} if pin else {},
        "version_of": _in_venv(venv),
        "repos": [str(ROOT)],
    }
    if not no_tests:
        cfg["tests"] = [
            {
                "name": "onescript",
                "argv": [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "-p",
                    "no:cacheprovider",
                    "onescript/tests",
                ],
                "cwd": str(PKG.parent),
                "needs": ["pytest"],
            }
        ]
    return cfg


def _read(path: Path) -> tuple[str, str | None]:
    """Text and its hash, or ("", None) when the input is missing: recorded, not guessed."""
    if not path.exists():
        return "", None
    data = path.read_bytes()
    return data.decode("utf-8"), record.h256(data)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="onescript")
    p.add_argument("--box", type=Path, default=ROOT / ".flow" / "onescript")
    p.add_argument(
        "--keys", type=Path, default=ROOT / ".flow" / "onescript-keys" / "keys.json"
    )
    p.add_argument(
        "--venv",
        type=Path,
        default=Path(os.environ.get("WILLOW_HOME", "~")).expanduser()
        / "venvs"
        / "willow-bot",
        help="the venv whose tools the toolchain gate checks (the bot's)",
    )
    p.add_argument("--now", help="fixed clock, for replays and tests")
    p.add_argument("--no-tests", action="store_true", help="skip the tests gate")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("checkin")
    t = sub.add_parser("turn")
    t.add_argument("bite")
    sub.add_parser("checkout")
    args = p.parse_args(argv)

    clock = (lambda: args.now) if args.now else _now
    law_text, law_sha = _read(CONSTITUTION)
    ci_text, ci_sha = _read(CI)
    if args.keys.resolve().is_relative_to(args.box.resolve()):
        print("refused: the keys file can't live inside the box")
        return 2
    keys = _keys(args.keys)
    law = _law(law_text)
    run = Run(args.box, keys, law, clock)
    run.rec.append(
        "invocation",
        run.sys,
        cmd=args.cmd,
        argv=list(argv if argv is not None else sys.argv[1:]),
        root=str(ROOT),
        box=str(args.box),
        venv=str(args.venv),
        inputs={
            "governance/CONSTITUTION.md": law_sha,
            ".github/workflows/tests.yml": ci_sha,
            "onescript": run.version,
        },
        trace_ids=len(law["trace_ids"]),
    )

    if args.cmd == "checkin":
        try:
            rep = run.checkin(_gate_cfg(args.no_tests, ci_text, args.venv))
        except boot.BoxWontOpen as e:
            print(f"BOX WON'T OPEN: {e}")
            return 3
        print(_checkin_screen(rep))
        return 1 if rep["hard_close"] else 0

    if args.cmd == "turn":
        who, family = DESK
        ident = {"who": who, "family": family, "sig": gate.sign(keys[who], who, family)}
        out = run.turn(ident, args.bite)
        print(json.dumps(out, indent=1, sort_keys=True, default=str))
        return 0

    _, screen = run.checkout()
    print(screen)
    return 0


def _checkin_screen(rep: dict) -> str:
    L = ["CHECK-IN"]
    held = sum(p["held"] for p in rep["probes"])
    L.append(f"probes: {held}/{len(rep['probes'])} held")
    for g in rep["gates"]:
        why = f" — {g['why']}" if g["why"] else ""
        L.append(f"  {g['verdict']:12} {g['gate']}: {g['where']}{why}")
    if rep["hard_close"]:
        L.append("HARD CLOSE:")
        L += [f"  {x}" for x in rep["lines"]]
        L.append("options: " + " | ".join(rep["options"]))
    else:
        L.append("open")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
