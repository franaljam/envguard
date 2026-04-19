"""Tests for envguard.caster."""
import pytest
from envguard.caster import CastResult, CastError, cast_env


def test_cast_int():
    result = cast_env({"PORT": "8080"}, {"PORT": "int"})
    assert result.casted["PORT"] == 8080
    assert not result.has_failures()


def test_cast_float():
    result = cast_env({"RATIO": "3.14"}, {"RATIO": "float"})
    assert abs(result.casted["RATIO"] - 3.14) < 1e-9


def test_cast_bool_true_variants():
    for val in ("true", "1", "yes", "on", "True", "YES"):
        r = cast_env({"FLAG": val}, {"FLAG": "bool"})
        assert r.casted["FLAG"] is True, f"Expected True for {val!r}"


def test_cast_bool_false_variants():
    for val in ("false", "0", "no", "off", "False", "NO"):
        r = cast_env({"FLAG": val}, {"FLAG": "bool"})
        assert r.casted["FLAG"] is False


def test_cast_list():
    result = cast_env({"HOSTS": "a, b, c"}, {"HOSTS": "list"})
    assert result.casted["HOSTS"] == ["a", "b", "c"]


def test_cast_list_single_item():
    result = cast_env({"HOSTS": "localhost"}, {"HOSTS": "list"})
    assert result.casted["HOSTS"] == ["localhost"]


def test_cast_str_passthrough():
    result = cast_env({"NAME": "hello"}, {"NAME": "str"})
    assert result.casted["NAME"] == "hello"


def test_key_not_in_schema_kept_as_string():
    result = cast_env({"OTHER": "42"}, {})
    assert result.casted["OTHER"] == "42"


def test_invalid_int_collected_as_failure():
    result = cast_env({"PORT": "abc"}, {"PORT": "int"})
    assert result.has_failures()
    assert "PORT" in result.failed
    assert "PORT" not in result.casted


def test_invalid_bool_collected_as_failure():
    result = cast_env({"FLAG": "maybe"}, {"FLAG": "bool"})
    assert result.has_failures()
    assert "FLAG" in result.failed


def test_strict_mode_raises_on_failure():
    with pytest.raises(CastError):
        cast_env({"PORT": "bad"}, {"PORT": "int"}, strict=True)


def test_original_not_mutated():
    env = {"PORT": "9000"}
    cast_env(env, {"PORT": "int"})
    assert env["PORT"] == "9000"


def test_summary_no_failures():
    result = cast_env({"PORT": "80"}, {"PORT": "int"})
    assert "1 keys successfully" in result.summary()


def test_summary_with_failures():
    result = cast_env({"PORT": "bad"}, {"PORT": "int"})
    assert "failed" in result.summary()
    assert "PORT" in result.summary()


def test_unknown_type_hint_collected():
    result = cast_env({"X": "val"}, {"X": "datetime"})
    assert result.has_failures()
    assert "unknown type hint" in result.failed["X"]
