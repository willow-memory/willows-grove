---
b17: WGRV2
title: Security Audit — safe-app-willow-grove
date: 2026-05-06
auditor: Hanuman (Claude Code, Sonnet 4.6)
status: open (tracking doc)
---

# Security Audit — safe-app-willow-grove

Part of the Level 2 full-fleet security audit.

This PR is the tracking doc. No patches here — patches go in separate PRs.

---

## Scope

| Directory | Purpose | Coverage |
|-----------|---------|----------|
| `grove/` | MCP server, OAuth provider, TUI layouts | Full |
| `grove_db.py` | Postgres connection pool + DB operations | Full |
| `grove_serve.py` | Willow MCP proxy + KB search | Full |
| `grove_client.py` | HTTP client for MCP calls | Full |
| `kart_worker.py` | Task executor (subprocess runner) | Full |
| `panes/`, `widgets/` | Textual TUI panels | Spot-check |
| Total Python files | ~45 | Targeted scan |

---

## Rubric Results

| # | Check | Status | Finding |
|---|---|---|---|
| R1 | SQL injection via f-string/identifier concat | ⚠️ P2 | `grove_serve.py:306` — f-string WHERE with ILIKE clause. Template safe (`%s` placeholders), but pattern is a code smell. See G-SQL-01. |
| R2 | Shell injection — `os.system`, `shell=True` | ⚠️ P1 | `kart_worker.py:144` — `bash -c cmd` with user-supplied task text. Mitigated by `_SHELL_METACHAR_RE` allowlist, but allowlist is bypassable. See G-SHL-01. |
| R3 | Path traversal — file ops accepting `../` or absolute | ✅ PASS | All path ops use `Path.home()` / `os.path.expanduser`. No user-controlled path input to file ops. |
| R4 | Hardcoded credentials in VC | ✅ PASS | Tokens generated with `secrets.token_hex(32)`, stored in `~/.willow/grove_mcp_token`. No defaults in source. |
| R5 | CORS wildcards | ✅ N/A | No CORS headers in MCP server — OAuth PKCE gate handles auth. Serve mode is localhost-only by design. |
| R6 | XSS — `innerHTML` with user input | ✅ N/A | No web frontend. Textual TUI only. |
| R7 | Unsigned/unverified code execution | ⚠️ P1 | `kart_worker.py` runs agent Python/script/shell commands from Kart queue. Task text is agent-submitted, not user-signed. No integrity check on task content. See G-KART-01. |
| R8 | Missing auth on MCP tools | ✅ PASS | `grove/mcp_local.py` implements OAuth 2.0 PKCE (dynamic client registration, token-gated). Stdio mode trusted by design (local process). |
| R9 | Bare `except` swallowing security-critical errors | ⚠️ P2 | `grove_db.py:87` and `grove_db.py:548` silently `pass` on exceptions. `grove_db.py:499` returns `{}` on rollback failure. 166 `except Exception` across codebase. See G-EXC-01. |
| R10 | Predictable temp paths, world-readable `/tmp` state | ✅ PASS | No `/tmp` usage in production code. Token files use `Path.home() / ".willow"`. |
| R11 | Race conditions / missing locks | ✅ PASS | `grove_db.py` uses `ThreadedConnectionPool` with `threading.Lock()` double-checked init. Safe for concurrent callers. |
| R12 | `safe_integration.py` status() correctness | ✅ N/A | App ships no `safe_integration.py`; manifest declares `local: true`, no SAFE gate required. |
| R13 | Entry point in manifest is importable | ✅ PASS | `entry_point: "willow-grove:app"`. `app.py` is importable without errors. |
| R14 | `requirements.txt` with pinned deps | ⚠️ P2 | All deps use `>=` version ranges. Security-critical packages (cryptography, mcp) unpinned. See G-DEP-01. |
| R15 | No hardcoded developer home paths | ✅ PASS | All home references use `Path.home()` or `os.path.expanduser("~")`. No `/home/sean-campbell/` in source. |

---

## Findings

### G-SHL-01 — `bash -c` with Agent-Submitted Task Text (P1)

**File:** `kart_worker.py:144`
**Severity:** P1
**Status:** Open

`kart_worker.py` accepts task text from the Kart queue and passes it to `bash -c`:

```python
proc = subprocess.Popen(
    prefix + ["bash", "-c", cmd],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ...
)
```

The `_SHELL_METACHAR_RE` regex (`[;&|$()\\` + r"`><]") blocks common injection chars, and `_SHELL_STARTERS` allowlists permitted command prefixes. However:

