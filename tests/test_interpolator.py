"""Tests for envguard.interpolator."""
import pytest

from envguard.interpolator import InterpolationError, interpolate, interpolate_env


# ---------------------------------------------------------------------------
# interpolate()
# ---------------------------------------------------------------------------

def test_no_references_unchanged():
    assert interpolate("hello", {}) == "hello"


def test_dollar_brace_syntax():
    assert interpolate("${FOO}", {"FOO": "bar"}) == "bar"


def test_dollar_plain_syntax():
    assert interpolate("$FOO", {"FOO": "bar"}) == "bar"


def test_mixed_syntax_in_one_value():
    result = interpolate("${A}/$B", {"A": "x", "B": "y"})
    assert result == "x/y"


def test_strict_raises_on_missing():
    with pytest.raises(InterpolationError, match="Undefined variable: 'MISSING'"):
        interpolate("${MISSING}", {}, strict=True)


def test_non_strict_leaves_unresolved():
    result = interpolate("${MISSING}", {}, strict=False)
    assert result == "${MISSING}"


def test_partial_resolution_non_strict():
    result = interpolate("$A-${B}", {"A": "hello"}, strict=False)
    assert result == "hello-${B}"


# ---------------------------------------------------------------------------
# interpolate_env()
# ---------------------------------------------------------------------------

def test_interpolate_env_basic():
    env = {"BASE": "/app", "LOG": "${BASE}/logs"}
    result = interpolate_env(env)
    assert result == {"BASE": "/app", "LOG": "/app/logs"}


def test_interpolate_env_does_not_mutate_original():
    env = {"A": "1", "B": "$A"}
    original = dict(env)
    interpolate_env(env)
    assert env == original


def test_interpolate_env_uses_extra():
    env = {"PATH_FULL": "${ROOT}/bin"}
    result = interpolate_env(env, extra={"ROOT": "/usr"})
    assert result["PATH_FULL"] == "/usr/bin"


def test_interpolate_env_extra_not_in_output():
    env = {"X": "$Y"}
    result = interpolate_env(env, extra={"Y": "42"})
    assert "Y" not in result


def test_interpolate_env_strict_raises():
    env = {"A": "${UNDEFINED}"}
    with pytest.raises(InterpolationError):
        interpolate_env(env, strict=True)


def test_interpolate_env_non_strict_passthrough():
    env = {"A": "${UNDEFINED}"}
    result = interpolate_env(env, strict=False)
    assert result["A"] == "${UNDEFINED}"
