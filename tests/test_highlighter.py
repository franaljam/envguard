"""Tests for envguard.highlighter."""
import pytest
from envguard.highlighter import highlight_env, HighlightResult


_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "API_KEY": "secret",
    "DEBUG": "true",
    "feature_flag": "on",
}


def test_no_criteria_returns_empty_highlighted():
    result = highlight_env(_ENV)
    assert result.highlighted == []
    assert result.count() == 0


def test_no_criteria_env_is_copy():
    result = highlight_env(_ENV)
    assert result.env == _ENV
    assert result.env is not _ENV


def test_prefix_matches_keys():
    result = highlight_env(_ENV, prefixes=["DB_"])
    assert "DB_HOST" in result.highlighted
    assert "DB_PORT" in result.highlighted
    assert "API_KEY" not in result.highlighted


def test_exact_match():
    result = highlight_env(_ENV, exact=["DEBUG"])
    assert result.highlighted == ["DEBUG"]


def test_pattern_match():
    result = highlight_env(_ENV, patterns=[r"_KEY$"])
    assert "API_KEY" in result.highlighted
    assert "DB_HOST" not in result.highlighted


def test_multiple_criteria_combined():
    result = highlight_env(_ENV, prefixes=["DB_"], exact=["DEBUG"])
    assert "DB_HOST" in result.highlighted
    assert "DB_PORT" in result.highlighted
    assert "DEBUG" in result.highlighted
    assert "API_KEY" not in result.highlighted


def test_highlighted_sorted():
    result = highlight_env(_ENV, prefixes=["DB_"])
    assert result.highlighted == sorted(result.highlighted)


def test_count_matches_length():
    result = highlight_env(_ENV, prefixes=["DB_"])
    assert result.count() == len(result.highlighted)


def test_summary_with_matches():
    result = highlight_env(_ENV, exact=["DEBUG"])
    assert "1" in result.summary()
    assert "DEBUG" in result.summary()


def test_summary_no_matches():
    result = highlight_env(_ENV)
    assert result.summary() == "No keys highlighted."


def test_original_not_mutated():
    original = dict(_ENV)
    highlight_env(_ENV, prefixes=["DB_"])
    assert _ENV == original


def test_no_match_returns_empty_list():
    result = highlight_env(_ENV, prefixes=["NONEXISTENT_"])
    assert result.highlighted == []


def test_duplicate_criteria_no_duplicate_highlighted():
    """Keys matched by multiple criteria should appear only once in highlighted."""
    result = highlight_env(_ENV, prefixes=["DB_"], exact=["DB_HOST"])
    assert result.highlighted.count("DB_HOST") == 1
