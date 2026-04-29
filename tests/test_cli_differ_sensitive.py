"""Tests for envguard.cli_differ_sensitive."""
import argparse
import pytest

from envguard.cli_differ_sensitive import cmd_sensitive_diff, register_sensitive_diff_parser


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content: str):
    path.write_text(content)
    return str(path)


def _args(left, right, show_values=False):
    ns = argparse.Namespace()
    ns.left = left
    ns.right = right
    ns.show_values = show_values
    return ns


def test_identical_files_exit_zero(tmp_env, capsys):
    f = _write(tmp_env / "a.env", "APP=myapp\nPORT=8080\n")
    args = _args(f, f)
    assert cmd_sensitive_diff(args) == 0
    out = capsys.readouterr().out
    assert "No differences" in out


def test_non_sensitive_change_exits_one(tmp_env, capsys):
    a = _write(tmp_env / "a.env", "PORT=8080\n")
    b = _write(tmp_env / "b.env", "PORT=9090\n")
    args = _args(a, b)
    assert cmd_sensitive_diff(args) == 1
    out = capsys.readouterr().out
    assert "PORT" in out


def test_sensitive_change_exits_one(tmp_env, capsys):
    a = _write(tmp_env / "a.env", "DB_PASSWORD=old\n")
    b = _write(tmp_env / "b.env", "DB_PASSWORD=new\n")
    args = _args(a, b)
    assert cmd_sensitive_diff(args) == 1
    out = capsys.readouterr().out
    assert "Sensitive" in out
    assert "DB_PASSWORD" in out


def test_show_values_prints_values(tmp_env, capsys):
    a = _write(tmp_env / "a.env", "PORT=8080\n")
    b = _write(tmp_env / "b.env", "PORT=9090\n")
    args = _args(a, b, show_values=True)
    cmd_sensitive_diff(args)
    out = capsys.readouterr().out
    assert "8080" in out
    assert "9090" in out


def test_missing_file_exits_two(tmp_env, capsys):
    a = _write(tmp_env / "a.env", "PORT=8080\n")
    args = _args(a, str(tmp_env / "missing.env"))
    assert cmd_sensitive_diff(args) == 2


def test_added_key_shown(tmp_env, capsys):
    a = _write(tmp_env / "a.env", "APP=x\n")
    b = _write(tmp_env / "b.env", "APP=x\nGITHUB_TOKEN=abc\n")
    args = _args(a, b)
    assert cmd_sensitive_diff(args) == 1
    out = capsys.readouterr().out
    assert "GITHUB_TOKEN" in out


def test_register_adds_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_sensitive_diff_parser(sub)
    parsed = parser.parse_args(["sensitive-diff", "left.env", "right.env"])
    assert parsed.left == "left.env"
    assert parsed.right == "right.env"
    assert parsed.show_values is False
