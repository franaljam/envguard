"""Tests for envguard.differ_length."""
import pytest
from envguard.differ_length import LengthChange, LengthDiffResult, diff_lengths


def _left():
    return {"A": "hello", "B": "world", "C": "x"}


def _right():
    return {"A": "hello", "B": "longer_value", "D": "new"}


# --- LengthChange ---

def test_delta_when_both_present():
    c = LengthChange(key="K", left_length=3, right_length=7)
    assert c.delta == 4


def test_delta_none_when_left_absent():
    c = LengthChange(key="K", left_length=None, right_length=5)
    assert c.delta is None


def test_direction_added():
    c = LengthChange(key="K", left_length=None, right_length=5)
    assert c.direction == "added"


def test_direction_removed():
    c = LengthChange(key="K", left_length=5, right_length=None)
    assert c.direction == "removed"


def test_direction_grew():
    c = LengthChange(key="K", left_length=2, right_length=10)
    assert c.direction == "grew"


def test_direction_shrank():
    c = LengthChange(key="K", left_length=10, right_length=2)
    assert c.direction == "shrank"


def test_direction_unchanged():
    c = LengthChange(key="K", left_length=5, right_length=5)
    assert c.direction == "unchanged"


# --- diff_lengths ---

def test_identical_envs_no_changes():
    env = {"A": "hello", "B": "world"}
    result = diff_lengths(env, env)
    assert not result.has_changes()
    assert result.changes == []


def test_added_key_detected():
    result = diff_lengths({}, {"NEW": "value"})
    assert result.has_changes()
    assert len(result.added()) == 1
    assert result.added()[0].key == "NEW"


def test_removed_key_detected():
    result = diff_lengths({"OLD": "value"}, {})
    assert result.has_changes()
    assert len(result.removed()) == 1
    assert result.removed()[0].key == "OLD"


def test_grew_value_detected():
    result = diff_lengths({"K": "hi"}, {"K": "hello world"})
    assert len(result.grew()) == 1
    assert result.grew()[0].delta == 9


def test_shrank_value_detected():
    result = diff_lengths({"K": "hello world"}, {"K": "hi"})
    assert len(result.shrank()) == 1
    assert result.shrank()[0].delta == -9


def test_min_delta_filters_small_changes():
    result = diff_lengths({"K": "abc"}, {"K": "abcd"}, min_delta=5)
    assert not result.has_changes()


def test_min_delta_allows_large_changes():
    result = diff_lengths({"K": "hi"}, {"K": "hello world"}, min_delta=5)
    assert result.has_changes()


def test_summary_no_changes():
    env = {"A": "same"}
    result = diff_lengths(env, env)
    assert "No length changes" in result.summary()


def test_summary_with_changes():
    result = diff_lengths(_left(), _right())
    s = result.summary()
    assert "Length changes" in s


def test_keys_sorted_in_output():
    result = diff_lengths({"Z": "a", "A": "b"}, {"Z": "aaaa", "A": "bb"})
    keys = [c.key for c in result.changes]
    assert keys == sorted(keys)
