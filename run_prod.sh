#!/usr/bin/env bash
# run_prod.sh — launch Willow Grove against the prod DB (grove_prod)
# Sean's personal instance, isolated from fleet dev writes.
#
# Usage: ./run_prod.sh
#
# Willow KB context still comes from willow_20 via the MCP server.
# Only the Grove messages/channels DB is different.

set -e

cd "$(dirname "$0")"

export WILLOW_PG_DB="grove_prod"
export WILLOW_PG_USER="${WILLOW_PG_USER:-sean-campbell}"
export GROVE_SENDER="${GROVE_SENDER:-sean-campbell}"

exec python3 app.py "$@"
