import argparse
import pytest
from pathlib import Path
from envguard.cli_sorter import cmd_sort, register_sort_parser


@pytest.fixture
def tmp_env(tmp_path):
    def _write(content):
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def _args(**kwargs):
    defaults = {"reverse": False, "inplace": False, "group": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_sort_prints_sorted(tmp_env, capsys):
    f = tmp_env("ZEBRA=1\nAPPLE=2\n")
    rc = cmd_sort(_args(file=f))
    out = capsys.readouterr().out
    assert rc == 0
    assert out.index("APPLE") < out.index("ZEBRA")


def test_already_sorted_message(tmp_env, capsys):
    f = tmp_env("ALPHA=1\nBETA=2\n")
    rc = cmd_sort(_args(file=f))
    out = capsys.readouterr().out
    assert rc == 0
    assert "Already sorted" in out


def test_inplace_writes_file(tmp_env):
    f = tmp_env("Z=z\nA=a\n")
    rc = cmd_sort(_args(file=f, inplace=True))
    assert rc == 0
    content = Path(f).read_text()
    assert content.index("A=a") < content.index("Z=z")


def test_reverse_sort(tmp_env, capsys):
    f = tmp_env("A=1\nZ=2\n")
    rc = cmd_sort(_args(file=f, reverse=True))
    out = capsys.readouterr().out
    assert out.index("Z") < out.index("A")


def test_group_sort(tmp_env, capsys):
    f = tmp_env("OTHER=o\nDB_HOST=h\nAPP_NAME=n\n")
    rc = cmd_sort(_args(file=f, group=["APP", "DB"]))
    out = capsys.readouterr().out
    assert out.index("APP_NAME") < out.index("DB_HOST") < out.index("OTHER")


def test_register_sort_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_sort_parser(sub)
    args = parser.parse_args(["sort", "myfile.env"])
    assert args.file == "myfile.env"
