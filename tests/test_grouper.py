import pytest
from envguard.grouper import group_env, GroupResult


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "mydb",
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PORT": "6379",
    "APP_ENV": "production",
    "DEBUG": "false",
}


def test_explicit_prefixes_group_correctly():
    result = group_env(ENV, prefixes=["DB", "REDIS"])
    assert set(result.groups["DB"]) == {"DB_HOST", "DB_PORT", "DB_NAME"}
    assert set(result.groups["REDIS"]) == {"REDIS_HOST", "REDIS_PORT"}


def test_ungrouped_keys_collected():
    result = group_env(ENV, prefixes=["DB", "REDIS"])
    assert "APP_ENV" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_auto_detect_prefixes():
    result = group_env(ENV)
    assert "DB" in result.groups
    assert "REDIS" in result.groups


def test_auto_detect_single_occurrence_not_grouped():
    env = {"DB_HOST": "h", "DB_PORT": "p", "LONE_KEY": "v"}
    result = group_env(env)
    assert "LONE" not in result.groups
    assert "LONE_KEY" in result.ungrouped


def test_group_names_sorted():
    result = group_env(ENV, prefixes=["REDIS", "DB"])
    assert result.group_names() == ["DB", "REDIS"]


def test_summary_contains_group_info():
    result = group_env(ENV, prefixes=["DB", "REDIS"])
    s = result.summary()
    assert "[DB]" in s
    assert "[REDIS]" in s
    assert "ungrouped" in s


def test_empty_env():
    result = group_env({}, prefixes=["DB"])
    assert result.groups["DB"] == {}
    assert result.ungrouped == {}


def test_no_prefixes_all_ungrouped():
    env = {"FOO": "1", "BAR": "2"}
    result = group_env(env, prefixes=[])
    assert result.ungrouped == env
    assert result.groups == {}
