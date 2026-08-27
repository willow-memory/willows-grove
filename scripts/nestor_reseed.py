#!/usr/bin/env python3
"""scripts/nestor_reseed.py — re-emit the design's sealed pairs into a
persistent Grove-owned Nestor store.
b17: WGRV1  ΔΣ=42

Point memory infra inward, per the Discipline section of
``docs/design/willow-grove-premise.md``:

    "Grove's design decisions live in a Nestor store. During this session,
     decisions were seeded into a scratch store … For the persistent build,
     a Grove-owned Nestor store on $WILLOW_HOME/nestor/willows-grove.db
     holds every design decision as an evidence-backed sealed pair."

This script does exactly that. It reads every pair (plus its evidence and
warrant rows) from the session's scratch store and re-emits them into the
persistent store, preserving every field: source_text, source_norm,
source_lang, target_text, target_lang, status, verifier, weight, origin,
created_at, seal_sig, reason, superseded_by — and every evidence + warrant
row per pair.

Idempotent: pairs whose ``source_norm`` already exists in the destination
(under the same source_lang/target_lang) are skipped whole — no re-insert,
no re-seal, no duplicated evidence/warrants. Re-runs after a partial pass
converge without operator intervention.

Not invoked automatically. Runs when a human runs it — the pattern-in-
waiting for future Grove sessions once ``$WILLOW_HOME`` is provisioned.

Usage
-----
Defaults read from the current scratch store and write to
``~/.willow/nestor/willows-grove.db``::

    python3 scripts/nestor_reseed.py

Both endpoints are overridable::

    python3 scripts/nestor_reseed.py \\
        --src /tmp/…/scratchpad/nestor/keep/willows-grove.db \\
        --dst /some/other/place/willows-grove.db

``$WILLOW_HOME`` overrides the destination root if set::

    WILLOW_HOME=/opt/willow python3 scripts/nestor_reseed.py
    # writes to /opt/willow/nestor/willows-grove.db
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


DEFAULT_SRC = Path(
    "/tmp/claude-0/-home-user/074fda02-b18b-5e38-929a-080e00431ad6"
    "/scratchpad/nestor/keep/willows-grove.db"
)


def _default_dst() -> Path:
    """``$WILLOW_HOME/nestor/willows-grove.db`` if set, else
    ``~/.willow/nestor/willows-grove.db``."""
    home = os.environ.get("WILLOW_HOME")
    root = Path(home) if home else Path.home() / ".willow"
    return root / "nestor" / "willows-grove.db"


# Fields memory_insert accepts. Kept explicit so a nestor-meaning bump that
# adds a column does not silently drop it — the row assembled here is precisely
# what lands in the destination.
_PAIR_INSERT_FIELDS = (
    "id",
    "source_text",
    "source_norm",
    "source_lang",
    "target_text",
    "target_lang",
    "status",
    "verifier",
    "weight",
    "origin",
    "created_at",
    "seal_sig",
    "reason",
    "superseded_by",
)


def _pair_insert_payload(row: dict) -> dict:
    """Copy of ``row`` restricted to insert-legal fields.

    Coerces ``weight`` to float since ``memory_list`` returns it as a string in
    at least one nestor-meaning release; the insert schema expects a number.
    """
    payload: dict = {}
    for field in _PAIR_INSERT_FIELDS:
        value = row.get(field, "")
        payload[field] = value if value is not None else ""
    try:
        payload["weight"] = float(payload["weight"] or 0.0)
    except (TypeError, ValueError):
        payload["weight"] = 0.0
    return payload


def _reseed(src_path: Path, dst_path: Path) -> dict:
    """Do the copy. Returns a small counters dict for the CLI to print."""
    try:
        from nestor.sqlite_store import SqliteStore
    except ImportError as exc:
        raise SystemExit(
            "nestor-meaning is not installed in this environment. "
            "Install it (`pip install nestor-meaning`) and re-run. "
            f"({exc})"
        )

    if not src_path.exists():
        raise SystemExit(f"source Nestor store not found: {src_path}")

    dst_path.parent.mkdir(parents=True, exist_ok=True)

    src = SqliteStore(str(src_path))
    dst = SqliteStore(str(dst_path))
    src.memory_init()
    dst.memory_init()

    counters = {"pairs_seen": 0, "pairs_inserted": 0, "pairs_skipped": 0,
                "evidence_added": 0, "warrants_added": 0}

    # Fetch everything from the source. memory_list caps at limit=50 by default,
    # so we page through in chunks of 200 until we get less than we asked for.
    all_rows: list[dict] = []
    offset = 0
    page = 200
    while True:
        chunk = src.memory_list(limit=page, offset=offset)
        if not chunk:
            break
        all_rows.extend(chunk)
        if len(chunk) < page:
            break
        offset += page

    for row in all_rows:
        counters["pairs_seen"] += 1
        source_norm = row.get("source_norm", "") or ""
        source_lang = row.get("source_lang", "") or ""
        target_lang = row.get("target_lang", "") or ""

        # Idempotency: a matching source_norm in the same lang pair is treated
        # as already-seeded; skip pair + its evidence + its warrants together
        # so a re-run does not duplicate evidence rows.
        existing = dst.memory_find(source_norm, source_lang, target_lang)
        if existing is not None:
            counters["pairs_skipped"] += 1
            continue

        # Insert the pair verbatim. memory_insert accepts status='sealed' and
        # a non-empty seal_sig; preserving both is how "seal_sig preserved" is
        # honored end-to-end. memory_seal is available for the case where the
        # source stored a draft that a later pass sealed under a new verifier,
        # but here the seal_sig on the pair is already the record we want.
        dst.memory_insert(_pair_insert_payload(row))
        counters["pairs_inserted"] += 1

        # Evidence: copy every attached row. memory_add_evidence is append-only
        # so preserving the src id lets a reviewer cross-check both stores by
        # id if they ever diverge.
        for ev in src.memory_evidence_for(row["id"]):
            dst.memory_add_evidence({
                "id": ev.get("id", ""),
                "pair_id": row["id"],
                "kind": ev.get("kind", "") or "",
                "locator": ev.get("locator", "") or "",
                "attaches_to": ev.get("attaches_to", "") or "",
                "reason": ev.get("reason", "") or "",
                "attached_by": ev.get("attached_by", "") or "",
                "created_at": ev.get("created_at", "") or "",
            })
            counters["evidence_added"] += 1

        # Warrants: same treatment. `check` (the check procedure) is preserved
        # verbatim — Nestor stores it as check_procedure internally; the dict
        # key here mirrors what memory_warrants_for hands back.
        for warr in src.memory_warrants_for(row["id"]):
            dst.memory_add_warrant({
                "id": warr.get("id", ""),
                "pair_id": row["id"],
                "kind": warr.get("kind", "") or "",
                "authority": warr.get("authority", "") or "",
                "locator": warr.get("locator", "") or "",
                "expected_digest": warr.get("expected_digest", "") or "",
                "attached_by": warr.get("attached_by", "") or "",
                "created_at": warr.get("created_at", "") or "",
                "check": warr.get("check", "") or "",
            })
            counters["warrants_added"] += 1

    return counters


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC,
                        help=f"source Nestor store (default: {DEFAULT_SRC})")
    parser.add_argument("--dst", type=Path, default=None,
                        help="destination Nestor store (default: "
                             "$WILLOW_HOME/nestor/willows-grove.db or "
                             "~/.willow/nestor/willows-grove.db)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would be copied without writing")
    args = parser.parse_args(argv)

    dst = args.dst or _default_dst()

    print(f"nestor reseed:")
    print(f"  src → {args.src}")
    print(f"  dst → {dst}")
    if args.dry_run:
        print("  (dry-run — no writes)")
        # Dry-run: only count what the source has. Still requires the module.
        try:
            from nestor.sqlite_store import SqliteStore
        except ImportError as exc:
            print(f"  nestor-meaning not installed: {exc}", file=sys.stderr)
            return 2
        src = SqliteStore(str(args.src))
        src.memory_init()
        rows = src.memory_list(limit=10_000)
        print(f"  would consider {len(rows)} pair(s).")
        return 0

    counters = _reseed(args.src, dst)
    print(
        "  done. "
        f"seen={counters['pairs_seen']} "
        f"inserted={counters['pairs_inserted']} "
        f"skipped={counters['pairs_skipped']} "
        f"evidence={counters['evidence_added']} "
        f"warrants={counters['warrants_added']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
