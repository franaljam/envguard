import pytest
from envguard.schema import FieldSchema, SchemaResult, SchemaViolation, validate_schema


def test_valid_env_no_violations():
    schema = {"HOST": FieldSchema(), "PORT": FieldSchema()}
    result = validate_schema({"HOST": "localhost", "PORT": "8080"}, schema)
    assert result.is_valid()
    assert result.violations == []


def test_missing_required_key():
    schema = {"HOST": FieldSchema(required=True)}
    result = validate_schema({}, schema)
    assert not result.is_valid()
    assert any(v.key == "HOST" for v in result.errors())


def test_optional_missing_key_no_violation():
    schema = {"DEBUG": FieldSchema(required=False)}
    result = validate_schema({}, schema)
    assert result.is_valid()


def test_pattern_match_passes():
    schema = {"PORT": FieldSchema(pattern=r"\d+")}
    result = validate_schema({"PORT": "8080"}, schema)
    assert result.is_valid()


def test_pattern_match_fails():
    schema = {"PORT": FieldSchema(pattern=r"\d+")}
    result = validate_schema({"PORT": "abc"}, schema)
    assert not result.is_valid()
    assert any(v.key == "PORT" for v in result.errors())


def test_allowed_values_passes():
    schema = {"ENV": FieldSchema(allowed_values=["dev", "prod", "staging"])}
    result = validate_schema({"ENV": "prod"}, schema)
    assert result.is_valid()


def test_allowed_values_fails():
    schema = {"ENV": FieldSchema(allowed_values=["dev", "prod"])}
    result = validate_schema({"ENV": "test"}, schema)
    assert not result.is_valid()
    assert any("allowed values" in v.message for v in result.errors())


def test_non_empty_fails_on_empty_string():
    schema = {"SECRET": FieldSchema(non_empty=True)}
    result = validate_schema({"SECRET": ""}, schema)
    assert not result.is_valid()


def test_non_empty_passes_with_value():
    schema = {"SECRET": FieldSchema(non_empty=True)}
    result = validate_schema({"SECRET": "abc"}, schema)
    assert result.is_valid()


def test_summary_ok():
    result = SchemaResult()
    assert result.summary() == "Schema OK"


def test_summary_with_errors():
    result = SchemaResult(violations=[SchemaViolation("X", "msg", "error")])
    assert "1 error" in result.summary()
