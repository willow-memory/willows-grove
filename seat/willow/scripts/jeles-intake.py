#!/usr/bin/env python3
"""Seat intake wrapper — same as Jeles ``scripts/jeles-intake.py``.

Home: willows-grove/seat/willow. Point JELES_INTAKE_DIR or run from a cwd
where the seat intake tree is visible; default intake lives at
``seat/willow/jeles-intake/``.

    . $WILLOW_HOME/fleet.env
    python3 seat/willow/scripts/jeles-intake.py --probe-only
"""
from __future__ import annotations

import os
from pathlib import Path

# Prefer seat-local intake when the operator has not set an override.
_SEAT = Path(__file__).resolve().parents[1]
_INTAKE = _SEAT / "jeles-intake"
if _INTAKE.is_dir() and "JELES_INTAKE_DIR" not in os.environ:
    os.environ["JELES_INTAKE_DIR"] = str(_INTAKE)

try:
    from jeles.intake import main
except ImportError:
    import sys

    # Auto-resolve python interpreter with Jeles installed if running from another venv
    candidates: list[Path] = []
    if "JELES_PYTHON" in os.environ:
        candidates.append(Path(os.environ["JELES_PYTHON"]))
    jeles_repo = os.environ.get(
        "JELES_REPO",
        str(Path.home() / "github" / "hornbook-knowledge" / "Jeles"),
    )
    candidates.append(Path(jeles_repo) / ".venv" / "bin" / "python3")
    candidates.append(Path(jeles_repo) / ".venv" / "bin" / "python")
    willow_home = os.environ.get(
        "WILLOW_HOME",
        str(Path.home() / "sean-data-vault" / "willow-operator-box"),
    )
    candidates.append(Path(willow_home) / "venvs" / "willow-mcp" / "bin" / "python")
    candidates.append(Path(willow_home) / "venvs" / "jeles" / "bin" / "python3")
    candidates.append(
        Path.home() / "github" / "willow-memory" / "willow-mcp" / ".venv" / "bin" / "python"
    )

    this_exe = Path(sys.executable).absolute()
    for cand in candidates:
        cand_abs = cand.absolute()
        if cand_abs.is_file() and os.access(cand_abs, os.X_OK) and cand_abs != this_exe:
            os.execv(str(cand_abs), [str(cand_abs), *sys.argv])
    raise

if __name__ == "__main__":
    raise SystemExit(main())
