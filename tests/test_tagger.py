import pytest
from envguard.tagger import tag_env, TagResult


def _env(**kwargs):
    return {k: v for k, v in kwargs.items()}


def test_secret_key_gets_secret_tag():
    r = tag_env({"DB_PASSWORD": "hunter2"})
    assert "secret" in r.tags["DB_PASSWORD"]


def test_token_key_gets_secret_tag():
    r = tag_env({"AUTH_TOKEN": "abc"})
    assert "secret" in r.tags["AUTH_TOKEN"]


def test_plain_key_gets_config_tag():
    r = tag_env({"APP_PORT": "8080"})
    assert "config" in r.tags["APP_PORT"]
    assert "secret" not in r.tags["APP_PORT"]


def test_feature_flag_key():
    r = tag_env({"ENABLE_DARK_MODE": "true"})
    assert "feature-flag" in r.tags["ENABLE_DARK_MODE"]


def test_feature_flag_not_also_config():
    r = tag_env({"FEATURE_X": "1"})
    assert "config" not in r.tags["FEATURE_X"]


def test_keys_with_tag_filters_correctly():
    r = tag_env({"DB_SECRET": "x", "APP_NAME": "y", "ENABLE_FF": "1"})
    secrets = r.keys_with_tag("secret")
    assert "DB_SECRET" in secrets
    assert "APP_NAME" not in secrets


def test_extra_tags_applied():
    r = tag_env({"APP_NAME": "myapp"}, extra_tags={"APP_NAME": {"custom"}})
    assert "custom" in r.tags["APP_NAME"]


def test_summary_no_keys():
    r = tag_env({})
    assert r.summary() == "No tags assigned."


def test_summary_lists_keys():
    r = tag_env({"APP_PORT": "8080"})
    s = r.summary()
    assert "APP_PORT" in s
    assert "config" in s


def test_empty_env_returns_empty_tags():
    r = tag_env({})
    assert r.tags == {}
