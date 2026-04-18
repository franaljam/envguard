import pytest
from envguard.profiler import profile_env, ProfileResult


def test_empty_dict():
    result = profile_env({})
    assert result.total == 0
    assert result.empty == 0
    assert result.sensitive_keys == []


def test_total_count():
    result = profile_env({"A": "1", "B": "2", "C": "3"})
    assert result.total == 3


def test_empty_values_counted():
    result = profile_env({"A": "", "B": "val", "C": ""})
    assert result.empty == 2


def test_sensitive_keys_detected():
    env = {"DB_PASSWORD": "secret", "API_KEY": "abc", "HOST": "localhost"}
    result = profile_env(env)
    assert "DB_PASSWORD" in result.sensitive_keys
    assert "API_KEY" in result.sensitive_keys
    assert "HOST" not in result.sensitive_keys


def test_longest_key():
    env = {"SHORT": "a", "MUCH_LONGER_KEY": "b"}
    result = profile_env(env)
    assert result.longest_key == "MUCH_LONGER_KEY"


def test_longest_value_key():
    env = {"A": "short", "B": "a much longer value here"}
    result = profile_env(env)
    assert result.longest_value_key == "B"


def test_duplicate_values_detected():
    env = {"A": "same", "B": "same", "C": "different"}
    result = profile_env(env)
    assert "same" in result.duplicate_values
    assert set(result.duplicate_values["same"]) == {"A", "B"}


def test_no_duplicates_when_unique():
    env = {"A": "x", "B": "y", "C": "z"}
    result = profile_env(env)
    assert result.duplicate_values == {}


def test_summary_contains_total():
    env = {"FOO": "bar", "BAZ": ""}
    result = profile_env(env)
    summary = result.summary()
    assert "2" in summary
    assert "Empty" in summary


def test_summary_shows_duplicates():
    env = {"A": "dup", "B": "dup"}
    result = profile_env(env)
    assert "dup" in result.summary()
