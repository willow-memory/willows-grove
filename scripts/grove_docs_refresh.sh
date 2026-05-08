#!/usr/bin/env bash
# Regenerate Grove-derived docs under docs/generated/.
# b17: GREFR  ΔΣ=42
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-}:$ROOT"
exec python3 scripts/grove_docs_extract.py \
  --limit "${GROVE_DOCS_LIMIT:-10000}" \
  --out docs/generated \
  all "$@"
