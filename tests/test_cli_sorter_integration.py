import subprocess
import sys
from pathlib import Path
import pytest


@pytest.fixture
def envs(tmp_path):
    def _make(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _make


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envguard", *args],
        capture_output=True, text=True
    )


def test_sort_exit_zero(envs):
    f = envs(".env", "Z=1\nA=2\n")
    result = run("sort", f)
    assert result.returncode == 0


def test_sort_output_ordered(envs):
    f = envs(".env", "Z=1\nA=2\nM=3\n")
    result = run("sort", f)
    out = result.stdout
    assert out.index("A") < out.index("M") < out.index("Z")


def test_sort_inplace_modifies_file(envs, tmp_path):
    f = envs(".env", "Z=z\nA=a\n")
    run("sort", "--inplace", f)
    content = Path(f).read_text()
    assert content.index("A") < content.index("Z")
