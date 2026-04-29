"""Diff two env dicts, highlighting changes to sensitive keys separately."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"password", r"passwd", r"secret", r"token", r"api[_]?key",
        r"private[_]?key", r"auth", r"credential", r"cert",
    ]
]


def _is_sensitive(key: str) -> bool:
    return any(p.search(key) for p in _SENSITIVE_PATTERNS)


@dataclass
class SensitiveChange:
    key: str
    left: Optional[str]
    right: Optional[str]
    is_sensitive: bool

    @property
    def added(self) -> bool:
        return self.left is None and self.right is not None

    @property
    def removed(self) -> bool:
        return self.left is not None and self.right is None

    @property
    def modified(self) -> bool:
        return self.left is not None and self.right is not None and self.left != self.right


@dataclass
class SensitiveDiffResult:
    changes: List[SensitiveChange] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.changes)

    def sensitive_changes(self) -> List[SensitiveChange]:
        return [c for c in self.changes if c.is_sensitive]

    def non_sensitive_changes(self) -> List[SensitiveChange]:
        return [c for c in self.changes if not c.is_sensitive]

    def summary(self) -> str:
        total = len(self.changes)
        sensitive = len(self.sensitive_changes())
        if total == 0:
            return "No differences found."
        return (
            f"{total} change(s) detected "
            f"({sensitive} sensitive, {total - sensitive} non-sensitive)."
        )


def diff_sensitive(
    left: Dict[str, str],
    right: Dict[str, str],
) -> SensitiveDiffResult:
    """Compare two env dicts and classify changes by sensitivity."""
    result = SensitiveDiffResult()
    all_keys = sorted(set(left) | set(right))
    for key in all_keys:
        lv = left.get(key)
        rv = right.get(key)
        if lv != rv:
            result.changes.append(
                SensitiveChange(
                    key=key,
                    left=lv,
                    right=rv,
                    is_sensitive=_is_sensitive(key),
                )
            )
    return result
