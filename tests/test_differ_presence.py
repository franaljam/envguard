"""Tests for envguard.differ_presence."""
from __future__ import annotations

import pytest

from envguard.differ_presence import PresenceChange, PresenceDiffResult, diff_presence


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _left():
    return {"A": "1", "B": "2", "C": "3"}


def _right():
    return {"B": "99", "C": "3", "D": "4"}


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_identical_envs_no_changes():
    env = {"A": "1", "B": "2"}
    result = diff_presence(env, env.copy())
    assert not result.has_changes
    assert result.left_only == []
    assert result.right_only == []
    assert sorted(result.common) == ["A", "B"]


def test_left_only_key_detected():
    result = diff_presence(_left(), _right())
    assert "A" in result.left_only
    assert "A" not in result.right_only


def test_right_only_key_detected():
    result = diff_presence(_left(), _right())
    assert "D" in result.right_only
    assert "D" not in result.left_only


def test_common_keys_listed():
    result = diff_presence(_left(), _right())
    assert "B" in result.common
    assert "C" in result.common


def test_has_changes_true_when_asymmetric():
    result = diff_presence(_left(), _right())
    assert result.has_changes is True


def test_has_changes_false_when_same_keys_different_values():
    left = {"X": "hello"}
    right = {"X": "world"}
    result = diff_presence(left, right)
    assert not result.has_changes
    assert result.common == ["X"]


def test_changes_list_contains_correct_sides():
    result = diff_presence(_left(), _right())
    sides = {c.key: c.side for c in result.changes}
    assert sides["A"] == "left_only"
    assert sides["D"] == "right_only"


def test_changes_list_sorted():
    left = {"Z": "1", "A": "2"}
    right = {"M": "3"}
    result = diff_presence(left, right)
    left_keys = [c.key for c in result.changes if c.side == "left_only"]
    assert left_keys == sorted(left_keys)


def test_summary_no_differences():
    env = {"A": "1"}
    result = diff_presence(env, env.copy())
    assert result.summary() == "No presence differences."


def test_summary_with_differences():
    result = diff_presence(_left(), _right())
    s = result.summary()
    assert "left" in s
    assert "right" in s


def test_empty_envs_no_changes():
    result = diff_presence({}, {})
    assert not result.has_changes
    assert result.common == []


def test_left_empty_all_right_only():
    right = {"A": "1", "B": "2"}
    result = diff_presence({}, right)
    assert result.right_only == ["A", "B"]
    assert result.left_only == []
