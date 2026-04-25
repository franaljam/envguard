"""Compute statistical diff metrics between two env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StatEntry:
    key: str
    left_len: int
    right_len: int
    delta: int  # right_len - left_len


@dataclass
class StatResult:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[StatEntry] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    @property
    def total_keys(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed) + len(self.unchanged)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        if self.unchanged:
            parts.append(f"={len(self.unchanged)} unchanged")
        return ", ".join(parts) if parts else "no changes"


def diff_stats(
    left: Dict[str, str],
    right: Dict[str, str],
) -> StatResult:
    """Return a StatResult describing value-level differences between left and right."""
    result = StatResult()
    all_keys = set(left) | set(right)

    for key in sorted(all_keys):
        in_left = key in left
        in_right = key in right

        if in_left and not in_right:
            result.removed.append(key)
        elif in_right and not in_left:
            result.added.append(key)
        elif left[key] == right[key]:
            result.unchanged.append(key)
        else:
            lv, rv = left[key], right[key]
            result.changed.append(
                StatEntry(
                    key=key,
                    left_len=len(lv),
                    right_len=len(rv),
                    delta=len(rv) - len(lv),
                )
            )

    return result
