"""Tests for envguard.differ_stats."""
import pytest

from envguard.differ_stats import diff_stats, StatEntry, StatResult


def _left():
    return {"A": "hello", "B": "world", "C": "same"}


def _right():
    return {"A": "hi", "C": "same", "D": "new"}


def test_identical_envs_no_changes():
    env = {"A": "1", "B": "2"}
    result = diff_stats(env, env.copy())
    assert not result.has_changes
    assert result.unchanged == ["A", "B"]


def test_added_key_detected():
    result = diff_stats({}, {"NEW": "val"})
    assert "NEW" in result.added
    assert result.has_changes


def test_removed_key_detected():
    result = diff_stats({"OLD": "val"}, {})
    assert "OLD" in result.removed
    assert result.has_changes


def test_changed_value_detected():
    result = diff_stats({"A": "hello"}, {"A": "hi"})
    assert len(result.changed) == 1
    entry = result.changed[0]
    assert entry.key == "A"
    assert entry.left_len == 5
    assert entry.right_len == 2
    assert entry.delta == -3


def test_unchanged_key_listed():
    result = diff_stats({"X": "same"}, {"X": "same"})
    assert "X" in result.unchanged
    assert not result.has_changes


def test_mixed_diff():
    result = diff_stats(_left(), _right())
    assert "B" in result.removed
    assert "D" in result.added
    assert any(e.key == "A" for e in result.changed)
    assert "C" in result.unchanged


def test_total_keys_counts_all():
    result = diff_stats(_left(), _right())
    assert result.total_keys == len(set(_left()) | set(_right()))


def test_summary_no_changes():
    env = {"A": "1"}
    result = diff_stats(env, env.copy())
    assert result.summary() == "no changes"


def test_summary_with_changes():
    result = diff_stats(_left(), _right())
    s = result.summary()
    assert "+" in s
    assert "-" in s
    assert "~" in s


def test_keys_sorted_alphabetically():
    result = diff_stats({"Z": "1", "A": "1"}, {"Z": "1", "A": "1"})
    assert result.unchanged == ["A", "Z"]
