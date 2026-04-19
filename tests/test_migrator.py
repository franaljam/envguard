import pytest
from envguard.migrator import migrate_env, MigrationResult


BASE = {"DB_HOST": "localhost", "DB_PORT": "5432", "OLD_KEY": "value"}


def test_no_operations_returns_copy():
    result = migrate_env(BASE)
    assert result.migrated == BASE
    assert not result.changed()


def test_rename_existing_key():
    result = migrate_env(BASE, renames={"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in result.migrated
    assert "OLD_KEY" not in result.migrated
    assert result.renamed == [("OLD_KEY", "NEW_KEY")]


def test_rename_missing_key_skipped():
    result = migrate_env(BASE, renames={"MISSING": "NEW_KEY"})
    assert result.renamed == []
    assert "NEW_KEY" not in result.migrated


def test_remove_existing_key():
    result = migrate_env(BASE, removals=["DB_PORT"])
    assert "DB_PORT" not in result.migrated
    assert result.removed == ["DB_PORT"]


def test_remove_missing_key_skipped():
    result = migrate_env(BASE, removals=["GHOST"])
    assert result.removed == []


def test_add_new_key():
    result = migrate_env(BASE, additions={"CACHE_URL": "redis://localhost"})
    assert result.migrated["CACHE_URL"] == "redis://localhost"
    assert result.added == ["CACHE_URL"]


def test_add_existing_key_not_overwritten():
    result = migrate_env(BASE, additions={"DB_HOST": "newhost"})
    assert result.migrated["DB_HOST"] == "localhost"
    assert result.added == []


def test_original_not_mutated():
    original = dict(BASE)
    migrate_env(BASE, renames={"DB_HOST": "DATABASE_HOST"}, removals=["DB_PORT"])
    assert BASE == original


def test_combined_operations():
    result = migrate_env(
        BASE,
        renames={"OLD_KEY": "NEW_KEY"},
        removals=["DB_PORT"],
        additions={"FEATURE_FLAG": "true"},
    )
    assert "NEW_KEY" in result.migrated
    assert "DB_PORT" not in result.migrated
    assert result.migrated["FEATURE_FLAG"] == "true"
    assert result.changed()


def test_summary_no_changes():
    result = migrate_env(BASE)
    assert result.summary() == "no changes"


def test_summary_with_changes():
    result = migrate_env(
        BASE,
        renames={"OLD_KEY": "NEW_KEY"},
        removals=["DB_PORT"],
        additions={"X": "1"},
    )
    s = result.summary()
    assert "renamed" in s
    assert "removed" in s
    assert "added" in s
