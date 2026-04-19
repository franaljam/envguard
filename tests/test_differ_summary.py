"""Tests for envguard.differ_summary."""
import pytest

from envguard.snapshot import Snapshot
from envguard.differ_summary import diff_snapshots, SnapshotDiff, ChangeEntry


def _snap(label: str, variables: dict) -> Snapshot:
    return Snapshot(label=label, variables=variables, created_at="2024-01-01T00:00:00")


def test_no_changes_when_identical():
    base = _snap("base", {"A": "1", "B": "2"})
    head = _snap("head", {"A": "1", "B": "2"})
    result = diff_snapshots(base, head)
    assert not result.has_changes
    assert result.changes == []


def test_added_key_detected():
    base = _snap("base", {"A": "1"})
    head = _snap("head", {"A": "1", "B": "2"})
    result = diff_snapshots(base, head)
    assert len(result.added) == 1
    assert result.added[0].key == "B"
    assert result.added[0].new_value == "2"
    assert result.added[0].old_value is None


def test_removed_key_detected():
    base = _snap("base", {"A": "1", "B": "2"})
    head = _snap("head", {"A": "1"})
    result = diff_snapshots(base, head)
    assert len(result.removed) == 1
    assert result.removed[0].key == "B"
    assert result.removed[0].old_value == "2"


def test_modified_key_detected():
    base = _snap("base", {"A": "old"})
    head = _snap("head", {"A": "new"})
    result = diff_snapshots(base, head)
    assert len(result.modified) == 1
    entry = result.modified[0]
    assert entry.key == "A"
    assert entry.old_value == "old"
    assert entry.new_value == "new"


def test_ignore_values_skips_modified():
    base = _snap("base", {"A": "old"})
    head = _snap("head", {"A": "new"})
    result = diff_snapshots(base, head, ignore_values=True)
    assert not result.has_changes


def test_labels_preserved():
    base = _snap("staging", {})
    head = _snap("production", {})
    result = diff_snapshots(base, head)
    assert result.base_label == "staging"
    assert result.head_label == "production"


def test_changes_sorted_by_key():
    base = _snap("base", {"Z": "1", "A": "1"})
    head = _snap("head", {"Z": "2", "A": "2"})
    result = diff_snapshots(base, head)
    keys = [c.key for c in result.changes]
    assert keys == sorted(keys)


def test_multiple_change_types_together():
    base = _snap("base", {"KEEP": "v", "REMOVE": "r", "CHANGE": "old"})
    head = _snap("head", {"KEEP": "v", "ADD": "a", "CHANGE": "new"})
    result = diff_snapshots(base, head)
    assert len(result.added) == 1
    assert len(result.removed) == 1
    assert len(result.modified) == 1
    assert result.has_changes
