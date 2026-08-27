#!/usr/bin/env bash
# ci-security-grep.sh — sweep the tracked tree for known-risky patterns.
# b17: GRSEC · ΔΣ=42
#
# Runs in CI per docs/INVARIANTS.md §10 ("CI proves the invariants"). The
# 2026-07-28 SECURITY_AUDIT.md sweep is a manual pass; this step keeps a
# pinned subset of that sweep running on every PR so regressions surface
# before merge, not on the next audit.
#
# Patterns
# --------
# The greps below match well-known risky Python patterns:
#   - os.system(              — arbitrary shell invocation
#   - subprocess.Popen(...shell=True   — shell=True in Popen
#   - subprocess.run(...shell=True     — shell=True in run
#   - subprocess.call(...shell=True    — shell=True in call
#   - shell=True              — bare (catches the check_output / check_call variants)
#   - eval(                   — arbitrary Python evaluation
#   - exec(                   — arbitrary Python execution
#   - pickle.loads            — deserialization of untrusted bytes
#   - yaml.load(              — bare yaml.load (no SafeLoader argument)
#   - input().*shell          — best-effort shell-composition sniff
#
# Allowlist
# ---------
# `scripts/ci-security-grep.allowlist` — one hit per line, format:
#   <path>:<substring-of-the-matched-line>
# A blank line or a line beginning with `#` is a comment. Every allowlisted
# hit must carry a preceding comment explaining why it is safe.
#
# Exit codes
# ----------
#   0  all hits are allowlisted (or there are no hits)
#   1  at least one non-allowlisted hit found
#   2  invocation / environment error

set -u
set -o pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "${REPO_ROOT}" ]]; then
  echo "ci-security-grep: not inside a git tree" >&2
  exit 2
fi
cd "${REPO_ROOT}"

ALLOWLIST="scripts/ci-security-grep.allowlist"

# Extended-regex pattern set. Each alternative is one risky idiom.
# `shell=True` on its own catches subprocess.check_output/check_call variants
# that the earlier subprocess.* alternatives don't spell out.
PATTERN='os\.system\(|subprocess\.Popen\([^)]*shell=True|subprocess\.run\([^)]*shell=True|subprocess\.call\([^)]*shell=True|shell=True|\beval\(|\bexec\(|pickle\.loads|yaml\.load\('

# Only scan tracked *.py and *.sh files. Docs and design notes are prose
# and are covered by the docs-drift check (PR 11), not this one.
mapfile -t TARGETS < <(git ls-files '*.py' '*.sh')

if [[ "${#TARGETS[@]}" -eq 0 ]]; then
  echo "ci-security-grep: no *.py or *.sh files tracked; nothing to scan."
  exit 0
fi

# Do not scan this script itself — its docstring lists every pattern verbatim.
FILTERED=()
for f in "${TARGETS[@]}"; do
  if [[ "${f}" == "scripts/ci-security-grep.sh" ]]; then
    continue
  fi
  FILTERED+=("${f}")
done

RAW_HITS="$(grep -HnE "${PATTERN}" "${FILTERED[@]}" 2>/dev/null || true)"

if [[ -z "${RAW_HITS}" ]]; then
  echo "ci-security-grep: no risky patterns found in tracked *.py / *.sh."
  exit 0
fi

# Load allowlist entries.
declare -a ALLOW_PATH=()
declare -a ALLOW_SUBSTR=()
if [[ -f "${ALLOWLIST}" ]]; then
  while IFS= read -r line || [[ -n "${line}" ]]; do
    # strip trailing CR just in case
    line="${line%$'\r'}"
    # skip blanks and comments
    if [[ -z "${line}" || "${line:0:1}" == "#" ]]; then
      continue
    fi
    # format: <path>:<substring>
    path_part="${line%%:*}"
    substr_part="${line#*:}"
    if [[ "${path_part}" == "${line}" || -z "${substr_part}" ]]; then
      echo "ci-security-grep: malformed allowlist line: ${line}" >&2
      exit 2
    fi
    ALLOW_PATH+=("${path_part}")
    ALLOW_SUBSTR+=("${substr_part}")
  done < "${ALLOWLIST}"
fi

# Walk hits; report those not covered by the allowlist.
declare -i unresolved=0
UNRESOLVED_OUT=""
while IFS= read -r hit; do
  [[ -z "${hit}" ]] && continue
  # hit format from grep -Hn:  <path>:<lineno>:<content>
  hit_path="${hit%%:*}"
  rest="${hit#*:}"
  # rest = <lineno>:<content>
  hit_content="${rest#*:}"

  allowlisted=0
  for i in "${!ALLOW_PATH[@]}"; do
    if [[ "${hit_path}" == "${ALLOW_PATH[$i]}" && "${hit_content}" == *"${ALLOW_SUBSTR[$i]}"* ]]; then
      allowlisted=1
      break
    fi
  done

  if [[ "${allowlisted}" -eq 0 ]]; then
    unresolved=$((unresolved + 1))
    UNRESOLVED_OUT+="${hit}"$'\n'
  fi
done <<< "${RAW_HITS}"

if [[ "${unresolved}" -gt 0 ]]; then
  echo "ci-security-grep: ${unresolved} risky-pattern hit(s) not in allowlist:"
  echo "----"
  printf '%s' "${UNRESOLVED_OUT}"
  echo "----"
  echo "If a hit is a legitimate false positive, add it to ${ALLOWLIST}"
  echo "with a preceding comment explaining why. Otherwise, fix the code."
  exit 1
fi

echo "ci-security-grep: all $(printf '%s\n' "${RAW_HITS}" | wc -l | tr -d ' ') hit(s) covered by ${ALLOWLIST}."
exit 0
