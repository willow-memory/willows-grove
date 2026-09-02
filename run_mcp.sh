#!/usr/bin/env bash
# run_mcp.sh — Grove MCP server (stdio or serve)
# b17: GRMLC · ΔΣ=42
#
# Usage:
#   ./run_mcp.sh              # stdio (Claude/Cursor spawns this)
#   ./run_mcp.sh --serve      # HTTP on :8767 for remote clients
#   ./run_mcp.sh --serve --watch

set -euo pipefail
cd "$(dirname "$0")"

# Resolve a Python interpreter, in order of preference:
#   1. $GROVE_VENV/bin/python3   — explicit override (set by systemd/grove-serve)
#   2. ./.venv/bin/python3       — a repo-local venv, the conventional home
#   3. python3 on PATH           — last resort; may lack the pinned deps
PY=""
if [[ -n "${GROVE_VENV:-}" && -x "${GROVE_VENV}/bin/python3" ]]; then
  PY="${GROVE_VENV}/bin/python3"
elif [[ -x "$(pwd)/.venv/bin/python3" ]]; then
  PY="$(pwd)/.venv/bin/python3"
else
  PY="$(command -v python3)"
fi

# The MCP SDK (>=2.0) is required in serve mode and for stdio push. Warn loudly
# rather than crash cryptically when the resolved interpreter lacks it.
if ! "$PY" -c "import mcp.server.mcpserver" >/dev/null 2>&1; then
  echo "warning: $PY cannot import mcp.server.mcpserver — the MCP SDK (>=2.0) is missing." >&2
  echo "         create a venv and install deps, then set GROVE_VENV or use ./.venv:" >&2
  echo "           python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt" >&2
fi

export PYTHONPATH="$(pwd)${PYTHONPATH:+:$PYTHONPATH}"
export WILLOW_PG_DB="${WILLOW_PG_DB:-willow_20}"
export WILLOW_PG_USER="${WILLOW_PG_USER:-${USER:-}}"
# 8767: willow-mcp --serve owns 8765, 8766 is the loopback-only desk page.
export GROVE_MCP_PORT="${GROVE_MCP_PORT:-8767}"

echo "Grove MCP: $PY -m grove.mcp_local $*" >&2
exec "$PY" -m grove.mcp_local "$@"
