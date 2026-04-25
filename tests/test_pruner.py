"""Tests for envguard.pruner."""
import pytest
from envguard.pruner import prune_env, PruneResult


BASE = {
    "APP_NAME": "myapp",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "LEGACY_TOKEN": "abc",
    "LEGACY_KEY": "xyz",
    "EMPTY_VAR": "",
    "DEBUG": "true",
}


def test_no_criteria_returns_copy():
    result = prune_env(BASE)
    assert result.pruned == BASE
    assert result.removed == []


def test_original_not_mutated():
    original = dict(BASE)
    prune_env(BASE, keys=["APP_NAME"])
    assert BASE == original


def test_prune_by_exact_key():
    result = prune_env(BASE, keys=["APP_NAME"])
    assert "APP_NAME" not in result.pruned
    assert "APP_NAME" in result.removed


def test_prune_multiple_exact_keys():
    result = prune_env(BASE, keys=["APP_NAME", "DEBUG"])
    assert "APP_NAME" not in result.pruned
    assert "DEBUG" not in result.pruned
    assert len(result.removed) == 2


def test_prune_missing_key_silently_ignored():
    result = prune_env(BASE, keys=["NONEXISTENT"])
    assert result.removed == []
    assert result.pruned == BASE


def test_prune_by_prefix():
    result = prune_env(BASE, prefixes=["LEGACY_"])
    assert "LEGACY_TOKEN" not in result.pruned
    assert "LEGACY_KEY" not in result.pruned
    assert set(result.removed) == {"LEGACY_TOKEN", "LEGACY_KEY"}


def test_prune_by_pattern():
    result = prune_env(BASE, patterns=["DB_*"])
    assert "DB_HOST" not in result.pruned
    assert "DB_PORT" not in result.pruned
    assert set(result.removed) == {"DB_HOST", "DB_PORT"}


def test_empty_only_skips_non_empty_keys():
    result = prune_env(BASE, keys=["APP_NAME", "EMPTY_VAR"], empty_only=True)
    assert "EMPTY_VAR" in result.removed
    assert "APP_NAME" not in result.removed
    assert "APP_NAME" in result.pruned


def test_changed_false_when_nothing_removed():
    result = prune_env(BASE)
    assert result.changed() is False


def test_changed_true_when_keys_removed():
    result = prune_env(BASE, keys=["DEBUG"])
    assert result.changed() is True


def test_summary_no_changes():
    result = prune_env(BASE)
    assert result.summary() == "No keys pruned."


def test_summary_with_removals():
    result = prune_env({"A": "1", "B": "2"}, keys=["A", "B"])
    assert "2 key(s)" in result.summary()


def test_combined_criteria_prefix_and_pattern():
    result = prune_env(BASE, prefixes=["LEGACY_"], patterns=["DB_*"])
    for k in ["LEGACY_TOKEN", "LEGACY_KEY", "DB_HOST", "DB_PORT"]:
        assert k not in result.pruned
