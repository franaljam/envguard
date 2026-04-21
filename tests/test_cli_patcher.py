import argparse
import pytest
from pathlib import Path

from envguard.cli_patcher import cmd_patch


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(file, set_keys=None, delete=None, output=None, summary=False):
    ns = argparse.Namespace(
        file=str(file),
        set=set_keys,
        delete=delete,
        output=str(output) if output else None,
        summary=summary,
    )
    return ns


def test_patch_no_changes_exits_zero(tmp_env):
    _write(tmp_env, "HOST=localhost\n")
    rc = cmd_patch(_args(tmp_env))
    assert rc == 0


def test_patch_set_exits_one(tmp_env):
    _write(tmp_env, "HOST=localhost\n")
    rc = cmd_patch(_args(tmp_env, set_keys=["HOST=prod"]))
    assert rc == 1


def test_patch_delete_exits_one(tmp_env):
    _write(tmp_env, "HOST=localhost\nDEBUG=true\n")
    rc = cmd_patch(_args(tmp_env, delete=["DEBUG"]))
    assert rc == 1


def test_patch_set_invalid_format_exits_two(tmp_env, capsys):
    _write(tmp_env, "HOST=localhost\n")
    rc = cmd_patch(_args(tmp_env, set_keys=["BADFORMAT"]))
    assert rc == 2
    captured = capsys.readouterr()
    assert "KEY=VALUE" in captured.err


def test_patch_missing_file_exits_two(tmp_path, capsys):
    rc = cmd_patch(_args(tmp_path / "missing.env"))
    assert rc == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_patch_output_written_to_file(tmp_env, tmp_path):
    _write(tmp_env, "HOST=localhost\n")
    out = tmp_path / "patched.env"
    rc = cmd_patch(_args(tmp_env, set_keys=["HOST=prod"], output=out))
    assert rc == 1
    assert "HOST=prod" in out.read_text()


def test_patch_summary_printed(tmp_env, capsys):
    _write(tmp_env, "HOST=localhost\n")
    cmd_patch(_args(tmp_env, set_keys=["HOST=prod"], summary=True))
    captured = capsys.readouterr()
    assert "patch" in captured.out.lower()
