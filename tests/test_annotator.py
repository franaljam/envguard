"""Tests for envguard.annotator."""
import pytest
from envguard.annotator import annotate_env, AnnotationResult


@pytest.fixture
def base_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "s3cr3t",
        "DEBUG": "false",
    }


@pytest.fixture
def annotations():
    return {
        "DATABASE_URL": "Primary database connection string",
        "SECRET_KEY": "Django secret key – keep private",
    }


def test_returns_annotation_result(base_env, annotations):
    result = annotate_env(base_env, annotations)
    assert isinstance(result, AnnotationResult)


def test_annotated_key_contains_comment(base_env, annotations):
    result = annotate_env(base_env, annotations)
    assert "# Primary database connection string" in result.annotated["DATABASE_URL"]


def test_annotated_value_preserved(base_env, annotations):
    result = annotate_env(base_env, annotations)
    assert result.annotated["DATABASE_URL"].startswith("postgres://localhost/db")


def test_unannotated_key_still_present_by_default(base_env, annotations):
    result = annotate_env(base_env, annotations)
    assert "DEBUG" in result.annotated
    assert result.annotated["DEBUG"] == "false"


def test_unannotated_key_in_skipped(base_env, annotations):
    result = annotate_env(base_env, annotations)
    assert "DEBUG" in result.skipped()


def test_annotated_keys_not_in_skipped(base_env, annotations):
    result = annotate_env(base_env, annotations)
    assert "DATABASE_URL" not in result.skipped()
    assert "SECRET_KEY" not in result.skipped()


def test_skip_unannotated_omits_key(base_env, annotations):
    result = annotate_env(base_env, annotations, skip_unannotated=True)
    assert "DEBUG" not in result.annotated


def test_skip_unannotated_keeps_annotated_keys(base_env, annotations):
    result = annotate_env(base_env, annotations, skip_unannotated=True)
    assert "DATABASE_URL" in result.annotated
    assert "SECRET_KEY" in result.annotated


def test_comments_dict_populated(base_env, annotations):
    result = annotate_env(base_env, annotations)
    assert result.comments["DATABASE_URL"] == "Primary database connection string"
    assert result.comments["SECRET_KEY"] == "Django secret key – keep private"


def test_source_not_mutated(base_env, annotations):
    original = dict(base_env)
    annotate_env(base_env, annotations)
    assert base_env == original


def test_summary_string(base_env, annotations):
    result = annotate_env(base_env, annotations)
    s = result.summary()
    assert "2 key(s) annotated" in s
    assert "1 skipped" in s


def test_empty_annotations(base_env):
    result = annotate_env(base_env, {})
    assert result.annotated == base_env
    assert len(result.skipped()) == len(base_env)


def test_all_annotated_zero_skipped(base_env):
    ann = {k: "desc" for k in base_env}
    result = annotate_env(base_env, ann)
    assert result.skipped() == []
