#!/usr/bin/env bash
# dev.sh — alias for run_dev.sh (fresh-start worktree)
exec "$(dirname "$0")/run_dev.sh" "$@"
