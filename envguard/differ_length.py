"""Diff .env files by value length changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LengthChange:
    key: str
    left_length: Optional[int]  # None if key absent
    right_length: Optional[int]  # None if key absent

    @property
    def delta(self) -> Optional[int]:
        if self.left_length is None or self.right_length is None:
            return None
        return self.right_length - self.left_length

    @property
    def direction(self) -> str:
        if self.left_length is None:
            return "added"
        if self.right_length is None:
            return "removed"
        if self.delta > 0:
            return "grew"
        if self.delta < 0:
            return "shrank"
        return "unchanged"


@dataclass
class LengthDiffResult:
    changes: List[LengthChange] = field(default_factory=list)

    def has_changes(self) -> bool:
        return any(c.direction != "unchanged" for c in self.changes)

    def added(self) -> List[LengthChange]:
        return [c for c in self.changes if c.direction == "added"]

    def removed(self) -> List[LengthChange]:
        return [c for c in self.changes if c.direction == "removed"]

    def grew(self) -> List[LengthChange]:
        return [c for c in self.changes if c.direction == "grew"]

    def shrank(self) -> List[LengthChange]:
        return [c for c in self.changes if c.direction == "shrank"]

    def summary(self) -> str:
        if not self.has_changes():
            return "No length changes detected."
        parts = []
        if self.added():
            parts.append(f"{len(self.added())} added")
        if self.removed():
            parts.append(f"{len(self.removed())} removed")
        if self.grew():
            parts.append(f"{len(self.grew())} grew")
        if self.shrank():
            parts.append(f"{len(self.shrank())} shrank")
        return "Length changes: " + ", ".join(parts) + "."


def diff_lengths(
    left: Dict[str, str],
    right: Dict[str, str],
    min_delta: int = 0,
) -> LengthDiffResult:
    """Compare value lengths between two env dicts.

    Args:
        left: baseline env dict.
        right: target env dict.
        min_delta: only report changes where |delta| >= this value (0 = all).
    """
    all_keys = sorted(set(left) | set(right))
    changes: List[LengthChange] = []
    for key in all_keys:
        l_len = len(left[key]) if key in left else None
        r_len = len(right[key]) if key in right else None
        entry = LengthChange(key=key, left_length=l_len, right_length=r_len)
        if entry.direction == "unchanged":
            continue
        if entry.delta is not None and abs(entry.delta) < min_delta:
            continue
        changes.append(entry)
    return LengthDiffResult(changes=changes)
