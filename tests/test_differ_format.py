"""Tests for envguard.differ_format."""
from __future__ import annotations

import os
import pytest

from envguard.differ_format import (
    FormatDiffResult,
    FormatChange,
    diff_format,
    _detect_quote_style,
    _detect_spacing,
)


# ---------------------------------------------------------------------------
# unit helpers
# ---------------------------------------------------------------------------

def test_detect_quote_style_double():
    assert _detect_quote_style('"hello world"') == "double"


def test_detect_quote_style_single():
    assert _detect_quote_style("'hello world'") == "single"


def test_detect_quote_style_none():
    assert _detect_quote_style("hello") is None


def test_detect_spacing_compact():
    assert _detect_spacing("KEY=value") == "compact"


def test_detect_spacing_spaced():
    assert _detect_spacing("KEY = value") == "spaced"


def test_detect_spacing_mixed_right():
    assert _detect_spacing("KEY= value") == "mixed"


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _write


# ---------------------------------------------------------------------------
# diff_format tests
# ---------------------------------------------------------------------------

def test_no_differences_when_identical(tmp_env):
    content = 'KEY=value\nOTHER="quoted"\n'
    left = tmp_env("left.env", content)
    right = tmp_env("right.env", content)
    result = diff_format(left, right)
    assert not result.has_changes


def test_quote_change_detected(tmp_env):
    left = tmp_env("left.env", 'DB_HOST="localhost"\n')
    right = tmp_env("right.env", "DB_HOST=localhost\n")
    result = diff_format(left, right)
    assert result.has_changes
    assert result.changes[0].key == "DB_HOST"
    assert result.changes[0].quote_changed


def test_spacing_change_detected(tmp_env):
    left = tmp_env("left.env", "PORT=8080\n")
    right = tmp_env("right.env", "PORT = 8080\n")
    result = diff_format(left, right)
    assert result.has_changes
    assert result.changes[0].spacing_changed


def test_keys_only_in_one_file_ignored(tmp_env):
    left = tmp_env("left.env", "ONLY_LEFT=1\nSHARED=val\n")
    right = tmp_env("right.env", "SHARED=val\nONLY_RIGHT=2\n")
    result = diff_format(left, right)
    keys = [c.key for c in result.changes]
    assert "ONLY_LEFT" not in keys
    assert "ONLY_RIGHT" not in keys


def test_summary_no_changes(tmp_env):
    c = "A=1\n"
    result = diff_format(tmp_env("l.env", c), tmp_env("r.env", c))
    assert "No formatting" in result.summary


def test_summary_with_changes(tmp_env):
    left = tmp_env("l.env", 'X="val"\n')
    right = tmp_env("r.env", "X=val\n")
    result = diff_format(left, right)
    assert "1 formatting difference" in result.summary
    assert "X" in result.summary


def test_comments_and_blanks_skipped(tmp_env):
    left = tmp_env("l.env", "# comment\n\nKEY=val\n")
    right = tmp_env("r.env", "KEY=val\n")
    result = diff_format(left, right)
    assert not result.has_changes
