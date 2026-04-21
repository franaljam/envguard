import argparse
import pytest
from unittest.mock import patch
from pathlib import Path

from envguard.cli_compressor import cmd_compress, register_compress_parser


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(file, *, no_dedup=False, no_interp=False, remove="", show=False):
    ns = argparse.Namespace(
        file=str(file),
        no_dedup=no_dedup,
        no_interp=no_interp,
        remove=remove,
        show=show,
    )
    return ns


def test_compress_no_redundancy_exits_zero(tmp_env, capsys):
    _write(tmp_env, "A=1\nB=2\n")
    with pytest.raises(SystemExit) as exc:
        cmd_compress(_args(tmp_env))
    assert exc.value.code == 0


def test_compress_duplicate_exits_one(tmp_env, capsys):
    _write(tmp_env, "A=same\nB=same\n")
    with pytest.raises(SystemExit) as exc:
        cmd_compress(_args(tmp_env))
    assert exc.value.code == 1


def test_compress_summary_printed(tmp_env, capsys):
    _write(tmp_env, "A=same\nB=same\n")
    with pytest.raises(SystemExit):
        cmd_compress(_args(tmp_env))
    out = capsys.readouterr().out
    assert "Removed" in out


def test_compress_show_prints_result(tmp_env, capsys):
    _write(tmp_env, "A=1\nB=2\n")
    with pytest.raises(SystemExit):
        cmd_compress(_args(tmp_env, show=True))
    out = capsys.readouterr().out
    assert "A=1" in out


def test_compress_explicit_remove(tmp_env, capsys):
    _write(tmp_env, "A=1\nB=2\nC=3\n")
    with pytest.raises(SystemExit) as exc:
        cmd_compress(_args(tmp_env, remove="B", no_dedup=True, no_interp=True))
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert "B" in out


def test_compress_missing_file_exits_two(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        cmd_compress(_args(tmp_path / "missing.env"))
    assert exc.value.code == 2


def test_register_compress_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_compress_parser(sub)
    args = parser.parse_args(["compress", "myfile.env"])
    assert args.file == "myfile.env"
    assert not args.no_dedup
    assert not args.no_interp
