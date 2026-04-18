"""Schema validation for .env files using a simple schema definition."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


class SchemaError(Exception):
    pass


@dataclass
class FieldSchema:
    required: bool = True
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    non_empty: bool = False


@dataclass
class SchemaViolation:
    key: str
    message: str
    level: str = "error"  # "error" or "warning"


@dataclass
class SchemaResult:
    violations: List[SchemaViolation] = field(default_factory=list)

    def is_valid(self) -> bool:
        return not any(v.level == "error" for v in self.violations)

    def errors(self) -> List[SchemaViolation]:
        return [v for v in self.violations if v.level == "error"]

    def warnings(self) -> List[SchemaViolation]:
        return [v for v in self.violations if v.level == "warning"]

    def summary(self) -> str:
        if not self.violations:
            return "Schema OK"
        parts = []
        if self.errors():
            parts.append(f"{len(self.errors())} error(s)")
        if self.warnings():
            parts.append(f"{len(self.warnings())} warning(s)")
        return "Schema violations: " + ", ".join(parts)


def validate_schema(
    env: Dict[str, str],
    schema: Dict[str, FieldSchema],
) -> SchemaResult:
    violations: List[SchemaViolation] = []

    for key, field_schema in schema.items():
        if key not in env:
            if field_schema.required:
                violations.append(SchemaViolation(key, f"Required key '{key}' is missing."))
            continue

        value = env[key]

        if field_schema.non_empty and not value:
            violations.append(SchemaViolation(key, f"Key '{key}' must not be empty."))
            continue

        if field_schema.pattern and not re.fullmatch(field_schema.pattern, value):
            violations.append(
                SchemaViolation(key, f"Value of '{key}' does not match pattern '{field_schema.pattern}'.")
            )

        if field_schema.allowed_values is not None and value not in field_schema.allowed_values:
            violations.append(
                SchemaViolation(key, f"Value of '{key}' is not in allowed values {field_schema.allowed_values}.")
            )

    return SchemaResult(violations=violations)
