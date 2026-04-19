import pytest
from envguard.scorer import score_env, ScoreResult


def _clean_env(n=3):
    return {f"KEY_{i}": f"value{i}" for i in range(n)}


def test_perfect_score_clean_env():
    result = score_env(_clean_env())
    assert result.total == result.max_total
    assert result.grade == "A"


def test_empty_value_reduces_completeness():
    env = {"KEY_A": "val", "KEY_B": ""}
    result = score_env(env)
    comp = next(b for b in result.breakdowns if b.category == "completeness")
    assert comp.score < comp.max_score
    assert any("KEY_B" in n for n in comp.notes)


def test_lowercase_key_reduces_naming():
    env = {"key_lower": "val"}
    result = score_env(env)
    naming = next(b for b in result.breakdowns if b.category == "naming")
    assert naming.score < naming.max_score


def test_large_env_reduces_size_score():
    env = {f"KEY_{i}": "v" for i in range(60)}
    result = score_env(env)
    size = next(b for b in result.breakdowns if b.category == "size")
    assert size.score < size.max_score
    assert size.notes


def test_summary_string():
    result = score_env(_clean_env())
    s = result.summary()
    assert "Score:" in s
    assert "Grade:" in s


def test_grade_f_for_terrible_env():
    env = {"a": "", "b": "", "c": "", "d": "", "e": "", "f": ""}
    result = score_env(env)
    # lots of empty + lowercase keys
    assert result.grade in ("D", "F")


def test_empty_env_returns_result():
    result = score_env({})
    assert isinstance(result, ScoreResult)
    assert result.total >= 0
