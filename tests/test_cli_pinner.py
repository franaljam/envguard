"""Tests for envguard.cli_pinner."""
import json
import pytest
from argparse import Namespace
from pathlib import Path
from envguard.cli_pinner import cmd_pin, cmd_drift
from envguard.pinner import save_pinfile


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> str:
    p.write_text(content)
    return str(p)


def _args(**kwargs):
    return Namespace(**kwargs)


def test_cmd_pin_creates_lockfile(tmp_env):
    env_file = _write(tmp_env / ".env", "FOO=bar\nBAZ=qux\n")
    lock_file = str(tmp_env / ".env.lock")
    args = _args(env_file=env_file, output=lock_file)
    rc = cmd_pin(args)
    assert rc == 0
    assert Path(lock_file).exists()
    data = json.loads(Path(lock_file).read_text())
    assert "FOO" in data and "BAZ" in data


def test_cmd_drift_no_drift(tmp_env):
    env_file = _write(tmp_env / ".env", "FOO=bar\n")
    lock_file = str(tmp_env / ".env.lock")
    cmd_pin(_args(env_file=env_file, output=lock_file))
    rc = cmd_drift(_args(env_file=env_file, pinfile=lock_file))
    assert rc == 0


def test_cmd_drift_detects_change(tmp_env):
    env_file = _write(tmp_env / ".env", "FOO=bar\n")
    lock_file = str(tmp_env / ".env.lock")
    cmd_pin(_args(env_file=env_file, output=lock_file))
    _write(tmp_env / ".env", "FOO=changed\n")
    rc = cmd_drift(_args(env_file=env_file, pinfile=lock_file))
    assert rc == 1


def test_cmd_drift_detects_new_key(tmp_env):
    env_file = _write(tmp_env / ".env", "FOO=bar\n")
    lock_file = str(tmp_env / ".env.lock")
    cmd_pin(_args(env_file=env_file, output=lock_file))
    _write(tmp_env / ".env", "FOO=bar\nNEW=val\n")
    rc = cmd_drift(_args(env_file=env_file, pinfile=lock_file))
    assert rc == 1


def test_cmd_drift_detects_removed_key(tmp_env):
    env_file = _write(tmp_env / ".env", "FOO=bar\nEXTRA=x\n")
    lock_file = str(tmp_env / ".env.lock")
    cmd_pin(_args(env_file=env_file, output=lock_file))
    _write(tmp_env / ".env", "FOO=bar\n")
    rc = cmd_drift(_args(env_file=env_file, pinfile=lock_file))
    assert rc == 1
