"""Tests for envguard.auditor."""
import pytest
from envguard.auditor import audit_env, AuditResult


def test_no_issues_for_clean_env():
    result = audit_env({"HOST": "localhost", "PORT": "8080", "DEBUG": "false"})
    assert not result.has_issues
    assert result.summary() == "No audit issues found."


def test_empty_value_is_warning():
    result = audit_env({"HOST": ""})
    assert result.has_issues
    assert len(result.warnings) == 1
    assert result.warnings[0].key == "HOST"
    assert len(result.errors) == 0


def test_weak_password_is_error():
    result = audit_env({"DB_PASSWORD": "password"})
    assert len(result.errors) == 1
    assert result.errors[0].key == "DB_PASSWORD"
    assert "Weak" in result.errors[0].message


def test_weak_check_disabled():
    result = audit_env({"DB_PASSWORD": "password"}, check_weak=False)
    assert not any(i.severity == "error" for i in result.issues)


def test_short_secret_is_warning():
    result = audit_env({"API_KEY": "abc"})
    warns = [i for i in result.warnings if "short" in i.message]
    assert len(warns) == 1


def test_strong_secret_no_issue():
    result = audit_env({"API_KEY": "s3cur3-r4nd0m-v4lue-xyz"})
    assert not result.has_issues


def test_summary_counts_errors_and_warnings():
    result = audit_env({"SECRET_TOKEN": "x", "HOST": ""})
    summary = result.summary()
    assert "error" in summary
    assert "warning" in summary


def test_multiple_issues():
    vars_ = {
        "DB_PASSWORD": "changeme",
        "API_SECRET": "short",
        "EMPTY_VAR": "",
    }
    result = audit_env(vars_)
    keys = {i.key for i in result.issues}
    assert "DB_PASSWORD" in keys
    assert "EMPTY_VAR" in keys
