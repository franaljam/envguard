import json
import pytest
from envguard.freezer import freeze_env, compare_freeze, save_freeze, load_freeze, FreezeResult


ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


def test_freeze_returns_checksum_per_key():
    result = freeze_env(ENV)
    assert set(result.keys()) == set(ENV.keys())
    for v in result.values():
        assert len(v) == 64  # sha256 hex


def test_same_value_same_checksum():
    a = freeze_env({"K": "val"})
    b = freeze_env({"K": "val"})
    assert a["K"] == b["K"]


def test_different_value_different_checksum():
    a = freeze_env({"K": "val1"})
    b = freeze_env({"K": "val2"})
    assert a["K"] != b["K"]


def test_compare_identical_is_frozen():
    baseline = freeze_env(ENV)
    result = compare_freeze(ENV, baseline)
    assert result.is_frozen()
    assert result.thawed == []
    assert result.added == []
    assert result.removed == []


def test_compare_detects_changed_value():
    baseline = freeze_env(ENV)
    modified = {**ENV, "DB_HOST": "remotehost"}
    result = compare_freeze(modified, baseline)
    assert "DB_HOST" in result.thawed
    assert result.is_frozen() is False


def test_compare_detects_added_key():
    baseline = freeze_env(ENV)
    extended = {**ENV, "NEW_KEY": "newval"}
    result = compare_freeze(extended, baseline)
    assert "NEW_KEY" in result.added


def test_compare_detects_removed_key():
    baseline = freeze_env(ENV)
    reduced = {k: v for k, v in ENV.items() if k != "SECRET"}
    result = compare_freeze(reduced, baseline)
    assert "SECRET" in result.removed


def test_summary_no_drift():
    baseline = freeze_env(ENV)
    result = compare_freeze(ENV, baseline)
    assert "matches" in result.summary()


def test_summary_with_drift():
    baseline = freeze_env(ENV)
    result = compare_freeze({**ENV, "DB_HOST": "other"}, baseline)
    assert "Drift" in result.summary()
    assert "changed" in result.summary()


def test_save_and_load_roundtrip(tmp_path):
    baseline = freeze_env(ENV)
    path = str(tmp_path / "freeze.json")
    save_freeze(baseline, path)
    loaded = load_freeze(path)
    assert loaded == baseline


def test_save_creates_valid_json(tmp_path):
    baseline = freeze_env(ENV)
    path = str(tmp_path / "freeze.json")
    save_freeze(baseline, path)
    with open(path) as fh:
        data = json.load(fh)
    assert isinstance(data, dict)
