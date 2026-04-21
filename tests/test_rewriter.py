"""Tests for envguard.rewriter."""
import pytest

from envguard.rewriter import rewrite_env, write_env_file


@pytest.fixture()
def base():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_no_options_returns_copy(base):
    result = rewrite_env(base)
    assert result.rewritten == base
    assert not result.changed()


def test_original_not_mutated(base):
    original = dict(base)
    rewrite_env(base, set_keys={"HOST": "newhost"}, remove_keys=["DEBUG"])
    assert base == original


def test_set_new_key(base):
    result = rewrite_env(base, set_keys={"USER": "admin"})
    assert result.rewritten["USER"] == "admin"
    assert "USER" in result.added
    assert result.changed()


def test_set_overwrites_existing_key(base):
    result = rewrite_env(base, set_keys={"PORT": "9999"})
    assert result.rewritten["PORT"] == "9999"
    assert "PORT" in result.updated
    assert "PORT" not in result.added


def test_set_same_value_not_marked_updated(base):
    result = rewrite_env(base, set_keys={"PORT": "5432"})
    assert "PORT" not in result.updated
    assert not result.changed()


def test_remove_existing_key(base):
    result = rewrite_env(base, remove_keys=["DEBUG"])
    assert "DEBUG" not in result.rewritten
    assert "DEBUG" in result.removed


def test_remove_missing_key_silently_ignored(base):
    result = rewrite_env(base, remove_keys=["NONEXISTENT"])
    assert result.rewritten == base
    assert not result.changed()


def test_rename_existing_key(base):
    result = rewrite_env(base, rename_keys={"HOST": "DB_HOST"})
    assert "DB_HOST" in result.rewritten
    assert "HOST" not in result.rewritten
    assert "DB_HOST" in result.updated


def test_rename_missing_key_silently_ignored(base):
    result = rewrite_env(base, rename_keys={"MISSING": "NEW"})
    assert result.rewritten == base
    assert not result.changed()


def test_summary_no_changes(base):
    result = rewrite_env(base)
    assert result.summary() == "no changes"


def test_summary_with_changes(base):
    result = rewrite_env(
        base,
        set_keys={"PORT": "9999", "USER": "admin"},
        remove_keys=["DEBUG"],
    )
    summary = result.summary()
    assert "updated" in summary
    assert "added" in summary
    assert "removed" in summary


def test_write_env_file(tmp_path, base):
    path = tmp_path / ".env"
    write_env_file(path, base)
    content = path.read_text()
    for key, value in base.items():
        assert f"{key}={value}" in content


def test_write_env_file_each_key_on_own_line(tmp_path, base):
    path = tmp_path / ".env"
    write_env_file(path, base)
    lines = [l for l in path.read_text().splitlines() if l.strip()]
    assert len(lines) == len(base)
