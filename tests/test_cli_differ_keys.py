import argparse
import pytest
from envguard.cli_differ_keys import cmd_key_diff
from pathlib import Path


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def _args(base, target, no_renames=False, rename_threshold=0.7):
    ns = argparse.Namespace(
        base=str(base),
        target=str(target),
        no_renames=no_renames,
        rename_threshold=rename_threshold,
    )
    return ns


def test_identical_files_exit_zero(tmp_env, capsys):
    b = _write(tmp_env / "base.env", "HOST=localhost\nPORT=5432\n")
    t = _write(tmp_env / "target.env", "HOST=localhost\nPORT=5432\n")
    code = cmd_key_diff(_args(b, t))
    assert code == 0


def test_added_key_exits_one(tmp_env, capsys):
    b = _write(tmp_env / "base.env", "HOST=localhost\n")
    t = _write(tmp_env / "target.env", "HOST=localhost\nNEW=val\n")
    code = cmd_key_diff(_args(b, t))
    out = capsys.readouterr().out
    assert code == 1
    assert "NEW" in out


def test_removed_key_exits_one(tmp_env, capsys):
    b = _write(tmp_env / "base.env", "HOST=localhost\nOLD=val\n")
    t = _write(tmp_env / "target.env", "HOST=localhost\n")
    code = cmd_key_diff(_args(b, t))
    out = capsys.readouterr().out
    assert code == 1
    assert "OLD" in out


def test_renamed_key_shown(tmp_env, capsys):
    b = _write(tmp_env / "base.env", "DB_HOST=localhost\n")
    t = _write(tmp_env / "target.env", "DB_HOSTNAME=localhost\n")
    code = cmd_key_diff(_args(b, t, rename_threshold=0.6))
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "DB_HOSTNAME" in out


def test_no_renames_flag(tmp_env, capsys):
    b = _write(tmp_env / "base.env", "DB_HOST=localhost\n")
    t = _write(tmp_env / "target.env", "DB_HOSTNAME=localhost\n")
    code = cmd_key_diff(_args(b, t, no_renames=True))
    out = capsys.readouterr().out
    assert "Renamed" not in out


def test_bad_file_returns_two(tmp_env):
    code = cmd_key_diff(_args("/nonexistent/a.env", "/nonexistent/b.env"))
    assert code == 2
