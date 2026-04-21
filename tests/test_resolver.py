"""Tests for envguard.resolver."""
import os
import pytest
from envguard.resolver import resolve_env, ResolveResult


def test_no_references_returns_copy():
    env = {"A": "hello", "B": "world"}
    result = resolve_env(env)
    assert result.entries["A"].resolved == "hello"
    assert result.entries["B"].resolved == "world"
    assert not result.changed()


def test_brace_reference_resolved_from_env():
    env = {"BASE": "/app", "LOG": "${BASE}/logs"}
    result = resolve_env(env, fallback_to_os=False)
    assert result.entries["LOG"].resolved == "/app/logs"
    assert result.changed()


def test_plain_dollar_reference_resolved_from_env():
    env = {"HOST": "localhost", "URL": "http://$HOST:8080"}
    result = resolve_env(env, fallback_to_os=False)
    assert result.entries["URL"].resolved == "http://localhost:8080"


def test_fallback_to_os_env(monkeypatch):
    monkeypatch.setenv("OS_VAR", "from_os")
    env = {"VALUE": "${OS_VAR}"}
    result = resolve_env(env, fallback_to_os=True)
    assert result.entries["VALUE"].resolved == "from_os"
    assert "OS_VAR=os" in result.entries["VALUE"].sources


def test_fallback_to_os_disabled(monkeypatch):
    monkeypatch.setenv("OS_VAR", "from_os")
    env = {"VALUE": "${OS_VAR}"}
    result = resolve_env(env, fallback_to_os=False)
    assert result.entries["VALUE"].resolved == "${OS_VAR}"
    assert "OS_VAR" in result.unresolved


def test_defaults_used_when_not_in_env():
    env = {"MSG": "Hello ${NAME}"}
    result = resolve_env(env, fallback_to_os=False, defaults={"NAME": "World"})
    assert result.entries["MSG"].resolved == "Hello World"
    assert "NAME=default" in result.entries["MSG"].sources


def test_unresolved_reference_tracked():
    env = {"X": "${MISSING}"}
    result = resolve_env(env, fallback_to_os=False)
    assert "MISSING" in result.unresolved
    assert result.entries["X"].resolved == "${MISSING}"


def test_strict_raises_on_missing():
    from envguard.interpolator import InterpolationError
    env = {"X": "${GHOST}"}
    with pytest.raises(InterpolationError):
        resolve_env(env, fallback_to_os=False, strict=True)


def test_summary_message():
    env = {"A": "${MISSING}", "B": "plain"}
    result = resolve_env(env, fallback_to_os=False)
    summary = result.summary()
    assert "0 reference" in summary or "resolved" in summary
    assert "1 unresolved" in summary


def test_original_not_mutated():
    env = {"K": "${V}", "V": "val"}
    original = dict(env)
    resolve_env(env)
    assert env == original


def test_source_tracks_env_origin():
    env = {"BASE": "/base", "FULL": "${BASE}/sub"}
    result = resolve_env(env, fallback_to_os=False)
    assert "BASE=env" in result.entries["FULL"].sources
