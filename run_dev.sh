#!/usr/bin/env bash
# run_dev.sh — launch Grove dashboard (fresh-start worktree)
# b17: WGRV1 · ΔΣ=42
#
# Usage: ./run_dev.sh
#        ./dev.sh          (wrapper)
#
# Override venv:  GROVE_VENV=/path/to/venv ./run_dev.sh

set -euo pipefail
cd "$(dirname "$0")"

find_python() {
  if [[ -n "${GROVE_VENV:-}" ]]; then
    echo "${GROVE_VENV}/bin/python3"
    return
  fi
  local candidates=(
    "$HOME/willow-2.0/.venv-dev/bin/python3"
    "$HOME/github/willow-2.0/.venv-dev/bin/python3"
    "$HOME/.willow/venv/bin/python3"
    "$HOME/.willow-venv/bin/python3"
    "$(dirname "$0")/.venv/bin/python3"
  )
  local c
  for c in "${candidates[@]}"; do
    if [[ -x "$c" ]] && "$c" -c "import textual, psycopg2" 2>/dev/null; then
      echo "$c"
      return
    fi
  done
  return 1
}

PY="$(find_python)" || {
  echo "No Python with textual + psycopg2 found. Try:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  echo "  GROVE_VENV=\$HOME/willow-2.0/.venv-dev ./run_dev.sh" >&2
  exit 1
}

export WILLOW_PG_DB="${WILLOW_PG_DB:-willow_20}"
export WILLOW_PG_USER="${WILLOW_PG_USER:-${USER:-}}"
export WILLOW_STORE_ROOT="${WILLOW_STORE_ROOT:-$HOME/.willow/store}"
export GROVE_SENDER="${GROVE_SENDER:-${WILLOW_AGENT_NAME:-Auto}}"

if [[ -z "${WILLOW_ROOT:-}" ]]; then
  for _wr in "$HOME/willow-2.0" "$HOME/github/willow-2.0"; do
    if [[ -f "$_wr/willow.sh" ]]; then
      export WILLOW_ROOT="$_wr"
      break
    fi
  done
fi

if [[ -n "${WILLOW_ROOT:-}" ]]; then
  export PYTHONPATH="${WILLOW_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
  "${PY}" -m willow.fylgja.global_settings --init 2>/dev/null || true
fi

# Fresh-start shell has no fleet boot yet; keep env for when it returns.
export GROVE_SKIP_FLEET="${GROVE_SKIP_FLEET:-1}"
export GROVE_SKIP_KART="${GROVE_SKIP_KART:-1}"

echo "Grove dashboard DEV (fresh-start): $(pwd)" >&2
echo "Using: $PY (db=${WILLOW_PG_DB})" >&2
echo "Keys: 1=Home  2=Workspace  q=quit" >&2
exec "$PY" app.py "$@"
