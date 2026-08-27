# b17: WGRV1 ΔΣ=42
"""Reader for the seed's six movements (D16 human-onboarding story).

D16 (`docs/design/willow-grove-premise.md`) seals: the six-part canon *IS*
the human onboarding — six movements, one per chapter, walked at first
boot. The canonical source is the charter's seed dir
(`willow-memory/willow/seed/`), which holds either:

* a `canon/` tree of `NN-<slug>.md` chapter files (the current shape,
  operator-ratified 2026-07-22), or
* a single `seed.py` script whose `movement_N_<slug>` functions carry the
  onboarding voice inline as docstrings (SEED9 shape).

This reader supports both, so Grove's `/seed/` route (D16) renders the
real story when the charter is on disk. When it isn't, Grove still boots:
`load_movements()` returns a six-movement stub carrying titles + a
one-sentence body per D16's outline, so `/seed/` is proof-of-life on any
host (autonomous-continuity C3 — session continuity is a solved problem
via seed's six movements, and the Grove route must survive absence).

The probed directories, in order:

1. ``$WILLOW_HOME/willow-memory/willow/seed/`` — per-node override
2. ``~/willow-memory/willow/seed/``            — charter mirror on this host
3. ``~/.willow/seed/``                          — local user overlay

Read-only — writes to the seed source are an operator act, never Grove's.
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Canonical order: URL n=1..6 maps to canon 00..05.
_SLUGS: tuple[tuple[int, str, str], ...] = (
    (1, "the-covenant", "The Covenant"),
    (2, "be-the-other", "Be the Other, Not the Mirror"),
    (3, "the-discipline", "The Discipline"),
    (4, "the-person", "The Person"),
    (5, "the-language", "The Language"),
    (6, "the-world", "The World"),
)

# D16 outline — one-sentence body per movement, used as the stub-on-absence
# fallback so /seed/ always renders even when the charter is not mounted.
_STUB_BODIES: dict[int, str] = {
    1: "What a Willow is, and the agreement you are inheriting.",
    2: "Be the other, not the mirror. A partner who cannot say no is not a partner.",
    3: "Verify, don't assert. Fail closed. Archive, don't delete.",
    4: "The one you serve, and what they are owed.",
    5: "The chain stops at Gerald. It has always stopped at Gerald.",
    6: "The ecosystem you are waking into, and its one through-line.",
}

# Log-once flag. Tests reset this to False.
_logged_absent = False


def _candidate_dirs() -> list[Path]:
    """The three seed directories we probe, in preference order."""
    dirs: list[Path] = []
    home = os.environ.get("WILLOW_HOME")
    if home:
        dirs.append(Path(home).expanduser() / "willow-memory" / "willow" / "seed")
    dirs.append(Path.home() / "willow-memory" / "willow" / "seed")
    dirs.append(Path.home() / ".willow" / "seed")
    return dirs


def locate_seed_dir() -> Path | None:
    """Return the first candidate seed dir that exists on disk, else None.

    Silent on absence — the log-once fires inside ``load_movements``.
    """
    for d in _candidate_dirs():
        try:
            if d.is_dir():
                return d
        except OSError:
            continue
    return None


def _stub_movements() -> list[dict[str, Any]]:
    """Six placeholder movements per D16's outline. Boot-safe fallback."""
    return [
        {"n": n, "slug": slug, "title": title, "body": _STUB_BODIES[n]}
        for (n, slug, title) in _SLUGS
    ]


