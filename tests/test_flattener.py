import pytest
from envguard.flattener import flatten_env, FlattenResult


def test_no_prefix_returns_copy():
    env = {"FOO": "1", "BAR": "2"}
    result = flatten_env(env)
    assert result.env == env
    assert not result.changed()


def test_original_not_mutated():
    env = {"APP__HOST": "localhost"}
    flatten_env(env, prefix="APP")
    assert "APP__HOST" in env


def test_strips_prefix_segment():
    env = {"APP__HOST": "localhost", "APP__PORT": "5432"}
    result = flatten_env(env, prefix="APP")
    assert result.env == {"HOST": "localhost", "PORT": "5432"}
    assert result.changed()


def test_non_matching_keys_kept():
    env = {"APP__HOST": "localhost", "OTHER": "val"}
    result = flatten_env(env, prefix="APP")
    assert "HOST" in result.env
    assert "OTHER" in result.env


def test_renamed_maps_old_to_new():
    env = {"DB__NAME": "mydb"}
    result = flatten_env(env, prefix="DB")
    assert result.renamed == {"DB__NAME": "NAME"}


def test_custom_separator():
    env = {"NS.KEY": "value"}
    result = flatten_env(env, separator=".", prefix="NS")
    assert result.env == {"KEY": "value"}


def test_lowercase_keys():
    env = {"APP__HOST": "localhost"}
    result = flatten_env(env, prefix="APP", lowercase_keys=True)
    assert "host" in result.env


def test_summary_no_changes():
    env = {"FOO": "bar"}
    result = flatten_env(env)
    assert result.summary() == "No keys flattened."


def test_summary_with_changes():
    env = {"SVC__URL": "http://x"}
    result = flatten_env(env, prefix="SVC")
    summary = result.summary()
    assert "SVC__URL" in summary
    assert "URL" in summary


def test_no_prefix_none_does_not_rename_separator_keys():
    env = {"A__B": "1"}
    result = flatten_env(env, prefix=None)
    assert result.env == {"A__B": "1"}
    assert not result.renamed
