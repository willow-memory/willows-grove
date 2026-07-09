#!/usr/bin/env python3
"""grove_channel_audit.py — find and heal shadow channels.
b17: WGRV1  ΔΣ=42

A shadow channel is a row whose name normalizes to the same value as another
row's ('#fleet' vs 'fleet'). Writes addressed to the shadow spelling landed in
the shadow row and were invisible to every reader of the canonical name.

    python3 grove_channel_audit.py            # audit only, exit 1 if shadows exist
    python3 grove_channel_audit.py --merge    # move messages to canonical, drop shadows

Safe to run standing (cron / fleet_health): audit mode never writes.
"""
from __future__ import annotations

import argparse
import sys

import grove_db as db


def _canonical(rows: list[dict], norm: str) -> dict:
    """The row to keep: the exactly-named one, else the oldest by id."""
    exact = [r for r in rows if r["name"] == norm]
    return exact[0] if exact else min(rows, key=lambda r: r["id"])


def audit(conn) -> dict[str, list[dict]]:
    channels = db.list_channels(conn, include_archived=True)
    return db.duplicate_channel_groups(channels)


def merge(conn, groups: dict[str, list[dict]]) -> int:
    moved_total = 0
    cur = conn.cursor()
    for norm, rows in sorted(groups.items()):
        keep = _canonical(rows, norm)
        shadows = [r for r in rows if r["id"] != keep["id"]]
        for sh in shadows:
            cur.execute(
                "UPDATE messages SET channel_id = %s WHERE channel_id = %s",
                (keep["id"], sh["id"]),
            )
            moved = cur.rowcount
            cur.execute("DELETE FROM channels WHERE id = %s", (sh["id"],))
            moved_total += moved
            print(f"  merged {sh['name']!r} (id={sh['id']}) → {keep['name']!r} "
                  f"(id={keep['id']}): {moved} message(s) moved, shadow dropped")
        if keep["name"] != norm:
            cur.execute("UPDATE channels SET name = %s WHERE id = %s", (norm, keep["id"]))
            print(f"  renamed kept row id={keep['id']} {keep['name']!r} → {norm!r}")
    conn.commit()
    return moved_total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merge", action="store_true",
                    help="apply the merge (default: audit only, no writes)")
    args = ap.parse_args()

    conn = db.get_connection()
    try:
        groups = audit(conn)
        if not groups:
            print("grove channels: no shadows — every name is canonical")
            return 0

        print(f"grove channels: {len(groups)} shadowed name(s)")
        for norm, rows in sorted(groups.items()):
            listing = ", ".join(f"{r['name']!r}(id={r['id']})" for r in sorted(rows, key=lambda r: r["id"]))
            print(f"  {norm!r}: {listing}")

        if not args.merge:
            print("\nre-run with --merge to heal (messages move to the canonical row)")
            return 1

        moved = merge(conn, groups)
        print(f"\nmerged: {moved} message(s) relocated")
        remaining = audit(conn)
        if remaining:
            print(f"STILL SHADOWED: {sorted(remaining)}", file=sys.stderr)
            return 1
        print("verified: no shadows remain")
        return 0
    finally:
        db.release_connection(conn)


if __name__ == "__main__":
    raise SystemExit(main())
