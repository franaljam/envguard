import argparse
import os
import pytest
from envguard.cli_promoter import cmd_promote, register_promote_parser


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path, content):
    path.write_text(content)
    return str(path)


def _args(source, target, **kwargs):
    ns = argparse.Namespace(
        source=source,
        target=target,
        keys=kwargs.get("keys", None),
        overwrite=kwargs.get("overwrite", False),
        output=kwargs.get("output", None),
        verbose=kwargs.get("verbose", False),
    )
    return ns


def test_promote_new_key(tmp_env, capsys):
    src = _write(tmp_env / "src.env", "NEW_KEY=hello\nDB_HOST=prod\n")
    tgt = _write(tmp_env / "tgt.env", "DB_HOST=staging\n")
    code = cmd_promote(_args(src, tgt))
    assert code == 0
    out = capsys.readouterr().out
    assert "Promoted" in out


def test_promote_overwrite_flag(tmp_env, capsys):
    src = _write(tmp_env / "src.env", "DB_HOST=prod\n")
    tgt = _write(tmp_env / "tgt.env", "DB_HOST=staging\n")
    code = cmd_promote(_args(src, tgt, overwrite=True))
    assert code == 0
    out = capsys.readouterr().out
    assert "Overwritten" in out


def test_promote_writes_output_file(tmp_env):
    src = _write(tmp_env / "src.env", "NEW_KEY=val\n")
    tgt = _write(tmp_env / "tgt.env", "EXISTING=yes\n")
    out_path = str(tmp_env / "merged.env")
    cmd_promote(_args(src, tgt, output=out_path))
    assert os.path.exists(out_path)
    content = open(out_path).read()
    assert "NEW_KEY=val" in content
    assert "EXISTING=yes" in content


def test_promote_verbose_shows_keys(tmp_env, capsys):
    src = _write(tmp_env / "src.env", "FOO=bar\n")
    tgt = _write(tmp_env / "tgt.env", "")
    cmd_promote(_args(src, tgt, verbose=True))
    out = capsys.readouterr().out
    assert "FOO" in out


def test_register_promote_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_promote_parser(sub)
    args = parser.parse_args(["promote", "a.env", "b.env", "--overwrite"])
    assert args.overwrite is True
    assert args.source == "a.env"
