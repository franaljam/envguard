import argparse
import pytest
from pathlib import Path
from envguard.cli_scorer import cmd_score


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str):
    f = p / ".env"
    f.write_text(content)
    return str(f)


def _args(file, verbose=False):
    ns = argparse.Namespace(file=file, verbose=verbose)
    return ns


def test_score_clean_env_exits_zero(tmp_env, capsys):
    f = _write(tmp_env, "KEY_A=hello\nKEY_B=world\n")
    rc = cmd_score(_args(f))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Score:" in out


def test_score_shows_grade(tmp_env, capsys):
    f = _write(tmp_env, "KEY_A=hello\n")
    cmd_score(_args(f))
    out = capsys.readouterr().out
    assert "Grade:" in out


def test_score_verbose_shows_notes(tmp_env, capsys):
    f = _write(tmp_env, "bad_key=\n")
    cmd_score(_args(f, verbose=True))
    out = capsys.readouterr().out
    assert "-" in out  # note lines


def test_score_missing_file_returns_2(tmp_env):
    rc = cmd_score(_args("/nonexistent/.env"))
    assert rc == 2


def test_score_empty_env(tmp_env, capsys):
    f = _write(tmp_env, "")
    rc = cmd_score(_args(f))
    assert rc == 0
