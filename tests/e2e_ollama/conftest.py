# b17: WGRV1 ΔΣ=42
"""Fixtures for the Ollama-backed watcher e2e suite (INVARIANTS.md §10).

The suite exercises the C11 LEFT-side write path end-to-end: a real
Postgres LISTEN/NOTIFY on ``grove.messages`` feeds the resident watcher,
which classifies each row through a real Ollama instance and writes the
resulting atom to ``kb_journal``. To keep the assertion surface local we
stub ``willow_mcp.server.kb_journal`` — the write we care about is the
one Grove hands to willow-mcp; the willow-mcp mock e2e (PR 10) tests
willow-mcp's side of that same seam separately.

Fixtures:

* ``ollama_ready`` — session-scoped readiness probe against Ollama's
  ``/api/tags`` endpoint. Missing service is routed through
  ``_missing_witness``: pytest.skip locally, pytest.fail on CI.
* ``pulled_model`` — pulls the smallest known model once per session.
  Cached in ``_MODEL_CACHE`` so a suite with N tests pays the ~30-60s
  pull cost exactly once. Failure to pull any candidate is routed
  through ``_missing_witness``.
* ``grove_pg_schema`` — ensures ``grove.channels`` + ``grove.messages``
  and the ``grove_channel`` NOTIFY trigger exist (idempotent, mirrors
  ``schema.sql``), then yields a fresh ``channel_id`` for the test and
  cleans up any rows the test inserted afterwards. Missing
  ``WILLOW_DB_URL``, ``psycopg2``, or Postgres reachability is routed
  through ``_missing_witness``.
* ``willow_mcp_capture`` — installs a fake ``willow_mcp.server`` in
  ``sys.modules`` with a ``kb_journal`` that appends to a captures list;
  yields the list; restores ``sys.modules`` on teardown. This is the
  seam that lets the test assert ``sender="resident-watcher"`` + the
  ``domain:*`` tag + verbatim text on every write.

INVARIANTS.md §10 ("CI proves the invariants") requires CI witnesses to
fail loudly, not silently skip: on CI the sidecars MUST be there, so a
missing service is a broken environment, not a green-worthy skip. The
``_missing_witness`` helper below reads ``$GITHUB_ACTIONS`` and dispatches
to ``pytest.fail`` on CI or ``pytest.skip`` locally — preserving developer
ergonomics on laptops while making CI honest. (Grove v0.9 PR 12, Loki
finding M14.)
"""
from __future__ import annotations

import json
import os
import sys
import time
import types
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Config knobs — tunable per environment, sane defaults for CI.
# ---------------------------------------------------------------------------

# Order matters: the first that pulls successfully wins. Smallest first so a
# green run pays the least. ``qwen2.5:0.5b`` is roughly ~400 MB, the smallest
# general-purpose Ollama tag; ``tinyllama`` is a battle-tested fallback.
_MODEL_CANDIDATES = ("qwen2.5:0.5b", "tinyllama:latest", "smollm:135m")

_OLLAMA_READY_TIMEOUT_SECONDS = 30.0
_OLLAMA_PULL_TIMEOUT_SECONDS = 300.0  # cold pull: model download + extract

_MODEL_CACHE: dict[str, str] = {}


def _missing_witness(reason: str) -> None:
    """INVARIANTS.md §10 dispatch — fail loudly on CI, skip locally.

    Every §10 assertion downstream is gated on the e2e_ollama fixtures
    succeeding, so a raw ``pytest.skip`` on a missing sidecar makes CI
    green with no witness actually run. On CI (``$GITHUB_ACTIONS=true``)
    the runner MUST provide Ollama, Postgres, and psycopg2; their
    absence is a broken build, not an operator-side excuse. Off CI —
    developer laptops, ad-hoc probes — a skip is the right posture: the
    suite is expensive and shouldn't block unrelated work.

    A single ``never returns`` point of control so the three fixtures
    below stay honest and the discipline is one line to audit.
    (Grove v0.9 PR 12, Loki finding M14-e2e_ollama-fail-not-skip.)
    """
    on_ci = os.environ.get("GITHUB_ACTIONS", "").strip().lower() == "true"
    if on_ci:
        pytest.fail(reason)
    else:
        pytest.skip(reason)


def _ollama_base_url() -> str:
    """Prefer explicit ``OLLAMA_HOST``; fall back to the loopback default."""
    raw = os.environ.get("OLLAMA_HOST", "").strip() or "http://127.0.0.1:11434"
    # Ollama sometimes exports OLLAMA_HOST without a scheme (e.g. "127.0.0.1:11434").
    if "://" not in raw:
        raw = "http://" + raw
    return raw.rstrip("/")


def _http_get(url: str, timeout: float = 5.0) -> tuple[int, bytes]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), resp.read()


