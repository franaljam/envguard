"""Tests for envguard.tracer."""
import textwrap
from pathlib import Path

import pytest

from envguard.tracer import TraceEntry, TraceResult, trace_env


@pytest.fixture()
def src_dir(tmp_path):
    return tmp_path


def _write(p: Path, name: str, content: str) -> Path:
    f = p / name
    f.write_text(textwrap.dedent(content))
    return f


def test_no_keys_returns_empty(src_dir):
    result = trace_env({}, [str(src_dir)])
    assert result.entries == []
    assert result.found_keys() == []


def test_finds_os_environ_get(src_dir):
    _write(src_dir, "app.py", """
        import os
        x = os.environ.get('DATABASE_URL')
    """)
    result = trace_env({"DATABASE_URL": "postgres://"}, [str(src_dir)])
    assert "DATABASE_URL" in result.found_keys()
    assert len(result.for_key("DATABASE_URL")) == 1


def test_finds_shell_dollar_brace(src_dir):
    _write(src_dir, "run.sh", """
        echo ${SECRET_KEY}
    """)
    result = trace_env({"SECRET_KEY": "abc"}, [str(src_dir)])
    assert "SECRET_KEY" in result.found_keys()


def test_multiple_files(src_dir):
    _write(src_dir, "a.py", "x = os.environ.get('API_KEY')\n")
    _write(src_dir, "b.py", "y = os.environ.get('API_KEY')\n")
    result = trace_env({"API_KEY": ""}, [str(src_dir)])
    assert len(result.for_key("API_KEY")) == 2


def test_unknown_key_not_in_results(src_dir):
    _write(src_dir, "c.py", "x = os.environ.get('OTHER_KEY')\n")
    result = trace_env({"MY_KEY": "val"}, [str(src_dir)])
    assert "OTHER_KEY" not in result.found_keys()


def test_summary_no_usages():
    r = TraceResult()
    assert r.summary() == "No usages found."


def test_summary_with_entries(src_dir):
    _write(src_dir, "x.py", "os.environ.get('FOO')\n")
    result = trace_env({"FOO": "bar"}, [str(src_dir)])
    s = result.summary()
    assert "FOO" in s
    assert "1 usage" in s


def test_extension_filter(src_dir):
    _write(src_dir, "app.rb", "ENV['TOKEN']\n")
    _write(src_dir, "app.py", "os.environ.get('TOKEN')\n")
    result = trace_env({"TOKEN": ""}, [str(src_dir)], extensions=[".rb"])
    # .py should be excluded
    for e in result.entries:
        assert e.file.endswith(".rb")
