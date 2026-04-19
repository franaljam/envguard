import pytest
from envguard.depcheck import check_dependencies, _extract_refs


def test_no_references_no_broken():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = check_dependencies(env)
    assert not result.has_broken()
    assert result.dependencies["HOST"] == []
    assert result.dependencies["PORT"] == []


def test_brace_reference_resolved():
    env = {"BASE": "http", "URL": "${BASE}://example.com"}
    result = check_dependencies(env)
    assert not result.has_broken()
    assert "BASE" in result.dependencies["URL"]


def test_plain_dollar_reference_resolved():
    env = {"HOST": "localhost", "DSN": "postgres://$HOST/db"}
    result = check_dependencies(env)
    assert not result.has_broken()
    assert "HOST" in result.dependencies["DSN"]


def test_broken_reference_detected():
    env = {"DSN": "postgres://${HOST}/db"}
    result = check_dependencies(env)
    assert result.has_broken()
    assert "HOST" in result.broken["DSN"]


def test_multiple_broken_references():
    env = {"URL": "${SCHEME}://${HOST}:${PORT}"}
    result = check_dependencies(env)
    assert set(result.broken["URL"]) == {"SCHEME", "HOST", "PORT"}


def test_partial_resolution():
    env = {"HOST": "localhost", "URL": "${HOST}:${PORT}"}
    result = check_dependencies(env)
    assert result.has_broken()
    assert "PORT" in result.broken["URL"]
    assert "HOST" not in result.broken.get("URL", [])


def test_summary_no_broken():
    env = {"A": "hello"}
    result = check_dependencies(env)
    assert result.summary() == "All references resolved."


def test_summary_with_broken():
    env = {"URL": "${MISSING}"}
    result = check_dependencies(env)
    s = result.summary()
    assert "broken" in s
    assert "MISSING" in s


def test_original_not_mutated():
    env = {"A": "${B}"}
    result = check_dependencies(env)
    result.env["A"] = "changed"
    assert env["A"] == "${B}"


def test_extract_refs_mixed():
    refs = _extract_refs("${FOO} and $BAR")
    assert "FOO" in refs
    assert "BAR" in refs
