"""Subprocess integration tests for the segment sub-command."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def envs(tmp_path: Path):
    def _make(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _make


def run(*args: str) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    return subprocess.run(
        [sys.executable, "-m", "envguard", *args],
        capture_output=True,
        text=True,
    )


def test_segment_exit_zero(envs):
    f = envs("test.env", "DB_HOST=localhost\nAPP=myapp\n")
    result = run("segment", f, "--rule", "db:^DB_")
    assert result.returncode == 0


def test_segment_output_contains_summary(envs):
    f = envs("test.env", "DB_HOST=localhost\nDB_PORT=5432\nAPP=myapp\n")
    result = run("segment", f, "--rule", "db:^DB_")
    assert "db" in result.stdout


def test_segment_json_flag_produces_json(envs):
    import json

    f = envs("test.env", "DB_HOST=localhost\nAPP=myapp\n")
    result = run("segment", f, "--rule", "db:^DB_", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "segments" in data
