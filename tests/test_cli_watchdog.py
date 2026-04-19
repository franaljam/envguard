"""Tests for envguard.cli_watchdog."""
import argparse
import time
import threading
from pathlib import Path

import pytest

from envguard.cli_watchdog import cmd_watch, register_watch_parser


@pytest.fixture
def tmp_env(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY=value\n")
    return str(p)


def _args(file, duration=0.1, interval=0.05):
    ns = argparse.Namespace(file=file, duration=duration, interval=interval)
    return ns


def test_watch_no_change_exits_zero(tmp_env):
    with pytest.raises(SystemExit) as exc:
        cmd_watch(_args(tmp_env))
    assert exc.value.code == 0


def test_watch_change_exits_one(tmp_env):
    def mutate():
        time.sleep(0.04)
        Path(tmp_env).write_text("KEY=changed\n")

    t = threading.Thread(target=mutate)
    t.start()
    with pytest.raises(SystemExit) as exc:
        cmd_watch(_args(tmp_env, duration=0.3, interval=0.04))
    t.join()
    assert exc.value.code == 1


def test_watch_missing_file_exits_two(tmp_path):
    with pytest.raises(SystemExit) as exc:
        cmd_watch(_args(str(tmp_path / "missing.env")))
    assert exc.value.code == 2


def test_register_watch_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_watch_parser(sub)
    ns = parser.parse_args(["watch", "some.env", "--duration", "3"])
    assert ns.file == "some.env"
    assert ns.duration == 3.0
