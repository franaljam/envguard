"""Tests for envguard.trimmer."""
import pytest
from envguard.trimmer import trim_env


BASE = {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "postgres://", "DEBUG": "true"}


def test_no_criteria_returns_copy():
    result = trim_env(BASE)
    assert result.trimmed == BASE
    assert result.removed == []
    assert not result.changed()


def test_explicit_key_removed():
    result = trim_env(BASE, keys=["DEBUG"])
    assert "DEBUG" not in result.trimmed
    assert "DEBUG" in result.removed
    assert result.changed()


def test_multiple_explicit_keys_removed():
    result = trim_env(BASE, keys=["DEBUG", "APP_PORT"])
    assert "DEBUG" not in result.trimmed
    assert "APP_PORT" not in result.trimmed
    assert len(result.removed) == 2


def test_missing_key_silently_ignored():
    result = trim_env(BASE, keys=["NONEXISTENT"])
    assert result.removed == []
    assert result.trimmed == BASE


def test_pattern_removes_matching_keys():
    result = trim_env(BASE, pattern=r"^APP_")
    assert "APP_HOST" not in result.trimmed
    assert "APP_PORT" not in result.trimmed
    assert "DB_URL" in result.trimmed
    assert len(result.removed) == 2


def test_drop_empty_removes_blank_values():
    env = {"A": "value", "B": "", "C": ""}
    result = trim_env(env, drop_empty=True)
    assert "B" not in result.trimmed
    assert "C" not in result.trimmed
    assert "A" in result.trimmed
    assert sorted(result.removed) == ["B", "C"]


def test_combined_criteria():
    env = {"APP_HOST": "x", "DEBUG": "", "DB_URL": "y"}
    result = trim_env(env, keys=["DB_URL"], drop_empty=True)
    assert "DB_URL" not in result.trimmed
    assert "DEBUG" not in result.trimmed
    assert "APP_HOST" in result.trimmed


def test_original_not_mutated():
    original = dict(BASE)
    trim_env(BASE, keys=["DEBUG"], pattern=r"^APP_")
    assert BASE == original


def test_summary_no_removals():
    result = trim_env(BASE)
    assert result.summary() == "No keys removed."


def test_summary_with_removals():
    result = trim_env({"A": "1", "B": "2"}, keys=["A", "B"])
    assert "2 key(s)" in result.summary()
