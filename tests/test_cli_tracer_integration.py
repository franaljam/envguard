"""Subprocess integration tests for envguard trace command."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def envs(tmp_path):
    return tmp_path


def _make(p: Path, name: str, content: str) -> Path:
    f = p / name
    f.write_text(content)
    return f


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "envguard", *args],
        capture_output=True,
        text=True,
    )


def test_trace_exit_zero(envs):
    env_file = _make(envs, ".env", "MY_VAR=hello\n")
    _make(envs, "app.py", "os.environ.get('MY_VAR')\n")
    result = run("trace", str(env_file), str(envs))
    assert result.returncode == 0


def test_trace_output_contains_key(envs):
    env_file = _make(envs, ".env", "MY_VAR=hello\n")
    _make(envs, "app.py", "os.environ.get('MY_VAR')\n")
    result = run("trace", str(env_file), str(envs))
    assert "MY_VAR" in result.stdout


def test_trace_warn_unused_nonzero(envs):
    env_file = _make(envs, ".env", "ORPHAN=1\n")
    result = run("trace", str(env_file), str(envs), "--warn-unused")
    assert result.returncode == 1
    assert "ORPHAN" in result.stderr
