"""Tests for envguard.cli_differ_counts."""
import argparse
import pytest
from pathlib import Path
from envguard.cli_differ_counts import cmd_count_diff


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(left, right, verbose=False):
    ns = argparse.Namespace(left=str(left), right=str(right), verbose=verbose)
    return ns


def test_identical_files_exit_zero(tmp_env):
    f = _write(tmp_env / "a.env", "A=1\nB=2\n")
    result = cmd_count_diff(_args(f, f))
    assert result == 0


def test_added_key_exits_one(tmp_env):
    left = _write(tmp_env / "left.env", "A=1\n")
    right = _write(tmp_env / "right.env", "A=1\nB=2\n")
    result = cmd_count_diff(_args(left, right))
    assert result == 1


def test_removed_key_exits_one(tmp_env):
    left = _write(tmp_env / "left.env", "A=1\nB=2\n")
    right = _write(tmp_env / "right.env", "A=1\n")
    result = cmd_count_diff(_args(left, right))
    assert result == 1


def test_value_change_only_exits_zero(tmp_env):
    left = _write(tmp_env / "left.env", "A=old\n")
    right = _write(tmp_env / "right.env", "A=new\n")
    result = cmd_count_diff(_args(left, right))
    assert result == 0


def test_missing_file_exits_two(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\n")
    result = cmd_count_diff(_args(left, tmp_env / "missing.env"))
    assert result == 2
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_verbose_shows_added_keys(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\n")
    right = _write(tmp_env / "right.env", "A=1\nNEW_KEY=2\n")
    cmd_count_diff(_args(left, right, verbose=True))
    captured = capsys.readouterr()
    assert "NEW_KEY" in captured.out


def test_verbose_shows_removed_keys(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\nOLD_KEY=x\n")
    right = _write(tmp_env / "right.env", "A=1\n")
    cmd_count_diff(_args(left, right, verbose=True))
    captured = capsys.readouterr()
    assert "OLD_KEY" in captured.out


def test_summary_printed(tmp_env, capsys):
    left = _write(tmp_env / "left.env", "A=1\nB=2\n")
    right = _write(tmp_env / "right.env", "A=1\nC=3\n")
    cmd_count_diff(_args(left, right))
    captured = capsys.readouterr()
    assert "Key count" in captured.out or "count" in captured.out.lower()
