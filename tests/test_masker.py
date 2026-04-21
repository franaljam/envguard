"""Tests for envguard.masker."""
import pytest
from envguard.masker import mask_env, MaskResult


_BASE = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "API_KEY": "abc123",
    "DEBUG": "true",
    "AUTH_TOKEN": "tok-xyz",
}


def test_non_sensitive_values_unchanged():
    result = mask_env({"APP_NAME": "myapp", "DEBUG": "true"})
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["DEBUG"] == "true"
    assert result.masked_keys == []


def test_sensitive_values_masked():
    result = mask_env(_BASE)
    assert result.masked["DB_PASSWORD"] == "***"
    assert result.masked["API_KEY"] == "***"
    assert result.masked["AUTH_TOKEN"] == "***"


def test_non_sensitive_values_untouched_in_mixed_env():
    result = mask_env(_BASE)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["DEBUG"] == "true"


def test_masked_keys_list_correct():
    result = mask_env(_BASE)
    assert set(result.masked_keys) == {"DB_PASSWORD", "API_KEY", "AUTH_TOKEN"}


def test_original_not_mutated():
    env = {"DB_PASSWORD": "secret", "X": "y"}
    mask_env(env)
    assert env["DB_PASSWORD"] == "secret"


def test_custom_placeholder():
    result = mask_env({"API_KEY": "abc"}, placeholder="[HIDDEN]")
    assert result.masked["API_KEY"] == "[HIDDEN]"


def test_reveal_prefix():
    result = mask_env({"API_KEY": "abc123xyz"}, reveal_prefix=3)
    assert result.masked["API_KEY"] == "abc***"


def test_reveal_prefix_short_value_fully_masked():
    result = mask_env({"API_KEY": "ab"}, reveal_prefix=3)
    assert result.masked["API_KEY"] == "***"


def test_extra_patterns():
    result = mask_env({"MY_CERT": "data"}, extra_patterns=["CERT"])
    assert result.masked["MY_CERT"] == "***"
    assert "MY_CERT" in result.masked_keys


def test_explicit_keys_overrides_auto_detection():
    env = {"API_KEY": "abc", "APP_NAME": "myapp"}
    result = mask_env(env, explicit_keys=["APP_NAME"])
    # APP_NAME masked even though not sensitive; API_KEY left alone
    assert result.masked["APP_NAME"] == "***"
    assert result.masked["API_KEY"] == "abc"


def test_count_matches_masked_keys():
    result = mask_env(_BASE)
    assert result.count() == len(result.masked_keys)


def test_summary_no_masks():
    result = mask_env({"X": "1"})
    assert result.summary() == "No keys masked."


def test_summary_with_masks():
    result = mask_env({"API_KEY": "abc"})
    assert "1 key(s) masked" in result.summary()
    assert "API_KEY" in result.summary()


def test_original_keys_preserved_in_result():
    env = {"A": "1", "B": "2"}
    result = mask_env(env)
    assert set(result.original_keys) == {"A", "B"}
