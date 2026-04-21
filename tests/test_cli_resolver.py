"""Unit tests for envguard.cli_resolver."""
import argparse
import os
import pytest
from pathlib import Path

from envguard.cli_resolver import cmd_resolve, register_resolve_parser


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> str:
    f = p / ".env"
    f.write_text(content)
    return str(f)


def _args(**kwargs):
    defaults = {
        "file": ".env",
        "default": None,
        "no_os": False,
        "strict": False,
        "verbose": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_resolve_no_refs_exits_zero(tmp_env):
    path = _write(tmp_env, "A=hello\nB=world\n")
    assert cmd_resolve(_args(file=path)) == 0


def test_resolve_with_env_ref_exits_zero(tmp_env):
    path = _write(tmp_env, "BASE=/app\nLOG=${BASE}/logs\n")
    assert cmd_resolve(_args(file=path, no_os=True)) == 0


def test_unresolved_ref_exits_one(tmp_env):
    path = _write(tmp_env, "X=${GHOST}\n")
    assert cmd_resolve(_args(file=path, no_os=True)) == 1


def test_strict_unresolved_exits_nonzero(tmp_env):
    path = _write(tmp_env, "X=${GHOST}\n")
    # strict raises InterpolationError, which propagates as uncaught or exits 1
    from envguard.interpolator import InterpolationError
    with pytest.raises(InterpolationError):
        cmd_resolve(_args(file=path, no_os=True, strict=True))


def test_default_resolves_missing(tmp_env):
    path = _write(tmp_env, "MSG=Hello ${NAME}\n")
    assert cmd_resolve(_args(file=path, no_os=True, default=["NAME=World"])) == 0


def test_verbose_does_not_crash(tmp_env, capsys):
    path = _write(tmp_env, "BASE=/x\nFULL=${BASE}/y\n")
    code = cmd_resolve(_args(file=path, no_os=True, verbose=True))
    assert code == 0
    captured = capsys.readouterr()
    assert "FULL" in captured.out


def test_missing_file_exits_two(tmp_env):
    assert cmd_resolve(_args(file="/no/such/file.env")) == 2


def test_register_resolve_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_resolve_parser(sub)
    parsed = parser.parse_args(["resolve", "my.env"])
    assert parsed.file == "my.env"
    assert parsed.strict is False
    assert parsed.no_os is False
