"""Subprocess integration tests for the inspect sub-command."""
import subprocess
import sys
import pytest


@pytest.fixture()
def envs(tmp_path):
    def _make(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _make


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envguard", *args],
        capture_output=True,
        text=True,
    )


def test_inspect_exit_zero(envs):
    f = envs("a.env", "APP=myapp\nPORT=8080\n")
    result = run("inspect", f)
    assert result.returncode == 0


def test_inspect_output_contains_summary(envs):
    f = envs("a.env", "APP=myapp\nDB_PASSWORD=secret\n")
    result = run("inspect", f)
    assert "Inspected" in result.stdout


def test_inspect_verbose_shows_keys(envs):
    f = envs("a.env", "APP=myapp\nDB_PASSWORD=secret\n")
    result = run("inspect", f, "--verbose")
    assert "DB_PASSWORD" in result.stdout


def test_inspect_missing_file_exits_two(tmp_path):
    result = run("inspect", str(tmp_path / "ghost.env"))
    assert result.returncode == 2
