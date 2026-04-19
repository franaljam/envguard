import pytest
import argparse
from pathlib import Path
from envguard.cli_grouper import cmd_group, register_group_parser


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path: Path, content: str):
    path.write_text(content)


def _args(file, **kwargs):
    ns = argparse.Namespace(
        file=str(file),
        prefix=kwargs.get("prefix", None),
        separator=kwargs.get("separator", "_"),
        group=kwargs.get("group", None),
        verbose=kwargs.get("verbose", False),
    )
    return ns


def test_group_summary_printed(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\nDEBUG=false\n")
    rc = cmd_group(_args(tmp_env, prefix=["DB"]))
    out = capsys.readouterr().out
    assert rc == 0
    assert "[DB]" in out


def test_verbose_shows_keys(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\n")
    rc = cmd_group(_args(tmp_env, prefix=["DB"], verbose=True))
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out


def test_filter_by_group(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=prod\n")
    rc = cmd_group(_args(tmp_env, prefix=["DB", "APP"], group="APP"))
    out = capsys.readouterr().out
    assert rc == 0
    assert "APP_ENV=prod" in out
    assert "DB_HOST" not in out


def test_missing_group_returns_one(tmp_env, capsys):
    _write(tmp_env, "DB_HOST=localhost\n")
    rc = cmd_group(_args(tmp_env, prefix=["DB"], group="REDIS"))
    assert rc == 1


def test_register_group_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_group_parser(sub)
    args = parser.parse_args(["group", "myfile.env", "--prefix", "DB"])
    assert args.prefix == ["DB"]
