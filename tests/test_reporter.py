"""Tests for envguard.reporter formatting functions."""
import pytest
from envguard.reporter import format_diff_report, format_validation_report


def make_diff(missing=None, extra=None, changed=None):
    return {
        "missing_keys": set(missing or []),
        "extra_keys": set(extra or []),
        "changed_values": changed or {},
    }


def make_validation(valid=True, missing=None, empty=None):
    return {
        "valid": valid,
        "missing_keys": list(missing or []),
        "empty_keys": list(empty or []),
    }


def test_diff_no_differences():
    report = format_diff_report(make_diff(), use_color=False)
    assert "No differences found." in report


def test_diff_missing_key():
    report = format_diff_report(make_diff(missing=["DB_HOST"]), use_color=False)
    assert "MISSING" in report
    assert "DB_HOST" in report


def test_diff_extra_key():
    report = format_diff_report(make_diff(extra=["DEBUG"]), use_color=False)
    assert "EXTRA" in report
    assert "DEBUG" in report


def test_diff_changed_value():
    report = format_diff_report(
        make_diff(changed={"PORT": ("8080", "9090")}), use_color=False
    )
    assert "CHANGED" in report
    assert "PORT" in report
    assert "8080" in report
    assert "9090" in report


def test_diff_report_has_header():
    report = format_diff_report(make_diff(), use_color=False)
    assert "Env Diff Report" in report


def test_validation_valid():
    report = format_validation_report(make_validation(valid=True), use_color=False)
    assert "valid" in report.lower()
    assert "MISSING" not in report


def test_validation_missing_key():
    report = format_validation_report(
        make_validation(valid=False, missing=["SECRET_KEY"]), use_color=False
    )
    assert "MISSING" in report
    assert "SECRET_KEY" in report


def test_validation_empty_key():
    report = format_validation_report(
        make_validation(valid=False, empty=["API_TOKEN"]), use_color=False
    )
    assert "EMPTY" in report
    assert "API_TOKEN" in report


def test_validation_report_has_header():
    report = format_validation_report(make_validation(), use_color=False)
    assert "Env Validation Report" in report
