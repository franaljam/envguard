import pytest
from envguard.padder import pad_env, PadResult


REF = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


def test_no_missing_keys_returns_copy():
    env = {"HOST": "prod.db", "PORT": "5432", "DEBUG": "false"}
    result = pad_env(env, REF)
    assert result.env == env
    assert result.padded == {}
    assert not result.changed()


def test_original_not_mutated():
    env = {"HOST": "prod.db"}
    original = dict(env)
    pad_env(env, REF)
    assert env == original


def test_missing_key_added_with_empty_default():
    env = {"HOST": "prod.db"}
    result = pad_env(env, REF)
    assert "PORT" in result.env
    assert result.env["PORT"] == ""
    assert "PORT" in result.padded


def test_missing_key_added_with_ref_value_when_default_none():
    env = {"HOST": "prod.db"}
    result = pad_env(env, REF, default=None)
    assert result.env["PORT"] == "5432"
    assert result.env["DEBUG"] == "false"


def test_custom_default_used():
    env = {}
    result = pad_env(env, REF, default="PLACEHOLDER")
    for key in REF:
        assert result.env[key] == "PLACEHOLDER"


def test_overwrite_replaces_existing():
    env = {"HOST": "old", "PORT": "9999", "DEBUG": "true"}
    result = pad_env(env, REF, default=None, overwrite=True)
    assert result.env["HOST"] == "localhost"
    assert result.env["PORT"] == "5432"
    assert result.env["DEBUG"] == "false"


def test_overwrite_false_keeps_existing():
    env = {"HOST": "keep-me"}
    result = pad_env(env, REF, default=None, overwrite=False)
    assert result.env["HOST"] == "keep-me"


def test_changed_true_when_keys_padded():
    result = pad_env({}, REF)
    assert result.changed()


def test_summary_no_changes():
    env = dict(REF)
    result = pad_env(env, REF)
    assert "No keys padded" in result.summary()


def test_summary_with_changes():
    result = pad_env({}, REF)
    s = result.summary()
    assert "Padded" in s
    assert str(len(REF)) in s


def test_padded_keys_are_subset_of_ref():
    """All keys recorded in padded must come from the reference dict."""
    env = {"HOST": "prod.db"}
    result = pad_env(env, REF)
    assert set(result.padded.keys()).issubset(set(REF.keys()))


def test_padded_does_not_include_existing_keys():
    """Keys already present in env should not appear in padded, even when overwrite=False."""
    env = {"HOST": "prod.db"}
    result = pad_env(env, REF, overwrite=False)
    assert "HOST" not in result.padded
