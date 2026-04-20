"""Unit tests for envguard.cli_grapher."""
import argparse
import os
import pytest

from envguard.cli_grapher import cmd_graph


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path, text):
    path.write_text(text)


def _args(file, verbose=False):
    ns = argparse.Namespace(file=str(file), verbose=verbose)
    return ns


def test_graph_no_refs_exits_zero(tmp_env):
    _write(tmp_env, "A=hello\nB=world\n")
    assert cmd_graph(_args(tmp_env)) == 0


def test_graph_with_refs_exits_zero(tmp_env):
    _write(tmp_env, "HOST=localhost\nURL=http://${HOST}/api\n")
    assert cmd_graph(_args(tmp_env)) == 0


def test_graph_cycle_exits_one(tmp_env):
    _write(tmp_env, "A=${B}\nB=${A}\n")
    assert cmd_graph(_args(tmp_env)) == 1


def test_graph_missing_file_exits_two(tmp_path):
    missing = tmp_path / "missing.env"
    assert cmd_graph(_args(missing)) == 2


def test_graph_verbose_prints_edges(tmp_env, capsys):
    _write(tmp_env, "DB=postgres\nURL=${DB}:5432\n")
    ret = cmd_graph(_args(tmp_env, verbose=True))
    captured = capsys.readouterr()
    assert ret == 0
    assert "URL" in captured.out
    assert "DB" in captured.out


def test_graph_verbose_no_refs_message(tmp_env, capsys):
    _write(tmp_env, "A=1\nB=2\n")
    cmd_graph(_args(tmp_env, verbose=True))
    captured = capsys.readouterr()
    assert "No inter-variable" in captured.out


def test_graph_summary_in_output(tmp_env, capsys):
    _write(tmp_env, "X=foo\n")
    cmd_graph(_args(tmp_env))
    captured = capsys.readouterr()
    assert "Graph summary" in captured.out
