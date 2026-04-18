"""Tests for the CLI layer."""
import pytest
from pathlib import Path
from envguard.cli import main


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


# --- diff command ---

def test_diff_identical_files(tmp_dir):
    a = write(tmp_dir / "a.env", "FOO=bar\nBAZ=qux\n")
    b = write(tmp_dir / "b.env", "FOO=bar\nBAZ=qux\n")
    rc = main(["diff", str(a), str(b), "--no-color"])
    assert rc == 0


def test_diff_detects_difference(tmp_dir):
    a = write(tmp_dir / "a.env", "FOO=bar\n")
    b = write(tmp_dir / "b.env", "FOO=changed\n")
    rc = main(["diff", str(a), str(b), "--no-color"])
    assert rc == 1


def test_diff_missing_key(tmp_dir):
    a = write(tmp_dir / "a.env", "FOO=bar\nMISSING=x\n")
    b = write(tmp_dir / "b.env", "FOO=bar\n")
    rc = main(["diff", str(a), str(b), "--no-color"])
    assert rc == 1


def test_diff_ignore_values(tmp_dir):
    a = write(tmp_dir / "a.env", "FOO=bar\n")
    b = write(tmp_dir / "b.env", "FOO=different\n")
    rc = main(["diff", str(a), str(b), "--no-color", "--ignore-values"])
    assert rc == 0


def test_diff_bad_file(tmp_dir):
    missing = tmp_dir / "nope.env"
    rc = main(["diff", str(missing), str(missing), "--no-color"])
    assert rc == 2


# --- validate command ---

def test_validate_passes(tmp_dir):
    env = write(tmp_dir / "prod.env", "DB_URL=postgres://localhost\nSECRET=abc\n")
    schema = write(tmp_dir / "schema.env", "DB_URL=\nSECRET=\n")
    rc = main(["validate", str(env), str(schema), "--no-color"])
    assert rc == 0


def test_validate_fails_missing(tmp_dir):
    env = write(tmp_dir / "prod.env", "DB_URL=postgres://localhost\n")
    schema = write(tmp_dir / "schema.env", "DB_URL=\nSECRET=\n")
    rc = main(["validate", str(env), str(schema), "--no-color"])
    assert rc == 1


def test_validate_bad_file(tmp_dir):
    missing = tmp_dir / "nope.env"
    schema = write(tmp_dir / "schema.env", "KEY=\n")
    rc = main(["validate", str(missing), str(schema), "--no-color"])
    assert rc == 2
