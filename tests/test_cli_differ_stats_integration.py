"""Integration tests for `envguard stats` via subprocess."""
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
        [sys.executable, "-m", "envguard", "stats", *args],
        capture_output=True,
        text=True,
    )


def test_stats_exit_zero_identical(envs):
    f = envs("a.env", "KEY=value\n")
    result = run(f, f)
    assert result.returncode == 0


def test_stats_exit_one_on_diff(envs):
    a = envs("a.env", "KEY=hello\n")
    b = envs("b.env", "KEY=world\n")
    result = run(a, b)
    assert result.returncode == 1


def test_stats_output_contains_summary(envs):
    a = envs("a.env", "KEY=hello\n")
    b = envs("b.env", "KEY=world\n")
    result = run(a, b)
    assert "Summary" in result.stdout


def test_stats_verbose_flag(envs):
    a = envs("a.env", "A=long_value\nB=removed\n")
    b = envs("b.env", "A=short\nC=added\n")
    result = run("-v", a, b)
    assert result.returncode == 1
    combined = result.stdout + result.stderr
    assert any(word in combined for word in ("Added", "Removed", "Changed"))
