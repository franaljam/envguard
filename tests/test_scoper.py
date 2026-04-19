import pytest
from envguard.scoper import scope_env, ScopeResult


def _env():
    return {
        "PROD_DB_HOST": "db.prod",
        "PROD_DB_PORT": "5432",
        "DEV_DB_HOST": "localhost",
        "APP_NAME": "myapp",
        "DEBUG": "false",
    }


def test_returns_scope_result():
    result = scope_env(_env(), "PROD")
    assert isinstance(result, ScopeResult)


def test_matched_keys_filtered_by_prefix():
    result = scope_env(_env(), "PROD")
    assert set(result.env.keys()) == {"DB_HOST", "DB_PORT"}


def test_strip_prefix_false_keeps_full_key():
    result = scope_env(_env(), "PROD", strip_prefix=False)
    assert "PROD_DB_HOST" in result.env


def test_unmatched_keys_collected():
    result = scope_env(_env(), "PROD")
    assert "DEV_DB_HOST" in result.unmatched_keys
    assert "APP_NAME" in result.unmatched_keys


def test_extra_keys_always_included():
    result = scope_env(_env(), "PROD", extra_keys=["APP_NAME"])
    assert "APP_NAME" in result.env
    assert result.env["APP_NAME"] == "myapp"


def test_extra_key_not_in_unmatched():
    result = scope_env(_env(), "PROD", extra_keys=["APP_NAME"])
    assert "APP_NAME" not in result.unmatched_keys


def test_count_matches_matched_keys():
    result = scope_env(_env(), "PROD")
    assert result.count() == len(result.matched_keys)


def test_summary_contains_scope_name():
    result = scope_env(_env(), "PROD")
    assert "PROD" in result.summary()


def test_empty_env_returns_empty_result():
    result = scope_env({}, "PROD")
    assert result.env == {}
    assert result.matched_keys == []


def test_no_match_returns_all_unmatched():
    result = scope_env(_env(), "STAGING")
    assert result.env == {}
    assert len(result.unmatched_keys) == len(_env())


def test_original_not_mutated():
    original = _env()
    scope_env(original, "PROD")
    assert "PROD_DB_HOST" in original
