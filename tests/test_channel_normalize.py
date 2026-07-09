"""tests/test_channel_normalize.py
b17: WGRV1  ΔΣ=42

Regression cover for the shadow-channel bug: a sender writing to '#fleet'
minted a second channel instead of resolving to 'fleet', and every message
posted there was invisible to readers of the canonical name.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grove_db import (  # noqa: E402
    duplicate_channel_groups,
    find_channel_in,
    normalize_channel_name,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("fleet", "fleet"),
        ("#fleet", "fleet"),
        ("  fleet  ", "fleet"),
        (" #fleet ", "fleet"),
        ("##fleet", "fleet"),
        ("dm:hanuman", "dm:hanuman"),
        ("stupid-human-things", "stupid-human-things"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_channel_name(raw, expected):
    assert normalize_channel_name(raw) == expected


def test_normalize_preserves_interior_hash():
    assert normalize_channel_name("re#play") == "re#play"


CHANNELS = [
    {"id": 12, "name": "fleet"},
    {"id": 1, "name": "hanuman"},
    {"id": 212, "name": "dm:hanuman"},
]


@pytest.mark.parametrize("spelling", ["fleet", "#fleet", " fleet", "#fleet "])
def test_find_channel_in_folds_sender_spellings(spelling):
    """The bug: '#fleet' missed channel 12 and the caller then created a new one."""
    ch = find_channel_in(CHANNELS, spelling)
    assert ch is not None, f"{spelling!r} failed to resolve — a shadow channel would be created"
    assert ch["id"] == 12


def test_find_channel_in_misses_unknown_name():
    assert find_channel_in(CHANNELS, "nonexistent") is None


def test_find_channel_in_rejects_empty_name():
    assert find_channel_in(CHANNELS, "#") is None
    assert find_channel_in(CHANNELS, "   ") is None


def test_duplicate_channel_groups_flags_the_shadow():
    """The standing check: two rows normalizing to one name is the defect signature."""
    shadowed = CHANNELS + [{"id": 243, "name": "#fleet"}]
    dupes = duplicate_channel_groups(shadowed)
    assert set(dupes) == {"fleet"}
    assert sorted(c["id"] for c in dupes["fleet"]) == [12, 243]


def test_duplicate_channel_groups_clean_when_canonical():
    assert duplicate_channel_groups(CHANNELS) == {}
