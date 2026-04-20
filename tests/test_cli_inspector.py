"""Unit tests for envguard.cli_inspector."""
import argparse
import os
import pytest
from envguard.cli_inspector import cmd_inspect, register_inspect_parser


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content):
    path.write_text(content)
    return str(path)


def _args(file, verbose=False, sensitive_only=False):
    ns = argparse.Namespace(
        file=file,
        verbose=verbose,
        sensitive_only=sensitive_only,
    )
    return ns


def test_inspect_exits_zero(tmp_env):
    path = _write(tmp_env, "APP_NAME=myapp\nPORT=8080\n")
    assert cmd_inspect(_args(path)) == 0


def test_inspect_missing_file_exits_two(tmp_path):
    missing = str(tmp_path / "missing.env")
    assert cmd_inspect(_args(missing)) == 2


def test_inspect_prints_summary(tmp_env, capsys):
    path = _write(tmp_env, "APP_NAME=myapp\n")
    cmd_inspect(_args(path))
    out = capsys.readouterr().out
    assert "Inspected" in out


def test_inspect_verbose_shows_table(tmp_env, capsys):
    path = _write(tmp_env, "DB_PASSWORD=secret\nAPP=app\n")
    cmd_inspect(_args(path, verbose=True))
    out = capsys.readouterr().out
    assert "DB_PASSWORD" in out
    assert "SENS" in out


def test_inspect_sensitive_only_flag(tmp_env, capsys):
    path = _write(tmp_env, "API_KEY=abc\nAPP=app\n")
    cmd_inspect(_args(path, sensitive_only=True))
    out = capsys.readouterr().out
    assert "API_KEY" in out


def test_inspect_sensitive_only_no_sensitive(tmp_env, capsys):
    path = _write(tmp_env, "APP=app\nPORT=80\n")
    cmd_inspect(_args(path, sensitive_only=True))
    out = capsys.readouterr().out
    assert "No sensitive" in out


def test_register_inspect_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_inspect_parser(sub)
    args = parser.parse_args(["inspect", "some.env"])
    assert args.file == "some.env"
    assert args.verbose is False
    assert args.sensitive_only is False
