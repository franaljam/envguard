"""Load schema definitions from YAML or JSON files."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict

from envguard.schema import FieldSchema, SchemaError


def _parse_field(data: dict) -> FieldSchema:
    return FieldSchema(
        required=data.get("required", True),
        pattern=data.get("pattern"),
        allowed_values=data.get("allowed_values"),
        non_empty=data.get("non_empty", False),
    )


def load_schema_json(path: str) -> Dict[str, FieldSchema]:
    """Load a schema from a JSON file."""
    p = Path(path)
    if not p.exists():
        raise SchemaError(f"Schema file not found: {path}")
    try:
        raw = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise SchemaError(f"Invalid JSON in schema file: {exc}") from exc
    if not isinstance(raw, dict):
        raise SchemaError("Schema file must be a JSON object.")
    return {key: _parse_field(val) for key, val in raw.items()}


def load_schema_yaml(path: str) -> Dict[str, FieldSchema]:
    """Load a schema from a YAML file."""
    try:
        import yaml
    except ImportError as exc:
        raise SchemaError("PyYAML is required to load YAML schemas: pip install pyyaml") from exc
    p = Path(path)
    if not p.exists():
        raise SchemaError(f"Schema file not found: {path}")
    try:
        raw = yaml.safe_load(p.read_text())
    except yaml.YAMLError as exc:
        raise SchemaError(f"Invalid YAML in schema file: {exc}") from exc
    if not isinstance(raw, dict):
        raise SchemaError("Schema file must be a YAML mapping.")
    return {key: _parse_field(val) for key, val in raw.items()}


def load_schema(path: str) -> Dict[str, FieldSchema]:
    """Auto-detect format by extension and load schema."""
    if path.endswith(".json"):
        return load_schema_json(path)
    if path.endswith((".yml", ".yaml")):
        return load_schema_yaml(path)
    raise SchemaError(f"Unsupported schema file format: {path}")
