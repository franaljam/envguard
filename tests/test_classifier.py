import pytest
from envguard.classifier import classify_env, ClassifyResult


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret",
        "AWS_ACCESS_KEY": "key",
        "FEATURE_DARK_MODE": "true",
        "LOG_LEVEL": "INFO",
        "APP_NAME": "myapp",
        "PORT": "8080",
    }


def test_database_keys_classified(mixed_env):
    result = classify_env(mixed_env)
    assert "DB_HOST" in result.keys_in("database")
    assert "DB_PORT" in result.keys_in("database")


def test_auth_key_classified(mixed_env):
    result = classify_env(mixed_env)
    assert "API_KEY" in result.keys_in("auth")


def test_cloud_key_classified(mixed_env):
    result = classify_env(mixed_env)
    assert "AWS_ACCESS_KEY" in result.keys_in("cloud")


def test_feature_flag_classified(mixed_env):
    result = classify_env(mixed_env)
    assert "FEATURE_DARK_MODE" in result.keys_in("feature_flag")


def test_logging_classified(mixed_env):
    result = classify_env(mixed_env)
    assert "LOG_LEVEL" in result.keys_in("logging")


def test_network_classified(mixed_env):
    result = classify_env(mixed_env)
    assert "PORT" in result.keys_in("network")


def test_uncategorized_key(mixed_env):
    result = classify_env(mixed_env)
    assert "APP_NAME" in result.uncategorized


def test_empty_env():
    result = classify_env({})
    assert result.categories == {}
    assert result.uncategorized == []


def test_category_names_sorted(mixed_env):
    result = classify_env(mixed_env)
    names = result.category_names()
    assert names == sorted(names)


def test_summary_contains_category(mixed_env):
    result = classify_env(mixed_env)
    s = result.summary()
    assert "database" in s
    assert "auth" in s


def test_summary_empty_env():
    result = classify_env({})
    assert result.summary() == "No keys classified."
