"""Unit tests for cli_differ_schema."""
import argparse
import json
import os
import pytest

from envguard.cli_differ_schema import cmd_schema_diff


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content):
    path.write_text(content)
    return str(path)


def _args(
    left, right, schema=None, verbose=False, no_fail_on_regression=False
):
    ns = argparse.Namespace(
        left=left,
        right=right,
        schema=schema,
        verbose=verbose,
        no_fail_on_regression=no_fail_on_regression,
    )
    return ns


def test_identical_files_exit_zero(tmp_env):
    f = _write(tmp_env / "a.env", "A=1\nB=2\n")
    assert cmd_schema_diff(_args(f, f)) == 0


def test_changed_value_exits_one(tmp_env):
    left = _write(tmp_env / "l.env", "A=old\n")
    right = _write(tmp_env / "r.env", "A=new\n")
    assert cmd_schema_diff(_args(left, right)) == 1


def test_missing_left_file_exits_two(tmp_env):
    right = _write(tmp_env / "r.env", "A=1\n")
    assert cmd_schema_diff(_args("/no/such/file.env", right)) == 2


def test_missing_right_file_exits_two(tmp_env):
    left = _write(tmp_env / "l.env", "A=1\n")
    assert cmd_schema_diff(_args(left, "/no/such/file.env")) == 2


def test_schema_regression_exits_one(tmp_env):
    schema_data = {
        "fields": [
            {"name": "PORT", "required": False, "pattern": "\\d+"}
        ]
    }
    schema_file = tmp_env / "schema.json"
    schema_file.write_text(json.dumps(schema_data))
    left = _write(tmp_env / "l.env", "PORT=8080\n")
    right = _write(tmp_env / "r.env", "PORT=abc\n")
    result = cmd_schema_diff(_args(left, right, schema=str(schema_file)))
    assert result == 1


def test_no_fail_on_regression_flag(tmp_env):
    schema_data = {
        "fields": [
            {"name": "PORT", "required": False, "pattern": "\\d+"}
        ]
    }
    schema_file = tmp_env / "schema.json"
    schema_file.write_text(json.dumps(schema_data))
    left = _write(tmp_env / "l.env", "PORT=8080\n")
    right = _write(tmp_env / "r.env", "PORT=abc\n")
    result = cmd_schema_diff(
        _args(left, right, schema=str(schema_file), no_fail_on_regression=True)
    )
    # still exits 1 because values changed, but not due to regression check
    assert result == 1


def test_bad_schema_file_exits_two(tmp_env):
    left = _write(tmp_env / "l.env", "A=1\n")
    right = _write(tmp_env / "r.env", "A=1\n")
    result = cmd_schema_diff(_args(left, right, schema="/no/schema.json"))
    assert result == 2
