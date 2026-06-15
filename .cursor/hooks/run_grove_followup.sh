#!/usr/bin/env bash
# Wrapper: Cursor hooks run from project root — keep PYTHONPATH stable.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
export WILLOW_PG_DB="${WILLOW_PG_DB:-willow_20}"
export WILLOW_PG_USER="${WILLOW_PG_USER:-sean-campbell}"
exec python3 "$HERE/grove_followup.py"
