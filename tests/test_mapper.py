"""Tests for envguard.mapper."""
from __future__ import annotations

import pytest
from pathlib import Path

from envguard.mapper import map_envs, MapResult


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Return a helper that writes a .env file and returns its path."""
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


# ---------------------------------------------------------------------------
# map_envs basic behaviour
# ---------------------------------------------------------------------------

def test_returns_map_result(tmp_env):
    a = tmp_env("a.env", "FOO=1\n")
    result = map_envs([a])
    assert isinstance(result, MapResult)


def test_single_file_all_keys_present(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    result = map_envs([a])
    assert "FOO" in result
    assert "BAR" in result


def test_key_appears_in_correct_file(tmp_env):
    a = tmp_env("a.env", "FOO=hello\n")
    result = map_envs([a])
    assert result["FOO"].appears_in(a)


def test_key_shared_across_files(tmp_env):
    a = tmp_env("a.env", "SHARED=1\n")
    b = tmp_env("b.env", "SHARED=1\n")
    result = map_envs([a, b])
    assert result["SHARED"].appears_in(a)
    assert result["SHARED"].appears_in(b)


def test_consistent_same_value(tmp_env):
    a = tmp_env("a.env", "KEY=same\n")
    b = tmp_env("b.env", "KEY=same\n")
    result = map_envs([a, b])
    assert result["KEY"].is_consistent()


def test_inconsistent_different_values(tmp_env):
    a = tmp_env("a.env", "KEY=foo\n")
    b = tmp_env("b.env", "KEY=bar\n")
    result = map_envs([a, b])
    assert not result["KEY"].is_consistent()


def test_inconsistent_keys_listed(tmp_env):
    a = tmp_env("a.env", "KEY=foo\nSTABLE=x\n")
    b = tmp_env("b.env", "KEY=bar\nSTABLE=x\n")
    result = map_envs([a, b])
    assert result.inconsistent_keys() == ["KEY"]


def test_unique_to_returns_exclusive_keys(tmp_env):
    a = tmp_env("a.env", "ONLY_A=1\nSHARED=2\n")
    b = tmp_env("b.env", "SHARED=2\n")
    result = map_envs([a, b])
    assert result.unique_to(a) == ["ONLY_A"]
    assert result.unique_to(b) == []


def test_summary_contains_counts(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "FOO=99\n")
    result = map_envs([a, b])
    s = result.summary()
    assert "2" in s  # 2 unique keys
    assert "inconsistent" in s


def test_empty_files_produce_empty_result(tmp_env):
    a = tmp_env("a.env", "")
    result = map_envs([a])
    assert result.keys() == []


def test_no_files_returns_empty_result():
    result = map_envs([])
    assert result.keys() == []
