"""Tests for envguard.inspector."""
import pytest
from envguard.inspector import inspect_env, InspectResult, KeyInfo


@pytest.fixture()
def sample_env():
    return {
        "DB_PASSWORD": "s3cr3t",
        "APP_NAME": "myapp",
        "PORT": "8080",
        "DEBUG": "true",
        "EMPTY_VAR": "",
        "SPACED_VAL": "  hello  ",
        "API_KEY": "abc123",
        "FLOAT_VAL": "3.14",
    }


def test_returns_inspect_result(sample_env):
    result = inspect_env(sample_env)
    assert isinstance(result, InspectResult)


def test_entry_count_matches_env(sample_env):
    result = inspect_env(sample_env)
    assert len(result.entries) == len(sample_env)


def test_sensitive_key_detected(sample_env):
    result = inspect_env(sample_env)
    assert "DB_PASSWORD" in result.sensitive_keys
    assert "API_KEY" in result.sensitive_keys


def test_non_sensitive_key_not_flagged(sample_env):
    result = inspect_env(sample_env)
    assert "APP_NAME" not in result.sensitive_keys
    assert "PORT" not in result.sensitive_keys


def test_empty_key_detected(sample_env):
    result = inspect_env(sample_env)
    assert "EMPTY_VAR" in result.empty_keys


def test_non_empty_key_not_in_empty(sample_env):
    result = inspect_env(sample_env)
    assert "APP_NAME" not in result.empty_keys


def test_whitespace_detected(sample_env):
    result = inspect_env(sample_env)
    info = result.for_key("SPACED_VAL")
    assert info is not None
    assert info.has_whitespace is True


def test_no_whitespace_for_clean_value(sample_env):
    result = inspect_env(sample_env)
    info = result.for_key("APP_NAME")
    assert info.has_whitespace is False


def test_numeric_value_detected(sample_env):
    result = inspect_env(sample_env)
    assert result.for_key("PORT").is_numeric is True
    assert result.for_key("FLOAT_VAL").is_numeric is True


def test_non_numeric_value(sample_env):
    result = inspect_env(sample_env)
    assert result.for_key("APP_NAME").is_numeric is False


def test_boolean_value_detected(sample_env):
    result = inspect_env(sample_env)
    assert result.for_key("DEBUG").is_boolean is True


def test_non_boolean_value(sample_env):
    result = inspect_env(sample_env)
    assert result.for_key("APP_NAME").is_boolean is False


def test_length_recorded(sample_env):
    result = inspect_env(sample_env)
    info = result.for_key("APP_NAME")
    assert info.length == len("myapp")


def test_for_key_returns_none_for_missing(sample_env):
    result = inspect_env(sample_env)
    assert result.for_key("NONEXISTENT") is None


def test_summary_string(sample_env):
    result = inspect_env(sample_env)
    s = result.summary()
    assert "Inspected" in s
    assert "sensitive" in s
    assert "empty" in s


def test_empty_env_returns_empty_result():
    result = inspect_env({})
    assert result.entries == []
    assert result.sensitive_keys == []
    assert result.empty_keys == []
