#!/usr/bin/env bash
# Kart task: poll open PR checks until all complete or one fails.
# Uses `gh pr checks` (current state) — not statusCheckRollup, which keeps stale failures.
set -euo pipefail
PRS=(
  "hornbook-knowledge/Jeles#78"
  "Die-Namic-Systems/Nestor#276"
  "willow-memory/willow-mcp#417"
  "rudi193-cmd/Forge#12"
)
INTERVAL="${INTERVAL:-45}"
MAX_ROUNDS="${MAX_ROUNDS:-40}"

round=0
while (( round < MAX_ROUNDS )); do
  round=$((round + 1))
  echo "=== round $round $(date -u +%H:%M:%S)Z ==="
  pending=0
  failed=0
  for spec in "${PRS[@]}"; do
    repo="${spec%%#*}"
    num="${spec##*#}"
    lines=$(gh pr checks "$num" --repo "$repo" 2>/dev/null || true)
    if [[ -z "${lines//[$'\t ']/}" ]]; then
      summary="pending=0|fail=0"
    else
      summary=$(printf '%s\n' "$lines" | awk '
        $2 == "skipping" { next }
        $2 == "pending" { pend++ }
        $2 == "fail" { fail++ }
        END { printf "pending=%d|fail=%d", pend+0, fail+0 }
      ')
    fi
    mergeable=$(gh pr view "$num" --repo "$repo" --json mergeable,state -q '"\(.state)|\(.mergeable // "UNKNOWN")"' 2>/dev/null || echo "ERROR|UNKNOWN")
    echo "$repo#$num  $mergeable|$summary"
    pend=$(echo "$summary" | sed -n 's/.*pending=\([0-9]*\).*/\1/p')
    fail=$(echo "$summary" | sed -n 's/.*fail=\([0-9]*\).*/\1/p')
    [[ "$pend" =~ ^[0-9]+$ ]] && (( pending += pend )) || pending=999
    [[ "$fail" =~ ^[0-9]+$ ]] && (( failed += fail )) || true
  done
  if (( failed > 0 )); then
    echo "FAIL: $failed failing check(s) — exiting"
    exit 1
  fi
  if (( pending == 0 )); then
    echo "ALL GREEN (checks complete, none failed)"
    exit 0
  fi
  echo "waiting ${INTERVAL}s ($pending checks still running)..."
  sleep "$INTERVAL"
done
echo "TIMEOUT after $MAX_ROUNDS rounds"
exit 2
