"""Type-aware diff: compare env values and report type changes (e.g. int->str)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _infer_type(value: str) -> str:
    """Infer a simple type label for a string value."""
    if value == "":
        return "empty"
    if value.lower() in ("true", "false"):
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


@dataclass
class TypeChange:
    key: str
    left_value: str
    right_value: str
    left_type: str
    right_type: str

    @property
    def is_type_change(self) -> bool:
        return self.left_type != self.right_type


@dataclass
class TypeDiffResult:
    changes: List[TypeChange] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.changes or self.added or self.removed)

    def type_changes(self) -> List[TypeChange]:
        return [c for c in self.changes if c.is_type_change]

    def value_changes(self) -> List[TypeChange]:
        return [c for c in self.changes if not c.is_type_change]

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        tc = self.type_changes()
        vc = self.value_changes()
        if tc:
            parts.append(f"{len(tc)} type change(s)")
        if vc:
            parts.append(f"{len(vc)} value change(s)")
        return ", ".join(parts) if parts else "no changes"


def diff_types(
    left: Dict[str, str],
    right: Dict[str, str],
) -> TypeDiffResult:
    """Compare two env dicts and report value/type changes."""
    result = TypeDiffResult()
    all_keys = set(left) | set(right)
    for key in sorted(all_keys):
        if key not in left:
            result.added.append(key)
        elif key not in right:
            result.removed.append(key)
        elif left[key] != right[key]:
            result.changes.append(
                TypeChange(
                    key=key,
                    left_value=left[key],
                    right_value=right[key],
                    left_type=_infer_type(left[key]),
                    right_type=_infer_type(right[key]),
                )
            )
    return result
