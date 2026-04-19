"""Tests for envguard.comparator."""
import pytest
from envguard.comparator import compare_envs, CompareResult


def test_identical_envs_are_equal():
    env = {"A": "1", "B": "2"}
    result = compare_envs(env, env.copy())
    assert result.is_equal()
    assert result.summary() == "Environments are identical."


def test_changed_value_detected():
    result = compare_envs({"A": "old"}, {"A": "new"})
    assert len(result.changed()) == 1
    assert result.changed()[0].key == "A"
    assert result.changed()[0].left == "old"
    assert result.changed()[0].right == "new"


def test_left_only_key():
    result = compare_envs({"A": "1", "B": "2"}, {"A": "1"})
    assert len(result.left_only()) == 1
    assert result.left_only()[0].key == "B"


def test_right_only_key():
    result = compare_envs({"A": "1"}, {"A": "1", "C": "3"})
    assert len(result.right_only()) == 1
    assert result.right_only()[0].key == "C"


def test_ignore_values_treats_changed_as_match():
    result = compare_envs({"A": "old"}, {"A": "new"}, ignore_values=True)
    assert result.is_equal()
    assert len(result.matches()) == 1


def test_summary_multiple_differences():
    result = compare_envs({"A": "1", "B": "old"}, {"B": "new", "C": "3"})
    s = result.summary()
    assert "changed" in s
    assert "left-only" in s
    assert "right-only" in s


def test_keys_sorted_in_output():
    result = compare_envs({"Z": "1", "A": "1"}, {"Z": "1", "A": "1"})
    keys = [c.key for c in result.comparisons]
    assert keys == sorted(keys)


def test_empty_envs_are_equal():
    result = compare_envs({}, {})
    assert result.is_equal()
