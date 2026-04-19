import pytest
from envguard.differ_keys import diff_keys, KeyDiffResult


A = {"HOST": "localhost", "PORT": "5432", "DB_NAME": "mydb"}
B = {"HOST": "localhost", "PORT": "5432", "DB_NAME": "mydb"}


def test_identical_envs_no_changes():
    result = diff_keys(A, B)
    assert not result.has_changes()
    assert result.added == []
    assert result.removed == []
    assert result.renamed == []


def test_added_key_detected():
    result = diff_keys(A, {**A, "NEW_KEY": "val"})
    assert "NEW_KEY" in result.added
    assert not result.removed


def test_removed_key_detected():
    base = {**A, "OLD_KEY": "val"}
    result = diff_keys(base, A)
    assert "OLD_KEY" in result.removed
    assert not result.added


def test_common_keys_listed():
    result = diff_keys(A, B)
    assert sorted(result.common) == sorted(A.keys())


def test_rename_detected():
    base = {"DB_HOST": "localhost"}
    target = {"DB_HOSTNAME": "localhost"}
    result = diff_keys(base, target, detect_renames=True, rename_threshold=0.6)
    assert len(result.renamed) == 1
    old, new = result.renamed[0]
    assert old == "DB_HOST"
    assert new == "DB_HOSTNAME"
    assert result.added == []
    assert result.removed == []


def test_rename_disabled():
    base = {"DB_HOST": "localhost"}
    target = {"DB_HOSTNAME": "localhost"}
    result = diff_keys(base, target, detect_renames=False)
    assert result.renamed == []
    assert "DB_HOST" in result.removed
    assert "DB_HOSTNAME" in result.added


def test_summary_no_changes():
    result = diff_keys(A, B)
    assert result.summary() == "No key changes detected."


def test_summary_with_changes():
    result = diff_keys({"A": "1"}, {"B": "2"})
    s = result.summary()
    assert "added" in s or "removed" in s or "renamed" in s


def test_has_changes_true_on_add():
    result = diff_keys({}, {"X": "1"})
    assert result.has_changes()


def test_rename_threshold_too_low_no_match():
    base = {"X": "1"}
    target = {"COMPLETELY_DIFFERENT": "1"}
    result = diff_keys(base, target, detect_renames=True, rename_threshold=0.99)
    assert result.renamed == []
