import pytest
from envguard.patcher import patch_env, PatchResult


@pytest.fixture()
def base():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_no_options_returns_copy(base):
    result = patch_env(base)
    assert result.env == base
    assert not result.changed()


def test_original_not_mutated(base):
    original = dict(base)
    patch_env(base, set_keys={"HOST": "prod.db"}, delete_keys=["DEBUG"])
    assert base == original


def test_set_new_key(base):
    result = patch_env(base, set_keys={"NEW_KEY": "hello"})
    assert result.env["NEW_KEY"] == "hello"
    assert result.changed()
    action = result.actions[0]
    assert action.operation == "set"
    assert action.old_value is None
    assert action.new_value == "hello"


def test_set_overwrites_existing(base):
    result = patch_env(base, set_keys={"HOST": "prod.db"})
    assert result.env["HOST"] == "prod.db"
    action = result.actions[0]
    assert action.old_value == "localhost"
    assert action.new_value == "prod.db"


def test_delete_existing_key(base):
    result = patch_env(base, delete_keys=["DEBUG"])
    assert "DEBUG" not in result.env
    assert result.changed()
    action = result.actions[0]
    assert action.operation == "delete"
    assert action.old_value == "true"


def test_delete_missing_key_silently_ignored(base):
    result = patch_env(base, delete_keys=["NONEXISTENT"])
    assert not result.changed()


def test_combined_set_and_delete(base):
    result = patch_env(base, set_keys={"PORT": "5433"}, delete_keys=["DEBUG"])
    assert result.env["PORT"] == "5433"
    assert "DEBUG" not in result.env
    assert len(result.actions) == 2


def test_summary_no_changes(base):
    result = patch_env(base)
    assert result.summary() == "No patches applied."


def test_summary_with_changes(base):
    result = patch_env(base, set_keys={"HOST": "prod"}, delete_keys=["DEBUG"])
    summary = result.summary()
    assert "2 patch(es)" in summary
    assert "updated" in summary
    assert "deleted" in summary


def test_summary_new_key(base):
    result = patch_env(base, set_keys={"BRAND_NEW": "val"})
    assert "added" in result.summary()
