import pytest
from envguard.transformer import (
    transform_env,
    rename_keys,
    TransformError,
    TransformResult,
)


SAMPLE = {"DB_HOST": "  localhost  ", "API_KEY": "secret", "EMPTY": ""}


def test_no_transforms_returns_copy():
    result = transform_env(SAMPLE)
    assert result.transformed == SAMPLE
    assert result.applied == []


def test_strip_whitespace():
    result = transform_env(SAMPLE, strip=True)
    assert result.transformed["DB_HOST"] == "localhost"
    assert result.transformed["API_KEY"] == "secret"
    assert "strip_whitespace" in result.applied


def test_uppercase_values():
    env = {"KEY": "hello"}
    result = transform_env(env, uppercase_values=True)
    assert result.transformed["KEY"] == "HELLO"


def test_mask_non_empty():
    result = transform_env(SAMPLE, mask=True)
    assert result.transformed["API_KEY"] == "***"
    assert result.transformed["EMPTY"] == ""


def test_multiple_transforms_applied_in_order():
    env = {"X": "  hello  "}
    result = transform_env(env, strip=True, uppercase_values=True)
    assert result.transformed["X"] == "HELLO"
    assert len(result.applied) == 2


def test_changed_keys_reports_modified():
    env = {"A": "  val  ", "B": "clean"}
    result = transform_env(env, strip=True)
    assert "A" in result.changed_keys()
    assert "B" not in result.changed_keys()


def test_original_not_mutated():
    env = {"K": "  v  "}
    transform_env(env, strip=True)
    assert env["K"] == "  v  "


def test_rename_keys_adds_prefix():
    env = {"HOST": "localhost", "PORT": "5432"}
    renamed = rename_keys(env, "APP_")
    assert "APP_HOST" in renamed
    assert "APP_PORT" in renamed
    assert "HOST" not in renamed


def test_rename_keys_preserves_values():
    env = {"FOO": "bar"}
    renamed = rename_keys(env, "X_")
    assert renamed["X_FOO"] == "bar"


def test_transform_result_is_dataclass():
    result = transform_env({"A": "1"})
    assert isinstance(result, TransformResult)
