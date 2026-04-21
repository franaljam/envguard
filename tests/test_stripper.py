"""Tests for envguard.stripper."""
import pytest
from envguard.stripper import strip_env, StripResult


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "abc",
    "APP_DEBUG": "true",
    "FEATURE_FLAG": "on",
}


def test_no_criteria_returns_copy():
    result = strip_env(SAMPLE)
    assert result.stripped == SAMPLE
    assert result.removed == []
    assert not result.changed()


def test_original_not_mutated():
    env = {"A": "1", "B": "2"}
    strip_env(env, keys=["A"])
    assert "A" in env


def test_strip_by_exact_keys():
    result = strip_env(SAMPLE, keys=["DB_HOST", "APP_DEBUG"])
    assert "DB_HOST" not in result.stripped
    assert "APP_DEBUG" not in result.stripped
    assert "DB_PORT" in result.stripped
    assert len(result.removed) == 2


def test_strip_by_prefix():
    result = strip_env(SAMPLE, prefixes=["DB_"])
    assert "DB_HOST" not in result.stripped
    assert "DB_PORT" not in result.stripped
    assert "APP_SECRET" in result.stripped
    assert result.removed == ["DB_HOST", "DB_PORT"]


def test_strip_by_pattern():
    result = strip_env(SAMPLE, patterns=[r"SECRET|FLAG"])
    assert "APP_SECRET" not in result.stripped
    assert "FEATURE_FLAG" not in result.stripped
    assert "DB_HOST" in result.stripped


def test_strip_multiple_criteria_combined():
    result = strip_env(SAMPLE, keys=["FEATURE_FLAG"], prefixes=["DB_"])
    assert "FEATURE_FLAG" not in result.stripped
    assert "DB_HOST" not in result.stripped
    assert "APP_SECRET" in result.stripped


def test_invert_keeps_only_matched():
    result = strip_env(SAMPLE, prefixes=["APP_"], invert=True)
    assert set(result.stripped.keys()) == {"APP_SECRET", "APP_DEBUG"}
    assert "DB_HOST" not in result.stripped


def test_missing_key_silently_ignored():
    result = strip_env(SAMPLE, keys=["NONEXISTENT"])
    assert result.stripped == SAMPLE
    assert result.removed == []


def test_summary_no_removal():
    result = strip_env(SAMPLE)
    assert result.summary() == "No keys stripped."


def test_summary_with_removal():
    result = strip_env({"A": "1", "B": "2"}, keys=["A"])
    assert "1 key(s)" in result.summary()
    assert "A" in result.summary()


def test_changed_true_when_keys_removed():
    result = strip_env(SAMPLE, keys=["DB_HOST"])
    assert result.changed()


def test_removed_list_is_sorted():
    env = {"Z_KEY": "z", "A_KEY": "a", "M_KEY": "m"}
    result = strip_env(env, keys=["Z_KEY", "A_KEY", "M_KEY"])
    assert result.removed == ["A_KEY", "M_KEY", "Z_KEY"]
