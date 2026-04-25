"""Tests for envguard.differ_schema."""
import pytest
from envguard.differ_schema import diff_schema, SchemaDiffResult
from envguard.schema import FieldSchema


def _field(required=False, pattern=None, allowed_values=None):
    return FieldSchema(
        required=required,
        pattern=pattern,
        allowed_values=allowed_values,
    )


def test_identical_envs_no_changes():
    env = {"A": "1", "B": "2"}
    result = diff_schema(env, env.copy())
    assert not result.has_changes()


def test_value_changed_detected():
    left = {"A": "old"}
    right = {"A": "new"}
    result = diff_schema(left, right)
    assert result.has_changes()
    assert result.entries[0].value_changed


def test_key_only_in_left():
    result = diff_schema({"X": "1"}, {})
    entry = result.entries[0]
    assert entry.left_value == "1"
    assert entry.right_value is None


def test_key_only_in_right():
    result = diff_schema({}, {"X": "1"})
    entry = result.entries[0]
    assert entry.left_value is None
    assert entry.right_value == "1"


def test_no_schema_always_valid():
    result = diff_schema({"A": "x"}, {"A": "y"})
    for e in result.entries:
        assert e.left_valid
        assert e.right_valid


def test_pattern_violation_right_side():
    fields = {"PORT": _field(pattern=r"\d+")}
    result = diff_schema({"PORT": "8080"}, {"PORT": "abc"}, schema_fields=fields)
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.left_valid
    assert not entry.right_valid
    assert len(result.validity_regressions()) == 1


def test_pattern_fix_is_improvement():
    fields = {"PORT": _field(pattern=r"\d+")}
    result = diff_schema({"PORT": "bad"}, {"PORT": "9000"}, schema_fields=fields)
    assert len(result.validity_improvements()) == 1
    assert result.validity_regressions() == []


def test_allowed_values_violation():
    fields = {"ENV": _field(allowed_values=["prod", "staging", "dev"])}
    result = diff_schema({"ENV": "prod"}, {"ENV": "local"}, schema_fields=fields)
    entry = next(e for e in result.entries if e.key == "ENV")
    assert entry.left_valid
    assert not entry.right_valid


def test_required_missing_on_right_is_invalid():
    fields = {"DB_URL": _field(required=True)}
    result = diff_schema({"DB_URL": "postgres://"}, {}, schema_fields=fields)
    entry = next(e for e in result.entries if e.key == "DB_URL")
    assert entry.left_valid
    assert not entry.right_valid


def test_summary_contains_key_count():
    result = diff_schema({"A": "1", "B": "2"}, {"A": "1", "B": "3"})
    s = result.summary()
    assert "2 keys" in s
    assert "1 value" in s


def test_schema_fields_stored_on_result():
    fields = {"X": _field(required=True)}
    result = diff_schema({"X": "1"}, {"X": "1"}, schema_fields=fields)
    assert "X" in result.schema_fields
