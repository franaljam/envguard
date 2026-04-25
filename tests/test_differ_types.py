"""Tests for envguard.differ_types."""
import pytest
from envguard.differ_types import TypeChange, TypeDiffResult, _infer_type, diff_types


# --- _infer_type ---

def test_infer_empty():
    assert _infer_type("") == "empty"

def test_infer_bool_true():
    assert _infer_type("true") == "bool"
    assert _infer_type("True") == "bool"
    assert _infer_type("FALSE") == "bool"

def test_infer_int():
    assert _infer_type("42") == "int"
    assert _infer_type("-7") == "int"

def test_infer_float():
    assert _infer_type("3.14") == "float"
    assert _infer_type("-0.5") == "float"

def test_infer_str():
    assert _infer_type("hello") == "str"
    assert _infer_type("localhost:5432") == "str"


# --- diff_types ---

def _left():
    return {"PORT": "8080", "DEBUG": "true", "NAME": "app"}

def _right():
    return {"PORT": "8080", "DEBUG": "true", "NAME": "app"}


def test_identical_envs_no_changes():
    result = diff_types(_left(), _right())
    assert not result.has_changes()
    assert result.summary() == "no changes"


def test_added_key_detected():
    right = {**_left(), "NEW_KEY": "value"}
    result = diff_types(_left(), right)
    assert "NEW_KEY" in result.added
    assert result.has_changes()


def test_removed_key_detected():
    right = {k: v for k, v in _left().items() if k != "NAME"}
    result = diff_types(_left(), right)
    assert "NAME" in result.removed


def test_value_change_same_type():
    right = {**_left(), "NAME": "other"}
    result = diff_types(_left(), right)
    assert len(result.value_changes()) == 1
    assert result.value_changes()[0].key == "NAME"
    assert not result.type_changes()


def test_type_change_int_to_str():
    left = {"PORT": "8080"}
    right = {"PORT": "https://example.com"}
    result = diff_types(left, right)
    tc = result.type_changes()
    assert len(tc) == 1
    assert tc[0].left_type == "int"
    assert tc[0].right_type == "str"
    assert tc[0].is_type_change


def test_type_change_bool_to_str():
    left = {"DEBUG": "true"}
    right = {"DEBUG": "yes"}
    result = diff_types(left, right)
    tc = result.type_changes()
    assert tc[0].left_type == "bool"
    assert tc[0].right_type == "str"


def test_summary_includes_all_categories():
    left = {"A": "1", "B": "hello"}
    right = {"A": "world", "C": "new"}
    result = diff_types(left, right)
    s = result.summary()
    assert "added" in s
    assert "removed" in s
    assert "type change" in s


def test_type_change_is_type_change_false_when_same_type():
    tc = TypeChange("K", "foo", "bar", "str", "str")
    assert not tc.is_type_change


def test_empty_dicts_no_changes():
    result = diff_types({}, {})
    assert not result.has_changes()
