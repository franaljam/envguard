import pytest
from envguard.stringer import to_dotenv, to_ini, to_docker, stringify_env, StringerError


SAMPLE = {"DB_HOST": "localhost", "APP_PORT": "8080", "SECRET": 'my "secret"'}


def test_to_dotenv_basic():
    result = to_dotenv({"KEY": "value"})
    assert result.lines == ["KEY=value"]
    assert result.format == "dotenv"


def test_to_dotenv_escapes_spaces():
    result = to_dotenv({"MSG": "hello world"})
    assert result.lines == ['MSG="hello world"']


def test_to_dotenv_escapes_quotes():
    result = to_dotenv({"X": 'say "hi"'})
    assert result.lines == ['X="say \\"hi\\""']


def test_to_dotenv_sort():
    result = to_dotenv({"Z": "1", "A": "2"}, sort=True)
    assert result.lines[0].startswith("A=")
    assert result.lines[1].startswith("Z=")


def test_to_dotenv_text_joins_lines():
    result = to_dotenv({"A": "1", "B": "2"}, sort=True)
    assert result.text() == "A=1\nB=2"


def test_to_ini_has_section():
    result = to_ini({"KEY": "val"}, section="app")
    assert result.lines[0] == "[app]"
    assert "KEY = val" in result.lines


def test_to_ini_default_section():
    result = to_ini({"X": "1"})
    assert result.lines[0] == "[env]"


def test_to_docker_format():
    result = to_docker({"PORT": "80"})
    assert result.lines == ["-e PORT=80"]
    assert result.format == "docker"


def test_to_docker_escapes_spaces():
    result = to_docker({"MSG": "hello world"})
    assert result.lines == ['-e MSG="hello world"']


def test_stringify_env_dotenv():
    result = stringify_env({"A": "1"}, fmt="dotenv")
    assert result.format == "dotenv"


def test_stringify_env_ini():
    result = stringify_env({"A": "1"}, fmt="ini", section="cfg")
    assert "[cfg]" in result.lines


def test_stringify_env_docker():
    result = stringify_env({"A": "1"}, fmt="docker")
    assert result.format == "docker"


def test_stringify_env_unknown_format_raises():
    with pytest.raises(StringerError, match="Unknown format"):
        stringify_env({"A": "1"}, fmt="xml")
