import pytest
from envguard.redactor import (
    RedactorConfig,
    redact_env,
    redacted_keys,
    REDACT_PLACEHOLDER,
)


ENV = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "API_KEY": "abc123",
    "SECRET_TOKEN": "xyz",
    "PORT": "8080",
    "AUTH_TOKEN": "tok",
}


def test_non_sensitive_values_unchanged():
    result = redact_env(ENV)
    assert result["APP_NAME"] == "myapp"
    assert result["PORT"] == "8080"


def test_sensitive_values_redacted():
    result = redact_env(ENV)
    assert result["DB_PASSWORD"] == REDACT_PLACEHOLDER
    assert result["API_KEY"] == REDACT_PLACEHOLDER
    assert result["SECRET_TOKEN"] == REDACT_PLACEHOLDER
    assert result["AUTH_TOKEN"] == REDACT_PLACEHOLDER


def test_original_dict_not_mutated():
    original = dict(ENV)
    redact_env(original)
    assert original["DB_PASSWORD"] == "s3cr3t"


def test_redacted_keys_returns_correct_keys():
    keys = redacted_keys(ENV)
    assert "DB_PASSWORD" in keys
    assert "API_KEY" in keys
    assert "APP_NAME" not in keys
    assert "PORT" not in keys


def test_custom_placeholder():
    cfg = RedactorConfig(placeholder="[hidden]")
    result = redact_env(ENV, cfg)
    assert result["DB_PASSWORD"] == "[hidden]"


def test_custom_patterns():
    cfg = RedactorConfig(patterns=[r"port"])
    result = redact_env(ENV, cfg)
    assert result["PORT"] == REDACT_PLACEHOLDER
    assert result["DB_PASSWORD"] == "s3cr3t"  # not matched by custom pattern


def test_empty_env():
    assert redact_env({}) == {}
    assert redacted_keys({}) == []


def test_case_insensitive_matching():
    env = {"db_password": "val", "DbPassword": "val2"}
    keys = redacted_keys(env)
    assert "db_password" in keys
    assert "DbPassword" in keys
