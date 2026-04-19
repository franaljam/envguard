import argparse
import pytest
from pathlib import Path
from envguard.cli_freezer import cmd_freeze, cmd_thaw_check
from envguard.freezer import freeze_env, save_freeze


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> str:
    p.write_text(content)
    return str(p)


def _args(**kwargs):
    ns = argparse.Namespace(**kwargs)
    return ns


def test_cmd_freeze_creates_file(tmp_env):
    env_file = _write(tmp_env / ".env", "DB_HOST=localhost\nSECRET=abc\n")
    out = str(tmp_env / "freeze.json")
    args = _args(env_file=env_file, output=out)
    rc = cmd_freeze(args)
    assert rc == 0
    assert (tmp_env / "freeze.json").exists()


def test_cmd_freeze_output_message(tmp_env, capsys):
    env_file = _write(tmp_env / ".env", "A=1\nB=2\n")
    out = str(tmp_env / "freeze.json")
    args = _args(env_file=env_file, output=out)
    cmd_freeze(args)
    captured = capsys.readouterr()
    assert "Frozen 2 keys" in captured.out


def test_thaw_check_no_drift_exits_zero(tmp_env):
    env_file = _write(tmp_env / ".env", "A=1\nB=2\n")
    freeze_path = str(tmp_env / "freeze.json")
    save_freeze(freeze_env({"A": "1", "B": "2"}), freeze_path)
    args = _args(env_file=env_file, freeze_file=freeze_path, verbose=False)
    rc = cmd_thaw_check(args)
    assert rc == 0


def test_thaw_check_drift_exits_one(tmp_env):
    env_file = _write(tmp_env / ".env", "A=changed\nB=2\n")
    freeze_path = str(tmp_env / "freeze.json")
    save_freeze(freeze_env({"A": "original", "B": "2"}), freeze_path)
    args = _args(env_file=env_file, freeze_file=freeze_path, verbose=False)
    rc = cmd_thaw_check(args)
    assert rc == 1


def test_thaw_check_verbose_shows_changed(tmp_env, capsys):
    env_file = _write(tmp_env / ".env", "A=new\n")
    freeze_path = str(tmp_env / "freeze.json")
    save_freeze(freeze_env({"A": "old"}), freeze_path)
    args = _args(env_file=env_file, freeze_file=freeze_path, verbose=True)
    cmd_thaw_check(args)
    captured = capsys.readouterr()
    assert "CHANGED" in captured.out
    assert "A" in captured.out
