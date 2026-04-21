"""Tests for envguard.segmenter."""
import pytest
from envguard.segmenter import segment_env, SegmentResult


MIXED = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "REDIS_URL": "redis://localhost",
    "APP_NAME": "myapp",
    "LOG_LEVEL": "INFO",
}


def test_returns_segment_result():
    result = segment_env({}, {})
    assert isinstance(result, SegmentResult)


def test_no_rules_all_unmatched():
    result = segment_env(MIXED, {})
    assert result.unmatched == MIXED
    assert result.segment_names() == []


def test_prefix_rule_groups_correctly():
    rules = {"database": r"^DB_", "cache": r"^REDIS_"}
    result = segment_env(MIXED, rules)
    assert set(result.segments["database"].keys()) == {"DB_HOST", "DB_PORT"}
    assert set(result.segments["cache"].keys()) == {"REDIS_URL"}


def test_unmatched_keys_collected():
    rules = {"database": r"^DB_"}
    result = segment_env(MIXED, rules)
    assert "APP_NAME" in result.unmatched
    assert "LOG_LEVEL" in result.unmatched
    assert "REDIS_URL" in result.unmatched


def test_first_matching_rule_wins():
    rules = {"first": r"^DB_", "second": r"^DB_HOST"}
    result = segment_env({"DB_HOST": "x"}, rules)
    assert "DB_HOST" in result.segments["first"]
    assert "DB_HOST" not in result.segments["second"]


def test_original_not_mutated():
    original = {"DB_HOST": "localhost", "APP": "x"}
    copy = dict(original)
    segment_env(original, {"db": r"^DB_"})
    assert original == copy


def test_segment_names_sorted():
    rules = {"zebra": r"^Z", "alpha": r"^A"}
    result = segment_env({}, rules)
    assert result.segment_names() == ["alpha", "zebra"]


def test_count_returns_correct_number():
    rules = {"database": r"^DB_"}
    result = segment_env(MIXED, rules)
    assert result.count("database") == 2


def test_count_unknown_segment_returns_zero():
    result = segment_env(MIXED, {})
    assert result.count("nonexistent") == 0


def test_summary_contains_segment_names():
    rules = {"database": r"^DB_", "cache": r"^REDIS_"}
    result = segment_env(MIXED, rules)
    summary = result.summary()
    assert "database" in summary
    assert "cache" in summary


def test_summary_no_segments_message():
    result = segment_env({}, {})
    assert "no segments" in result.summary()


def test_empty_env_produces_empty_segments():
    rules = {"database": r"^DB_"}
    result = segment_env({}, rules)
    assert result.segments["database"] == {}
    assert result.unmatched == {}
