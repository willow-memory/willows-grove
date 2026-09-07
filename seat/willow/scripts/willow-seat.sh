#!/usr/bin/env bash
# willow-seat.sh — orchestrator shell front-end (script-first, MCP via wtool).
#
# Home: willows-grove/seat/willow (Willow desk). Heimdallr does not maintain this.
#
#   bash seat/willow/scripts/willow-seat.sh probe
#   bash seat/willow/scripts/willow-seat.sh desk
#   bash seat/willow/scripts/willow-seat.sh wtool diagnostic_summary '{"app_id":"willow"}'
#   bash seat/willow/scripts/willow-seat.sh jeles corpus_sources
#   bash seat/willow/scripts/willow-seat.sh seams
#   bash seat/willow/scripts/willow-seat.sh ollama
#
set -euo pipefail

SEAT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROVE_REPO="$(cd "$SEAT_DIR/../.." && pwd)"
WM_ROOT="$(cd "$GROVE_REPO/.." && pwd)"
WMCP_REPO="${WMCP_REPO:-$WM_ROOT/willow-mcp}"
RATATOSK_REPO="${RATATOSK_REPO:-$WM_ROOT/ratatosk}"
WILLOW_HOME="${WILLOW_HOME:-$WM_ROOT/.willow}"

load_operator_env() {
  # Prefer fleet join (sources WILLOW_VAULT_BOX + charter paths). Fall back to
  # vault env, then legacy $WILLOW_HOME/env.
  if [[ -f "$WILLOW_HOME/fleet.env" ]]; then
    # shellcheck disable=SC1090
    source "$WILLOW_HOME/fleet.env"
    return 0
  fi
  local vault="${WILLOW_VAULT_BOX:-$HOME/sean-data-vault/willow-operator-box}"
  if [[ -f "$vault/env" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$vault/env"
    set +a
  elif [[ -f "$WILLOW_HOME/env" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$WILLOW_HOME/env"
    set +a
  fi
}

load_operator_env
export WILLOW_HOME WILLOW_STORE_ROOT="${WILLOW_STORE_ROOT:-$WILLOW_HOME/store}"
export WILLOW_APP_ID=willow
export WILLOW_SEAT_DIR="$SEAT_DIR"
export RATATOSK_REPO

PY="${WMCP_REPO}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="${WILLOW_HOME}/venvs/willow-mcp/bin/python"
fi
if [[ ! -x "$PY" ]]; then
  echo "error: willow-mcp venv python not found" >&2
  exit 1
fi

WTOOL="$WMCP_REPO/tools/wtool.py"
JELES_SERVER_ID="8cae3d1dcdf4"

wtool() {
  "$PY" "$WTOOL" "$@"
}

cmd="${1:-probe}"
shift || true

case "$cmd" in
  help|-h|--help)
    sed -n '2,12p' "$0" | tr -d '#'
    echo "Commands: probe desk wtool jeles seams ollama lint-mai"
    ;;

  probe)
    echo "== env"
    echo "WILLOW_HOME=$WILLOW_HOME"
    echo "WILLOW_VAULT_BOX=${WILLOW_VAULT_BOX:-"(unset)"}"
    echo "WILLOW_CHARTER_REPO=${WILLOW_CHARTER_REPO:-"(unset)"}"
    echo
    echo "== diagnostic_summary"
    wtool diagnostic_summary '{"app_id":"willow"}' | "$PY" -m json.tool 2>/dev/null | head -40 || wtool diagnostic_summary '{"app_id":"willow"}'
    echo
    echo "== ratatosk (session runtime)"
    "$PY" - "$RATATOSK_REPO" <<'PYPROBE'
import os
import sys
from pathlib import Path

repo = Path(sys.argv[1])
channel = os.environ.get("RATATOSK_GROVE_CHANNEL", "")
print(f"RATATOSK_GROVE_CHANNEL={channel or '(unset)'}")
print(f"RATATOSK_REPO={repo}")

if repo.is_dir():
    sys.path.insert(0, str(repo))

try:
    import ratatosk.grove as grove
except ImportError:
    print("package: not importable (pip install willow-ratatosk or set RATATOSK_REPO)")
    sys.exit(0)

try:
    from importlib.metadata import version as pkg_version
    print(f"package: willow-ratatosk {pkg_version('willow-ratatosk')}")
except Exception:
    print("package: import ok (version unknown)")

receipt = grove.send("willow-seat probe")
print(f"grove.send: ok={receipt.ok} skipped={receipt.skipped} detail={receipt.detail}")
PYPROBE
    echo
    echo "== mcp serve ports (phone sign-in is NOT :8766 desk)"
    for port in 8765 8767 8768; do
      if curl -sf --max-time 1 "http://127.0.0.1:${port}/" >/dev/null 2>&1 \
        || curl -sf --max-time 1 "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
        echo "  :${port} reachable"
      else
        echo "  :${port} (no http listener)"
      fi
    done
    echo
    echo "== net-status"
    willow-mcp net-status 2>/dev/null || true
    echo
    echo "== gates (federation)"
    willow-mcp gates willow --json 2>/dev/null | "$PY" -c "
import json,sys
for g in json.load(sys.stdin):
    if 'federat' in g.get('id','') or g.get('id','').endswith('mcp_federation'):
        print(g['id'], g.get('state_label', g.get('state')))
" 2>/dev/null || true
    echo
    echo "== ollama"
    curl -sf "${OLLAMA_HOST:-http://127.0.0.1:11434}/api/tags" \
      | "$PY" -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('models',[])), 'models'); [print(' -',m['name']) for m in d.get('models',[])]" \
      2>/dev/null || echo "not reachable at ${OLLAMA_HOST:-http://127.0.0.1:11434}"
    ;;

  desk)
    wtool dispatch_list '{"app_id":"willow","limit":20,"status":""}' \
      | "$PY" -m json.tool 2>/dev/null || wtool dispatch_list '{"app_id":"willow","limit":20,"status":""}'
    ;;

  wtool)
    wtool "$@"
    ;;

  jeles)
    tool="${1:?jeles tool name required}"
    shift || true
    args="${1:-{\"app_id\":\"willow\"}}"
    wtool federation_call "{\"app_id\":\"willow\",\"server_id\":\"$JELES_SERVER_ID\",\"tool\":\"$tool\",\"arguments\":$args}"
    ;;

  seams)
    "$PY" "$WMCP_REPO/scripts/fleet_seams.py" "$@"
    ;;

  ollama)
    curl -sf "${OLLAMA_HOST:-http://127.0.0.1:11434}/api/tags" \
      | "$PY" -m json.tool
    ;;

  lint-mai)
    "$PY" "$WMCP_REPO/tools/mai_lint.py" "$@"
    ;;

  *)
    echo "unknown command: $cmd (try: probe desk wtool jeles seams ollama lint-mai)" >&2
    exit 2
    ;;
esac
