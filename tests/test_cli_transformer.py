import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile, os

from envguard.cli_transformer import cmd_transform


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def _args(**kwargs):
    defaults = dict(file=None, strip=False, uppercase=False, mask=False, prefix="")
    defaults.update(kwargs)
    m = MagicMock()
    for k, v in defaults.items():
        setattr(m, k, v)
    return m


def test_transform_strip(tmp_env, capsys):
    path = tmp_env("KEY=  hello  \n")
    rc = cmd_transform(_args(file=path, strip=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "KEY=hello" in out


def test_transform_uppercase(tmp_env, capsys):
    path = tmp_env("WORD=hello\n")
    rc = cmd_transform(_args(file=path, uppercase=True))
    assert rc == 0
    assert "WORD=HELLO" in capsys.readouterr().out


def test_transform_mask(tmp_env, capsys):
    path = tmp_env("SECRET=abc\nEMPTY=\n")
    rc = cmd_transform(_args(file=path, mask=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "SECRET=***" in out
    assert "EMPTY=" in out


def test_transform_prefix(tmp_env, capsys):
    path = tmp_env("HOST=localhost\n")
    rc = cmd_transform(_args(file=path, prefix="APP_"))
    assert rc == 0
    assert "APP_HOST=localhost" in capsys.readouterr().out


def test_transform_bad_file(capsys):
    rc = cmd_transform(_args(file="/nonexistent/.env"))
    assert rc == 1


def test_transform_no_ops_passes_through(tmp_env, capsys):
    path = tmp_env("FOO=bar\n")
    rc = cmd_transform(_args(file=path))
    assert rc == 0
    assert "FOO=bar" in capsys.readouterr().out
