"""Integration tests for the 'resolve' CLI subcommand."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture()
def envs(tmp_path):
    return tmp_path


def _make(p: Path, name: str, content: str) -> str:
    f = p / name
    f.write_text(content)
    return str(f)


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envguard", *args],
        capture_output=True,
        text=True,
    )


def test_resolve_exit_zero_no_refs(envs):
    path = _make(envs, "plain.env", "FOO=bar\nBAZ=qux\n")
    proc = run("resolve", path)
    assert proc.returncode == 0


def test_resolve_exit_zero_with_refs(envs):
    path = _make(envs, "refs.env", "BASE=/app\nFULL=${BASE}/bin\n")
    proc = run("resolve", path, "--no-os")
    assert proc.returncode == 0


def test_resolve_exit_one_on_unresolved(envs):
    path = _make(envs, "broken.env", "X=${UNDEFINED_XYZ_VAR}\n")
    proc = run("resolve", path, "--no-os")
    assert proc.returncode == 1
    assert "UNDEFINED_XYZ_VAR" in proc.stderr


def test_resolve_output_contains_summary(envs):
    path = _make(envs, "summary.env", "A=1\nB=${A}\n")
    proc = run("resolve", path, "--no-os")
    assert "resolved" in proc.stdout.lower() or "reference" in proc.stdout.lower()


def test_resolve_verbose_shows_mapping(envs):
    path = _make(envs, "verbose.env", "HOST=localhost\nURL=http://${HOST}:80\n")
    proc = run("resolve", path, "--no-os", "--verbose")
    assert proc.returncode == 0
    assert "URL" in proc.stdout
