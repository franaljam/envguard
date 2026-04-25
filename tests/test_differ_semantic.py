"""Tests for envguard.differ_semantic."""
import pytest

from envguard.differ_semantic import (
    SemanticChange,
    SemanticDiffResult,
    _infer_semantic_type,
    _normalize,
    diff_semantic,
)


# ---------------------------------------------------------------------------
# _infer_semantic_type
# ---------------------------------------------------------------------------

def test_infer_empty():
    assert _infer_semantic_type("") == "empty"


def test_infer_boolean():
    for v in ("true", "True", "false", "yes", "no", "1", "0", "on", "off"):
        assert _infer_semantic_type(v) == "boolean", v


def test_infer_integer():
    assert _infer_semantic_type("42") == "integer"
    assert _infer_semantic_type("-7") == "integer"


def test_infer_float():
    assert _infer_semantic_type("3.14") == "float"


def test_infer_list():
    assert _infer_semantic_type("a,b,c") == "list"


def test_infer_url():
    assert _infer_semantic_type("https://example.com") == "url"


def test_infer_string():
    assert _infer_semantic_type("hello") == "string"


# ---------------------------------------------------------------------------
# _normalize
# ---------------------------------------------------------------------------

def test_normalize_true_variants():
    for v in ("true", "True", "yes", "YES", "1", "on", "ON"):
        assert _normalize(v) == "true", v


def test_normalize_false_variants():
    for v in ("false", "False", "no", "0", "off"):
        assert _normalize(v) == "false", v


def test_normalize_strips_whitespace():
    assert _normalize("  hello  ") == "hello"


# ---------------------------------------------------------------------------
# diff_semantic
# ---------------------------------------------------------------------------

def _left():
    return {"A": "true", "B": "42", "C": "hello", "D": "only_left"}


def _right():
    return {"A": "yes", "B": "99", "C": "hello", "E": "only_right"}


def test_identical_envs_no_changes():
    env = {"X": "1", "Y": "2"}
    result = diff_semantic(env, env.copy())
    assert not result.has_changes()
    assert result.summary() == "no changes"


def test_left_only_key_detected():
    result = diff_semantic(_left(), _right())
    assert "D" in result.left_only


def test_right_only_key_detected():
    result = diff_semantic(_left(), _right())
    assert "E" in result.right_only


def test_semantically_equal_boolean_variants():
    result = diff_semantic({"FLAG": "true"}, {"FLAG": "yes"})
    assert len(result.changes) == 1
    assert result.changes[0].semantically_equal is True
    assert result.meaningful_changes() == []


def test_meaningful_change_detected():
    result = diff_semantic({"PORT": "42"}, {"PORT": "99"})
    assert len(result.meaningful_changes()) == 1


def test_type_change_detected():
    result = diff_semantic({"VAL": "true"}, {"VAL": "hello"})
    assert result.changes[0].type_changed is True


def test_summary_reports_meaningful_and_trivial():
    result = diff_semantic(
        {"A": "true", "B": "1"},
        {"A": "yes", "B": "2"},
    )
    s = result.summary()
    assert "meaningful" in s
    assert "trivial" in s
