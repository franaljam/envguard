import pytest
from envguard.templater import generate_template, render_template, TemplateResult


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "AUTH_TOKEN": "tok",
    }


def test_non_sensitive_keys_blanked(sample_env):
    result = generate_template(sample_env)
    assert result.template["APP_NAME"] == ""
    assert result.template["DEBUG"] == ""


def test_sensitive_keys_blanked(sample_env):
    result = generate_template(sample_env)
    assert result.template["DB_PASSWORD"] == ""
    assert result.template["API_KEY"] == ""
    assert result.template["AUTH_TOKEN"] == ""


def test_sensitive_keys_listed(sample_env):
    result = generate_template(sample_env)
    assert set(result.sensitive_keys) == {"DB_PASSWORD", "API_KEY", "AUTH_TOKEN"}


def test_source_keys_preserved(sample_env):
    result = generate_template(sample_env)
    assert result.source_keys == list(sample_env.keys())


def test_custom_placeholder(sample_env):
    result = generate_template(sample_env, placeholder="CHANGE_ME")
    assert result.template["APP_NAME"] == "CHANGE_ME"


def test_sensitive_placeholder_separate(sample_env):
    result = generate_template(sample_env, placeholder="", sensitive_placeholder="<SECRET>")
    assert result.template["DB_PASSWORD"] == "<SECRET>"
    assert result.template["APP_NAME"] == ""


def test_keep_values_preserves_non_sensitive(sample_env):
    result = generate_template(sample_env, keep_values=True)
    assert result.template["APP_NAME"] == "myapp"
    assert result.template["DEBUG"] == "true"
    assert result.template["DB_PASSWORD"] == ""


def test_original_not_mutated(sample_env):
    original = dict(sample_env)
    generate_template(sample_env)
    assert sample_env == original


def test_render_template_basic(sample_env):
    result = generate_template(sample_env)
    rendered = render_template(result)
    for key in sample_env:
        assert key in rendered


def test_render_template_with_header(sample_env):
    result = generate_template(sample_env)
    rendered = render_template(result, comment_header="Auto-generated template")
    assert rendered.startswith("# Auto-generated template")


def test_summary_contains_counts(sample_env):
    result = generate_template(sample_env)
    s = result.summary()
    assert "5" in s  # total keys
    assert "3" in s  # sensitive keys
