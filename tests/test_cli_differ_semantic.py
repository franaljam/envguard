"""Tests for envguard.cli_differ_semantic."""
import argparse
import os
import textwrap
from pathlib import Path

import pytest

from envguard.cli_differ_semantic import cmd_semantic_diff


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> str:
    p = directory / name
    p.write_text(textwrap.dedent(content))
    return str(p)


def _args(left, right, strict=False, no_color=True):
    ns = argparse.Namespace(
        left=left,
        right=right,
        strict=strict,
        no_color=no_color,
    )
    return ns


def test_identical_files_exit_zero(tmp_env):
    f = _write(tmp_env, "a.env", "KEY=value\n")
    code = cmd_semantic_diff(_args(f, f))
    assert code == 0


def test_added_key_exits_one(tmp_env):
    left = _write(tmp_env, "l.env", "A=1\n")
    right = _write(tmp_env, "r.env", "A=1\nB=2\n")
    code = cmd_semantic_diff(_args(left, right))
    assert code == 1


def test_trivial_change_exits_one_without_strict(tmp_env):
    left = _write(tmp_env, "l.env", "FLAG=true\n")
    right = _write(tmp_env, "r.env", "FLAG=yes\n")
    code = cmd_semantic_diff(_args(left, right, strict=False))
    assert code == 1


def test_trivial_change_exits_zero_with_strict(tmp_env):
    left = _write(tmp_env, "l.env", "FLAG=true\n")
    right = _write(tmp_env, "r.env", "FLAG=yes\n")
    code = cmd_semantic_diff(_args(left, right, strict=True))
    assert code == 0


def test_meaningful_change_exits_one_with_strict(tmp_env):
    left = _write(tmp_env, "l.env", "PORT=8080\n")
    right = _write(tmp_env, "r.env", "PORT=9090\n")
    code = cmd_semantic_diff(_args(left, right, strict=True))
    assert code == 1


def test_missing_file_exits_two(tmp_env):
    left = _write(tmp_env, "l.env", "A=1\n")
    code = cmd_semantic_diff(_args(left, str(tmp_env / "missing.env")))
    assert code == 2


def test_output_contains_summary(tmp_env, capsys):
    left = _write(tmp_env, "l.env", "A=1\nB=old\n")
    right = _write(tmp_env, "r.env", "A=1\nB=new\n")
    cmd_semantic_diff(_args(left, right))
    captured = capsys.readouterr()
    assert "meaningful" in captured.out