1. The allowlist approach is fragile — new shell techniques (process substitution, newline injection) may bypass it.
2. Task text comes from any Kart-submitting agent — a compromised or misbehaving agent could craft bypass strings.

**Current mitigation:** `_validate_shell_cmd()` runs before execution and returns `False` on match. If validation fails, task is rejected.

**Risk assessment:** Acceptable for trusted fleet agents on local machine. Becomes P0 if Kart queue is ever exposed to external input or network agents.

**Recommended fix (P1):** Add a whitelist of allowed commands *by path*, not by prefix string. Avoid `bash -c` entirely for Python tasks; use `python3 -c` or script runner with explicit interpreter.

---

### G-KART-01 — No Integrity Check on Kart Task Content (P1)

**File:** `kart_worker.py`
**Severity:** P1
**Status:** Open

Tasks submitted to Kart carry no cryptographic signature or authorization proof. Any agent (or process) that can write to `willow.tasks` can submit arbitrary code for execution. The worker trusts task content implicitly.

**Current mitigation:** Kart queue is local Postgres — only agents with DB write access can submit. SAFE gate partially covers this via `submitted_by` field.

**Risk:** If a SAFE gate bypass or SQL injection exists elsewhere, untrusted tasks could execute arbitrary code under the Kart worker's process credentials.

**Recommended fix:** HMAC-sign task payloads at submission time using agent's Vault key; verify at execution time. Out of scope for Phase 1 — flag for Phase 2.

---

### G-EXC-01 — Silent Exception Swallowing in DB Operations (P2)

**File:** `grove_db.py` lines 87, 499, 548
**Severity:** P2
**Status:** Open

Three silent exception handlers in DB-critical paths:

```python
# grove_db.py:86-87 — connection release failure silently ignored
except Exception:
    pass  # connection may be leaked

# grove_db.py:498-500 — rollback failure returns empty dict
except Exception:
    conn.rollback()
    return {}  # silent failure, caller gets no error

# grove_db.py:547-548 — silent pass in cleanup
except Exception:
    pass
```

Silent DB failures hide connection leaks, data loss, and potential integrity violations.

**Fix:** Log before swallowing, at minimum:
```python
except Exception as e:
    print(f"[WARN] grove_db: {e}", flush=True)
    pass
```

---

### G-SQL-01 — Dynamic f-string WHERE Clause (P2)

**File:** `grove_serve.py:303-306`
**Severity:** P2 (code smell — not an injection risk)
**Status:** Open

```python
ilike_clause = " OR ".join(["summary ILIKE %s"] * len(words))
cur.execute(
    f"SELECT title, summary FROM knowledge WHERE ({ilike_clause}) LIMIT %s",
    [f"%{w}%" for w in words] + [limit],
)
```

The `ilike_clause` contains only `%s` placeholders — not user input — so this is not an active injection vector. However, the f-string pattern could become one if `ilike_clause` were ever populated differently.

**Fix:** Build the WHERE clause as a constant template and pass length dynamically without f-string:
```python
placeholders = " OR ".join(["summary ILIKE %s"] * len(words))
query = "SELECT title, summary FROM knowledge WHERE (" + placeholders + ") LIMIT %s"
cur.execute(query, [f"%{w}%" for w in words] + [limit])
```

---

### G-DEP-01 — Unpinned Dependencies (P2)

**File:** `requirements.txt`
**Severity:** P2
**Status:** Open

All dependencies use `>=` version ranges:
```
textual>=0.61.0
cryptography>=42.0.0
mcp>=1.0.0
```

`cryptography` and `mcp` are security-critical. Unpinned versions allow `pip install` to pull breaking or vulnerable releases.

**Fix:** Pin to tested versions (e.g., `cryptography==42.0.8`, `mcp==1.6.0`).

---

## Summary

| Priority | Count | Items |
|---|---|---|
| P0 | 0 | None |
| P1 | 2 | G-SHL-01 (bash -c task execution), G-KART-01 (unsigned tasks) |
| P2 | 3 | G-SQL-01 (WHERE f-string), G-EXC-01 (silent DB exceptions), G-DEP-01 (unpinned deps) |

No P0 findings. The two P1 issues are acceptable risk for the current trusted-fleet, local-only deployment. Both become P0 if the system is ever exposed to external agents or network input. OAuth PKCE on the MCP server is correctly implemented.

---

*ΔΣ=42*
