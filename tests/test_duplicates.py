import pytest
from pathlib import Path
from envguard.duplicates import find_duplicates, DuplicateResult


@pytest.fixture
def tmp_env(tmp_path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def test_no_duplicates(tmp_env):
    path = tmp_env("FOO=bar\nBAZ=qux\n")
    result = find_duplicates(path)
    assert not result.has_duplicates()


def test_single_duplicate(tmp_env):
    path = tmp_env("FOO=first\nFOO=second\n")
    result = find_duplicates(path)
    assert result.has_duplicates()
    assert "FOO" in result.duplicates
    assert result.duplicates["FOO"] == ["first", "second"]


def test_multiple_duplicates(tmp_env):
    path = tmp_env("A=1\nB=2\nA=3\nB=4\n")
    result = find_duplicates(path)
    assert set(result.duplicates.keys()) == {"A", "B"}


def test_skips_comments_and_blanks(tmp_env):
    path = tmp_env("# comment\n\nFOO=bar\nFOO=baz\n")
    result = find_duplicates(path)
    assert "FOO" in result.duplicates
    assert len(result.duplicates) == 1


def test_summary_no_duplicates(tmp_env):
    path = tmp_env("X=1\n")
    result = find_duplicates(path)
    assert result.summary() == "No duplicate keys found."


def test_summary_with_duplicates(tmp_env):
    path = tmp_env("KEY=a\nKEY=b\n")
    result = find_duplicates(path)
    summary = result.summary()
    assert "KEY" in summary
    assert '"a"' in summary
    assert '"b"' in summary


def test_triple_occurrence(tmp_env):
    path = tmp_env("Z=1\nZ=2\nZ=3\n")
    result = find_duplicates(path)
    assert result.duplicates["Z"] == ["1", "2", "3"]
