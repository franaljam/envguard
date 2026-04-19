"""Tests for envguard.digester."""
import json
import os
import pytest
from envguard.digester import (
    digest_env, compare_digests, save_digest, load_digest, DigestResult
)


def test_digest_returns_result_for_each_key():
    env = {"KEY": "value", "OTHER": "data"}
    result = digest_env(env)
    assert "KEY" in result
    assert "OTHER" in result


def test_digest_same_value_same_hash():
    r1 = digest_env({"A": "hello"})
    r2 = digest_env({"A": "hello"})
    assert r1["A"] == r2["A"]


def test_digest_different_values_different_hash():
    r1 = digest_env({"A": "hello"})
    r2 = digest_env({"A": "world"})
    assert r1["A"] != r2["A"]


def test_digest_algorithm_md5():
    result = digest_env({"K": "v"}, algorithm="md5")
    assert result.algorithm == "md5"
    assert len(result["K"]) == 32


def test_compare_no_drift():
    env = {"A": "1", "B": "2"}
    old = digest_env(env)
    new = digest_env(env)
    cmp = compare_digests(old, new)
    assert not cmp.has_drift
    assert cmp.summary() == "no drift detected"


def test_compare_detects_changed():
    old = digest_env({"A": "old"})
    new = digest_env({"A": "new"})
    cmp = compare_digests(old, new)
    assert cmp.has_drift
    assert "A" in cmp.changed
    assert "1 changed" in cmp.summary()


def test_compare_detects_added():
    old = digest_env({"A": "1"})
    new = digest_env({"A": "1", "B": "2"})
    cmp = compare_digests(old, new)
    assert "B" in cmp.added
    assert "1 added" in cmp.summary()


def test_compare_detects_removed():
    old = digest_env({"A": "1", "B": "2"})
    new = digest_env({"A": "1"})
    cmp = compare_digests(old, new)
    assert "B" in cmp.removed
    assert "1 removed" in cmp.summary()


def test_save_and_load_roundtrip(tmp_path):
    env = {"X": "foo", "Y": "bar"}
    result = digest_env(env)
    path = str(tmp_path / "digest.json")
    save_digest(result, path)
    loaded = load_digest(path)
    assert loaded.digests == result.digests
    assert loaded.algorithm == result.algorithm


def test_save_creates_valid_json(tmp_path):
    path = str(tmp_path / "digest.json")
    save_digest(digest_env({"K": "v"}), path)
    with open(path) as f:
        data = json.load(f)
    assert "digests" in data
    assert "algorithm" in data
