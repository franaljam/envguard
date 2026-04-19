import pytest
from envguard.planner import plan_env, PlanResult


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_no_actions_returns_copy():
    result = plan_env(BASE)
    assert result.preview == BASE
    assert not result.changed()


def test_original_not_mutated():
    env = dict(BASE)
    plan_env(env, set_keys={"NEW": "val"}, delete_keys=["PORT"])
    assert env == BASE


def test_set_new_key():
    result = plan_env(BASE, set_keys={"NEW_KEY": "newval"})
    assert result.preview["NEW_KEY"] == "newval"
    assert result.changed()


def test_set_overwrites_existing():
    result = plan_env(BASE, set_keys={"HOST": "remotehost"})
    assert result.preview["HOST"] == "remotehost"


def test_delete_existing_key():
    result = plan_env(BASE, delete_keys=["DEBUG"])
    assert "DEBUG" not in result.preview
    assert result.changed()


def test_delete_missing_key_silently_ignored():
    result = plan_env(BASE, delete_keys=["NONEXISTENT"])
    assert result.preview == BASE
    assert not result.changed()
    assert len(result.actions) == 0


def test_rename_existing_key():
    result = plan_env(BASE, rename_keys={"PORT": "DB_PORT"})
    assert "PORT" not in result.preview
    assert result.preview["DB_PORT"] == "5432"


def test_rename_missing_key_skipped():
    result = plan_env(BASE, rename_keys={"MISSING": "NEW"})
    assert "NEW" not in result.preview
    assert len(result.actions) == 0


def test_combined_actions():
    result = plan_env(
        BASE,
        set_keys={"EXTRA": "1"},
        delete_keys=["DEBUG"],
        rename_keys={"HOST": "DB_HOST"},
    )
    assert result.preview["EXTRA"] == "1"
    assert "DEBUG" not in result.preview
    assert "DB_HOST" in result.preview
    assert len(result.actions) == 3


def test_summary_no_actions():
    result = plan_env(BASE)
    assert "No planned changes" in result.summary()


def test_summary_lists_actions():
    result = plan_env(BASE, set_keys={"X": "1"}, delete_keys=["PORT"])
    s = result.summary()
    assert "SET X=1" in s
    assert "DELETE PORT" in s
