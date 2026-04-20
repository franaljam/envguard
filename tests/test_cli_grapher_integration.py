"""Integration tests for `python -m envguard graph` subcommand."""
import subprocess
import sys
import os
import pytest


@pytest.fixture()
def envs(tmp_path):
    return tmp_path


def _make(directory, name, content):
    p = directory / name
    p.write_text(content)
    return str(p)


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envguard", *args],
        capture_output=True,
        text=True,
    )


def test_graph_exit_zero_no_cycles(envs):
    f = _make(envs, ".env", "HOST=localhost\nPORT=8080\n")
    result = run("graph", f)
    assert result.returncode == 0


def test_graph_exit_one_on_cycle(envs):
    f = _make(envs, ".env", "A=${B}\nB=${A}\n")
    result = run("graph", f)
    assert result.returncode == 1


def test_graph_output_contains_summary(envs):
    f = _make(envs, ".env", "DB=pg\nURL=${DB}:5432\n")
    result = run("graph", f)
    assert "Graph summary" in result.stdout


def test_graph_missing_file_exits_two(envs):
    result = run("graph", str(envs / "nonexistent.env"))
    assert result.returncode == 2
