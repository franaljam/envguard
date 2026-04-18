"""Integration-style tests that exercise the full CLI pipeline."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def envs(tmp_path):
    base = tmp_path / "base.env"
    target = tmp_path / "target.env"
    schema = tmp_path / "schema.env"
    base.write_text("DB_URL=postgres://localhost\nSECRET=hunter2\nDEBUG=true\n")
    target.write_text("DB_URL=postgres://prod\nSECRET=hunter2\n")
    schema.write_text("DB_URL=\nSECRET=\n")
    return {"base": base, "target": target, "schema": schema, "dir": tmp_path}


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envguard"] + list(args),
        capture_output=True,
        text=True,
    )


def test_diff_subprocess_exit_code_one_on_diff(envs):
    result = run("diff", str(envs["base"]), str(envs["target"]), "--no-color")
    assert result.returncode == 1
    assert "DEBUG" in result.stdout


def test_diff_subprocess_exit_code_zero_identical(envs):
    result = run("diff", str(envs["base"]), str(envs["base"]), "--no-color")
    assert result.returncode == 0


def test_validate_subprocess_passes(envs):
    result = run("validate", str(envs["target"]), str(envs["schema"]), "--no-color")
    assert result.returncode == 0


def test_validate_subprocess_fails(envs):
    incomplete = envs["dir"] / "incomplete.env"
    incomplete.write_text("DB_URL=postgres://prod\n")
    result = run("validate", str(incomplete), str(envs["schema"]), "--no-color")
    assert result.returncode == 1
    assert "SECRET" in result.stdout


def test_unknown_command_exits_nonzero():
    result = run("unknown")
    assert result.returncode != 0
