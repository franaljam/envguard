"""Tests for envguard.filter."""
import pytest
from envguard.filter import filter_env, FilterResult


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "abc",
    "APP_DEBUG": "true",
    "LOG_LEVEL": "info",
}


def test_no_criteria_returns_all():
    result = filter_env(ENV)
    assert result.matched == ENV
    assert result.excluded == {}


def test_filter_by_prefix():
    result = filter_env(ENV, prefixes=["DB_"])
    assert set(result.matched) == {"DB_HOST", "DB_PORT"}
    assert "APP_SECRET" in result.excluded


def test_filter_by_multiple_prefixes():
    result = filter_env(ENV, prefixes=["DB_", "APP_"])
    assert set(result.matched) == {"DB_HOST", "DB_PORT", "APP_SECRET", "APP_DEBUG"}


def test_filter_by_exact_keys():
    result = filter_env(ENV, keys=["LOG_LEVEL", "DB_HOST"])
    assert set(result.matched) == {"LOG_LEVEL", "DB_HOST"}


def test_filter_by_pattern():
    result = filter_env(ENV, patterns=[r"SECRET|DEBUG"])
    assert set(result.matched) == {"APP_SECRET", "APP_DEBUG"}


def test_filter_combined_prefix_and_pattern():
    result = filter_env(ENV, prefixes=["DB_"], patterns=[r"LOG"])
    assert "DB_HOST" in result.matched
    assert "LOG_LEVEL" in result.matched
    assert "APP_SECRET" not in result.matched


def test_invert_filter():
    result = filter_env(ENV, prefixes=["DB_"], invert=True)
    assert "DB_HOST" not in result.matched
    assert "APP_SECRET" in result.matched
    assert "LOG_LEVEL" in result.matched


def test_summary_string():
    result = filter_env(ENV, prefixes=["DB_"])
    s = result.summary()
    assert "2" in s
    assert "matched" in s


def test_count():
    result = filter_env(ENV, prefixes=["APP_"])
    assert result.count() == 2


def test_original_not_mutated():
    original = dict(ENV)
    filter_env(ENV, prefixes=["DB_"])
    assert ENV == original
