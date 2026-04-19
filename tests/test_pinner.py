"""Tests for envguard.pinner."""
import json
import pytest
from pathlib import Path
from envguard.pinner import pin_env, save_pinfile, load_pinfile, check_drift, _checksum


@pytest.fixture
def tmp_pin(tmp_path):
    return str(tmp_path / "env.lock")


ENV = {"DB_URL": "postgres://localhost/db", "SECRET": "abc123", "PORT": "5432"}


def test_pin_env_returns_checksums():
    pins = pin_env(ENV)
    assert set(pins.keys()) == set(ENV.keys())
    for k, v in ENV.items():
        assert pins[k] == _checksum(v)


def test_checksum_differs_for_different_values():
    assert _checksum("foo") != _checksum("bar")


def test_save_and_load_roundtrip(tmp_pin):
    save_pinfile(ENV, tmp_pin)
    loaded = load_pinfile(tmp_pin)
    assert loaded == pin_env(ENV)


def test_save_creates_valid_json(tmp_pin):
    save_pinfile(ENV, tmp_pin)
    data = json.loads(Path(tmp_pin).read_text())
    assert isinstance(data, dict)


def test_no_drift_when_env_unchanged(tmp_pin):
    save_pinfile(ENV, tmp_pin)
    result = check_drift(ENV, tmp_pin)
    assert not result.has_drift()
    assert result.summary() == "No drift detected."


def test_drift_detected_on_value_change(tmp_pin):
    save_pinfile(ENV, tmp_pin)
    changed = {**ENV, "SECRET": "newvalue"}
    result = check_drift(changed, tmp_pin)
    assert result.has_drift()
    assert "SECRET" in result.drifted


def test_new_key_detected(tmp_pin):
    save_pinfile(ENV, tmp_pin)
    added = {**ENV, "NEW_KEY": "hello"}
    result = check_drift(added, tmp_pin)
    assert "NEW_KEY" in result.new_keys


def test_removed_key_detected(tmp_pin):
    save_pinfile(ENV, tmp_pin)
    reduced = {k: v for k, v in ENV.items() if k != "PORT"}
    result = check_drift(reduced, tmp_pin)
    assert "PORT" in result.removed_keys


def test_summary_lists_all_drift_types(tmp_pin):
    save_pinfile(ENV, tmp_pin)
    env2 = {"DB_URL": "changed", "NEW_KEY": "x"}
    result = check_drift(env2, tmp_pin)
    summary = result.summary()
    assert "Drifted" in summary
    assert "New" in summary
    assert "Removed" in summary
