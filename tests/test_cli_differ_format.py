"""Tests for envguard.cli_differ_format."""
from __future__ import annotations

import argparse
import pytest

from envguard.cli_differ_format import cmd_format_diff, register_format_diff_parser


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _write


def _args(left: str, right: str, verbose: bool = False) -> argparse.Namespace:
    return argparse.Namespace(left=left, right=right, verbose=verbose)


def test_identical_files_exit_zero(tmp_env):
    c = "KEY=value\n"
    rc = cmd_format_diff(_args(tmp_env("l.env", c), tmp_env("r.env", c)))
    assert rc == 0


def test_format_diff_exits_one_on_change(tmp_env):
    left = tmp_env("l.env", 'KEY="value"\n')
    right = tmp_env("r.env", "KEY=value\n")
    rc = cmd_format_diff(_args(left, right))
    assert rc == 1


def test_missing_file_exits_two(tmp_env, capsys):
    existing = tmp_env("l.env", "KEY=val\n")
    rc = cmd_format_diff(_args(existing, "/nonexistent/path.env"))
    assert rc == 2
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_verbose_shows_detail(tmp_env, capsys):
    left = tmp_env("l.env", "PORT = 80\n")
    right = tmp_env("r.env", "PORT=80\n")
    rc = cmd_format_diff(_args(left, right, verbose=True))
    assert rc == 1
    captured = capsys.readouterr()
    assert "PORT" in captured.out
    assert "spacing" in captured.out


def test_register_adds_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_format_diff_parser(sub)
    ns = parser.parse_args(["format-diff", "a.env", "b.env"])
    assert ns.left == "a.env"
    assert ns.right == "b.env"
    assert ns.verbose is False


def test_no_change_summary_message(tmp_env, capsys):
    c = "A=1\nB=2\n"
    cmd_format_diff(_args(tmp_env("l.env", c), tmp_env("r.env", c)))
    out = capsys.readouterr().out
    assert "No formatting" in out
