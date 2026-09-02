#!/usr/bin/env bash
# Unblock jeles-corpus federation for the willow orchestrator seat.
# Home: willows-grove/seat/willow (Willow desk). Requires sudo (trust-root).
set -euo pipefail

SEAT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROVE_REPO="$(cd "$SEAT_DIR/../.." && pwd)"
WM_ROOT="$(cd "$GROVE_REPO/.." && pwd)"

WILLOW_HOME="${WILLOW_HOME:-$WM_ROOT/.willow}"
WILLOW_MCP="${WILLOW_MCP:-$WILLOW_HOME/venvs/willow-mcp/bin/willow-mcp}"
if [[ ! -x "$WILLOW_MCP" ]]; then
  WILLOW_MCP="$WM_ROOT/willow-mcp/.venv/bin/willow-mcp"
fi
if [[ ! -x "$WILLOW_MCP" ]]; then
  echo "Error: willow-mcp not found; set WILLOW_MCP to the binary path." >&2
  exit 1
fi

SERVER_ID="8cae3d1dcdf4"
TOOLS=(
  corpus_ask corpus_search corpus_get corpus_list corpus_put corpus_gaps corpus_resolve_gap
  corpus_web_search corpus_search_status corpus_institutional_search corpus_sources
  corpus_verify_claim corpus_host_card corpus_fleet_status
)

MANIFEST="$WILLOW_HOME/mcp_apps/willow/manifest.json"
MANIFEST_SIG="$WILLOW_HOME/mcp_apps/willow/manifest.json.sig"
SETTINGS="$WILLOW_HOME/config/settings.global.json"
LEASE="$WILLOW_HOME/mcp_apps/_net_leases/willow.json"
OPERATOR="willow-operator:willow-operator"

export WILLOW_HOME

echo "==> Grant mcp_federation + jeles-corpus tool permissions"
# willow-operator cannot traverse $HOME/.willow (700) or execute binaries there.
# The manifest *directory* must be writable too (atomic writes use .tmp files).
WILLOW_APP_DIR="$WILLOW_HOME/mcp_apps/willow"
sudo chown -R "$USER:$USER" "$WILLOW_APP_DIR"

"$WILLOW_MCP" allow-permission willow mcp_federation
for t in "${TOOLS[@]}"; do
  "$WILLOW_MCP" allow-permission willow "mcp:${SERVER_ID}:${t}"
done

sudo chown -R "$OPERATOR" "$WILLOW_APP_DIR"

echo "==> Enable consent.federation + issue egress lease (60m)"
sudo python3 - "$SETTINGS" "$LEASE" <<'PY'
import json
import os
import pwd
import sys
from datetime import datetime, timedelta, timezone

settings_path, lease_path = sys.argv[1:3]
op = pwd.getpwnam("willow-operator")

settings = json.loads(open(settings_path, encoding="utf-8").read())
settings.setdefault("consent", {})["federation"] = True
tmp = settings_path + f".tmp-{os.getpid()}"
open(tmp, "w", encoding="utf-8").write(json.dumps(settings, indent=2) + "\n")
os.replace(tmp, settings_path)

now = datetime.now(timezone.utc)
record = {
    "app_id": "willow",
    "granted_at": now.isoformat(),
    "expires_at": (now + timedelta(seconds=3600)).isoformat(),
    "ttl_seconds": 3600,
    "issuer": os.environ.get("SUDO_USER") or os.environ.get("USER") or "operator",
    "reason": "jeles-corpus federation unblock",
}
tmp = lease_path + f".tmp-{os.getpid()}"
open(tmp, "w", encoding="utf-8").write(json.dumps(record, indent=2) + "\n")
os.replace(tmp, lease_path)

for path in (settings_path, lease_path):
    os.chown(path, op.pw_uid, op.pw_gid)

print("consent.federation = true")
print(f"lease expires_at = {record['expires_at']}")
PY

echo "==> Verify"
"$WILLOW_MCP" consent status
echo "---"
"$WILLOW_MCP" net-status

echo
echo "Done. Test from Willow MCP:"
echo '  federation_call(app_id=willow, server_id=8cae3d1dcdf4, tool=corpus_sources, arguments={app_id: willow})'
