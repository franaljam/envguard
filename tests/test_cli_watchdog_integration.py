"""Subprocess integration tests for the watch subcommand."""
import subprocess
import sys
import time
import threading
from pathlib import Path

import pytest


@pytest.fixture
def envs(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FOO=bar\n")
    return tmp_path, p


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envguard", *args],
        capture_output=True,
        text=True,
    )


def test_watch_exit_zero_no_change(envs):
    _, p = envs
    result = run("watch", str(p), "--duration", "0.2", "--interval", "0.05")
    assert result.returncode == 0


def test_watch_output_contains_summary(envs):
    _, p = envs
    result = run("watch", str(p), "--duration", "0.2", "--interval", "0.05")
    assert "No changes detected" in result.stdout


def test_watch_missing_file_exits_two(tmp_path):
    result = run("watch", str(tmp_path / "ghost.env"), "--duration", "0.1")
    assert result.returncode == 2
