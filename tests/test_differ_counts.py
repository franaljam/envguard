"""Tests for envguard.differ_counts."""
import pytest
from envguard.differ_counts import diff_counts


def _left():
    return {"A": "1", "B": "2", "C": "3"}


def _right():
    return {"A": "1", "B": "2", "D": "4"}


def test_identical_envs_no_changes():
    env = {"X": "1", "Y": "2"}
    result = diff_counts(env, env)
    assert not result.has_changes()
    assert result.added == 0
    assert result.removed == 0
    assert result.delta() == 0


def test_added_key_detected():
    left = {"A": "1"}
    right = {"A": "1", "B": "2"}
    result = diff_counts(left, right)
    assert result.has_changes()
    assert result.added == 1
    assert result.removed == 0
    assert "B" in result.right_only


def test_removed_key_detected():
    left = {"A": "1", "B": "2"}
    right = {"A": "1"}
    result = diff_counts(left, right)
    assert result.has_changes()
    assert result.removed == 1
    assert result.added == 0
    assert "B" in result.left_only


def test_common_keys_counted():
    result = diff_counts(_left(), _right())
    assert result.common == 2
    assert "A" in result.shared
    assert "B" in result.shared


def test_left_count_and_right_count():
    left = {"A": "1", "B": "2", "C": "3"}
    right = {"A": "1", "B": "2"}
    result = diff_counts(left, right)
    assert result.left_count == 3
    assert result.right_count == 2


def test_delta_positive_when_right_has_more():
    left = {"A": "1"}
    right = {"A": "1", "B": "2", "C": "3"}
    result = diff_counts(left, right)
    assert result.delta() == 2


def test_delta_negative_when_left_has_more():
    left = {"A": "1", "B": "2", "C": "3"}
    right = {"A": "1"}
    result = diff_counts(left, right)
    assert result.delta() == -2


def test_summary_no_changes():
    env = {"X": "1"}
    result = diff_counts(env, env)
    assert "No count changes" in result.summary()
    assert "1" in result.summary()


def test_summary_with_changes():
    left = {"A": "1", "B": "2"}
    right = {"A": "1", "C": "3", "D": "4"}
    result = diff_counts(left, right)
    summary = result.summary()
    assert "+1 added" in summary
    assert "-1 removed" in summary


def test_empty_envs():
    result = diff_counts({}, {})
    assert not result.has_changes()
    assert result.left_count == 0
    assert result.right_count == 0
    assert result.delta() == 0


def test_value_changes_do_not_affect_count():
    left = {"A": "1", "B": "old"}
    right = {"A": "1", "B": "new"}
    result = diff_counts(left, right)
    assert not result.has_changes()
    assert result.common == 2
