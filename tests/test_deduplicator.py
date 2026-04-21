"""Tests for envguard.deduplicator."""
import pytest
from envguard.deduplicator import deduplicate_env, DeduplicateResult


def test_no_duplicates_returns_copy():
    env = {"A": "1", "B": "2", "C": "3"}
    result = deduplicate_env(env)
    assert result.env == env
    assert result.env is not env


def test_original_not_mutated():
    env = {"A": "x", "B": "x"}
    original = dict(env)
    deduplicate_env(env)
    assert env == original


def test_no_duplicates_no_change():
    env = {"A": "1", "B": "2"}
    result = deduplicate_env(env)
    assert not result.changed()
    assert result.removed_keys == []


def test_duplicate_value_removes_second_keep_first():
    env = {"A": "same", "B": "same"}
    result = deduplicate_env(env, keep="first")
    assert "A" in result.env
    assert "B" not in result.env
    assert result.removed_keys == ["B"]


def test_duplicate_value_removes_first_keep_last():
    env = {"A": "same", "B": "same"}
    result = deduplicate_env(env, keep="last")
    assert "B" in result.env
    assert "A" not in result.env
    assert result.removed_keys == ["A"]


def test_three_duplicates_keep_first():
    env = {"A": "v", "B": "v", "C": "v"}
    result = deduplicate_env(env, keep="first")
    assert result.env == {"A": "v"}
    assert set(result.removed_keys) == {"B", "C"}


def test_three_duplicates_keep_last():
    env = {"A": "v", "B": "v", "C": "v"}
    result = deduplicate_env(env, keep="last")
    assert result.env == {"C": "v"}
    assert set(result.removed_keys) == {"A", "B"}


def test_empty_values_ignored_by_default():
    env = {"A": "", "B": "", "C": "real"}
    result = deduplicate_env(env, ignore_empty=True)
    # Both empty keys should survive because empty values are not considered duplicates
    assert "A" in result.env
    assert "B" in result.env
    assert not result.changed()


def test_empty_values_deduplicated_when_flag_false():
    env = {"A": "", "B": "", "C": "real"}
    result = deduplicate_env(env, ignore_empty=False, keep="first")
    assert "A" in result.env
    assert "B" not in result.env
    assert result.changed()


def test_value_map_populated():
    env = {"X": "dup", "Y": "dup", "Z": "unique"}
    result = deduplicate_env(env)
    assert "dup" in result.value_map
    assert set(result.value_map["dup"]) == {"X", "Y"}
    assert "unique" not in result.value_map


def test_summary_no_changes():
    env = {"A": "1"}
    result = deduplicate_env(env)
    assert "No duplicate" in result.summary()


def test_summary_with_changes():
    env = {"A": "same", "B": "same"}
    result = deduplicate_env(env)
    summary = result.summary()
    assert "Removed" in summary
    assert "B" in summary


def test_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        deduplicate_env({"A": "1"}, keep="middle")
