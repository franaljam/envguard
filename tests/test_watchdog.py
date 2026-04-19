"""Tests for envguard.watchdog."""
import time
from pathlib import Path

import pytest

from envguard.watchdog import (
    WatchEvent,
    WatchResult,
    _changed_keys,
    _file_hash,
    watch_env,
)


@pytest.fixture
def tmp_env(tmp_path):
    p = tmp_path / ".env"
    p.write_text("FOO=bar\nBAZ=qux\n")
    return str(p)


def test_file_hash_returns_string(tmp_env):
    h = _file_hash(tmp_env)
    assert isinstance(h, str) and len(h) == 64


def test_file_hash_changes_on_edit(tmp_env):
    h1 = _file_hash(tmp_env)
    Path(tmp_env).write_text("FOO=changed\n")
    h2 = _file_hash(tmp_env)
    assert h1 != h2


def test_changed_keys_detects_modification():
    old = {"A": "1", "B": "2"}
    new = {"A": "1", "B": "9"}
    assert _changed_keys(old, new) == ["B"]


def test_changed_keys_detects_addition():
    old = {"A": "1"}
    new = {"A": "1", "B": "2"}
    assert _changed_keys(old, new) == ["B"]


def test_changed_keys_detects_removal():
    old = {"A": "1", "B": "2"}
    new = {"A": "1"}
    assert _changed_keys(old, new) == ["B"]


def test_watch_no_changes_returns_empty(tmp_env):
    result = watch_env(tmp_env, duration=0.1, interval=0.05)
    assert result.total_events() == 0
    assert result.summary() == "No changes detected."


def test_watch_detects_change(tmp_env):
    events = []

    def mutate():
        time.sleep(0.05)
        Path(tmp_env).write_text("FOO=new\n")

    import threading
    t = threading.Thread(target=mutate)
    t.start()
    result = watch_env(tmp_env, duration=0.4, interval=0.05, on_change=events.append)
    t.join()
    assert result.total_events() >= 1
    assert "FOO" in result.events[0].changed_keys


def test_watch_event_has_changes_flag():
    ev = WatchEvent(path="x", previous_hash="aaa", current_hash="bbb", changed_keys=["K"])
    assert ev.has_changes is True


def test_watch_event_no_changes_flag():
    ev = WatchEvent(path="x", previous_hash="aaa", current_hash="aaa", changed_keys=[])
    assert ev.has_changes is False


def test_watch_result_summary_with_events():
    ev = WatchEvent(path="x", previous_hash="a", current_hash="b", changed_keys=[])
    r = WatchResult(events=[ev])
    assert "1 change event" in r.summary()
