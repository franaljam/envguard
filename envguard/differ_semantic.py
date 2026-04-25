"""Semantic diff: detect meaningful changes beyond raw string equality."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _infer_semantic_type(value: str) -> str:
    """Classify a value into a broad semantic category."""
    if value == "":
        return "empty"
    low = value.lower()
    if low in ("true", "false", "yes", "no", "1", "0", "on", "off"):
        return "boolean"
    try:
        int(value)
        return "integer"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    if "," in value:
        return "list"
    if value.startswith(("http://", "https://")):
        return "url"
    return "string"


def _normalize(value: str) -> str:
    """Return a canonical form for comparison (e.g. booleans)."""
    low = value.strip().lower()
    if low in ("true", "yes", "1", "on"):
        return "true"
    if low in ("false", "no", "0", "off"):
        return "false"
    return value.strip()


@dataclass
class SemanticChange:
    key: str
    left: str
    right: str
    left_type: str
    right_type: str
    type_changed: bool
    semantically_equal: bool


@dataclass
class SemanticDiffResult:
    changes: List[SemanticChange] = field(default_factory=list)
    left_only: List[str] = field(default_factory=list)
    right_only: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.changes or self.left_only or self.right_only)

    def meaningful_changes(self) -> List[SemanticChange]:
        """Changes that are NOT semantically equivalent."""
        return [c for c in self.changes if not c.semantically_equal]

    def summary(self) -> str:
        meaningful = len(self.meaningful_changes())
        trivial = len(self.changes) - meaningful
        parts = []
        if meaningful:
            parts.append(f"{meaningful} meaningful change(s)")
        if trivial:
            parts.append(f"{trivial} trivial change(s)")
        if self.left_only:
            parts.append(f"{len(self.left_only)} removed")
        if self.right_only:
            parts.append(f"{len(self.right_only)} added")
        return ", ".join(parts) if parts else "no changes"


def diff_semantic(
    left: Dict[str, str],
    right: Dict[str, str],
) -> SemanticDiffResult:
    result = SemanticDiffResult()
    all_keys = set(left) | set(right)
    for key in sorted(all_keys):
        if key in left and key not in right:
            result.left_only.append(key)
        elif key in right and key not in left:
            result.right_only.append(key)
        else:
            lv, rv = left[key], right[key]
            if lv != rv:
                lt = _infer_semantic_type(lv)
                rt = _infer_semantic_type(rv)
                sem_eq = _normalize(lv) == _normalize(rv)
                result.changes.append(
                    SemanticChange(
                        key=key,
                        left=lv,
                        right=rv,
                        left_type=lt,
                        right_type=rt,
                        type_changed=(lt != rt),
                        semantically_equal=sem_eq,
                    )
                )
    return result
