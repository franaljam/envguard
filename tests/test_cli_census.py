"""Tests for envguard.cli_census."""
import argparse
import os
import pytest

from envguard.cli_census import cmd_census


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(file: str, verbose: bool = False) -> argparse.Namespace:
    return argparse.Namespace(file=file, verbose=verbose)


def test_census_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    assert cmd_census(_args(f)) == 0


def test_census_missing_file_exits_two(tmp_env):
    assert cmd_census(_args(str(tmp_env / "missing.env"))) == 2


def test_census_verbose_exits_zero(tmp_env, capsys):
    f = _write(
        tmp_env / ".env",
        "DB_HOST=localhost\nDB_PASSWORD=secret\nFEATURE=true\nEMPTY=\n",
    )
    rc = cmd_census(_args(f, verbose=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Sensitive keys" in out
    assert "DB_PASSWORD" in out


def test_census_summary_printed(tmp_env, capsys):
    f = _write(tmp_env / ".env", "APP_NAME=myapp\nAPP_PORT=8080\n")
    cmd_census(_args(f))
    out = capsys.readouterr().out
    assert "Total keys" in out


def test_census_verbose_shows_prefix_groups(tmp_env, capsys):
    f = _write(tmp_env / ".env", "DB_HOST=h\nDB_PORT=5432\nAPP_NAME=x\n")
    cmd_census(_args(f, verbose=True))
    out = capsys.readouterr().out
    assert "Prefix groups" in out
    assert "DB" in out


def test_census_verbose_shows_empty_keys(tmp_env, capsys):
    f = _write(tmp_env / ".env", "KEY=\nOTHER=val\n")
    cmd_census(_args(f, verbose=True))
    out = capsys.readouterr().out
    assert "Empty keys" in out
    assert "KEY" in out
