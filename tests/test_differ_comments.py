"""Tests for envguard.differ_comments."""
from __future__ import annotations

import pytest

from envguard.differ_comments import (
    CommentDiffResult,
    diff_comments,
    _extract_comment,
    _parse_comments,
)


# ---------------------------------------------------------------------------
# _extract_comment
# ---------------------------------------------------------------------------

def test_extract_comment_with_inline_comment():
    assert _extract_comment('value # my note') == 'my note'


def test_extract_comment_no_comment():
    assert _extract_comment('value') is None


def test_extract_comment_empty_comment():
    result = _extract_comment('value #')
    assert result == '' or result is None  # stripped empty string


# ---------------------------------------------------------------------------
# _parse_comments
# ---------------------------------------------------------------------------

def test_parse_comments_basic():
    lines = [
        'FOO=bar # a comment\n',
        'BAZ=qux\n',
    ]
    result = _parse_comments(lines)
    assert result['FOO'] == 'a comment'
    assert result['BAZ'] is None


def test_parse_comments_skips_blank_and_full_comments():
    lines = [
        '\n',
        '# full line comment\n',
        'KEY=val\n',
    ]
    result = _parse_comments(lines)
    assert list(result.keys()) == ['KEY']


# ---------------------------------------------------------------------------
# diff_comments
# ---------------------------------------------------------------------------

def _lines(*entries: str):
    return [e + '\n' for e in entries]


def test_no_changes_when_identical():
    left = _lines('FOO=bar # note', 'BAZ=qux')
    result = diff_comments(left, left)
    assert not result.has_changes
    assert result.summary() == 'No comment differences.'


def test_added_comment_detected():
    left = _lines('FOO=bar')
    right = _lines('FOO=bar # new note')
    result = diff_comments(left, right)
    assert result.has_changes
    assert len(result.added()) == 1
    assert result.added()[0].key == 'FOO'
    assert result.added()[0].right == 'new note'


def test_removed_comment_detected():
    left = _lines('FOO=bar # old note')
    right = _lines('FOO=bar')
    result = diff_comments(left, right)
    assert len(result.removed()) == 1
    assert result.removed()[0].key == 'FOO'
    assert result.removed()[0].left == 'old note'


def test_modified_comment_detected():
    left = _lines('FOO=bar # original')
    right = _lines('FOO=bar # updated')
    result = diff_comments(left, right)
    assert len(result.modified()) == 1
    change = result.modified()[0]
    assert change.key == 'FOO'
    assert change.left == 'original'
    assert change.right == 'updated'


def test_summary_lists_counts():
    left = _lines('A=1 # note', 'B=2', 'C=3 # keep')
    right = _lines('A=1 # changed', 'B=2 # added', 'C=3 # keep')
    result = diff_comments(left, right)
    summary = result.summary()
    assert 'added' in summary
    assert 'modified' in summary


def test_key_only_in_right_treated_as_added():
    left = _lines('FOO=1')
    right = _lines('FOO=1', 'BAR=2 # bar note')
    result = diff_comments(left, right)
    added_keys = [c.key for c in result.added()]
    assert 'BAR' in added_keys


def test_returns_comment_diff_result_instance():
    result = diff_comments([], [])
    assert isinstance(result, CommentDiffResult)
