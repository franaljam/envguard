import pytest
from envguard.splitter import split_env, SplitResult


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "CACHE_URL": "redis://localhost",
        "CACHE_TTL": "300",
        "APP_NAME": "envguard",
        "STANDALONE": "yes",
    }


def test_split_by_explicit_prefixes(mixed_env):
    result = split_env(mixed_env, prefixes=["DB", "CACHE"])
    assert "DB" in result.groups
    assert "CACHE" in result.groups
    assert set(result.groups["DB"]) == {"DB_HOST", "DB_PORT"}
    assert set(result.groups["CACHE"]) == {"CACHE_URL", "CACHE_TTL"}


def test_ungrouped_keys_collected(mixed_env):
    result = split_env(mixed_env, prefixes=["DB", "CACHE"])
    assert "APP_NAME" in result.ungrouped
    assert "STANDALONE" in result.ungrouped


def test_strip_prefix_removes_prefix(mixed_env):
    result = split_env(mixed_env, prefixes=["DB"], strip_prefix=True)
    assert "HOST" in result.groups["DB"]
    assert "PORT" in result.groups["DB"]
    assert result.groups["DB"]["HOST"] == "localhost"


def test_auto_detect_prefixes(mixed_env):
    result = split_env(mixed_env)
    assert "DB" in result.groups
    assert "CACHE" in result.groups


def test_auto_detect_single_occurrence_not_grouped():
    env = {"DB_HOST": "localhost", "STANDALONE": "yes"}
    result = split_env(env)
    assert "DB" not in result.groups
    assert "STANDALONE" in result.ungrouped


def test_group_names_sorted(mixed_env):
    result = split_env(mixed_env, prefixes=["DB", "CACHE"])
    assert result.group_names() == ["CACHE", "DB"]


def test_summary_output(mixed_env):
    result = split_env(mixed_env, prefixes=["DB", "CACHE"])
    s = result.summary()
    assert "CACHE" in s
    assert "DB" in s
    assert "2 group(s)" in s


def test_original_not_mutated(mixed_env):
    original = dict(mixed_env)
    split_env(mixed_env, prefixes=["DB"])
    assert mixed_env == original


def test_empty_env():
    result = split_env({}, prefixes=["DB"])
    assert result.groups == {}
    assert result.ungrouped == {}
