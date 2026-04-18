"""Tests for envguard.merger."""
import pytest
from envguard.merger import merge_envs, merge_env_files, MergeResult, MergeConflict


def test_merge_no_overlap():
    sources = {
        "base": {"A": "1", "B": "2"},
        "prod": {"C": "3"},
    }
    result = merge_envs(sources)
    assert result.merged == {"A": "1", "B": "2", "C": "3"}
    assert not result.has_conflicts


def test_merge_same_values_no_conflict():
    sources = {
        "base": {"A": "1"},
        "prod": {"A": "1"},
    }
    result = merge_envs(sources)
    assert not result.has_conflicts
    assert result.merged["A"] == "1"


def test_merge_conflict_detected():
    sources = {
        "base": {"SECRET": "abc"},
        "prod": {"SECRET": "xyz"},
    }
    result = merge_envs(sources)
    assert result.has_conflicts
    assert "SECRET" in result.conflict_keys()
    conflict = result.conflicts[0]
    assert conflict.values == {"base": "abc", "prod": "xyz"}


def test_merge_strategy_last():
    sources = {
        "base": {"A": "first"},
        "prod": {"A": "last"},
    }
    result = merge_envs(sources, strategy="last")
    assert result.merged["A"] == "last"


def test_merge_strategy_first():
    sources = {
        "base": {"A": "first"},
        "prod": {"A": "last"},
    }
    result = merge_envs(sources, strategy="first")
    assert result.merged["A"] == "first"


def test_merge_invalid_strategy():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs({"a": {"X": "1"}}, strategy="random")


def test_merge_multiple_sources_conflict_tracking():
    sources = {
        "base": {"X": "1"},
        "staging": {"X": "2"},
        "prod": {"X": "3"},
    }
    result = merge_envs(sources, strategy="last")
    assert result.merged["X"] == "3"
    assert result.has_conflicts
    assert set(result.conflicts[0].values.keys()) == {"base", "staging", "prod"}


def test_merge_env_files(tmp_path):
    base = tmp_path / "base.env"
    prod = tmp_path / "prod.env"
    base.write_text("A=1\nB=shared\n")
    prod.write_text("B=override\nC=3\n")

    result = merge_env_files(
        {"base": str(base), "prod": str(prod)}, strategy="last"
    )
    assert result.merged["A"] == "1"
    assert result.merged["B"] == "override"
    assert result.merged["C"] == "3"
    assert "B" in result.conflict_keys()
