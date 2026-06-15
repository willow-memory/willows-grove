"""grove/paths.py — Resolve Willow repo root and CLI for dashboard subprocesses.
b17: WGRV1 · ΔΣ=42
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def resolve_willow_root() -> Path:
    """Best-effort Willow 2.0 repo root (env, then common install paths)."""
    env = (os.environ.get("WILLOW_ROOT") or "").strip()
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p.resolve()
    here = Path(__file__).resolve().parent.parent
    candidates = [
        here,
        Path.home() / "willow-2.0",
        Path.home() / "github" / "willow-2.0",
        Path.home() / "willow-2.0",
    ]
    for p in candidates:
        if (p / "willow.sh").is_file() or (p / "sap").is_dir():
            return p.resolve()
    return here


def resolve_willow_cli() -> list[str]:
    """Argv prefix to invoke willow.sh (or bare willow on PATH)."""
    root = resolve_willow_root()
    sh = root / "willow.sh"
    if sh.is_file():
        return ["bash", str(sh)]
    return ["willow"]


def resolve_git_repo() -> Path:
    """Git working tree for status/PR panes."""
    env = (os.environ.get("GROVE_GIT_REPO") or "").strip()
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p.resolve()
    root = resolve_willow_root()
    here = Path(__file__).resolve().parent.parent
    for candidate in (here, root):
        if (candidate / ".git").exists():
            return candidate.resolve()
    return here
