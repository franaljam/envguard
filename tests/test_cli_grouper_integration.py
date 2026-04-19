import subprocess
import sys
from pathlib import Path
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
        [sys.executable, "-m", "envguard", *args],
        capture_output=True,
        text=True,
    )


def test_group_exit_zero(envs):
    f = envs(".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    r = run("group", f, "--prefix", "DB")
    assert r.returncode == 0


def test_group_output_contains_summary(envs):
    f = envs(".env", "DB_HOST=localhost\nDB_PORT=5432\nDEBUG=false\n")
    r = run("group", f, "--prefix", "DB")
    assert "[DB]" in r.stdout
    assert "ungrouped" in r.stdout


def test_group_verbose_lists_keys(envs):
    f = envs(".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    r = run("group", f, "--prefix", "DB", "--verbose")
    assert "DB_HOST=localhost" in r.stdout
