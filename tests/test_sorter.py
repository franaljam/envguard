import pytest
from envguard.sorter import sort_env, SortResult


ENV = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}


def test_sort_alphabetically():
    result = sort_env(ENV)
    assert result.order == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_reverse():
    result = sort_env(ENV, reverse=True)
    assert result.order == ["ZEBRA", "MANGO", "APPLE"]


def test_changed_detects_reorder():
    result = sort_env(ENV)
    assert result.changed() is True


def test_no_change_when_already_sorted():
    env = {"A": "1", "B": "2", "C": "3"}
    result = sort_env(env)
    assert result.changed() is False


def test_sorted_env_has_correct_values():
    result = sort_env(ENV)
    assert result.sorted_env["APPLE"] == "2"
    assert result.sorted_env["ZEBRA"] == "1"


def test_original_not_mutated():
    env = {"Z": "z", "A": "a"}
    sort_env(env)
    assert list(env.keys()) == ["Z", "A"]


def test_group_sort_puts_prefixed_keys_first():
    env = {"DB_HOST": "h", "APP_NAME": "n", "CACHE_URL": "u", "DB_PORT": "p"}
    result = sort_env(env, groups=["APP", "DB"])
    order = result.order
    assert order.index("APP_NAME") < order.index("DB_HOST")
    assert order.index("DB_HOST") < order.index("CACHE_URL")


def test_group_sort_ungrouped_keys_last():
    env = {"ZEBRA": "1", "APP_X": "2"}
    result = sort_env(env, groups=["APP"])
    assert result.order[0] == "APP_X"
    assert result.order[1] == "ZEBRA"
