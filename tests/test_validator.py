"""Tests for envguard.validator."""

import pytest
from envguard.validator import validate_env, ValidationResult


ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "supersecret",
    "DEBUG": "",
    "PORT": "8080",
}


def test_valid_when_all_required_present():
    result = validate_env(ENV, required_keys=["DATABASE_URL", "SECRET_KEY"])
    assert result.is_valid


def test_missing_required_key():
    result = validate_env(ENV, required_keys=["DATABASE_URL", "REDIS_URL"])
    assert not result.is_valid
    assert "REDIS_URL" in result.missing_required


def test_multiple_missing_keys():
    result = validate_env({}, required_keys=["A", "B", "C"])
    assert sorted(result.missing_required) == ["A", "B", "C"]


def test_non_empty_key_passes_when_has_value():
    result = validate_env(ENV, non_empty_keys=["SECRET_KEY"])
    assert result.is_valid


def test_non_empty_key_fails_when_empty_string():
    result = validate_env(ENV, non_empty_keys=["DEBUG"])
    assert not result.is_valid
    assert "DEBUG" in result.invalid_values
    assert "must not be empty" in result.invalid_values["DEBUG"]


def test_non_empty_key_also_required():
    result = validate_env({}, non_empty_keys=["SECRET_KEY"])
    assert "SECRET_KEY" in result.missing_required


def test_no_constraints_always_valid():
    result = validate_env(ENV)
    assert result.is_valid


def test_summary_no_issues():
    result = validate_env(ENV, required_keys=["PORT"])
    assert result.summary() == "All required keys present and valid."


def test_summary_with_issues():
    result = validate_env(ENV, required_keys=["MISSING"], non_empty_keys=["DEBUG"])
    summary = result.summary()
    assert "MISSING" in summary
    assert "DEBUG" in summary
    assert "must not be empty" in summary
