"""Tests for envguard.differ_encoding."""
import pytest
from envguard.differ_encoding import (
    EncodingChange,
    EncodingDiffResult,
    _detect_escapes,
    _has_non_ascii,
    diff_encoding,
)


# ---------------------------------------------------------------------------
# Unit helpers
# ---------------------------------------------------------------------------

def test_detect_escapes_newline():
    assert "newline" in _detect_escapes("hello\\nworld")


def test_detect_escapes_tab():
    assert "tab" in _detect_escapes("col1\\tcol2")


def test_detect_escapes_none():
    assert _detect_escapes("plain_value") == []


def test_has_non_ascii_true():
    assert _has_non_ascii("caf\u00e9") is True


def test_has_non_ascii_false():
    assert _has_non_ascii("plain") is False


# ---------------------------------------------------------------------------
# diff_encoding
# ---------------------------------------------------------------------------

def _left():
    return {"A": "hello", "B": "line1\\nline2", "C": "caf\u00e9"}


def _right():
    return {"A": "hello", "B": "line1\\nline2", "C": "caf\u00e9"}


def test_identical_envs_no_changes():
    result = diff_encoding(_left(), _right())
    assert not result.has_changes()


def test_added_key_detected():
    left = {"A": "val"}
    right = {"A": "val", "B": "new\\n"}
    result = diff_encoding(left, right)
    assert result.has_changes()
    assert "B" in result.keys_with_changes()


def test_removed_key_detected():
    left = {"A": "val", "B": "old"}
    right = {"A": "val"}
    result = diff_encoding(left, right)
    assert "B" in result.keys_with_changes()


def test_escape_added_detected():
    left = {"MSG": "hello world"}
    right = {"MSG": "hello\\nworld"}
    result = diff_encoding(left, right)
    assert result.has_changes()
    change = result.changes[0]
    assert change.key == "MSG"
    assert "newline" in change.right_escapes
    assert change.left_escapes == []


def test_non_ascii_added_detected():
    left = {"LABEL": "cafe"}
    right = {"LABEL": "caf\u00e9"}
    result = diff_encoding(left, right)
    assert result.has_changes()
    change = result.changes[0]
    assert change.left_non_ascii is False
    assert change.right_non_ascii is True


def test_no_encoding_change_when_values_differ_but_encoding_same():
    left = {"KEY": "foo"}
    right = {"KEY": "bar"}
    result = diff_encoding(left, right)
    assert not result.has_changes()


def test_summary_no_changes():
    result = diff_encoding({"A": "x"}, {"A": "x"})
    assert "No encoding differences" in result.summary()


def test_summary_with_changes():
    left = {"MSG": "hello"}
    right = {"MSG": "hello\\nworld"}
    result = diff_encoding(left, right)
    summary = result.summary()
    assert "MSG" in summary
    assert "1 key" in summary


def test_description_added():
    c = EncodingChange(key="X", left_value=None, right_value="v")
    assert "added" in c.description()


def test_description_removed():
    c = EncodingChange(key="X", left_value="v", right_value=None)
    assert "removed" in c.description()


def test_keys_with_changes_lists_all():
    left = {"A": "x", "B": "y"}
    right = {"A": "x\\t", "B": "y\\n"}
    result = diff_encoding(left, right)
    assert set(result.keys_with_changes()) == {"A", "B"}
