# b17: WGRV1 ΔΣ=42
"""Tests for grove.envelope_reader — P1 live source + D7 degradation.

stdlib unittest only; a tmp WILLOW_HOME + isolated fake HOME per test
so the real fleet directories under ~/willow-memory and ~/.willow can
never accidentally satisfy a probe.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from grove import envelope_reader as er
from grove.errors import Unreachable


def _envelope(env_id: str, **overrides) -> dict:
    """One minimally-shaped envelope for the fixtures below."""
    payload = {
        "id": env_id,
        "grantee": "kart",
        "kind": "filesystem",
        "mode": "read",
        "attestation": "attested",
    }
    payload.update(overrides)
    return payload


class EnvelopeReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)

        # Isolate HOME so ~/willow-memory/Willow/envelopes and ~/.willow/envelopes
        # never resolve to anything the host machine owns.
        self.fake_home = root / "no-home"
        self.fake_home.mkdir()

        # $WILLOW_HOME/envelopes lives here when a test wants it populated.
        self.willow_home = root / "willow_home"

        # Reset module-level log-once state before every test.
        er._logged_missing_dirs = False
        er._logged_missing_files = False
        er._logged_malformed = set()

    def _env(self, willow_home: str | None = None):
        env = {"HOME": str(self.fake_home)}
        if willow_home is not None:
            env["WILLOW_HOME"] = willow_home
        else:
            # Strip a real WILLOW_HOME the host may carry so the probe
            # only sees what the test set up.
            env["WILLOW_HOME"] = str(self.fake_home / "unset")
        return mock.patch.dict(os.environ, env, clear=False)

    # ---- three-state: unreachable (INVARIANTS.md §1) ----
    def test_no_dirs_raises_unreachable_and_logs_once(self) -> None:
        """No envelope directory in the probe path → raise Unreachable.
        Absence is a state, and it must render distinctly (INVARIANTS.md §1
        supersedes the earlier "empty on absence" reading)."""
        with self._env():
            with self.assertLogs(er.log, level="INFO") as caplog:
                with self.assertRaises(Unreachable) as ctx1:
                    er.read_all()
                with self.assertRaises(Unreachable) as ctx2:
                    er.read_all()

        self.assertIn("envelope directory", ctx1.exception.reason)
        self.assertIn("envelope directory", ctx2.exception.reason)

        missing_dir_logs = [
            r for r in caplog.records if "no envelope directory" in r.getMessage()
        ]
        self.assertEqual(
            len(missing_dir_logs),
            1,
            "missing-dir log must fire exactly once, not per call",
        )

    # ---- three-state: empty (reached, no data) ----
    def test_dir_present_but_no_files_returns_empty_envelope_list(self) -> None:
        """Directory exists but holds no usable json → empty list (reached).
        This is the "empty" three-state case, distinct from unreachable."""
        env_dir = self.willow_home / "envelopes"
        env_dir.mkdir(parents=True)
        with self._env(willow_home=str(self.willow_home)):
            result = er.read_all()
        self.assertEqual(result["schema"], er.SCHEMA_ID)
        self.assertEqual(result["envelopes"], [])

    # ---- normal path: two files in one dir ----
    def test_two_files_in_one_dir_merge(self) -> None:
        env_dir = self.willow_home / "envelopes"
        env_dir.mkdir(parents=True)
        (env_dir / "a.json").write_text(
            json.dumps({"schema": er.SCHEMA_ID, "envelopes": [_envelope("env-a")]}),
            encoding="utf-8",
        )
        (env_dir / "b.json").write_text(
            json.dumps({"schema": er.SCHEMA_ID, "envelopes": [_envelope("env-b")]}),
            encoding="utf-8",
        )

        with self._env(willow_home=str(self.willow_home)):
            result = er.read_all()

        self.assertEqual(result["schema"], er.SCHEMA_ID)
        ids = sorted(e["id"] for e in result["envelopes"])
        self.assertEqual(ids, ["env-a", "env-b"])

    def test_pre_approved_key_shape_is_read(self) -> None:
        """The charter file uses ``pre_approved`` — reader must find it."""
        env_dir = self.willow_home / "envelopes"
        env_dir.mkdir(parents=True)
        (env_dir / "pre-approved.json").write_text(
            json.dumps(
                {
                    "schema": er.SCHEMA_ID,
                    "pre_approved": [_envelope("charter-1"), _envelope("charter-2")],
                }
            ),
            encoding="utf-8",
        )

        with self._env(willow_home=str(self.willow_home)):
            result = er.read_all()

        ids = sorted(e["id"] for e in result["envelopes"])
        self.assertEqual(ids, ["charter-1", "charter-2"])

    # ---- malformed file discipline ----
    def test_malformed_file_is_skipped_and_logged_once(self) -> None:
        env_dir = self.willow_home / "envelopes"
        env_dir.mkdir(parents=True)
        good = env_dir / "good.json"
        good.write_text(
            json.dumps({"schema": er.SCHEMA_ID, "envelopes": [_envelope("good-1")]}),
            encoding="utf-8",
        )
        bad = env_dir / "bad.json"
        bad.write_text("{ not json", encoding="utf-8")

        with self._env(willow_home=str(self.willow_home)):
            with self.assertLogs(er.log, level="INFO") as caplog:
                result = er.read_all()
                # Second call re-reads the same bad file — must not log again.
                er.read_all()

        self.assertEqual([e["id"] for e in result["envelopes"]], ["good-1"])
        skip_logs = [
            r for r in caplog.records
            if "skipping malformed" in r.getMessage() and "bad.json" in r.getMessage()
        ]
        self.assertEqual(
            len(skip_logs),
            1,
            "malformed-file log must fire exactly once per path, not per call",
        )

    # ---- precedence: later dir wins on id collision ----
    def test_later_dir_overrides_earlier_on_id_collision(self) -> None:
        # $WILLOW_HOME/envelopes is candidate index 0; ~/.willow/envelopes is index 2.
        # Precedence rule: later probe order wins on collision, so the ~/.willow
        # payload should replace the $WILLOW_HOME one.
        wh_dir = self.willow_home / "envelopes"
        wh_dir.mkdir(parents=True)
        (wh_dir / "src.json").write_text(
            json.dumps(
                {
                    "schema": er.SCHEMA_ID,
                    "envelopes": [_envelope("shared", grantee="from-willow-home")],
                }
            ),
            encoding="utf-8",
        )

        dot_dir = self.fake_home / ".willow" / "envelopes"
        dot_dir.mkdir(parents=True)
        (dot_dir / "src.json").write_text(
            json.dumps(
                {
                    "schema": er.SCHEMA_ID,
                    "envelopes": [_envelope("shared", grantee="from-dot-willow")],
                }
            ),
            encoding="utf-8",
        )

        with self._env(willow_home=str(self.willow_home)):
            result = er.read_all()

        self.assertEqual(len(result["envelopes"]), 1)
        self.assertEqual(result["envelopes"][0]["grantee"], "from-dot-willow")

    # ---- new probe: $WILLOW_HOME/willow-memory/willow/envelopes/ ----
    def test_willow_home_charter_probe_path(self) -> None:
        """The reader honors ``$WILLOW_HOME/willow-memory/willow/envelopes/``
        — the charter mirror the operator actually keeps envelopes under
        (Bug 2 — standup finding: pre-approved.json + syscall-table.json
        went unread because the reader only knew ``$WILLOW_HOME/envelopes``
        and ``~/willow-memory/Willow/...``, not the lowercase charter hop)."""
        env_dir = self.willow_home / "willow-memory" / "willow" / "envelopes"
        env_dir.mkdir(parents=True)
        (env_dir / "pre-approved.json").write_text(
            json.dumps(
                {
                    "schema": er.SCHEMA_ID,
                    "pre_approved": [_envelope("charter-fs-read")],
                }
            ),
            encoding="utf-8",
        )
        (env_dir / "syscall-table.json").write_text(
            json.dumps(
                {"schema": er.SCHEMA_ID, "envelopes": [_envelope("syscall-exec")]}
            ),
            encoding="utf-8",
        )

        with self._env(willow_home=str(self.willow_home)):
            result = er.read_all()

        ids = sorted(e["id"] for e in result["envelopes"])
        self.assertEqual(ids, ["charter-fs-read", "syscall-exec"])

    # ---- locator ----
    def test_locate_envelope_dirs_only_returns_existing(self) -> None:
        wh_dir = self.willow_home / "envelopes"
        wh_dir.mkdir(parents=True)
        # ~/willow-memory/Willow/envelopes and ~/.willow/envelopes deliberately absent.

        with self._env(willow_home=str(self.willow_home)):
            dirs = er.locate_envelope_dirs()

        self.assertEqual(dirs, [wh_dir])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
