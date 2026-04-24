"""Tests for envguard.differ_values."""
import pytest

from envguard.differ_values import ValueChange, ValueDiffResult, diff_values


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _left():
    return {"A": "1", "B": "2", "C": "3"}


def _right():
    return {"A": "1", "B": "99", "D": "4"}


# ---------------------------------------------------------------------------
# basic detection
# ---------------------------------------------------------------------------

def test_identical_envs_no_changes():
    env = {"X": "hello", "Y": "world"}
    result = diff_values(env, dict(env))
    assert not result.has_changes()
    assert result.changes == []


def test_added_key_detected():
    result = diff_values({}, {"NEW": "val"})
    assert result.has_changes()
    assert len(result.added()) == 1
    assert result.added()[0].key == "NEW"
    assert result.added()[0].old is None
    assert result.added()[0].new == "val"


def test_removed_key_detected():
    result = diff_values({"OLD": "val"}, {})
    assert result.has_changes()
    assert len(result.removed()) == 1
    assert result.removed()[0].key == "OLD"
    assert result.removed()[0].new is None


def test_changed_value_detected():
    result = diff_values({"K": "old"}, {"K": "new"})
    assert result.has_changes()
    assert len(result.modified()) == 1
    c = result.modified()[0]
    assert c.key == "K"
    assert c.old == "old"
    assert c.new == "new"
    assert c.kind == "changed"


def test_combined_diff():
    result = diff_values(_left(), _right())
    assert result.has_changes()
    assert len(result.added()) == 1    # D
    assert len(result.removed()) == 1  # C
    assert len(result.modified()) == 1 # B


# ---------------------------------------------------------------------------
# ignore_keys
# ---------------------------------------------------------------------------

def test_ignore_keys_skips_entry():
    result = diff_values({"A": "1", "B": "2"}, {"A": "1", "B": "99"}, ignore_keys=["B"])
    assert not result.has_changes()


def test_ignore_keys_partial():
    result = diff_values({"A": "1", "B": "2"}, {"A": "X", "B": "99"}, ignore_keys=["B"])
    assert result.has_changes()
    assert len(result.modified()) == 1
    assert result.modified()[0].key == "A"


# ---------------------------------------------------------------------------
# case_insensitive
# ---------------------------------------------------------------------------

def test_case_insensitive_treats_as_equal():
    result = diff_values({"K": "True"}, {"K": "true"}, case_insensitive=True)
    assert not result.has_changes()


def test_case_sensitive_by_default():
    result = diff_values({"K": "True"}, {"K": "true"})
    assert result.has_changes()


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_no_changes():
    result = diff_values({"A": "1"}, {"A": "1"})
    assert "No value differences" in result.summary()


def test_summary_with_changes():
    result = diff_values(_left(), _right())
    s = result.summary()
    assert "added" in s
    assert "removed" in s
    assert "changed" in s
