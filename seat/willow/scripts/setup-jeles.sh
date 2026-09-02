#!/usr/bin/env bash
# setup-jeles.sh — install Jeles, seed the bundled corpus, wire federation env.
#
# Home: willows-grove/seat/willow (Willow desk).
#
#   bash seat/willow/scripts/setup-jeles.sh
#   bash seat/willow/scripts/setup-jeles.sh --dry-run
#
set -euo pipefail

SEAT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROVE_REPO="$(cd "$SEAT_DIR/../.." && pwd)"
WM_ROOT="$(cd "$GROVE_REPO/.." && pwd)"
JELES_REPO="${JELES_REPO:-$HOME/github/hornbook-knowledge/Jeles}"
WILLOW_HOME="${WILLOW_HOME:-$WM_ROOT/.willow}"
FLEET_ENV="$WILLOW_HOME/fleet.env"
FED_REGISTRY="$WILLOW_HOME/mcp_apps/_federation/servers.json"
JELES_SERVER_ID="8cae3d1dcdf4"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      sed -n '2,8p' "$0" | tr -d '#'
      exit 0
      ;;
  esac
done

say() { printf '\n== %s ==\n' "$*"; }

if [[ ! -d "$JELES_REPO" ]]; then
  echo "error: Jeles checkout not found at $JELES_REPO (set JELES_REPO=)" >&2
  exit 1
fi

say "install jeles [mcp,nestor] editable"
JELES_VENV="$JELES_REPO/.venv"
if [[ ! -x "$JELES_VENV/bin/python3" ]]; then
  python3 -m venv "$JELES_VENV"
fi
"$JELES_VENV/bin/pip" install -q -e "$JELES_REPO[mcp,nestor]"
"$JELES_VENV/bin/python3" - <<'PY'
import importlib, os
from importlib.metadata import version
m = importlib.import_module("jeles")
print(f"  jeles {version('jeles')} @ {os.path.dirname(m.__file__)}")
for extra in ("mcp", "nestor"):
    try:
        if extra == "mcp":
            import mcp  # noqa: F401
        else:
            import nestor  # noqa: F401
        print(f"  extra [{extra}] ok")
    except ImportError as exc:
        print(f"  extra [{extra}] MISSING: {exc}")
PY

say "fleet environment"
if [[ -f "$FLEET_ENV" ]]; then
  # shellcheck disable=SC1090
  set -a; source "$FLEET_ENV"; set +a
else
  export WILLOW_HOME WILLOW_STORE_ROOT="${WILLOW_STORE_ROOT:-$WILLOW_HOME/store}"
  export JELES_CORPUS_APP_ID="${JELES_CORPUS_APP_ID:-jeles}"
fi
export JELES_CORPUS_APP_ID="${JELES_CORPUS_APP_ID:-jeles}"
export NESTOR_KEYRING="${NESTOR_KEYRING:-$HOME/.nestor/keep/verifiers.json}"

WMCP_PY="${WM_ROOT}/willow-mcp/.venv/bin/python3"
if [[ ! -x "$WMCP_PY" ]]; then
  WMCP_PY="${WILLOW_HOME}/venvs/willow-mcp/bin/python3"
fi

say "seed bundled corpus (74 files, ~968 Q/A pairs)"
if [[ "$DRY_RUN" -eq 1 ]]; then
  "$JELES_VENV/bin/jeles-seed" --dry-run
else
  "$JELES_VENV/bin/jeles-seed"
  say "promote commons domains (core-* asserted → machine)"
  "$JELES_VENV/bin/python3" "$JELES_REPO/scripts/jeles-commons-promote.py"
fi

say "federation env_keys for jeles-corpus (re-ratify + PGP sign)"
FED_DIR="$(dirname "$FED_REGISTRY")"
FED_OWNER="$(stat -c '%U:%G' "$FED_DIR" 2>/dev/null || echo unknown)"
if [[ "$FED_OWNER" != "$USER:$USER" && "$FED_OWNER" != "unknown" ]]; then
  sudo chown -R "$USER:$USER" "$FED_DIR"
  RESTORE_FED=1
else
  RESTORE_FED=0
fi
WILLOW_HOME="$WILLOW_HOME" JELES_REPO="$JELES_REPO" "$WMCP_PY" - <<'PY'
import os
from willow_mcp.mcp_federation import McpServerSpec, ratify

jeles = os.environ["JELES_REPO"]
spec = McpServerSpec(
    id="8cae3d1dcdf4",
    name="jeles-corpus",
    command=f"{jeles}/.venv/bin/jeles-corpus-mcp",
    args=(),
    env_keys=(
        "WILLOW_HOME",
        "WILLOW_STORE_ROOT",
        "JELES_CORPUS_APP_ID",
        "NESTOR_KEYRING",
        "NESTOR_SEAL_KEY",
    ),
    cwd=jeles,
    transport="stdio",
    source_path="operator-ratified (no .mcp.json declares this server)",
)
entry = ratify(
    spec,
    ratified_by="sean",
    reason="Jeles corpus setup — shared store, jeles gap seat, Nestor seals.",
)
print("  env_keys:", entry.get("env_keys"))
PY
if [[ "$RESTORE_FED" -eq 1 ]]; then
  sudo chown -R willow-operator:willow-operator "$FED_DIR"
fi

say "verify store + search"
"$JELES_VENV/bin/python3" - <<'PY'
from jeles import corpus
hits = corpus.search_nuggets("inflation", limit=5)
print(f"  search 'inflation': {len(hits)} hit(s)")
if hits:
    print(f"  sample: {hits[0].get('question','')[:72]}...")
PY

say "verify federation spawn env (via willow-mcp)"
if [[ -x "$WMCP_PY" ]]; then
  JELES_CORPUS_APP_ID="$JELES_CORPUS_APP_ID" \
  WILLOW_HOME="$WILLOW_HOME" \
  WILLOW_STORE_ROOT="${WILLOW_STORE_ROOT:-$WILLOW_HOME/store}" \
  NESTOR_KEYRING="$NESTOR_KEYRING" \
  "$WMCP_PY" - <<'PY'
import json, os
from willow_mcp import mcp_federation

entry = mcp_federation.get_ratified("8cae3d1dcdf4")
env = mcp_federation.load_server_env(entry)
for k in ("WILLOW_STORE_ROOT", "JELES_CORPUS_APP_ID", "NESTOR_KEYRING"):
    print(f"  spawn would pass {k}={env.get(k, '(absent)')!r}")
PY
else
  echo "  skip: willow-mcp venv not found"
fi

echo
echo "Jeles setup complete."
echo "  Store:  ${WILLOW_STORE_ROOT:-$WILLOW_HOME/store}/ask_jeles_corpus/store.db"
echo "  Seat intake: $SEAT_DIR/jeles-intake/"
echo "  Seed:   core-* domains → machine (commons); other seed → asserted"
echo "  Gaps:   JELES_CORPUS_APP_ID=$JELES_CORPUS_APP_ID (restart Cursor MCP for env_keys to apply live)"
