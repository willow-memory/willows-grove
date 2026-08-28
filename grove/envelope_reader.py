# b17: WGRV1 ΔΣ=42
"""Reader for the fleet envelope registry (P1 live source).

Envelopes are the mechanism from the Willow Grove premise (P1 —
*orchestrator write attestation*): a capability once opened by the
Operator Key, cited on every use, and rendered by Grove with its
attestation state so the operator can see which grants are live,
which are unattested, and which have gone invalid.

This reader is Grove's live source for `<grove-envelope-panel>`. It
mirrors ``grove/persona_roster.py`` shape:

* one small synchronous module, no threading or async
* read-only — envelope creation is an Operator Key act (CONST-0-3)
  and belongs to the charter, never to Grove
* D7 discipline — *absence is a state, not a failure*: when no
  envelope directory exists or none of the ones that do carry any
  files, ``read_all()`` returns an empty envelope list and logs
  the fact exactly once. Grove boots either way.

The probed directories, in order:

1. ``$WILLOW_HOME/constitutional/`` — where willow-mcp keeps and
   authenticates the Article III.2 registry.
2. ``~/.willow/constitutional/`` — the same place when ``WILLOW_HOME``
   is unset.
5. ``~/.willow/envelopes/`` — local user overlay (lowest priority).

Later directories in that list override earlier ones on an ``id``
collision (last-writer-wins). Any file that fails to parse is
skipped with a single log line naming the path and the reason —
one malformed file must not deny the operator sight of the rest.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from grove.errors import Unreachable

log = logging.getLogger(__name__)

SCHEMA_ID = "envelope-registry/v1.1"

# Keys under which an envelope file may carry its list of entries.
# The canonical charter file (``pre-approved.json``) uses ``pre_approved``;
# the P1 active-envelope registry uses ``envelopes`` / ``active``; the
# proposals lane uses ``proposals``. All are merged into one flat list.
_LIST_KEYS = ("envelopes", "pre_approved", "active", "proposals")

# Log-once flags. Tests reset these to False.
_logged_missing_dirs = False
_logged_missing_files = False
_logged_malformed: set[str] = set()


def _candidate_dirs() -> list[Path]:
    """The directories we probe, in preference order.

    ``$WILLOW_HOME/constitutional/`` is where the registry lives. willow-mcp's
    ``paths.envelope_registry_path()`` resolves there and its
    ``trusted_read()`` authenticates it there, so this reader and the engine
    that enforces the law now name the same file.

    Every earlier candidate was a pre-migration path — ``envelopes/`` in the
    sibling ``willow`` charter repo, and hops through ``willow-memory/willow/``
    that never existed after the 2026-08-10 org-folder move. willow-mcp had
    already migrated (its syscall table's ``registry`` field was repointed at
    the same time, and THE PLANTING carried over with its ``registry_path``
    rewritten); this reader had not, so Grove displayed a registry the engine
    did not enforce — 15 active envelopes bound to ``willow-2.0`` paths that
    were deleted at greenfield.

    Later entries override earlier ones on ``id`` collision (see ``read_all``).
    """
    dirs: list[Path] = []
    home = os.environ.get("WILLOW_HOME")
    if home:
        dirs.append(Path(home).expanduser() / "constitutional")
    dirs.append(Path.home() / ".willow" / "constitutional")
    return dirs


def locate_envelope_dirs() -> list[Path]:
    """Return the subset of candidate directories that exist on disk.

    Silent on absence — the log-once for "no directories found at all"
    fires inside ``read_all``, where the caller can distinguish empty
    from missing.
    """
    found: list[Path] = []
    for d in _candidate_dirs():
        try:
            if d.is_dir():
                found.append(d)
        except OSError:  # unreadable candidate — treat as absent
            continue
    return found


def _entries_from_payload(data: Any, path: Path) -> list[dict]:
    """Extract the list of envelope dicts from one parsed file payload.

    Tolerates the shapes we see in the wild:

    * top level is a dict with a list under one of ``_LIST_KEYS``
    * top level is a dict with an ``id`` field (single-envelope file)
    * top level is a list of envelope dicts

    Anything else is a malformed file — caller handles the log-once.
    """
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    if isinstance(data, dict):
        for key in _LIST_KEYS:
            value = data.get(key)
            # An EMPTY list is not an answer. The registry carries all of
            # pre_approved/active/proposals as sibling keys, so matching on
            # "is a list" made an empty earlier key shadow a populated later
            # one. Measured against the migrated registry: pre_approved is []
            # and active holds THE PLANTING, and this returned nothing while
            # the file plainly had an envelope in force.
            if isinstance(value, list) and value:
                return [e for e in value if isinstance(e, dict)]
        # Every known key present but all empty is a real, readable "none in
        # force" — distinct from the unknown-shape error below, which the
        # caller logs as unreadable.
        if any(isinstance(data.get(k), list) for k in _LIST_KEYS):
            return []
        if "id" in data:
            return [data]
    raise ValueError(f"no envelope entries found (unknown top-level shape)")


def _load_dir(directory: Path) -> list[dict]:
    """Parse every ``*.json`` file in ``directory``. Malformed files skipped.

    Emits one log line per unique malformed path. Files whose top-level
    shape is not recognized are treated as malformed for logging.
    """
    out: list[dict] = []
    try:
        candidates = sorted(directory.glob("*.json"))
    except OSError as err:
        key = str(directory)
        if key not in _logged_malformed:
            log.info("[grove.envelope_reader] skipping unreadable %s: %s", directory, err)
            _logged_malformed.add(key)
        return out

    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as err:
            key = str(path)
            if key not in _logged_malformed:
                log.info("[grove.envelope_reader] skipping malformed %s: %s", path, err)
                _logged_malformed.add(key)
            continue
        try:
            entries = _entries_from_payload(data, path)
        except ValueError as err:
            key = str(path)
            if key not in _logged_malformed:
                log.info("[grove.envelope_reader] skipping malformed %s: %s", path, err)
                _logged_malformed.add(key)
            continue
        out.extend(entries)
    return out


def read_all() -> dict:
    """Return the merged envelope registry.

    Shape::

        {"schema": "envelope-registry/v1.1", "envelopes": [ ... ]}

    Precedence: ``_candidate_dirs()`` order. Later directories override
    earlier ones on ``id`` collision — a per-node override in
    ``$WILLOW_HOME/envelopes/`` wins over the fleet charter mirror at
    ``~/willow-memory/Willow/envelopes/``. Files without an ``id`` are
    still returned but participate in no collision — their order is
    the order they were read.

    Three-state contract (INVARIANTS.md §1):

    * populated / empty → returns the envelope-registry payload (the
      ``envelopes`` list may be empty when directories exist but hold no
      usable files — that's the reader reaching its source and finding
      nothing).
    * unreachable       → raises ``Unreachable`` when NO envelope
      directory exists in the probe path at all.
    """
    global _logged_missing_dirs, _logged_missing_files

    dirs = locate_envelope_dirs()
    if not dirs:
        if not _logged_missing_dirs:
            log.info(
                "[grove.envelope_reader] no envelope directory found in known "
                "locations ($WILLOW_HOME/willow-memory/willow/envelopes, "
                "$WILLOW_HOME/envelopes, ~/willow-memory/willow/envelopes, "
                "~/willow-memory/Willow/envelopes, ~/.willow/envelopes) — "
                "raising Unreachable (INVARIANTS.md §1)."
            )
            _logged_missing_dirs = True
        raise Unreachable(
            "no envelope directory found in probe path "
            "($WILLOW_HOME/willow-memory/willow/envelopes, "
            "$WILLOW_HOME/envelopes, ~/willow-memory/willow/envelopes, "
            "~/willow-memory/Willow/envelopes, ~/.willow/envelopes)"
        )

    # Precedence: later dirs win. Walk in probe order, keying by id.
    keyed: dict[str, dict] = {}
    unkeyed: list[dict] = []
    total_files_read = 0
    for directory in dirs:
        entries = _load_dir(directory)
        total_files_read += 1 if entries else 0
        for entry in entries:
            env_id = entry.get("id")
            if isinstance(env_id, str) and env_id:
                keyed[env_id] = entry
            else:
                unkeyed.append(entry)

    envelopes = list(keyed.values()) + unkeyed

    if not envelopes and not _logged_missing_files:
        log.info(
            "[grove.envelope_reader] envelope directories exist but hold no "
            "usable *.json files — rendering empty registry (D7)."
        )
        _logged_missing_files = True

    return {"schema": SCHEMA_ID, "envelopes": envelopes}


__all__ = [
    "SCHEMA_ID",
    "locate_envelope_dirs",
    "read_all",
]
