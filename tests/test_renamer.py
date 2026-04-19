import pytest
from envguard.renamer import rename_env, RenameResult


ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_KEY": "secret"}


def test_no_renames_returns_copy():
    result = rename_env(ENV, {})
    assert result.renamed == ENV
    assert result.applied == []
    assert result.skipped == []
    assert not result.changed()


def test_single_rename():
    result = rename_env(ENV, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.renamed
    assert "DB_HOST" not in result.renamed
    assert result.renamed["DATABASE_HOST"] == "localhost"
    assert ("DB_HOST", "DATABASE_HOST") in result.applied
    assert result.changed()


def test_multiple_renames():
    result = rename_env(ENV, {"DB_HOST": "DATABASE_HOST", "APP_KEY": "APPLICATION_KEY"})
    assert "DATABASE_HOST" in result.renamed
    assert "APPLICATION_KEY" in result.renamed
    assert "DB_HOST" not in result.renamed
    assert "APP_KEY" not in result.renamed
    assert len(result.applied) == 2


def test_missing_key_is_skipped():
    result = rename_env(ENV, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" not in result.renamed
    assert "NEW_KEY" not in result.renamed
    assert "MISSING_KEY" in result.skipped
    assert not result.changed()


def test_original_not_mutated():
    original = dict(ENV)
    rename_env(ENV, {"DB_HOST": "DATABASE_HOST"})
    assert ENV == original


def test_values_preserved_after_rename():
    result = rename_env(ENV, {"DB_PORT": "DATABASE_PORT"})
    assert result.renamed["DATABASE_PORT"] == "5432"


def test_summary_shows_renames_and_skips():
    result = rename_env(ENV, {"DB_HOST": "DATABASE_HOST", "GHOST": "SPIRIT"})
    s = result.summary()
    assert "DB_HOST" in s
    assert "DATABASE_HOST" in s
    assert "GHOST" in s


def test_summary_no_renames():
    result = rename_env(ENV, {})
    assert result.summary() == "No renames applied."


def test_unchanged_keys_preserved():
    result = rename_env(ENV, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_PORT" in result.renamed
    assert "APP_KEY" in result.renamed