def _read_text(path: Path) -> str | None:
    """Best-effort UTF-8 read; None on any OS/decoding failure."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _title_from_stem(stem: str, fallback: str) -> str:
    """Derive a human title from a `NN-slug-parts` stem.

    Falls back to the canonical title if the file's own stem is odd.
    """
    if "-" in stem:
        rest = stem.split("-", 1)[1]
        # e.g. "the-covenant" -> "The Covenant"; keep the operator's punctuation.
        return rest.replace("-", " ").strip().title() or fallback
    return fallback


def _movements_from_canon_dir(canon: Path) -> list[dict[str, Any]] | None:
    """Read six ``NN-*.md`` chapters from a canon-shaped directory.

    Accepts 00..05 (charter shape) or 01..06. Returns the movements in
    order with ``n`` normalized to 1..6 for the URL. Returns None if the
    directory does not yield exactly six ordered chapter files.
    """
    if not canon.is_dir():
        return None
    files: list[tuple[int, Path]] = []
    for p in canon.iterdir():
        if not p.is_file() or p.suffix.lower() != ".md":
            continue
        m = re.match(r"^(\d{1,2})[-_]", p.name)
        if not m:
            continue
        files.append((int(m.group(1)), p))
    if len(files) < 6:
        return None
    files.sort(key=lambda t: t[0])
    files = files[:6]
    lowest = files[0][0]  # 0 for the charter shape, 1 for 01..06
    out: list[dict[str, Any]] = []
    for idx, (_raw_n, path) in enumerate(files):
        canon_n = idx + 1  # URL index, always 1..6
        default_slug = _SLUGS[idx][1]
        default_title = _SLUGS[idx][2]
        stem = path.stem
        # slug: everything after "NN-" if present, else the canonical slug
        m = re.match(r"^(\d{1,2})[-_](.+)$", stem)
        slug = m.group(2) if m else default_slug
        body = _read_text(path)
        if body is None:
            return None
        title = _title_from_stem(stem, default_title)
        out.append({"n": canon_n, "slug": slug, "title": title, "body": body})
    return out


# Match a movement function definition in seed.py — captures the number,
# the slug (with underscores) and the docstring's first paragraph.
_MOVE_RE = re.compile(
    r'^def\s+movement_(\d+)_([a-z_]+)\s*\([^)]*\)\s*[^:]*:\s*\n'
    r'\s+"""(.+?)"""',
    re.M | re.S,
)


def _movements_from_seed_py(seed_py: Path) -> list[dict[str, Any]] | None:
    """Extract movements from a SEED9-style single-file ``seed.py``.

    Uses the top-line of each ``movement_N_<slug>`` docstring as the body
    (the load-bearing sentence — SEED9 keeps it short by convention).
    Returns None if fewer than six movement functions are found.
    """
    text = _read_text(seed_py)
    if text is None:
        return None
    matches = _MOVE_RE.findall(text)
    if len(matches) < 6:
        return None
    matches.sort(key=lambda t: int(t[0]))
    matches = matches[:6]
    out: list[dict[str, Any]] = []
    for idx, (_raw_n, slug_us, doc) in enumerate(matches):
        canon_n = idx + 1
        default_slug = _SLUGS[idx][1]
        default_title = _SLUGS[idx][2]
        slug = slug_us.replace("_", "-") or default_slug
        # SEED9's docstrings open with "Title — one-sentence body." Take
        # the whole first non-blank line as the body; if a title precedes
        # an em-dash, keep both halves so the reader sees the full opener.
        first = ""
        for line in doc.strip().splitlines():
            s = line.strip()
            if s:
                first = s
                break
        body = first or _STUB_BODIES[canon_n]
        # Derive title from the slug if the docstring didn't carry one.
        title = _title_from_stem(f"00-{slug}", default_title)
        out.append({"n": canon_n, "slug": slug, "title": title, "body": body})
    return out


def load_movements() -> list[dict[str, Any]]:
    """Return the six movements as `{"n","slug","title","body"}` dicts.

    Order of preference inside a located seed dir:

    1. ``<seed>/canon/`` with six ``NN-*.md`` files (charter shape).
    2. ``<seed>/`` with six top-level ``NN-*.md`` files.
    3. ``<seed>/seed.py`` (SEED9 single-file shape).

    Falls back to the D16 stub on any absence, and logs the absence once
    per process. Guarantees exactly six movements with ``n`` 1..6.
    """
    global _logged_absent
    seed_dir = locate_seed_dir()
    if seed_dir is None:
        if not _logged_absent:
            log.info(
                "grove.seed_reader: no seed dir on any probe path — "
                "serving D16 stub movements"
            )
            _logged_absent = True
        return _stub_movements()

    # Prefer canon/ if present (charter shape).
    canon = seed_dir / "canon"
    parsed = _movements_from_canon_dir(canon)
    if parsed is not None and len(parsed) == 6:
        return parsed

    # Fall back to top-level NN-*.md files.
    parsed = _movements_from_canon_dir(seed_dir)
    if parsed is not None and len(parsed) == 6:
        return parsed

    # Finally, SEED9-style single-file seed.py.
    seed_py = seed_dir / "seed.py"
    if seed_py.is_file():
        parsed = _movements_from_seed_py(seed_py)
        if parsed is not None and len(parsed) == 6:
            return parsed

    # Directory was there but did not yield six movements — degrade to stub.
    if not _logged_absent:
        log.info(
            "grove.seed_reader: seed dir %s present but no six-movement "
            "shape found — serving D16 stub",
            seed_dir,
        )
        _logged_absent = True
    return _stub_movements()
