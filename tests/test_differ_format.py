"""Tests for envguard.differ_format."""
import pytest
from envguard.differ_format import (
    FormatChange,
    FormatDiffResult,
    diff_format,
    _detect_quoting,
    _has_spacing_around_eq,
    _has_trailing_whitespace,
)


# ---------------------------------------------------------------------------
# unit helpers
# ---------------------------------------------------------------------------

def test_detect_quoting_double():
    assert _detect_quoting('KEY="value"') == '"'


def test_detect_quoting_single():
    assert _detect_quoting("KEY='value'") == "'"


def test_detect_quoting_none():
    assert _detect_quoting('KEY=value') is None


def test_spacing_around_eq_detected():
    assert _has_spacing_around_eq('KEY = value') is True


def test_no_spacing_around_eq():
    assert _has_spacing_around_eq('KEY=value') is False


def test_trailing_whitespace_detected():
    assert _has_trailing_whitespace('KEY=value   ') is True


def test_no_trailing_whitespace():
    assert _has_trailing_whitespace('KEY=value') is False


# ---------------------------------------------------------------------------
# diff_format
# ---------------------------------------------------------------------------

def test_identical_lines_no_changes():
    left = {'A': 'A=hello', 'B': 'B=world'}
    right = {'A': 'A=hello', 'B': 'B=world'}
    result = diff_format(left, right)
    assert not result.has_changes()
    assert result.keys_with_issues() == []


def test_quote_style_change_detected():
    left = {'KEY': 'KEY=value'}
    right = {'KEY': 'KEY="value"'}
    result = diff_format(left, right)
    assert result.has_changes()
    assert 'KEY' in result.keys_with_issues()
    assert any('quote style' in i for i in result.changes[0].issues)


def test_spacing_change_detected():
    left = {'KEY': 'KEY=value'}
    right = {'KEY': 'KEY = value'}
    result = diff_format(left, right)
    assert result.has_changes()
    assert any("spacing" in i for i in result.changes[0].issues)


def test_trailing_whitespace_change_detected():
    left = {'KEY': 'KEY=value'}
    right = {'KEY': 'KEY=value   '}
    result = diff_format(left, right)
    assert result.has_changes()
    assert any('trailing' in i for i in result.changes[0].issues)


def test_keys_only_in_one_side_ignored():
    left = {'A': 'A=1', 'ONLY_LEFT': 'ONLY_LEFT=x'}
    right = {'A': 'A=1', 'ONLY_RIGHT': 'ONLY_RIGHT=y'}
    result = diff_format(left, right)
    assert not result.has_changes()


def test_multiple_issues_on_same_key():
    left = {'K': 'K=val'}
    right = {'K': 'K = "val"   '}
    result = diff_format(left, right)
    assert result.has_changes()
    assert len(result.changes[0].issues) >= 2


def test_summary_no_changes():
    result = FormatDiffResult()
    assert 'No formatting' in result.summary()


def test_summary_with_changes():
    change = FormatChange(
        key='DB_URL',
        left_raw='DB_URL=postgres',
        right_raw='DB_URL="postgres"',
        issues=['quote style changed (unquoted -> \'"\')'],
    )
    result = FormatDiffResult(changes=[change])
    summary = result.summary()
    assert 'DB_URL' in summary
    assert '1 key' in summary