def _http_post_json(url: str, payload: dict[str, Any], timeout: float = 30.0) -> tuple[int, bytes]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), resp.read()


# ---------------------------------------------------------------------------
# Ollama readiness — poll /api/tags until it answers, or give up.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def ollama_ready() -> str:
    """Return the Ollama base URL once ``/api/tags`` answers 200.

    On CI (``$GITHUB_ACTIONS=true``) fails the calling test if the
    service does not come up within ``_OLLAMA_READY_TIMEOUT_SECONDS`` —
    the CI Ollama sidecar MUST be there, so absence is a broken
    environment (INVARIANTS.md §10). Off CI the same case skips so an
    operator-only build shouldn't need Ollama to green.
    """
    base = _ollama_base_url()
    deadline = time.monotonic() + _OLLAMA_READY_TIMEOUT_SECONDS
    last_err: str | None = None
    while time.monotonic() < deadline:
        try:
            code, _ = _http_get(base + "/api/tags", timeout=3.0)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as err:
            last_err = f"{type(err).__name__}: {err}"
            time.sleep(1.0)
            continue
        if code == 200:
            return base
        last_err = f"HTTP {code}"
        time.sleep(1.0)
    _missing_witness(
        f"Ollama not reachable at {base}/api/tags within "
        f"{_OLLAMA_READY_TIMEOUT_SECONDS:.0f}s (last: {last_err}) — "
        "the e2e_ollama suite requires a live Ollama service (INVARIANTS.md §10)."
    )
    return base  # unreachable — _missing_witness raises


# ---------------------------------------------------------------------------
# Model pull — once per session, cached across tests.
# ---------------------------------------------------------------------------

def _list_models(base: str) -> list[str]:
    """Names currently held by the Ollama server (empty on any error)."""
    try:
        code, body = _http_get(base + "/api/tags", timeout=5.0)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError):
        return []
    if code != 200:
        return []
    try:
        data = json.loads(body.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return []
    if not isinstance(data, dict):
        return []
    models = data.get("models")
    if not isinstance(models, list):
        return []
    names: list[str] = []
    for m in models:
        if isinstance(m, dict):
            name = m.get("name") or m.get("model")
            if isinstance(name, str) and name:
                names.append(name)
    return names


def _pull_model(base: str, name: str) -> bool:
    """Pull one model tag. Returns True on success (or already-present)."""
    # Already there? Nothing to do.
    if name in _list_models(base):
        return True
    try:
        # stream=False so the whole pull runs in one blocking call; the
        # server sends a single JSON body at the end.
        code, _ = _http_post_json(
            base + "/api/pull",
            {"name": name, "stream": False},
            timeout=_OLLAMA_PULL_TIMEOUT_SECONDS,
        )
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError):
        return False
    if code != 200:
        return False
    return name in _list_models(base)


@pytest.fixture(scope="session")
def pulled_model(ollama_ready: str) -> str:
    """Return the name of a model that Ollama has locally and can generate with.

    Tries the ``_MODEL_CANDIDATES`` in order. Caches the winner in
    ``_MODEL_CACHE`` so a session with N tests pays the pull cost once.
    On CI a failed pull is a hard fail (the runner should have outbound
    network for the model registry); off CI it skips.
    """
    cached = _MODEL_CACHE.get(ollama_ready)
    if cached:
        return cached

    # Fast path — a candidate is already there from a prior run.
    have = set(_list_models(ollama_ready))
    for candidate in _MODEL_CANDIDATES:
        if candidate in have:
            _MODEL_CACHE[ollama_ready] = candidate
            return candidate

    # Slow path — pull the smallest that succeeds.
    failures: list[str] = []
    for candidate in _MODEL_CANDIDATES:
        if _pull_model(ollama_ready, candidate):
            _MODEL_CACHE[ollama_ready] = candidate
            return candidate
        failures.append(candidate)

    _missing_witness(
        f"Ollama at {ollama_ready} could not pull any of {failures} within "
        f"{_OLLAMA_PULL_TIMEOUT_SECONDS:.0f}s — likely no outbound network. "
        "On CI this is a hard failure (INVARIANTS.md §10); locally it skips."
    )
    return ""  # unreachable


# ---------------------------------------------------------------------------
# Postgres schema — grove.channels + grove.messages + NOTIFY trigger.
# ---------------------------------------------------------------------------

