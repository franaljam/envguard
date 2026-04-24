"""Tests for envguard.cli_linker."""
import argparse
import os
import pytest

from envguard.cli_linker import cmd_link


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(directory, name, content):
    p = directory / name
    p.write_text(content)
    return str(p)


def _args(files, verbose=False):
    ns = argparse.Namespace(files=files, verbose=verbose)
    return ns


def test_identical_files_exit_zero(tmp_env):
    f1 = _write(tmp_env, ".env.a", "KEY=value\n")
    f2 = _write(tmp_env, ".env.b", "KEY=value\n")
    assert cmd_link(_args([f1, f2])) == 0


def test_inconsistent_shared_key_exits_one(tmp_env):
    f1 = _write(tmp_env, ".env.a", "KEY=one\n")
    f2 = _write(tmp_env, ".env.b", "KEY=two\n")
    assert cmd_link(_args([f1, f2])) == 1


def test_no_shared_keys_exits_zero(tmp_env):
    f1 = _write(tmp_env, ".env.a", "ALPHA=1\n")
    f2 = _write(tmp_env, ".env.b", "BETA=2\n")
    assert cmd_link(_args([f1, f2])) == 0


def test_missing_file_exits_two(tmp_env):
    f1 = _write(tmp_env, ".env.a", "KEY=val\n")
    assert cmd_link(_args([f1, "/nonexistent/.env"])) == 2


def test_verbose_shows_shared_keys(tmp_env, capsys):
    f1 = _write(tmp_env, ".env.a", "KEY=val1\n")
    f2 = _write(tmp_env, ".env.b", "KEY=val2\n")
    cmd_link(_args([f1, f2], verbose=True))
    captured = capsys.readouterr()
    assert "KEY" in captured.out
    assert "INCONSISTENT" in captured.out


def test_verbose_consistent_key(tmp_env, capsys):
    f1 = _write(tmp_env, ".env.a", "KEY=same\n")
    f2 = _write(tmp_env, ".env.b", "KEY=same\n")
    cmd_link(_args([f1, f2], verbose=True))
    captured = capsys.readouterr()
    assert "consistent" in captured.out


def test_summary_printed(tmp_env, capsys):
    f1 = _write(tmp_env, ".env.a", "A=1\nB=2\n")
    f2 = _write(tmp_env, ".env.b", "B=3\nC=4\n")
    cmd_link(_args([f1, f2]))
    captured = capsys.readouterr()
    assert "shared" in captured.out
