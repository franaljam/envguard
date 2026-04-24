"""Tests for envguard.indexer."""
import pytest
from pathlib import Path

from envguard.indexer import IndexEntry, IndexResult, index_env_files


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


# ---------------------------------------------------------------------------
# IndexEntry helpers
# ---------------------------------------------------------------------------

def test_index_entry_appears_in():
    e = IndexEntry(key="FOO", files=["a.env"], values={"a.env": "1"})
    assert e.appears_in("a.env")
    assert not e.appears_in("b.env")


def test_index_entry_consistent_single_file():
    e = IndexEntry(key="FOO", files=["a.env"], values={"a.env": "1"})
    assert e.is_consistent()


def test_index_entry_consistent_same_values():
    e = IndexEntry(key="FOO", files=["a.env", "b.env"], values={"a.env": "1", "b.env": "1"})
    assert e.is_consistent()


def test_index_entry_inconsistent_different_values():
    e = IndexEntry(key="FOO", files=["a.env", "b.env"], values={"a.env": "1", "b.env": "2"})
    assert not e.is_consistent()


# ---------------------------------------------------------------------------
# index_env_files
# ---------------------------------------------------------------------------

def test_index_single_file(tmp_env):
    path = tmp_env("dev.env", "FOO=bar\nBAZ=qux\n")
    result = index_env_files([path])
    assert "FOO" in result
    assert "BAZ" in result
    assert len(result.sources) == 1


def test_index_multiple_files_shared_key(tmp_env):
    a = tmp_env("a.env", "FOO=same\n")
    b = tmp_env("b.env", "FOO=same\n")
    result = index_env_files([a, b])
    assert result["FOO"].is_consistent()
    assert len(result["FOO"].files) == 2


def test_index_multiple_files_inconsistent_key(tmp_env):
    a = tmp_env("a.env", "SECRET=abc\n")
    b = tmp_env("b.env", "SECRET=xyz\n")
    result = index_env_files([a, b])
    assert not result["SECRET"].is_consistent()
    assert "SECRET" in result.inconsistent_keys()


def test_keys_in_returns_correct_subset(tmp_env):
    a = tmp_env("a.env", "ONLY_A=1\nSHARED=x\n")
    b = tmp_env("b.env", "ONLY_B=2\nSHARED=x\n")
    result = index_env_files([a, b])
    keys_a = result.keys_in(str(Path(a).name) if False else a)
    assert "ONLY_A" in keys_a
    assert "SHARED" in keys_a
    assert "ONLY_B" not in keys_a


def test_unique_to_returns_exclusive_keys(tmp_env):
    a = tmp_env("a.env", "ONLY_A=1\nSHARED=x\n")
    b = tmp_env("b.env", "ONLY_B=2\nSHARED=x\n")
    result = index_env_files([a, b])
    unique_a = result.unique_to(a)
    assert "ONLY_A" in unique_a
    assert "SHARED" not in unique_a


def test_summary_string(tmp_env):
    a = tmp_env("a.env", "FOO=1\nBAR=2\n")
    b = tmp_env("b.env", "FOO=9\nBAZ=3\n")
    result = index_env_files([a, b])
    s = result.summary()
    assert "3 unique key" in s
    assert "2 file" in s
    assert "inconsistent" in s


def test_empty_file_produces_no_entries(tmp_env):
    path = tmp_env("empty.env", "\n# just a comment\n")
    result = index_env_files([path])
    assert len(result.entries) == 0
