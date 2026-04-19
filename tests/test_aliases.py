"""Tests for envguard.aliases."""
import pytest
from envguard.aliases import resolve_aliases, AliasResult


def test_no_aliases_returns_copy():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = resolve_aliases(env, {})
    assert result.env == env
    assert result.env is not env


def test_single_alias_resolved():
    env = {"DB_HOST": "localhost"}
    result = resolve_aliases(env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert result.env["DATABASE_HOST"] == "localhost"
    assert "DB_HOST" not in result.env


def test_resolved_tracks_mapping():
    env = {"DB_HOST": "localhost"}
    result = resolve_aliases(env, {"DB_HOST": "DATABASE_HOST"})
    assert result.resolved == {"DB_HOST": "DATABASE_HOST"}


def test_missing_alias_is_unresolved():
    env = {"FOO": "bar"}
    result = resolve_aliases(env, {"MISSING": "CANONICAL"})
    assert "MISSING" in result.unresolved
    assert "CANONICAL" not in result.env


def test_keep_alias_retains_original_key():
    env = {"DB_HOST": "localhost"}
    result = resolve_aliases(env, {"DB_HOST": "DATABASE_HOST"}, keep_alias=True)
    assert "DB_HOST" in result.env
    assert "DATABASE_HOST" in result.env


def test_multiple_aliases():
    env = {"A": "1", "B": "2"}
    result = resolve_aliases(env, {"A": "ALPHA", "B": "BETA"})
    assert result.env == {"ALPHA": "1", "BETA": "2"}
    assert len(result.resolved) == 2
    assert result.unresolved == []


def test_original_not_mutated():
    env = {"X": "val"}
    resolve_aliases(env, {"X": "Y"})
    assert "X" in env


def test_has_unresolved_false_when_all_resolved():
    env = {"A": "1"}
    result = resolve_aliases(env, {"A": "ALPHA"})
    assert not result.has_unresolved()


def test_has_unresolved_true_when_missing():
    env = {"A": "1"}
    result = resolve_aliases(env, {"MISSING": "CANONICAL"})
    assert result.has_unresolved()


def test_summary_contains_resolved_info():
    env = {"A": "1"}
    result = resolve_aliases(env, {"A": "ALPHA"})
    s = result.summary()
    assert "ALPHA" in s
    assert "A" in s
