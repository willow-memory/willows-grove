# b17: WGRV1 ΔΣ=42
"""tests/test_grove_reader_error_redaction.py — Loki M17 pin.

Cross-cutting hazard (Loki v0.9 audit finding M17): the eight writer
helpers in ``grove_reader.py`` returned raw ``str(e)`` on the failure
branch. For psycopg2 errors that string embeds internal state — schema
names, constraint names, DETAIL row values — that landed in the UI
verbatim.

Fix pinned: every writer's ``except`` block routes the caller-facing
error through ``grove_reader._redact_db_error(e)``, which maps the
exception TYPE (not the message) to a short generic string
(``constraint violation`` / ``database unreachable`` / ``database
error``). The full exception is still preserved in the ``_log.warning``
call so operators debug from server logs, not the caller's dict.

Harness: monkeypatch ``grove_db.get_connection`` to a fake conn whose
``cursor().execute()`` raises a ``psycopg2.errors.UniqueViolation`` whose
``str()`` carries an identifiable schema name (``grove.channels``), an
identifiable constraint name (``channels_name_key``), a row-value tell
(``secret-project``), and the tell-tale ``DETAIL:`` prefix. A
representative writer (``grove_create_text_channel``) is invoked; the
returned ``error`` field must contain none of those substrings.

On the unfixed tree the writer returns ``str(e)`` — every leak substring
is present and every ``assertNotIn`` fails. Fail-first by construction.

Stdlib unittest only. No live Postgres required.

INVARIANTS.md §1 — writer error responses are the caller's sole failure
signal on the success surface (``{ok, error}``); they must not double as
a channel that leaks database internals into the UI.
"""
from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import psycopg2  # noqa: E402
import psycopg2.errors  # noqa: E402

import grove_db  # noqa: E402
import grove_reader  # noqa: E402


# Identifiable substrings the UniqueViolation carries in its ``str()``.
# Each one is a piece of internal state that MUST NOT reach the caller.
_SCHEMA_NAME = "grove.channels"
_CONSTRAINT_NAME = "channels_name_key"
_ROW_VALUE = "secret-project"
_DETAIL_PREFIX = "DETAIL:"

_LEAK_TEMPLATE = (
    'duplicate key value violates unique constraint "{constraint}"\n'
    "DETAIL:  Key (name)=({row}) already exists in schema {schema}."
).format(constraint=_CONSTRAINT_NAME, row=_ROW_VALUE, schema=_SCHEMA_NAME)


class _LeakyCursor:
    """A cursor whose ``execute`` raises a psycopg2 UniqueViolation whose
    ``str()`` embeds a schema name, a constraint name, and a row value.
    """

    description = ()

    def execute(self, *args, **kwargs):  # noqa: D401 — mimic psycopg2 cursor API
        raise psycopg2.errors.UniqueViolation(_LEAK_TEMPLATE)

    def fetchall(self):
        return []

    def fetchone(self):
        return None

    def close(self):
        pass


class _LeakyConn:
    def cursor(self):
        return _LeakyCursor()

    def rollback(self):
        pass

    def commit(self):
        pass

    def close(self):
        pass


class GroveReaderErrorRedactionTests(unittest.TestCase):
    """Pin Loki M17: writer error responses must not leak DB internals."""

    def setUp(self):
        self._orig_get = grove_db.get_connection
        self._orig_release = grove_db.release_connection
        grove_db.get_connection = lambda: _LeakyConn()
        grove_db.release_connection = lambda conn: None

    def tearDown(self):
        grove_db.get_connection = self._orig_get
        grove_db.release_connection = self._orig_release

    def test_grove_create_text_channel_redacts_schema_and_constraint(self):
        # 'engineering' is a non-reserved name that passes
        # panes.chat_admin.normalize_channel_name. The reader's first
        # cursor.execute() then raises our leaky UniqueViolation, taking
        # the flow through the writer's caller-facing except block.
        result = grove_reader.grove_create_text_channel("engineering")

        # Writer contract: {ok: False, error: <str>} on failure.
        self.assertIsInstance(result, dict)
        self.assertIs(result.get("ok"), False)
        err = result.get("error")
        self.assertIsInstance(err, str)
        self.assertNotEqual(
            err, "",
            "error must be a non-empty caller signal, not the empty string",
        )

        # Load-bearing assertions: none of the psycopg2-embedded internal-
        # state substrings may reach the caller. On the unfixed tree
        # str(e) contains ALL of these and every assertion below fails.
        self.assertNotIn(
            _CONSTRAINT_NAME, err,
            f"constraint name leaked in caller-facing error: {err!r}",
        )
        self.assertNotIn(
            _SCHEMA_NAME, err,
            f"schema name leaked in caller-facing error: {err!r}",
        )
        self.assertNotIn(
            _ROW_VALUE, err,
            f"row value leaked in caller-facing error: {err!r}",
        )
        self.assertNotIn(
            _DETAIL_PREFIX, err,
            f"psycopg2 DETAIL line leaked in caller-facing error: {err!r}",
        )


if __name__ == "__main__":
    unittest.main()
