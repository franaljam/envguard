"""Tests for envguard.cli_differ_format."""
import argparse
import os
import pytest

from envguard.cli_differ_format import cmd_format_diff, _parse_raw_lines


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(directory, name: str, content: str) -> str:
    p = directory / name
    p.write_text(content, encoding="utf-8")
    return str(p)


def _args(left: str, right: str, verbose: bool = False) -> argparse.Namespace:
    return argparse.Namespace(left=left, right=right, verbose=verbose)


# ---------------------------------------------------------------------------
# _parse_raw_lines
# ---------------------------------------------------------------------------

def test_parse_raw_lines_basic(tmp_env):
    path = _write(tmp_env, "a.env", 'KEY=value\nOTHER="hello"\n')
    raw = _parse_raw_lines(path)
    assert 'KEY' in raw
    assert 'OTHER' in raw
    assert raw['KEY'] == 'KEY=value'


def test_parse_raw_lines_skips_comments(tmp_env):
    path = _write(tmp_env, "b.env", '# comment\nKEY=val\n')
    raw = _parse_raw_lines(path)
    assert list(raw.keys()) == ['KEY']


def test_parse_raw_lines_missing_file_exits_two(tmp_env):
    with pytest.raises(SystemExit) as exc:
        _parse_raw_lines(str(tmp_env / "missing.env"))
    assert exc.value.code == 2


# ---------------------------------------------------------------------------
# cmd_format_diff
# ---------------------------------------------------------------------------

def test_identical_files_exit_zero(tmp_env):
    content = 'KEY=value\nOTHER=hello\n'
    left = _write(tmp_env, "left.env", content)
    right = _write(tmp_env, "right.env", content)
    with pytest.raises(SystemExit) as exc:
        cmd_format_diff(_args(left, right))
    assert exc.value.code == 0


def test_quote_change_exits_one(tmp_env):
    left = _write(tmp_env, "left.env", 'KEY=value\n')
    right = _write(tmp_env, "right.env", 'KEY="value"\n')
    with pytest.raises(SystemExit) as exc:
        cmd_format_diff(_args(left, right))
    assert exc.value.code == 1


def test_spacing_change_exits_one(tmp_env):
    left = _write(tmp_env, "left.env", 'KEY=value\n')
    right = _write(tmp_env, "right.env", 'KEY = value\n')
    with pytest.raises(SystemExit) as exc:
        cmd_format_diff(_args(left, right))
    assert exc.value.code == 1


def test_verbose_flag_accepted(tmp_env, capsys):
    left = _write(tmp_env, "left.env", 'KEY=value\n')
    right = _write(tmp_env, "right.env", 'KEY="value"\n')
    with pytest.raises(SystemExit):
        cmd_format_diff(_args(left, right, verbose=True))
    captured = capsys.readouterr()
    assert 'left' in captured.out or 'KEY' in captured.out


def test_keys_only_in_one_file_no_diff(tmp_env):
    left = _write(tmp_env, "left.env", 'SHARED=val\nLEFT_ONLY=x\n')
    right = _write(tmp_env, "right.env", 'SHARED=val\nRIGHT_ONLY=y\n')
    with pytest.raises(SystemExit) as exc:
        cmd_format_diff(_args(left, right))
    assert exc.value.code == 0
