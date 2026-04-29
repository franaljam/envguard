"""Tests for envguard.differ_sensitive."""
import pytest
from envguard.differ_sensitive import (
    SensitiveDiffResult,
    SensitiveChange,
    diff_sensitive,
    _is_sensitive,
)


# ---------------------------------------------------------------------------
# _is_sensitive
# ---------------------------------------------------------------------------

def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True

def test_is_sensitive_token():
    assert _is_sensitive("GITHUB_TOKEN") is True

def test_is_sensitive_api_key():
    assert _is_sensitive("STRIPE_API_KEY") is True

def test_is_not_sensitive_plain():
    assert _is_sensitive("APP_NAME") is False

def test_is_not_sensitive_port():
    assert _is_sensitive("PORT") is False


# ---------------------------------------------------------------------------
# diff_sensitive
# ---------------------------------------------------------------------------

def _left():
    return {"APP_NAME": "myapp", "DB_PASSWORD": "old", "PORT": "8080"}

def _right():
    return {"APP_NAME": "myapp", "DB_PASSWORD": "new", "PORT": "9090"}


def test_identical_envs_no_changes():
    env = {"A": "1", "B": "2"}
    result = diff_sensitive(env, env.copy())
    assert not result.has_changes()
    assert result.changes == []


def test_sensitive_change_detected():
    result = diff_sensitive(_left(), _right())
    keys = [c.key for c in result.sensitive_changes()]
    assert "DB_PASSWORD" in keys


def test_non_sensitive_change_detected():
    result = diff_sensitive(_left(), _right())
    keys = [c.key for c in result.non_sensitive_changes()]
    assert "PORT" in keys


def test_unchanged_key_not_in_changes():
    result = diff_sensitive(_left(), _right())
    keys = [c.key for c in result.changes]
    assert "APP_NAME" not in keys


def test_added_key_detected():
    left = {"A": "1"}
    right = {"A": "1", "API_KEY": "secret"}
    result = diff_sensitive(left, right)
    assert result.has_changes()
    change = result.changes[0]
    assert change.key == "API_KEY"
    assert change.added is True
    assert change.is_sensitive is True


def test_removed_key_detected():
    left = {"PORT": "8080", "APP_NAME": "x"}
    right = {"PORT": "8080"}
    result = diff_sensitive(left, right)
    assert result.has_changes()
    change = result.changes[0]
    assert change.key == "APP_NAME"
    assert change.removed is True


def test_modified_flag():
    left = {"DB_PASSWORD": "old"}
    right = {"DB_PASSWORD": "new"}
    result = diff_sensitive(left, right)
    assert result.changes[0].modified is True


def test_summary_no_changes():
    env = {"X": "1"}
    result = diff_sensitive(env, env.copy())
    assert "No differences" in result.summary()


def test_summary_with_changes():
    result = diff_sensitive(_left(), _right())
    s = result.summary()
    assert "change" in s
    assert "sensitive" in s


def test_changes_sorted_by_key():
    left = {"Z": "1", "A": "x"}
    right = {"Z": "2", "A": "y"}
    result = diff_sensitive(left, right)
    keys = [c.key for c in result.changes]
    assert keys == sorted(keys)
