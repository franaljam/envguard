"""Subprocess-level integration tests for the `envguard patch` command."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def envs(tmp_path):
    return tmp_path


def _make(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "envguard", *args],
        capture_output=True,
        text=True,
    )


def test_patch_exit_zero_no_changes(envs):
    f = _make(envs, ".env", "HOST=localhost\n")
    result = run("patch", str(f))
    assert result.returncode == 0


def test_patch_exit_one_on_change(envs):
    f = _make(envs, ".env", "HOST=localhost\n")
    result = run("patch", str(f), "--set", "HOST=prod")
    assert result.returncode == 1


def test_patch_output_contains_new_value(envs):
    f = _make(envs, ".env", "HOST=localhost\nPORT=5432\n")
    result = run("patch", str(f), "--set", "PORT=5433")
    assert "PORT=5433" in result.stdout


def test_patch_delete_removes_key(envs):
    f = _make(envs, ".env", "HOST=localhost\nDEBUG=true\n")
    result = run("patch", str(f), "--delete", "DEBUG")
    assert "DEBUG" not in result.stdout
    assert result.returncode == 1


def test_patch_missing_file_exits_two(envs):
    result = run("patch", str(envs / "ghost.env"))
    assert result.returncode == 2
