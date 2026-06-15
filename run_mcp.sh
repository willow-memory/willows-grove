#!/usr/bin/env bash
# run_mcp.sh — Grove MCP server (stdio or serve)
# b17: GRMLC · ΔΣ=42
#
# Usage:
#   ./run_mcp.sh              # stdio (Claude/Cursor spawns this)
#   ./run_mcp.sh --serve      # HTTP on :8765 for remote clients
#   ./run_mcp.sh --serve --watch

set -euo pipefail
cd "$(dirname "$0")"

PY="${GROVE_VENV:-/home/sean-campbell/github/willow-2.0/.venv-dev}/bin/python3"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

export PYTHONPATH="$(pwd)${PYTHONPATH:+:$PYTHONPATH}"
export WILLOW_PG_DB="${WILLOW_PG_DB:-willow_20}"
export WILLOW_PG_USER="${WILLOW_PG_USER:-${USER:-}}"
export GROVE_MCP_PORT="${GROVE_MCP_PORT:-8765}"

echo "Grove MCP: $PY -m grove.mcp_local $*" >&2
exec "$PY" -m grove.mcp_local "$@"
