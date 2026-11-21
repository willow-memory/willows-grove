#!/usr/bin/env bash
# box-desk.sh — the desk from Willow boxes, with no MCP and no database.
#
# Home: willows-grove/seat/willow (Willow desk). Needs a Willow checkout and
# Python's standard library, nothing else. Runs are kept under
# $WILLOW_HOME/desk, never in this tree, so a box over the piles never reads
# its own write-ups.
#
#   bash seat/willow/scripts/box-desk.sh piles             # a fresh box over the piles, the desk's stack over it
#   bash seat/willow/scripts/box-desk.sh headlines         # each step's first line, from the last piles run
#   bash seat/willow/scripts/box-desk.sh github DIR        # GitHub's answers saved as JSON in DIR, as a box
#   bash seat/willow/scripts/box-desk.sh ask piles|github "QUESTION"
#
# DIR holds what `gh ... --json` printed, or what GitHub's API (or an MCP
# server over it) answered, one file a list: issues, pull requests, runs.
# Willow's gh-json reads either shape.
#
# DESK_PILES  the folder that holds the piles (default: the folder above willow-memory)
# WILLOW      a Willow checkout (default: $DESK_PILES/Willow)
# WILLOW_HOME where runs are kept (default: willow-memory/.willow)
#
# The key each run makes is a scratch key for that box alone, never the
# person's. Nothing here seals, and nothing reads the person's key.
set -euo pipefail

SEAT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROVE_REPO="$(cd "$SEAT_DIR/../.." && pwd)"
WM_ROOT="$(cd "$GROVE_REPO/.." && pwd)"
DESK_PILES="${DESK_PILES:-$(cd "$WM_ROOT/.." && pwd)}"
WILLOW="${WILLOW:-$DESK_PILES/Willow}"
WILLOW_HOME="${WILLOW_HOME:-$WM_ROOT/.willow}"
OUT="$WILLOW_HOME/desk"
PY="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1  # running add-ons from inside a pile must not write into it

if [[ ! -f "$WILLOW/kernel.py" ]]; then
  echo "refused: no Willow checkout at $WILLOW; set WILLOW" >&2
  exit 2
fi

fresh_box() {  # fresh_box NAME PILE: a box of its own, a scratch key, the desk's words
  local at="$OUT/$1"
  rm -rf "$at/box" "$at/scratch.key"
  mkdir -p "$at"
  install -m 600 "$SEAT_DIR/desk/words.txt" "$at/words.txt"
  "$PY" "$WILLOW/kernel.py" init --box "$at/box" --pile "$2" \
    --key "$at/scratch.key" --words "$at/words.txt" >/dev/null
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  help|-h|--help)
    sed -n '2,23p' "$0" | sed 's/^# \{0,1\}//'
    ;;

  piles)
    fresh_box piles "$DESK_PILES"
    sed "s|@PILES@|$DESK_PILES|g" "$SEAT_DIR/desk/stack.md" > "$OUT/piles/stack.md"
    code=0
    (cd "$WILLOW" && "$PY" adapters/stdlib/stack/stack.py --box "$OUT/piles/box" \
      --stack "$OUT/piles/stack.md" > "$OUT/piles/out.md" 2> "$OUT/piles/err.txt") || code=$?
    "$PY" "$WILLOW/kernel.py" verify --box "$OUT/piles/box"
    echo "the desk's stack: exit $code, $(wc -l < "$OUT/piles/out.md") lines in $OUT/piles/out.md"
    "$0" headlines
    ;;

  headlines)
    [[ -f "$OUT/piles/out.md" ]] || { echo "nothing run yet: box-desk.sh piles" >&2; exit 42; }
    awk '/^## /{print; next} /^- `/{step=$0; getline; getline; sub(/^ +/, "", $0); print "- " substr(step, 4, 70) "\n    " substr($0, 1, 160)}' "$OUT/piles/out.md"
    tail -1 "$OUT/piles/out.md"
    ;;

  github)
    dir="${1:?usage: box-desk.sh github DIR}"
    [[ -d "$dir" ]] || { echo "refused: $dir isn't a folder" >&2; exit 2; }
    rm -rf "$OUT/github/mirror"
    "$PY" "$WILLOW/adapters/stdlib/gh-json/gh_json.py" mirror --from "$dir" --to "$OUT/github/mirror"
    fresh_box github "$OUT/github/mirror"
    echo "ask it: box-desk.sh ask github \"what is in the merge queue\""
    ;;

  ask)
    which="${1:?usage: box-desk.sh ask piles|github QUESTION}"
    question="${2:?usage: box-desk.sh ask piles|github QUESTION}"
    [[ -d "$OUT/$which/box" ]] || { echo "no $which box yet: box-desk.sh $which" >&2; exit 42; }
    "$PY" "$WILLOW/kernel.py" bite --box "$OUT/$which/box" "$question" | "$PY" -c '
import json, sys
d = json.load(sys.stdin)
print(d["state"])
for s in d.get("served", []):
    print(" ", s["where"], " ".join(s["text"].split())[:150])
'
    ;;

  *)
    echo "unknown command: $cmd (try: piles headlines github ask)" >&2
    exit 2
    ;;
esac
