"""Tests for envguard.rotator."""
import pytest
from envguard.rotator import rotate_env, RotateResult


@pytest.fixture()
def base_env():
    return {
        "DB_PASSWORD": "old_pass",
        "API_TOKEN": "old_token",
        "APP_NAME": "myapp",
        "DEBUG": "true",
    }


def test_no_replacements_returns_copy(base_env):
    result = rotate_env(base_env, {})
    assert result.rotated == base_env
    assert result.rotated is not base_env


def test_original_not_mutated(base_env):
    original_copy = dict(base_env)
    rotate_env(base_env, {"DB_PASSWORD": "new_pass"})
    assert base_env == original_copy


def test_sensitive_key_rotated(base_env):
    result = rotate_env(base_env, {"DB_PASSWORD": "new_pass"})
    assert result.rotated["DB_PASSWORD"] == "new_pass"
    assert "DB_PASSWORD" in result.rotated_keys


def test_non_sensitive_key_skipped_by_default(base_env):
    result = rotate_env(base_env, {"APP_NAME": "newapp"})
    assert result.rotated["APP_NAME"] == "myapp"
    assert "APP_NAME" in result.skipped_keys
    assert "APP_NAME" not in result.rotated_keys


def test_non_sensitive_key_rotated_when_flag_disabled(base_env):
    result = rotate_env(base_env, {"APP_NAME": "newapp"}, sensitive_only=False)
    assert result.rotated["APP_NAME"] == "newapp"
    assert "APP_NAME" in result.rotated_keys


def test_multiple_sensitive_keys_rotated(base_env):
    replacements = {"DB_PASSWORD": "p2", "API_TOKEN": "t2"}
    result = rotate_env(base_env, replacements)
    assert result.rotated["DB_PASSWORD"] == "p2"
    assert result.rotated["API_TOKEN"] == "t2"
    assert len(result.rotated_keys) == 2


def test_exclude_prevents_rotation(base_env):
    result = rotate_env(
        base_env, {"DB_PASSWORD": "new_pass"}, exclude=["DB_PASSWORD"]
    )
    assert result.rotated["DB_PASSWORD"] == "old_pass"
    assert "DB_PASSWORD" in result.skipped_keys


def test_missing_key_in_env_is_skipped(base_env):
    result = rotate_env(base_env, {"MISSING_SECRET": "value"})
    assert "MISSING_SECRET" not in result.rotated
    assert "MISSING_SECRET" in result.skipped_keys


def test_changed_true_when_rotation_occurred(base_env):
    result = rotate_env(base_env, {"DB_PASSWORD": "new"})
    assert result.changed() is True


def test_changed_false_when_nothing_rotated(base_env):
    result = rotate_env(base_env, {"APP_NAME": "x"})
    assert result.changed() is False


def test_summary_no_rotation(base_env):
    result = rotate_env(base_env, {})
    assert result.summary() == "No keys rotated."


def test_summary_with_rotation(base_env):
    result = rotate_env(base_env, {"DB_PASSWORD": "new"})
    summary = result.summary()
    assert "Rotated 1 key" in summary
    assert "DB_PASSWORD" in summary
