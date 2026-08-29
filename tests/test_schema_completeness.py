"""tests/test_schema_completeness.py — schema.sql creates every table a
reader or /api/* endpoint actually queries.

PR-14 carryover #3 (docs/design/pr14-carryovers.md). PR 9's CI logs
showed two readers falling to `Unreachable` because their tables never
existed:

    relation "public.routing_decisions" does not exist
    relation "public.human_required_queue" does not exist

INVARIANTS.md §1 accepts `Unreachable` as a valid state — but when
`schema.sql` is missing a table, EVERY CI run for that reader hits
`Unreachable` and only that branch. The `populated` and `empty`
branches never execute against a live table, so a bug in either path
is invisible to CI. This test does not touch that discipline (readers
keep raising `Unreachable` exactly as before) — it only guards the
precondition that lets the other two branches run at all: the table
has to exist.

This is a static grep, deliberately in the same spirit as
`tests/test_state_vocabulary_audit.py`: extract literal table
references from the reader/endpoint source, and assert each one has a
`CREATE TABLE IF NOT EXISTS` in `schema.sql` (or is explicitly
allowlisted, with a reason, because it self-creates at runtime
elsewhere and does not depend on schema.sql at all).
"""
from __future__ import annotations

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_SQL = os.path.join(ROOT, "schema.sql")

# The reader/endpoint surface this audit sweeps. grove_serve.py hosts the
# /api/* handlers; grove_reader.py and grove_db.py are the two readers
# CLAUDE.md names; grove/*.py picks up the rest of the Grove package
# (kart_reader.py, resident_watcher.py, mcp_local.py, ...).
def _swept_files() -> list[str]:
    files = [
        os.path.join(ROOT, "grove_reader.py"),
        os.path.join(ROOT, "grove_db.py"),
        os.path.join(ROOT, "grove_serve.py"),
    ]
    package_dir = os.path.join(ROOT, "grove")
    for name in sorted(os.listdir(package_dir)):
        if name.endswith(".py"):
            files.append(os.path.join(package_dir, name))
    return [f for f in files if os.path.isfile(f)]


# Only fully-qualified `<schema>.<table>` references are in scope. Bare
# names (e.g. grove_db.py's `FROM messages`) rely on that connection's
# `SET search_path = grove, public` and resolve to a table this same
# audit already sees named explicitly elsewhere (grove.messages,
# grove.channels, ...) — qualifying-by-hand every call site would just
# duplicate that coverage, not add any.
_TABLE_REF_RE = re.compile(
    r"\b(?:FROM|INTO|UPDATE|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)"
)

# Postgres system catalogs, not application tables schema.sql could ever
# be expected to create.
_SYSTEM_CATALOGS = frozenset({
    "information_schema.columns",
    "pg_catalog.pg_trigger",
})

# Tables that self-create at runtime independent of schema.sql, so their
# absence from schema.sql is not the PR-9 failure mode (a missing table
# on a from-scratch CI database) — CI would never actually observe them
# as Unreachable-for-missing-table. Each entry names the fallback that
# makes it safe, matching the ALLOWED_SENTINELS pattern in
# test_state_vocabulary_audit.py: an intentional exception with a reason,
# not silent drift.
ALLOWED_SELF_CREATING = {
    # grove_db.py's own pool bootstrap (_bootstrap_schema -> init_schema)
    # runs this CREATE TABLE IF NOT EXISTS on first connection, before any
    # query can run — so a from-scratch database never sees "relation
    # does not exist" for it regardless of schema.sql's contents.
    "public.frank_ledger",
}


def _referenced_tables() -> dict[str, set[str]]:
    """Map each qualified table reference to the files it was found in."""
    found: dict[str, set[str]] = {}
    for path in _swept_files():
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        for match in _TABLE_REF_RE.finditer(src):
            table = match.group(1).lower()
            if table in _SYSTEM_CATALOGS:
                continue
            found.setdefault(table, set()).add(os.path.relpath(path, ROOT))
    return found


# `schema.sql` opens `SET search_path = grove, public` for its grove-schema
# block and creates several tables (channels, messages, ...) by their bare
# name under that search path. Every CREATE TABLE after that block uses a
# fully-qualified name (willow.routing_decisions, public.tasks, ...). So:
# any bare name schema.sql creates is a grove.* table; anything already
# qualified is taken verbatim.
_CREATE_TABLE_RE = re.compile(
    r"CREATE TABLE IF NOT EXISTS\s+([a-zA-Z_][a-zA-Z0-9_.]*)", re.IGNORECASE
)


def _schema_sql_tables() -> set[str]:
    with open(SCHEMA_SQL, encoding="utf-8") as fh:
        src = fh.read()
    tables = set()
    for name in _CREATE_TABLE_RE.findall(src):
        name = name.lower()
        tables.add(name if "." in name else f"grove.{name}")
    return tables


class SchemaCompletenessTests(unittest.TestCase):
    def test_schema_sql_exists(self) -> None:
        self.assertTrue(os.path.isfile(SCHEMA_SQL), f"missing {SCHEMA_SQL}")

    def test_every_referenced_table_exists_in_schema_sql(self) -> None:
        referenced = _referenced_tables()
        schema_tables = _schema_sql_tables()
        missing = {
            table: sorted(files)
            for table, files in referenced.items()
            if table not in schema_tables and table not in ALLOWED_SELF_CREATING
        }
        self.assertEqual(
            missing,
            {},
            "these tables are read by grove_reader.py / grove_db.py / "
            "grove_serve.py / grove/*.py but schema.sql has no "
            f"CREATE TABLE IF NOT EXISTS for them: {missing}. Add one "
            "matching the reader's actual SELECT columns, or add the "
            "table to ALLOWED_SELF_CREATING with the runtime fallback "
            "that makes schema.sql's silence safe.",
        )

    def test_the_audit_actually_finds_table_references(self) -> None:
        """Guard against a regex that silently stops matching — the
        failure mode that turns this whole file into a green no-op."""
        referenced = _referenced_tables()
        self.assertIn(
            "grove.messages",
            referenced,
            "the audit found no reference to grove.messages anywhere in "
            "the swept files — the extraction pattern has stopped "
            "matching",
        )
        self.assertIn("public.tasks", referenced)

    def test_confirmed_pr9_tables_are_covered(self) -> None:
        """Names the two tables PR 9's CI logs actually hit missing, so a
        regression on either is caught by name, not just by set-diff."""
        schema_tables = _schema_sql_tables()
        for table in ("public.routing_decisions", "public.human_required_queue"):
            self.assertIn(
                table,
                schema_tables,
                f"{table} is the exact PR-9 CI symptom "
                '(relation "..." does not exist) — schema.sql must '
                "create it",
            )


if __name__ == "__main__":
    unittest.main()
