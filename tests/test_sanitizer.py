"""Tests for envguard.sanitizer."""
import pytest
from envguard.sanitizer import sanitize_env


def test_no_changes_returns_copy():
    env = {"KEY": "value"}
    result = sanitize_env(env)
    assert result.sanitized == {"KEY": "value"}
    assert not result.changed()


def test_original_not_mutated():
    env = {"KEY": '"hello"'}
    result = sanitize_env(env)
    assert env["KEY"] == '"hello"'
    assert result.sanitized["KEY"] == "hello"


def test_strip_double_quotes():
    env = {"KEY": '"my value"'}
    result = sanitize_env(env, strip_quotes=True)
    assert result.sanitized["KEY"] == "my value"
    assert result.changed()


def test_strip_single_quotes():
    env = {"KEY": "'my value'"}
    result = sanitize_env(env, strip_quotes=True)
    assert result.sanitized["KEY"] == "my value"


def test_strip_quotes_disabled():
    env = {"KEY": '"quoted"'}
    result = sanitize_env(env, strip_quotes=False)
    assert result.sanitized["KEY"] == '"quoted"'
    assert not result.changed()


def test_remove_control_chars():
    env = {"KEY": "val\x00ue"}
    result = sanitize_env(env, remove_control_chars=True)
    assert "\x00" not in result.sanitized["KEY"]
    assert result.changed()


def test_remove_control_chars_disabled():
    env = {"KEY": "val\x00ue"}
    result = sanitize_env(env, remove_control_chars=False)
    assert result.sanitized["KEY"] == "val\x00ue"


def test_normalize_boolean_true_variants():
    for val in ("yes", "YES", "1", "on", "True"):
        env = {"FLAG": val}
        result = sanitize_env(env, normalize_booleans=True)
        assert result.sanitized["FLAG"] == "true", f"Failed for {val}"


def test_normalize_boolean_false_variants():
    for val in ("no", "NO", "0", "off", "False"):
        env = {"FLAG": val}
        result = sanitize_env(env, normalize_booleans=True)
        assert result.sanitized["FLAG"] == "false", f"Failed for {val}"


def test_normalize_boolean_disabled():
    env = {"FLAG": "yes"}
    result = sanitize_env(env, normalize_booleans=False)
    assert result.sanitized["FLAG"] == "yes"


def test_summary_no_changes():
    env = {"A": "clean"}
    result = sanitize_env(env)
    assert result.summary() == "No sanitization changes."


def test_summary_with_changes():
    env = {"KEY": '"quoted"'}
    result = sanitize_env(env)
    summary = result.summary()
    assert "Sanitized" in summary
    assert "KEY" in summary


def test_multiple_keys_multiple_changes():
    env = {"A": '"val"', "B": "yes", "C": "plain"}
    result = sanitize_env(env, strip_quotes=True, normalize_booleans=True)
    assert result.sanitized["A"] == "val"
    assert result.sanitized["B"] == "true"
    assert result.sanitized["C"] == "plain"
