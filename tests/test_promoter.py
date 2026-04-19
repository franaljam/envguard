import pytest
from envguard.promoter import promote_env, PromoteResult


SOURCE = {"DB_HOST": "prod-db", "DB_PORT": "5432", "NEW_KEY": "hello"}
TARGET = {"DB_HOST": "staging-db", "APP_ENV": "staging"}


def test_new_keys_promoted():
    r = promote_env(SOURCE, TARGET)
    assert "DB_PORT" in r.promoted
    assert "NEW_KEY" in r.promoted


def test_existing_key_skipped_by_default():
    r = promote_env(SOURCE, TARGET)
    assert "DB_HOST" in r.skipped
    assert r.merged["DB_HOST"] == "staging-db"


def test_overwrite_replaces_existing():
    r = promote_env(SOURCE, TARGET, overwrite=True)
    assert "DB_HOST" in r.overwritten
    assert r.merged["DB_HOST"] == "prod-db"


def test_explicit_keys_limits_promotion():
    r = promote_env(SOURCE, TARGET, keys=["NEW_KEY"])
    assert "NEW_KEY" in r.promoted
    assert "DB_PORT" not in r.promoted
    assert "DB_PORT" not in r.skipped


def test_missing_explicit_key_silently_ignored():
    r = promote_env(SOURCE, TARGET, keys=["DOES_NOT_EXIST"])
    assert not r.promoted
    assert not r.skipped


def test_merged_contains_all_target_keys():
    r = promote_env(SOURCE, TARGET)
    assert "APP_ENV" in r.merged


def test_original_dicts_not_mutated():
    src = dict(SOURCE)
    tgt = dict(TARGET)
    promote_env(src, tgt)
    assert src == SOURCE
    assert tgt == TARGET


def test_changed_true_when_promoted():
    r = promote_env(SOURCE, TARGET)
    assert r.changed()


def test_changed_false_when_all_skipped():
    r = promote_env({"DB_HOST": "x"}, TARGET)
    assert not r.changed()


def test_summary_contains_env_labels():
    r = promote_env(SOURCE, TARGET, source_env="prod", target_env="staging")
    s = r.summary()
    assert "prod" in s
    assert "staging" in s
