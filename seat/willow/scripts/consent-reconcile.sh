#!/usr/bin/env bash
# Sync consent.json mirror from canonical settings.global.json.
#
# Home: willows-grove/seat/willow (Willow desk).
# Trust-root files are owned by willow-operator; this script temporarily
# chowns them to you, runs reconcile (requires your terminal), then restores.
#
#   bash seat/willow/scripts/consent-reconcile.sh
#
set -euo pipefail

SEAT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROVE_REPO="$(cd "$SEAT_DIR/../.." && pwd)"
WM_ROOT="$(cd "$GROVE_REPO/.." && pwd)"
WILLOW_HOME="${WILLOW_HOME:-$WM_ROOT/.willow}"
CONFIG="$WILLOW_HOME/config"
LEGACY="$WILLOW_HOME/consent.json"
OPERATOR="willow-operator:willow-operator"

WILLOW_MCP="${WILLOW_MCP:-$WM_ROOT/willow-mcp/.venv/bin/willow-mcp}"
if [[ ! -x "$WILLOW_MCP" ]]; then
  WILLOW_MCP="${WILLOW_HOME}/venvs/willow-mcp/bin/willow-mcp"
fi
if [[ ! -x "$WILLOW_MCP" ]]; then
  WILLOW_MCP="$(command -v willow-mcp || true)"
fi
if [[ -z "$WILLOW_MCP" || ! -x "$WILLOW_MCP" ]]; then
  echo "error: willow-mcp binary not found" >&2
  exit 1
fi

if [[ -f "$WILLOW_HOME/env" ]]; then
  # shellcheck disable=SC1090
  source "$WILLOW_HOME/env"
fi
export WILLOW_HOME

if ! [[ -t 0 ]]; then
  echo "error: run from an interactive terminal (consent reconcile requires a TTY)" >&2
  exit 1
fi

echo "==> Temporarily chown consent paths to $USER"
sudo chown -R "$USER:$USER" "$CONFIG" "$LEGACY"

restore() {
  echo "==> Restore willow-operator ownership"
  sudo chown -R "$OPERATOR" "$CONFIG" "$LEGACY"
  # reconcile writes mode 600; MCP runs as the operator user in the
  # willow-operator group — group-read keeps trust-root ownership intact.
  sudo chmod 640 "$CONFIG/settings.global.json" "$LEGACY" "$CONFIG/.consent.lock" 2>/dev/null || true
}
trap restore EXIT

echo "==> Reconcile canonical consent → legacy mirror"
"$WILLOW_MCP" consent reconcile

echo "==> Verify"
"$WILLOW_MCP" consent status
