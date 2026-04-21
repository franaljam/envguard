"""Tests for envguard.cloner."""
import pytest
from envguard.cloner import clone_env


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_no_options_returns_identical_copy():
    result = clone_env(BASE)
    assert result.env == BASE
    assert result.env is not BASE


def test_original_not_mutated():
    original = dict(BASE)
    clone_env(original, overrides={"HOST": "prod.example.com"}, exclude=["DEBUG"])
    assert original == BASE


def test_override_existing_key():
    result = clone_env(BASE, overrides={"PORT": "3306"})
    assert result.env["PORT"] == "3306"
    assert "PORT" in result.overridden


def test_override_adds_new_key():
    result = clone_env(BASE, overrides={"NEW_KEY": "new_value"})
    assert result.env["NEW_KEY"] == "new_value"
    assert "NEW_KEY" in result.overridden


def test_exclude_removes_key():
    result = clone_env(BASE, exclude=["DEBUG"])
    assert "DEBUG" not in result.env
    assert "DEBUG" in result.excluded


def test_exclude_missing_key_silently_ignored():
    result = clone_env(BASE, exclude=["NONEXISTENT"])
    assert result.env == BASE
    assert result.excluded == []


def test_exclude_and_override_together():
    result = clone_env(BASE, overrides={"HOST": "prod"}, exclude=["DEBUG"])
    assert result.env["HOST"] == "prod"
    assert "DEBUG" not in result.env
    assert "PORT" in result.env


def test_excluded_key_not_in_overridden():
    result = clone_env(BASE, overrides={"DEBUG": "false"}, exclude=["DEBUG"])
    # exclude wins: key should not appear
    assert "DEBUG" not in result.env
    assert "DEBUG" not in result.overridden


def test_changed_false_when_no_options():
    result = clone_env(BASE)
    assert not result.changed()


def test_changed_true_when_overridden():
    result = clone_env(BASE, overrides={"HOST": "other"})
    assert result.changed()


def test_changed_true_when_excluded():
    result = clone_env(BASE, exclude=["PORT"])
    assert result.changed()


def test_summary_no_changes():
    result = clone_env(BASE)
    assert result.summary() == "clone identical to source"


def test_summary_with_override():
    result = clone_env(BASE, overrides={"HOST": "prod"})
    assert "overridden" in result.summary()
    assert "HOST" in result.summary()


def test_summary_with_exclude():
    result = clone_env(BASE, exclude=["DEBUG"])
    assert "excluded" in result.summary()
    assert "DEBUG" in result.summary()


def test_empty_source_with_overrides():
    result = clone_env({}, overrides={"KEY": "val"})
    assert result.env == {"KEY": "val"}
    assert "KEY" in result.overridden
