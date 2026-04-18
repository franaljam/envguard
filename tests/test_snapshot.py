"""Tests for envguard.snapshot."""
import json
import os
import pytest

from envguard.snapshot import (
    Snapshot,
    SnapshotError,
    create_snapshot,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture
def tmp_snap(tmp_path):
    return str(tmp_path / "snap.json")


def test_create_snapshot_stores_variables():
    variables = {"DB_HOST": "localhost", "PORT": "5432"}
    snap = create_snapshot(variables, label="staging")
    assert snap.label == "staging"
    assert snap.variables == variables
    assert snap.captured_at  # non-empty timestamp


def test_create_snapshot_does_not_mutate_original():
    variables = {"KEY": "value"}
    snap = create_snapshot(variables, label="test")
    variables["EXTRA"] = "new"
    assert "EXTRA" not in snap.variables


def test_save_and_load_roundtrip(tmp_snap):
    variables = {"APP_ENV": "production", "SECRET": "abc123"}
    snap = create_snapshot(variables, label="prod")
    save_snapshot(snap, tmp_snap)

    loaded = load_snapshot(tmp_snap)
    assert loaded.label == "prod"
    assert loaded.variables == variables
    assert loaded.captured_at == snap.captured_at


def test_save_creates_valid_json(tmp_snap):
    snap = create_snapshot({"X": "1"}, label="ci")
    save_snapshot(snap, tmp_snap)
    with open(tmp_snap) as fh:
        data = json.load(fh)
    assert data["label"] == "ci"
    assert data["variables"] == {"X": "1"}


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(str(tmp_path / "missing.json"))


def test_load_invalid_json_raises(tmp_snap):
    with open(tmp_snap, "w") as fh:
        fh.write("not json{{")
    with pytest.raises(SnapshotError, match="Invalid snapshot"):
        load_snapshot(tmp_snap)


def test_load_missing_label_key_raises(tmp_snap):
    with open(tmp_snap, "w") as fh:
        json.dump({"captured_at": "2024-01-01", "variables": {}}, fh)
    with pytest.raises(SnapshotError, match="Invalid snapshot"):
        load_snapshot(tmp_snap)


def test_save_bad_path_raises():
    snap = create_snapshot({}, label="x")
    with pytest.raises(SnapshotError, match="Could not write"):
        save_snapshot(snap, "/nonexistent_dir/snap.json")
