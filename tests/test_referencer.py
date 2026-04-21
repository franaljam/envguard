"""Tests for envguard.referencer."""
import textwrap
from pathlib import Path

import pytest

from envguard.referencer import ReferenceResult, ReferenceHit, find_references


@pytest.fixture()
def tmp_env(tmp_path):
    """Return a helper that writes a .env file and returns its Path."""
    counter = {"n": 0}

    def _write(content: str) -> Path:
        counter["n"] += 1
        p = tmp_path / f"env{counter['n']}.env"
        p.write_text(textwrap.dedent(content))
        return p

    return _write


def test_no_references_returns_empty(tmp_env):
    f = tmp_env("""
        HOST=localhost
        PORT=5432
    """)
    result = find_references("BASE_URL", [f])
    assert not result.found()
    assert result.hits == []


def test_brace_syntax_detected(tmp_env):
    f = tmp_env("""
        BASE_URL=http://localhost
        FULL_URL=${BASE_URL}/api
    """)
    result = find_references("BASE_URL", [f])
    assert result.found()
    assert len(result.hits) == 1
    assert result.hits[0].key == "FULL_URL"


def test_plain_dollar_syntax_detected(tmp_env):
    f = tmp_env("""
        HOST=localhost
        ADDR=$HOST:8080
    """)
    result = find_references("HOST", [f])
    assert result.found()
    assert result.hits[0].key == "ADDR"


def test_self_reference_excluded(tmp_env):
    """A key that references itself should not be reported."""
    f = tmp_env("""
        FOO=${FOO:-default}
    """)
    result = find_references("FOO", [f])
    assert not result.found()


def test_multiple_files_searched(tmp_env):
    f1 = tmp_env("A=1\nB=${A}\n")
    f2 = tmp_env("C=${A}\nD=4\n")
    result = find_references("A", [f1, f2])
    assert result.found()
    assert len(result.hits) == 2
    assert len(result.files()) == 2


def test_files_returns_unique_paths(tmp_env):
    f = tmp_env("B=${A}\nC=${A}\n")
    result = find_references("A", [f])
    assert len(result.files()) == 1


def test_comments_skipped(tmp_env):
    f = tmp_env("""
        # COMMENTED=${BASE}
        REAL=value
    """)
    result = find_references("BASE", [f])
    assert not result.found()


def test_missing_file_skipped(tmp_path):
    missing = tmp_path / "ghost.env"
    result = find_references("KEY", [missing])
    assert not result.found()


def test_summary_no_hits():
    r = ReferenceResult(target="X")
    assert "No references" in r.summary()


def test_summary_with_hits(tmp_env):
    f = tmp_env("URL=${BASE}/path\n")
    result = find_references("BASE", [f])
    summary = result.summary()
    assert "1 reference" in summary
    assert "URL" in summary


def test_line_number_recorded(tmp_env):
    f = tmp_env("FIRST=1\nSECOND=${FIRST}\nTHIRD=3\n")
    result = find_references("FIRST", [f])
    assert result.hits[0].line_number == 2
