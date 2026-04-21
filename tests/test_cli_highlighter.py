"""Tests for envguard.cli_highlighter."""
import argparse
import os
import tempfile
import pytest

from envguard.cli_highlighter import cmd_highlight, register_highlight_parser


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, content: str) -> None:
    path.write_text(content)


def _args(**kwargs) -> argparse.Namespace:
    defaults = dict(prefix=None, pattern=None, key=None, verbose=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_highlight_no_match_exits_zero(tmp_env):
    _write(tmp_env, "FOO=bar\nBAZ=qux\n")
    ns = _args(file=str(tmp_env))
    assert cmd_highlight(ns) == 0


def test_highlight_prefix_match_exits_one(tmp_env):
    _write(tmp_env, "DB_HOST=localhost\nAPP_NAME=test\n")
    ns = _args(file=str(tmp_env), prefix=["DB_"])
    assert cmd_highlight(ns) == 1


def test_highlight_exact_match_exits_one(tmp_env):
    _write(tmp_env, "DEBUG=true\nHOST=localhost\n")
    ns = _args(file=str(tmp_env), key=["DEBUG"])
    assert cmd_highlight(ns) == 1


def test_highlight_pattern_match_exits_one(tmp_env):
    _write(tmp_env, "API_KEY=secret\nHOST=localhost\n")
    ns = _args(file=str(tmp_env), pattern=[r"_KEY$"])
    assert cmd_highlight(ns) == 1


def test_highlight_verbose_shows_values(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\nAPP=test\n")
    ns = _args(file=str(tmp_env), prefix=["DB_"], verbose=True)
    cmd_highlight(ns)
    captured = capsys.readouterr()
    assert "DB_HOST" in captured.out
    assert "localhost" in captured.out


def test_highlight_missing_file_exits_two(tmp_env):
    ns = _args(file="/nonexistent/.env")
    assert cmd_highlight(ns) == 2


def test_register_highlight_parser_adds_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_highlight_parser(sub)
    args = parser.parse_args(["highlight", "some.env", "--key", "FOO"])
    assert args.key == ["FOO"]
