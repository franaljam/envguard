"""Integration tests for envguard schema-diff subcommand."""
import json
import subprocess
import sys
import pytest


@pytest.fixture
def envs(tmp_path):
    def _make(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _make


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envguard", "schema-diff", *args],
        capture_output=True,
        text=True,
    )


def test_schema_diff_exit_zero_identical(envs):
    f = envs("a.env", "KEY=value\n")
    proc = run(f, f)
    assert proc.returncode == 0


def test_schema_diff_exit_one_on_diff(envs):
    left = envs("l.env", "KEY=old\n")
    right = envs("r.env", "KEY=new\n")
    proc = run(left, right)
    assert proc.returncode == 1


def test_schema_diff_output_contains_summary(envs):
    left = envs("l.env", "A=1\nB=2\n")
    right = envs("r.env", "A=1\nB=3\n")
    proc = run(left, right)
    assert "keys compared" in proc.stdout


def test_schema_diff_with_schema_regression(envs, tmp_path):
    schema_data = {"fields": [{"name": "PORT", "required": False, "pattern": "\\d+"}]}
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema_data))
    left = envs("l.env", "PORT=8080\n")
    right = envs("r.env", "PORT=bad\n")
    proc = run(left, right, "--schema", str(schema_file))
    assert proc.returncode == 1
    assert "regression" in proc.stderr
