"""Tests for envguard.cli_differ_stats."""
import argparse
import os
import pytest

from envguard.cli_differ_stats import cmd_stats


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content):
    path.write_text(content)
    return str(path)


def _args(left, right, verbose=False):
    ns = argparse.Namespace(left=left, right=right, verbose=verbose)
    return ns


def test_identical_files_exit_zero(tmp_env):
    f = _write(tmp_env / "a.env", "A=1\nB=2\n")
    assert cmd_stats(_args(f, f)) == 0


def test_changed_file_exits_one(tmp_env):
    a = _write(tmp_env / "a.env", "A=hello\n")
    b = _write(tmp_env / "b.env", "A=hi\n")
    assert cmd_stats(_args(a, b)) == 1


def test_missing_left_exits_two(tmp_env):
    b = _write(tmp_env / "b.env", "A=1\n")
    assert cmd_stats(_args("/no/such/file.env", b)) == 2


def test_missing_right_exits_two(tmp_env):
    a = _write(tmp_env / "a.env", "A=1\n")
    assert cmd_stats(_args(a, "/no/such/file.env")) == 2


def test_verbose_shows_details(tmp_env, capsys):
    a = _write(tmp_env / "a.env", "A=hello\nB=gone\n")
    b = _write(tmp_env / "b.env", "A=hi\nC=new\n")
    cmd_stats(_args(a, b, verbose=True))
    out = capsys.readouterr().out
    assert "Added" in out or "Removed" in out or "Changed" in out


def test_summary_printed(tmp_env, capsys):
    a = _write(tmp_env / "a.env", "X=1\n")
    b = _write(tmp_env / "b.env", "X=1\n")
    cmd_stats(_args(a, b))
    out = capsys.readouterr().out
    assert "Summary" in out
