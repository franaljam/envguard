"""Tests for envguard.cli_tracer."""
import argparse
from pathlib import Path

import pytest

from envguard.cli_tracer import cmd_trace


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, name: str, content: str) -> Path:
    f = p / name
    f.write_text(content)
    return f


def _args(env_file, paths, verbose=False, warn_unused=False, ext=""):
    ns = argparse.Namespace(
        env_file=str(env_file),
        paths=[str(p) for p in paths],
        verbose=verbose,
        warn_unused=warn_unused,
        ext=ext,
    )
    return ns


def test_trace_found_exits_zero(tmp_env, capsys):
    env_file = _write(tmp_env, ".env", "API_KEY=secret\n")
    src = _write(tmp_env, "app.py", "x = os.environ.get('API_KEY')\n")
    rc = cmd_trace(_args(env_file, [tmp_env]))
    assert rc == 0
    out = capsys.readouterr().out
    assert "API_KEY" in out


def test_warn_unused_exits_one(tmp_env, capsys):
    env_file = _write(tmp_env, ".env", "UNUSED_KEY=val\n")
    rc = cmd_trace(_args(env_file, [tmp_env], warn_unused=True))
    assert rc == 1
    err = capsys.readouterr().err
    assert "UNUSED_KEY" in err


def test_verbose_shows_context(tmp_env, capsys):
    env_file = _write(tmp_env, ".env", "DB_URL=x\n")
    _write(tmp_env, "db.py", "os.environ.get('DB_URL')\n")
    rc = cmd_trace(_args(env_file, [tmp_env], verbose=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "db.py" in out


def test_bad_env_file_exits_two(tmp_env, capsys):
    rc = cmd_trace(_args("/nonexistent/.env", [str(tmp_env)]))
    assert rc == 2


def test_no_usages_summary(tmp_env, capsys):
    env_file = _write(tmp_env, ".env", "GHOST=1\n")
    rc = cmd_trace(_args(env_file, [tmp_env]))
    assert rc == 0
    out = capsys.readouterr().out
    assert "No usages" in out
