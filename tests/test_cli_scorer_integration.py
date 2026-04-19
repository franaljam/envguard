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
        capture_output=True, text=True,
    )


def test_score_exit_zero(envs):
    f = envs(".env", "KEY_A=val\nKEY_B=other\n")
    r = run("score", f)
    assert r.returncode == 0


def test_score_output_contains_grade(envs):
    f = envs(".env", "KEY_A=val\n")
    r = run("score", f)
    assert "Grade:" in r.stdout


def test_score_verbose_flag(envs):
    f = envs(".env", "bad_key=\n")
    r = run("score", "--verbose", f)
    assert r.returncode == 0
