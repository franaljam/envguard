"""Tests for envguard.enforcer."""

import pytest
from envguard.enforcer import enforce_env, EnforceViolation


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _rules(*items):
    return list(items)


def _rule(key, op, **kw):
    return {"key": key, "op": op, **kw}


# ---------------------------------------------------------------------------
# required / forbidden
# ---------------------------------------------------------------------------

def test_no_violations_when_all_rules_pass():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = enforce_env(env, [_rule("HOST", "required"), _rule("PORT", "required")])
    assert not result.violations
    assert not result.has_errors


def test_required_missing_key_is_error():
    result = enforce_env({}, [_rule("DB_URL", "required")])
    assert result.has_errors
    assert result.errors()[0].key == "DB_URL"


def test_forbidden_present_key_is_error():
    env = {"DEBUG": "true"}
    result = enforce_env(env, [_rule("DEBUG", "forbidden")])
    assert result.has_errors
    assert result.errors()[0].op == "forbidden"


def test_forbidden_absent_key_passes():
    result = enforce_env({}, [_rule("DEBUG", "forbidden")])
    assert not result.violations


# ---------------------------------------------------------------------------
# equals / not_equals
# ---------------------------------------------------------------------------

def test_equals_matching_value_passes():
    env = {"ENV": "production"}
    result = enforce_env(env, [_rule("ENV", "equals", value="production")])
    assert not result.violations


def test_equals_wrong_value_is_error():
    env = {"ENV": "staging"}
    result = enforce_env(env, [_rule("ENV", "equals", value="production")])
    assert result.has_errors


def test_not_equals_different_value_passes():
    env = {"LOG_LEVEL": "info"}
    result = enforce_env(env, [_rule("LOG_LEVEL", "not_equals", value="debug")])
    assert not result.violations


def test_not_equals_same_value_is_error():
    env = {"LOG_LEVEL": "debug"}
    result = enforce_env(env, [_rule("LOG_LEVEL", "not_equals", value="debug")])
    assert result.has_errors


# ---------------------------------------------------------------------------
# matches
# ---------------------------------------------------------------------------

def test_matches_valid_pattern_passes():
    env = {"PORT": "8080"}
    result = enforce_env(env, [_rule("PORT", "matches", value=r"^\d+$")])
    assert not result.violations


def test_matches_invalid_pattern_is_error():
    env = {"PORT": "abc"}
    result = enforce_env(env, [_rule("PORT", "matches", value=r"^\d+$")])
    assert result.has_errors


# ---------------------------------------------------------------------------
# min_length / max_length
# ---------------------------------------------------------------------------

def test_min_length_passes_when_long_enough():
    env = {"SECRET": "supersecretkey"}
    result = enforce_env(env, [_rule("SECRET", "min_length", length=8)])
    assert not result.violations


def test_min_length_fails_when_too_short():
    env = {"SECRET": "abc"}
    result = enforce_env(env, [_rule("SECRET", "min_length", length=8)])
    assert result.has_errors


def test_max_length_passes_when_short_enough():
    env = {"TAG": "v1"}
    result = enforce_env(env, [_rule("TAG", "max_length", length=10)])
    assert not result.violations


def test_max_length_fails_when_too_long():
    env = {"TAG": "this-is-a-very-long-tag"}
    result = enforce_env(env, [_rule("TAG", "max_length", length=10)])
    assert result.has_errors


# ---------------------------------------------------------------------------
# severity
# ---------------------------------------------------------------------------

def test_warning_severity_not_counted_as_error():
    result = enforce_env({}, [_rule("OPTIONAL_KEY", "required", severity="warning")])
    assert not result.has_errors
    assert result.has_warnings
    assert result.warnings()[0].key == "OPTIONAL_KEY"


def test_summary_all_pass():
    result = enforce_env({"A": "1"}, [_rule("A", "required")])
    assert result.summary() == "All rules passed."


def test_summary_with_errors():
    result = enforce_env({}, [_rule("A", "required")])
    assert "error" in result.summary()
