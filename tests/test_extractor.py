"""Tests for envguard.extractor."""
import pytest
from envguard.extractor import extract_env, ExtractResult


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "envguard",
    "APP_ENV": "production",
    "SECRET_KEY": "s3cr3t",
    "DEBUG": "false",
}


def test_no_criteria_returns_full_copy():
    result = extract_env(SAMPLE)
    assert result.extracted == SAMPLE
    assert result.extracted is not SAMPLE


def test_original_not_mutated():
    original = dict(SAMPLE)
    extract_env(SAMPLE, keys=["DB_HOST"])
    assert SAMPLE == original


def test_extract_by_exact_keys():
    result = extract_env(SAMPLE, keys=["DB_HOST", "DEBUG"])
    assert result.extracted == {"DB_HOST": "localhost", "DEBUG": "false"}
    assert result.missing == []


def test_missing_key_reported():
    result = extract_env(SAMPLE, keys=["DB_HOST", "NONEXISTENT"])
    assert "NONEXISTENT" in result.missing
    assert "DB_HOST" in result.extracted


def test_extract_by_prefix():
    result = extract_env(SAMPLE, prefix="DB_")
    assert set(result.extracted.keys()) == {"DB_HOST", "DB_PORT"}


def test_strip_prefix():
    result = extract_env(SAMPLE, prefix="DB_", strip_prefix=True)
    assert "HOST" in result.extracted
    assert "PORT" in result.extracted
    assert result.extracted["HOST"] == "localhost"


def test_extract_by_pattern():
    result = extract_env(SAMPLE, pattern=r"^APP_")
    assert set(result.extracted.keys()) == {"APP_NAME", "APP_ENV"}


def test_prefix_and_pattern_combined():
    result = extract_env(SAMPLE, prefix="DB_", pattern=r"SECRET")
    assert "DB_HOST" in result.extracted
    assert "DB_PORT" in result.extracted
    assert "SECRET_KEY" in result.extracted


def test_has_missing_true_when_key_absent():
    result = extract_env(SAMPLE, keys=["MISSING_KEY"])
    assert result.has_missing() is True


def test_has_missing_false_when_all_present():
    result = extract_env(SAMPLE, keys=["DB_HOST"])
    assert result.has_missing() is False


def test_found_returns_extracted_keys():
    result = extract_env(SAMPLE, prefix="APP_")
    assert set(result.found()) == {"APP_NAME", "APP_ENV"}


def test_source_keys_preserved():
    result = extract_env(SAMPLE, prefix="DB_")
    assert set(result.source_keys) == set(SAMPLE.keys())


def test_summary_contains_counts():
    result = extract_env(SAMPLE, keys=["DB_HOST", "GONE"])
    s = result.summary()
    assert "Extracted" in s
    assert "Missing" in s
    assert "GONE" in s
