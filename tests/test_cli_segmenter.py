"""Tests for envguard.cli_segmenter."""
import argparse
import json
from pathlib import Path

import pytest

from envguard.cli_segmenter import cmd_segment, register_segment_parser


@pytest.fixture()
def tmp_env(tmp_path: Path) -> Path:
    return tmp_path / ".env"


def _write(p: Path, content: str) -> None:
    p.write_text(content)


def _args(file: str, rules=None, strip_prefix=False, json_out=False, verbose=False):
    ns = argparse.Namespace(
        file=file,
        rule=rules,
        strip_prefix=strip_prefix,
        json=json_out,
        verbose=verbose,
    )
    return ns


def test_segment_exits_zero(tmp_env: Path):
    _write(tmp_env, "DB_HOST=localhost\nAPP=x\n")
    rc = cmd_segment(_args(str(tmp_env), rules=["db:^DB_"]))
    assert rc == 0


def test_segment_missing_file_exits_two(tmp_env: Path):
    rc = cmd_segment(_args("/no/such/file.env"))
    assert rc == 2


def test_segment_invalid_rule_exits_two(tmp_env: Path):
    _write(tmp_env, "DB_HOST=x\n")
    rc = cmd_segment(_args(str(tmp_env), rules=["badformat"]))
    assert rc == 2


def test_segment_json_output(tmp_env: Path, capsys):
    _write(tmp_env, "DB_HOST=localhost\nAPP=myapp\n")
    rc = cmd_segment(_args(str(tmp_env), rules=["db:^DB_"], json_out=True))
    assert rc == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "segments" in data
    assert "unmatched" in data
    assert "DB_HOST" in data["segments"]["db"]


def test_segment_verbose_shows_keys(tmp_env: Path, capsys):
    _write(tmp_env, "DB_HOST=localhost\nAPP=myapp\n")
    rc = cmd_segment(_args(str(tmp_env), rules=["db:^DB_"], verbose=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST" in out


def test_register_segment_parser_adds_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_segment_parser(sub)
    args = parser.parse_args(["segment", "myfile.env", "--rule", "db:^DB_"])
    assert args.file == "myfile.env"
    assert args.rule == ["db:^DB_"]
