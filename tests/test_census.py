"""Tests for envguard.census."""
import pytest
from envguard.census import census_env, CensusResult


@pytest.fixture()
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "s3cr3t",
        "FEATURE_FLAG": "true",
        "APP_DEBUG": "false",
        "API_KEY": "abc123",
        "EMPTY_VAR": "",
        "PLAIN": "hello",
        "TIMEOUT": "30",
    }


def test_returns_census_result(mixed_env):
    result = census_env(mixed_env)
    assert isinstance(result, CensusResult)


def test_total_count(mixed_env):
    result = census_env(mixed_env)
    assert result.total == len(mixed_env)


def test_empty_keys_detected(mixed_env):
    result = census_env(mixed_env)
    assert "EMPTY_VAR" in result.empty
    assert len(result.empty) == 1


def test_sensitive_keys_detected(mixed_env):
    result = census_env(mixed_env)
    assert "DB_PASSWORD" in result.sensitive
    assert "API_KEY" in result.sensitive


def test_non_sensitive_key_not_flagged(mixed_env):
    result = census_env(mixed_env)
    assert "DB_HOST" not in result.sensitive
    assert "PLAIN" not in result.sensitive


def test_boolean_keys_detected(mixed_env):
    result = census_env(mixed_env)
    assert "FEATURE_FLAG" in result.boolean
    assert "APP_DEBUG" in result.boolean


def test_numeric_keys_detected(mixed_env):
    result = census_env(mixed_env)
    assert "DB_PORT" in result.numeric
    assert "TIMEOUT" in result.numeric


def test_boolean_not_in_numeric(mixed_env):
    # "true" / "false" are booleans, not numerics
    result = census_env(mixed_env)
    assert "FEATURE_FLAG" not in result.numeric


def test_prefix_grouping(mixed_env):
    result = census_env(mixed_env)
    assert "DB" in result.by_prefix
    assert "DB_HOST" in result.by_prefix["DB"]
    assert "DB_PORT" in result.by_prefix["DB"]
    assert "DB_PASSWORD" in result.by_prefix["DB"]


def test_no_prefix_key_not_grouped():
    result = census_env({"PLAIN": "value"})
    assert "PLAIN" not in result.by_prefix


def test_empty_env():
    result = census_env({})
    assert result.total == 0
    assert result.empty == []
    assert result.sensitive == []
    assert result.boolean == []
    assert result.numeric == []
    assert result.by_prefix == {}


def test_summary_contains_total(mixed_env):
    result = census_env(mixed_env)
    summary = result.summary()
    assert "Total keys" in summary
    assert str(len(mixed_env)) in summary


def test_original_not_mutated(mixed_env):
    original = dict(mixed_env)
    census_env(mixed_env)
    assert mixed_env == original
