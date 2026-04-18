import json
import pytest
from pathlib import Path
from envguard.schema_loader import load_schema, load_schema_json
from envguard.schema import SchemaError


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def test_load_json_schema(tmp_dir):
    schema_data = {
        "HOST": {"required": True, "non_empty": True},
        "PORT": {"required": True, "pattern": "\\d+"},
        "ENV": {"required": False, "allowed_values": ["dev", "prod"]},
    }
    p = tmp_dir / "schema.json"
    p.write_text(json.dumps(schema_data))
    schema = load_schema_json(str(p))
    assert "HOST" in schema
    assert schema["HOST"].required is True
    assert schema["HOST"].non_empty is True
    assert schema["PORT"].pattern == "\\d+"
    assert schema["ENV"].allowed_values == ["dev", "prod"]
    assert schema["ENV"].required is False


def test_load_schema_auto_detect_json(tmp_dir):
    p = tmp_dir / "schema.json"
    p.write_text(json.dumps({"KEY": {"required": True}}))
    schema = load_schema(str(p))
    assert "KEY" in schema


def test_missing_file_raises(tmp_dir):
    with pytest.raises(SchemaError, match="not found"):
        load_schema_json(str(tmp_dir / "missing.json"))


def test_invalid_json_raises(tmp_dir):
    p = tmp_dir / "bad.json"
    p.write_text("not json{{{")
    with pytest.raises(SchemaError, match="Invalid JSON"):
        load_schema_json(str(p))


def test_non_object_json_raises(tmp_dir):
    p = tmp_dir / "list.json"
    p.write_text(json.dumps(["a", "b"]))
    with pytest.raises(SchemaError, match="JSON object"):
        load_schema_json(str(p))


def test_unsupported_format_raises(tmp_dir):
    p = tmp_dir / "schema.toml"
    p.write_text("")
    with pytest.raises(SchemaError, match="Unsupported"):
        load_schema(str(p))
