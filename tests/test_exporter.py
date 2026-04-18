"""Tests for envguard.exporter."""
import json
import pytest

from envguard.exporter import ExportError, export_env, to_json, to_shell


SAMPLE = {"DB_HOST": "localhost", "APP_ENV": "production", "PORT": "5432"}


def test_to_json_returns_valid_json():
    result = to_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_to_json_sorted_keys():
    result = to_json(SAMPLE)
    keys = list(json.loads(result).keys())
    assert keys == sorted(keys)


def test_to_json_indent():
    result = to_json({"A": "1"}, indent=4)
    assert "    " in result


def test_to_shell_produces_export_statements():
    result = to_shell({"FOO": "bar"})
    assert result == "export FOO='bar'"


def test_to_shell_escapes_single_quotes():
    result = to_shell({"MSG": "it's alive"})
    assert "it'\\''s alive" in result


def test_to_shell_sorted_keys():
    result = to_shell({"Z_VAR": "z", "A_VAR": "a"})
    lines = result.splitlines()
    assert lines[0].startswith("export A_VAR")
    assert lines[1].startswith("export Z_VAR")


def test_export_env_json():
    result = export_env(SAMPLE, "json")
    assert json.loads(result) == SAMPLE


def test_export_env_shell():
    result = export_env({"KEY": "value"}, "shell")
    assert "export KEY='value'" in result


def test_export_env_case_insensitive_format():
    result = export_env({"A": "1"}, "JSON")
    assert json.loads(result) == {"A": "1"}


def test_export_env_unsupported_format_raises():
    with pytest.raises(ExportError, match="Unsupported format"):
        export_env(SAMPLE, "toml")


def test_export_env_empty_variables():
    result = export_env({}, "json")
    assert json.loads(result) == {}


def test_to_shell_empty_value():
    result = to_shell({"EMPTY": ""})
    assert result == "export EMPTY=''"
