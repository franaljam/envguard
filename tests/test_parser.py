"""Tests for envguard.parser module."""

import pytest
from pathlib import Path

from envguard.parser import parse_env_file, EnvParseError


@pytest.fixture
def tmp_env(tmp_path):
    """Helper to create a temporary .env file."""
    def _write(content: str) -> Path:
        env_file = tmp_path / ".env"
        env_file.write_text(content, encoding="utf-8")
        return env_file
    return _write


def test_parse_simple_key_value(tmp_env):
    path = tmp_env("KEY=value\n")
    result = parse_env_file(path)
    assert result == {"KEY": "value"}


def test_parse_multiple_vars(tmp_env):
    path = tmp_env("APP_ENV=production\nDEBUG=false\nPORT=8080\n")
    result = parse_env_file(path)
    assert result == {"APP_ENV": "production", "DEBUG": "false", "PORT": "8080"}


def test_skips_comments_and_blank_lines(tmp_env):
    content = "# This is a comment\n\nKEY=value\n"
    path = tmp_env(content)
    result = parse_env_file(path)
    assert result == {"KEY": "value"}


def test_strips_double_quotes(tmp_env):
    path = tmp_env('SECRET="my secret value"\n')
    result = parse_env_file(path)
    assert result == {"SECRET": "my secret value"}


def test_strips_single_quotes(tmp_env):
    path = tmp_env("TOKEN='abc123'\n")
    result = parse_env_file(path)
    assert result == {"TOKEN": "abc123"}


def test_empty_value_returns_none(tmp_env):
    path = tmp_env("EMPTY_KEY=\n")
    result = parse_env_file(path)
    assert result == {"EMPTY_KEY": None}


def test_file_not_found_raises_error(tmp_path):
    with pytest.raises(EnvParseError, match="File not found"):
        parse_env_file(tmp_path / "nonexistent.env")


def test_invalid_syntax_raises_error(tmp_env):
    path = tmp_env("INVALID_LINE\n")
    with pytest.raises(EnvParseError, match="Invalid syntax at line 1"):
        parse_env_file(path)


def test_empty_key_raises_error(tmp_env):
    path = tmp_env("=value\n")
    with pytest.raises(EnvParseError, match="Empty key at line 1"):
        parse_env_file(path)


def test_invalid_syntax_reports_correct_line_number(tmp_env):
    """Ensure the error message references the correct line for multi-line files."""
    path = tmp_env("VALID=ok\n# comment\nBAD_LINE\n")
    with pytest.raises(EnvParseError, match="Invalid syntax at line 3"):
        parse_env_file(path)
