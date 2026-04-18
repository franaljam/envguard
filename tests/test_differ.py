"""Tests for envguard.differ module."""

import pytest
from envguard.differ import diff_envs, DiffResult


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


def test_no_differences():
    result = diff_envs(BASE, BASE.copy())
    assert not result.has_differences
    assert result.summary() == "No differences found."


def test_missing_key():
    target = {k: v for k, v in BASE.items() if k != "SECRET"}
    result = diff_envs(BASE, target)
    assert "SECRET" in result.missing
    assert not result.extra
    assert not result.changed


def test_extra_key():
    target = {**BASE, "NEW_VAR": "value"}
    result = diff_envs(BASE, target)
    assert "NEW_VAR" in result.extra
    assert not result.missing
    assert not result.changed


def test_changed_value():
    target = {**BASE, "DB_HOST": "prod-db.example.com"}
    result = diff_envs(BASE, target)
    assert "DB_HOST" in result.changed
    assert result.changed["DB_HOST"] == ("localhost", "prod-db.example.com")
    assert not result.missing
    assert not result.extra


def test_ignore_values_skips_changed():
    target = {**BASE, "DB_HOST": "prod-db.example.com"}
    result = diff_envs(BASE, target, ignore_values=True)
    assert not result.changed
    assert not result.missing
    assert not result.extra


def test_combined_differences():
    target = {"DB_HOST": "other", "EXTRA": "yes"}
    result = diff_envs(BASE, target)
    assert result.has_differences
    assert "DB_PORT" in result.missing
    assert "SECRET" in result.missing
    assert "EXTRA" in result.extra
    assert "DB_HOST" in result.changed


def test_summary_contains_sections():
    target = {"DB_HOST": "other", "EXTRA": "yes"}
    result = diff_envs(BASE, target)
    summary = result.summary()
    assert "Missing keys" in summary
    assert "Extra keys" in summary
    assert "Changed values" in summary


def test_empty_base_and_target():
    result = diff_envs({}, {})
    assert not result.has_differences
