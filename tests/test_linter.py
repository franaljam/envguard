import pytest
from envguard.linter import lint_env, LintResult


def test_clean_env_no_issues():
    result = lint_env({"DATABASE_URL": "postgres://localhost/db", "DEBUG": "false"})
    assert not result.has_issues()


def test_lowercase_key_is_warning():
    result = lint_env({"db_host": "localhost"})
    warnings = result.warnings()
    assert any("UPPER_SNAKE_CASE" in w.message for w in warnings)


def test_allow_lowercase_suppresses_warning():
    result = lint_env({"db_host": "localhost"}, allow_lowercase=True)
    assert not result.has_issues()


def test_key_starting_with_digit_is_error():
    result = lint_env({"1BAD_KEY": "value"})
    assert any(i.severity == "error" and "digit" in i.message for i in result.issues)


def test_key_with_spaces_is_error():
    result = lint_env({"BAD KEY": "value"})
    assert any(i.severity == "error" and "spaces" in i.message for i in result.issues)


def test_value_with_leading_whitespace_is_warning():
    result = lint_env({"KEY": " value"})
    assert any("whitespace" in w.message for w in result.warnings())


def test_value_with_trailing_whitespace_is_warning():
    result = lint_env({"KEY": "value "})
    assert any("whitespace" in w.message for w in result.warnings())


def test_value_with_newline_is_warning():
    result = lint_env({"KEY": "line1\nline2"})
    assert any("newline" in w.message for w in result.warnings())


def test_summary_counts():
    result = lint_env({"bad key": " spaced ", "1DIGIT": "ok"})
    s = result.summary()
    assert "error" in s and "warning" in s


def test_errors_and_warnings_filtered():
    result = lint_env({"bad key": " value"})
    assert all(i.severity == "error" for i in result.errors())
    assert all(i.severity == "warning" for i in result.warnings())
