"""Tests for envguard.linker."""
import pytest
from envguard.linker import LinkEntry, LinkResult, link_envs


DEV = {"DB_HOST": "localhost", "DEBUG": "true", "APP_PORT": "8000"}
STAGING = {"DB_HOST": "staging.db", "DEBUG": "false", "LOG_LEVEL": "info"}
PROD = {"DB_HOST": "prod.db", "LOG_LEVEL": "warn", "APP_PORT": "443"}


def _link(*envs):
    names = [f"env{i}" for i in range(len(envs))]
    return link_envs(dict(zip(names, envs)))


def test_all_keys_present():
    result = _link(DEV, STAGING)
    assert "DB_HOST" in result
    assert "DEBUG" in result
    assert "LOG_LEVEL" in result
    assert "APP_PORT" in result


def test_shared_keys_detected():
    result = _link(DEV, STAGING)
    shared = result.shared_keys()
    assert "DB_HOST" in shared
    assert "DEBUG" in shared
    # APP_PORT only in DEV, LOG_LEVEL only in STAGING
    assert "APP_PORT" not in shared
    assert "LOG_LEVEL" not in shared


def test_inconsistent_keys_detected():
    result = _link(DEV, STAGING)
    inconsistent = result.inconsistent_keys()
    assert "DB_HOST" in inconsistent
    assert "DEBUG" in inconsistent


def test_consistent_shared_key():
    a = {"KEY": "same"}
    b = {"KEY": "same"}
    result = link_envs({"a": a, "b": b})
    assert "KEY" not in result.inconsistent_keys()
    assert "KEY" in result.shared_keys()


def test_single_file_no_shared_keys():
    result = link_envs({"only": DEV})
    assert result.shared_keys() == []
    assert result.inconsistent_keys() == []


def test_entry_files_list():
    result = link_envs({"dev": DEV, "staging": STAGING})
    entry = result.entries["DB_HOST"]
    assert "dev" in entry.files
    assert "staging" in entry.files


def test_entry_values_map():
    result = link_envs({"dev": DEV, "staging": STAGING})
    entry = result.entries["DB_HOST"]
    assert entry.values["dev"] == "localhost"
    assert entry.values["staging"] == "staging.db"


def test_summary_string():
    result = _link(DEV, STAGING)
    s = result.summary()
    assert "shared" in s
    assert "inconsistent" in s


def test_three_way_link():
    result = link_envs({"dev": DEV, "staging": STAGING, "prod": PROD})
    entry = result.entries["DB_HOST"]
    assert len(entry.files) == 3
    assert not entry.is_consistent


def test_original_dicts_not_mutated():
    dev_copy = dict(DEV)
    staging_copy = dict(STAGING)
    link_envs({"dev": dev_copy, "staging": staging_copy})
    assert dev_copy == DEV
    assert staging_copy == STAGING
