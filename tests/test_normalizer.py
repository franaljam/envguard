"""Tests for envguard.normalizer."""
import pytest
from envguard.normalizer import normalize_env, NormalizeResult


def test_no_changes_returns_copy():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = normalize_env(env, normalize_bools=False, strip_inline_comments=False)
    assert result.normalized == env
    assert not result.changed()


def test_original_not_mutated():
    env = {"FLAG": "yes"}
    normalize_env(env)
    assert env["FLAG"] == "yes"


def test_normalize_bool_true_variants():
    for val in ("1", "yes", "on", "true", "True", "YES"):
        result = normalize_env({"FLAG": val})
        assert result.normalized["FLAG"] == "true", f"Failed for {val!r}"


def test_normalize_bool_false_variants():
    for val in ("0", "no", "off", "false", "False", "NO"):
        result = normalize_env({"FLAG": val})
        assert result.normalized["FLAG"] == "false", f"Failed for {val!r}"


def test_normalize_bool_disabled():
    env = {"FLAG": "yes"}
    result = normalize_env(env, normalize_bools=False)
    assert result.normalized["FLAG"] == "yes"


def test_strip_inline_comment():
    env = {"HOST": "localhost # primary host"}
    result = normalize_env(env, normalize_bools=False)
    assert result.normalized["HOST"] == "localhost"


def test_strip_inline_comment_disabled():
    env = {"HOST": "localhost # primary host"}
    result = normalize_env(env, normalize_bools=False, strip_inline_comments=False)
    assert result.normalized["HOST"] == "localhost # primary host"


def test_quoted_value_not_stripped():
    env = {"MSG": "'hello # world'"}
    result = normalize_env(env, normalize_bools=False)
    assert result.normalized["MSG"] == "'hello # world'"


def test_lowercase_values():
    env = {"ENV": "Production"}
    result = normalize_env(env, normalize_bools=False, strip_inline_comments=False, lowercase_values=True)
    assert result.normalized["ENV"] == "production"
    assert "ENV" in result.changed_keys


def test_changed_keys_tracked():
    env = {"A": "yes", "B": "hello"}
    result = normalize_env(env)
    assert "A" in result.changed_keys
    assert "B" not in result.changed_keys


def test_summary_with_changes():
    env = {"FLAG": "yes"}
    result = normalize_env(env)
    assert "1 key(s) normalized" in result.summary()


def test_summary_no_changes():
    env = {"KEY": "value"}
    result = normalize_env(env, normalize_bools=False, strip_inline_comments=False)
    assert result.summary() == "No normalization changes."


def test_empty_env_returns_empty():
    """Normalizing an empty dict should return an empty normalized dict with no changes."""
    result = normalize_env({})
    assert result.normalized == {}
    assert not result.changed()
    assert result.changed_keys == set()
