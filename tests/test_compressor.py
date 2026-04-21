import pytest
from envguard.compressor import compress_env, CompressResult


def _env(**kwargs):
    return dict(kwargs)


def test_no_redundancy_returns_copy():
    env = _env(A="1", B="2", C="3")
    result = compress_env(env)
    assert result.compressed == env
    assert result.removed == []
    assert not result.changed()


def test_original_not_mutated():
    env = _env(A="hello", B="hello")
    compress_env(env)
    assert env == {"A": "hello", "B": "hello"}


def test_duplicate_value_removed():
    env = _env(A="same", B="same")
    result = compress_env(env, remove_duplicates=True)
    assert result.changed()
    # One of the two should be removed
    assert len(result.removed) == 1
    assert len(result.compressed) == 1


def test_duplicate_value_disabled():
    env = _env(A="same", B="same")
    result = compress_env(env, remove_duplicates=False, remove_interpolated=False)
    assert not result.changed()
    assert result.compressed == env


def test_interpolated_reference_removed():
    env = _env(BASE_URL="http://example.com", URL="${BASE_URL}")
    result = compress_env(env, remove_interpolated=True, remove_duplicates=False)
    assert "URL" in result.removed
    assert "BASE_URL" in result.compressed


def test_plain_dollar_reference_removed():
    env = _env(HOST="localhost", DB_HOST="$HOST")
    result = compress_env(env, remove_interpolated=True, remove_duplicates=False)
    assert "DB_HOST" in result.removed


def test_interpolated_disabled_keeps_reference():
    env = _env(HOST="localhost", DB_HOST="${HOST}")
    result = compress_env(env, remove_interpolated=False, remove_duplicates=False)
    assert not result.changed()


def test_explicit_keys_removed():
    env = _env(A="1", B="2", C="3")
    result = compress_env(env, explicit_keys=["B"], remove_duplicates=False, remove_interpolated=False)
    assert "B" in result.removed
    assert "B" not in result.compressed
    assert result.reasons["B"] == "explicitly removed"


def test_explicit_missing_key_silently_ignored():
    env = _env(A="1")
    result = compress_env(env, explicit_keys=["MISSING"], remove_duplicates=False, remove_interpolated=False)
    assert result.removed == []


def test_empty_values_not_considered_duplicate():
    env = _env(A="", B="")
    result = compress_env(env, remove_duplicates=True)
    assert "A" not in result.removed
    assert "B" not in result.removed


def test_summary_no_changes():
    env = _env(A="1")
    result = compress_env(env)
    assert "compact" in result.summary()


def test_summary_with_changes():
    env = _env(A="dup", B="dup")
    result = compress_env(env)
    assert "Removed" in result.summary()
