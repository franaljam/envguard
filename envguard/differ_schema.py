"""Schema-aware diff: compare two env dicts against a shared schema."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envguard.schema import FieldSchema


@dataclass
class SchemaDiffEntry:
    key: str
    left_value: Optional[str]
    right_value: Optional[str]
    left_valid: bool
    right_valid: bool
    schema_field: Optional[FieldSchema] = None

    @property
    def value_changed(self) -> bool:
        return self.left_value != self.right_value

    @property
    def validity_changed(self) -> bool:
        return self.left_valid != self.right_valid


@dataclass
class SchemaDiffResult:
    entries: List[SchemaDiffEntry] = field(default_factory=list)
    schema_fields: Dict[str, FieldSchema] = field(default_factory=dict)

    def has_changes(self) -> bool:
        return any(e.value_changed or e.validity_changed for e in self.entries)

    def validity_regressions(self) -> List[SchemaDiffEntry]:
        """Keys that were valid on left but invalid on right."""
        return [e for e in self.entries if e.left_valid and not e.right_valid]

    def validity_improvements(self) -> List[SchemaDiffEntry]:
        """Keys that were invalid on left but valid on right."""
        return [e for e in self.entries if not e.left_valid and e.right_valid]

    def summary(self) -> str:
        total = len(self.entries)
        changed = sum(1 for e in self.entries if e.value_changed)
        regressions = len(self.validity_regressions())
        improvements = len(self.validity_improvements())
        parts = [f"{total} keys compared", f"{changed} value(s) changed"]
        if regressions:
            parts.append(f"{regressions} validity regression(s)")
        if improvements:
            parts.append(f"{improvements} validity improvement(s)")
        return ", ".join(parts)


def _validate_value(value: Optional[str], fschema: Optional[FieldSchema]) -> bool:
    if fschema is None:
        return True
    if value is None:
        return not fschema.required
    if fschema.pattern:
        import re
        if not re.fullmatch(fschema.pattern, value):
            return False
    if fschema.allowed_values and value not in fschema.allowed_values:
        return False
    return True


def diff_schema(
    left: Dict[str, str],
    right: Dict[str, str],
    schema_fields: Optional[Dict[str, FieldSchema]] = None,
) -> SchemaDiffResult:
    schema_fields = schema_fields or {}
    all_keys = sorted(set(left) | set(right) | set(schema_fields))
    entries: List[SchemaDiffEntry] = []
    for key in all_keys:
        lv = left.get(key)
        rv = right.get(key)
        fschema = schema_fields.get(key)
        entries.append(SchemaDiffEntry(
            key=key,
            left_value=lv,
            right_value=rv,
            left_valid=_validate_value(lv, fschema),
            right_valid=_validate_value(rv, fschema),
            schema_field=fschema,
        ))
    return SchemaDiffResult(entries=entries, schema_fields=schema_fields)
