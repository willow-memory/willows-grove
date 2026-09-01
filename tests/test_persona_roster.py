# b17: WGRV1 ΔΣ=42
"""Tests for grove.persona_roster — D10 consumer + D7 degradation.

stdlib unittest only; a minimal fleet-personas/v1 fixture is written
into a tmp WILLOW_HOME per test.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from grove import persona_roster as pr
from grove.errors import Unreachable


def _fixture_bytes(rows=None) -> str:
    return json.dumps(
        {
            "schema": "fleet-personas/v1",
            "agents": rows
            if rows is not None
            else [
                {
                    "agent": "willow",
                    "role": "primary",
                    "trust": "flagship",
                    "voice": {"register": "warm", "mandate": "the seat"},
                    "visual": {
                        "color": "#8FBC8F",
                        "sigil": "\U0001F333",
                        "color_token": "willow.green",
                    },
                    "canonical_file": "willow-memory/willow/personas/willow.md",
                    "emission_fields": ["utterance", "state"],
                },
                {
                    "agent": "loki",
                    "role": "scout",
                    "trust": "utility",
                    "voice": {"register": "sharp"},
                    "visual": {"color": "#7C1F3F", "sigil": "\U0001F98A"},
                    "canonical_file": "personas/loki.md",
                    "emission_fields": ["utterance"],
                },
                {
                    "agent": "nestor",
                    "role": "governance",
                    "trust": "governance",
                    "voice": {"register": "measured"},
                    "visual": {"color": "#4A5568", "sigil": "⚖"},
                    "canonical_file": "Nestor/personas/nestor.md",
                    "emission_fields": ["speech_act", "refusal"],
                },
            ],
        }
    )


class PersonaRosterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.willow_home = Path(self.tmp.name) / "willow_home"
        self.willow_home.mkdir()
        target = self.willow_home / "fleet_personas.json"
        target.write_text(_fixture_bytes(), encoding="utf-8")
        self.registry_path = target

        # Isolate HOME so no host-level candidate can accidentally match.
        self.fake_home = Path(self.tmp.name) / "no-home"
        self.fake_home.mkdir()

        # Point the in-repo fallback at an empty tmp dir by default, so
        # these tests exercise only the $WILLOW_HOME override and stay
        # isolated from this repo's real governance/fleet_personas.json.
        # Tests that specifically want the fallback path patch this
        # attribute themselves.
        self._no_fallback_dir = Path(self.tmp.name) / "no-fallback"
        self._no_fallback_dir.mkdir()
        self._fallback_patch = mock.patch.object(
            pr, "_IN_REPO_PERSONAS_PATH", self._no_fallback_dir / "fleet_personas.json"
        )
        self._fallback_patch.start()
        self.addCleanup(self._fallback_patch.stop)

        # Reset the log-once flag before every test.
        pr._logged_missing = False

    def _env(self, willow_home: str | None = None):
        env = dict(os.environ)
        env["HOME"] = str(self.fake_home)
        if willow_home is not None:
            env["WILLOW_HOME"] = willow_home
        else:
            # Ensure any stale WILLOW_HOME from the host does not leak in.
            env.pop("WILLOW_HOME", None)
        return mock.patch.dict(os.environ, env, clear=True)

    # ---- locate ----
    def test_locate_prefers_willow_home(self) -> None:
        with self._env(willow_home=str(self.willow_home)):
            found = pr.locate_personas_file()
        self.assertEqual(found, self.registry_path)

    # ---- load + read helpers ----
    def test_get_returns_willow_row_with_attribute_access(self) -> None:
        with self._env(willow_home=str(self.willow_home)):
            roster = pr.PersonaRoster.load()
        self.assertIsNotNone(roster)
        assert roster is not None  # for the type checker

        row = roster.get("willow")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row.role, "primary")
        self.assertEqual(row.trust, "flagship")
        self.assertEqual(row.voice["register"], "warm")
        self.assertEqual(row.visual["color_token"], "willow.green")
        self.assertEqual(row.canonical_file, "willow-memory/willow/personas/willow.md")
        self.assertIn("utterance", row.emission_fields)

    def test_by_role_returns_just_the_primary(self) -> None:
        with self._env(willow_home=str(self.willow_home)):
            roster = pr.PersonaRoster.load()
        assert roster is not None
        primaries = roster.by_role("primary")
        self.assertEqual(len(primaries), 1)
        self.assertEqual(primaries[0].get("agent"), "willow")

    def test_all_preserves_fleet_order(self) -> None:
        with self._env(willow_home=str(self.willow_home)):
            roster = pr.PersonaRoster.load()
        assert roster is not None
        self.assertEqual(
            [r.get("agent") for r in roster.all()],
            ["willow", "loki", "nestor"],
        )

    def test_get_returns_none_for_unknown_agent(self) -> None:
        with self._env(willow_home=str(self.willow_home)):
            roster = pr.PersonaRoster.load()
        assert roster is not None
        self.assertIsNone(roster.get("no-such-agent"))

    # ---- charter (on-disk) shape: _meta.schema + agents at top level ----
    def test_charter_shape_loads(self) -> None:
        """The real fleet_personas.json layout: schema nested under _meta,
        every non-_meta top-level key is an agent row. Grove must load it
        the same as the flat wrapper (Bug 1 — standup finding: 17 personas
        sat on disk, /api/personas returned empty envelope until the reader
        learned this shape)."""
        charter_home = Path(self.tmp.name) / "charter_willow_home"
        charter_home.mkdir()
        target = charter_home / "fleet_personas.json"
        target.write_text(
            json.dumps(
                {
                    "_meta": {
                        "schema": "fleet-personas/v1",
                        "generated_at": "2026-08-27T00:00:00Z",
                    },
                    "willow": {
                        "trust": "flagship",
                        "role": "primary",
                        "voice": {"register": "warm"},
                        "visual": {"color": "#8FBC8F", "sigil": "\U0001F333"},
                    },
                    "heimdallr": {
                        "trust": "watch",
                        "role": "bridge",
                        "voice": {"register": "measured"},
                        "visual": {"color": "#B6A87A", "sigil": "⚡"},
                    },
                    "hanuman": {
                        "trust": "utility",
                        "role": "builder",
                        "voice": {"register": "eager"},
                        "visual": {"color": "#D97706", "sigil": "\U0001F412"},
                    },
                }
            ),
            encoding="utf-8",
        )

        with self._env(willow_home=str(charter_home)):
            roster = pr.PersonaRoster.load()
        self.assertIsNotNone(roster)
        assert roster is not None

        # All three agents are present, in file order.
        self.assertEqual(
            [r.get("agent") for r in roster.all()],
            ["willow", "heimdallr", "hanuman"],
        )

        # get() lands regardless of whether the row carried an "agent" field
        # itself — the reader injects the top-level key.
        willow = roster.get("willow")
        self.assertIsNotNone(willow)
        assert willow is not None
        self.assertEqual(willow.trust, "flagship")
        self.assertEqual(willow.role, "primary")
        self.assertEqual(willow.visual["sigil"], "\U0001F333")
        self.assertEqual(willow.voice["register"], "warm")

        heim = roster.get("heimdallr")
        self.assertIsNotNone(heim)
        assert heim is not None
        self.assertEqual(heim.role, "bridge")

    def test_flat_personas_dict_shape_loads(self) -> None:
        """The flat wrapper with a ``personas`` dict payload keeps working
        alongside the ``agents`` list shape — the reader accepts both."""
        flat_home = Path(self.tmp.name) / "flat_willow_home"
        flat_home.mkdir()
        target = flat_home / "fleet_personas.json"
        target.write_text(
            json.dumps(
                {
                    "schema": "fleet-personas/v1",
                    "personas": {
                        "willow": {"trust": "flagship", "role": "primary"},
                        "loki": {"trust": "utility", "role": "scout"},
                    },
                }
            ),
            encoding="utf-8",
        )
        with self._env(willow_home=str(flat_home)):
            roster = pr.PersonaRoster.load()
        assert roster is not None
        self.assertEqual(
            sorted(r.get("agent") for r in roster.all()),
            ["loki", "willow"],
        )
        willow = roster.get("willow")
        assert willow is not None
        self.assertEqual(willow.trust, "flagship")

    # ---- schema guard ----
    def test_wrong_schema_id_raises_value_error(self) -> None:
        bad = Path(self.tmp.name) / "bad.json"
        bad.write_text(
            json.dumps({"schema": "fleet-personas/v2", "agents": []}),
            encoding="utf-8",
        )
        with self.assertRaises(ValueError) as ctx:
            pr.PersonaRoster(path=str(bad))
        self.assertIn("fleet-personas/v1", str(ctx.exception))

    # ---- three-state: unreachable case (INVARIANTS.md §1) ----
    def test_missing_file_raises_unreachable_and_logs_once(self) -> None:
        """Absence is a state, and it must render distinctly (INVARIANTS.md §1
        supersedes D7's implicit read). ``load()`` raises ``Unreachable``
        instead of returning ``None`` — the endpoint layer translates that
        into a 503 with ``state="unreachable"``."""
        empty_home = Path(self.tmp.name) / "empty_willow_home"
        empty_home.mkdir()
        with self._env(willow_home=str(empty_home)):
            with self.assertLogs(pr.log, level="INFO") as caplog:
                with self.assertRaises(Unreachable) as ctx1:
                    pr.PersonaRoster.load()
                with self.assertRaises(Unreachable) as ctx2:
                    pr.PersonaRoster.load()
                self.assertIsNone(pr.locate_personas_file())

        # Reason names the probe list so the operator can see what was tried.
        self.assertIn("fleet_personas.json", ctx1.exception.reason)
        self.assertIn("fleet_personas.json", ctx2.exception.reason)

        missing_msgs = [
            r for r in caplog.records if "not found" in r.getMessage()
        ]
        self.assertEqual(
            len(missing_msgs),
            1,
            "missing-source log must fire exactly once, not per call",
        )

    # ---- three-state: empty case (INVARIANTS.md §1) ----
    def test_empty_registry_loads_as_empty_roster(self) -> None:
        """File present, ``agents: []`` — populated=False, roster returned.
        This is the "empty" three-state case (reached, no data)."""
        empty_home = Path(self.tmp.name) / "empty_registry_home"
        empty_home.mkdir()
        target = empty_home / "fleet_personas.json"
        target.write_text(
            json.dumps({"schema": "fleet-personas/v1", "agents": []}),
            encoding="utf-8",
        )
        with self._env(willow_home=str(empty_home)):
            roster = pr.PersonaRoster.load()
        self.assertEqual(roster.all(), [])
        self.assertIsNone(roster.get("willow"))

    # ---- three-state: in-repo fallback (cold box, no $WILLOW_HOME) ----
    def test_falls_back_to_in_repo_copy_when_no_willow_home_override(self) -> None:
        """No ``$WILLOW_HOME`` override present — the in-repo copy at
        ``governance/fleet_personas.json`` is the reliable fallback so
        Grove always has a registry on a cold box."""
        fallback_dir = Path(self.tmp.name) / "in_repo_fallback"
        fallback_dir.mkdir()
        fallback_path = fallback_dir / "fleet_personas.json"
        fallback_path.write_text(_fixture_bytes(), encoding="utf-8")

        with mock.patch.object(pr, "_IN_REPO_PERSONAS_PATH", fallback_path):
            with self._env():
                roster = pr.PersonaRoster.load()

        self.assertEqual(roster.path, fallback_path)
        willow = roster.get("willow")
        self.assertIsNotNone(willow)
        assert willow is not None
        self.assertEqual(willow.role, "primary")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