def _ensure_grove_schema(cur: Any) -> None:
    """Idempotent create — mirrors the shape in ``schema.sql``.

    The e2e suite is entitled to assume the CI ``willow_20_test`` database
    already carries this from the bootstrap step, but re-issuing the DDL
    lets an operator run the tests against an empty database without
    thinking. Every statement is ``IF NOT EXISTS`` / ``OR REPLACE`` so
    the second call is a no-op.
    """
    cur.execute("CREATE SCHEMA IF NOT EXISTS grove;")
    cur.execute("SET search_path = grove, public;")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS grove.channels (
            id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name            TEXT NOT NULL UNIQUE,
            channel_type    TEXT NOT NULL DEFAULT 'group',
            description     TEXT,
            agent_name      TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_archived     BOOLEAN DEFAULT FALSE
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS grove.messages (
            id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            channel_id          BIGINT NOT NULL REFERENCES grove.channels(id),
            sender              TEXT NOT NULL,
            content             TEXT NOT NULL,
            message_type        TEXT NOT NULL DEFAULT 'text',
            reply_to_id         BIGINT REFERENCES grove.messages(id),
            willow_indexed_at   TIMESTAMP,
            to_agent            TEXT DEFAULT '__all__',
            bus_type            TEXT DEFAULT 'EVENT',
            priority            INTEGER DEFAULT 3,
            correlation_id      TEXT,
            ttl                 INTEGER,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted          INTEGER DEFAULT 0
        );
        """
    )
    cur.execute(
        """
        CREATE OR REPLACE FUNCTION grove.grove_notify_message()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            PERFORM pg_notify('grove_channel', NEW.channel_id::text);
            RETURN NEW;
        END;
        $$;
        """
    )
    cur.execute("DROP TRIGGER IF EXISTS trg_grove_notify ON grove.messages;")
    cur.execute(
        """
        CREATE TRIGGER trg_grove_notify
            AFTER INSERT ON grove.messages
            FOR EACH ROW EXECUTE FUNCTION grove.grove_notify_message();
        """
    )


@pytest.fixture(scope="function")
def grove_pg_schema():
    """Yield ``{"dsn": str, "channel_id": int}`` with a private test channel.

    Missing ``WILLOW_DB_URL``, ``psycopg2``, or Postgres reachability is
    routed through ``_missing_witness``: pytest.skip locally, pytest.fail
    on CI. The suite is Postgres-first (INVARIANTS.md §10), so on CI the
    sidecar MUST be there. Cleans up the channel + any messages it
    carries (best-effort) on teardown.
    """
    dsn = os.environ.get("WILLOW_DB_URL", "").strip()
    if not dsn:
        _missing_witness(
            "WILLOW_DB_URL unset — e2e_ollama needs a live Postgres "
            "(INVARIANTS.md §10)."
        )

    try:
        import psycopg2  # type: ignore
    except Exception as err:  # noqa: BLE001
        _missing_witness(f"psycopg2 unavailable ({err}) — e2e_ollama needs it (INVARIANTS.md §10).")

    try:
        conn = psycopg2.connect(dsn)
    except Exception as err:  # noqa: BLE001
        _missing_witness(f"Postgres unreachable at {dsn} ({err}) — e2e_ollama needs it (INVARIANTS.md §10).")

    conn.autocommit = True
    channel_id: int | None = None
    channel_name = f"e2e-ollama-{int(time.time() * 1000)}-{os.getpid()}"
    try:
        cur = conn.cursor()
        _ensure_grove_schema(cur)
        cur.execute(
            "INSERT INTO grove.channels (name, channel_type, description) "
            "VALUES (%s, 'group', 'e2e_ollama transient channel') RETURNING id;",
            (channel_name,),
        )
        row = cur.fetchone()
        if not row:
            _missing_witness("Could not create test channel row — schema anomaly (INVARIANTS.md §10).")
        channel_id = int(row[0])

        yield {"dsn": dsn, "channel_id": channel_id, "channel_name": channel_name}
    finally:
        try:
            cur = conn.cursor()
            if channel_id is not None:
                cur.execute(
                    "DELETE FROM grove.messages WHERE channel_id = %s;",
                    (channel_id,),
                )
                cur.execute(
                    "DELETE FROM grove.channels WHERE id = %s;",
                    (channel_id,),
                )
        except Exception:  # noqa: BLE001 — cleanup is best-effort
            pass
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# Fake willow_mcp.server — capture kb_journal writes without a live organ.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def willow_mcp_capture():
    """Patch ``willow_mcp_client.call_tool`` to capture ``kb_journal`` writes."""
    from unittest.mock import patch

    from grove import journal_writer as _jw
    from grove import willow_mcp_client

    captures: list[dict[str, Any]] = []

    def _call_tool(name, arguments):
        if name != "kb_journal":
            return None
        entry = {
            "app_id": arguments.get("app_id"),
            "content": arguments.get("content"),
            "source": arguments.get("source"),
            "tags": list(arguments.get("tags") or []),
            "ts_seen": time.time(),
        }
        captures.append(entry)
        return {"id": f"atom-e2e-{len(captures)}", "domain": "journal"}

    _jw._reset_log_once_for_tests()
    willow_mcp_client._reset_client_for_tests()
    with patch.object(willow_mcp_client, "call_tool", side_effect=_call_tool):
        yield captures
