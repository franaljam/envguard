"""Count-based diff: compare the number of keys between two env dicts."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class CountDiffResult:
    left_count: int
    right_count: int
    added: int
    removed: int
    common: int
    left_only: frozenset
    right_only: frozenset
    shared: frozenset

    def has_changes(self) -> bool:
        return self.added != 0 or self.removed != 0

    def delta(self) -> int:
        """Net change in key count (positive = more keys on right)."""
        return self.right_count - self.left_count

    def summary(self) -> str:
        if not self.has_changes():
            return f"No count changes. Both sides have {self.left_count} keys."
        parts = []
        if self.added:
            parts.append(f"+{self.added} added")
        if self.removed:
            parts.append(f"-{self.removed} removed")
        delta = self.delta()
        sign = "+" if delta >= 0 else ""
        return f"Key count: {self.left_count} -> {self.right_count} ({sign}{delta}). " + ", ".join(parts) + "."


def diff_counts(left: Dict[str, str], right: Dict[str, str]) -> CountDiffResult:
    """Return a CountDiffResult comparing key counts between left and right."""
    left_keys = frozenset(left.keys())
    right_keys = frozenset(right.keys())
    left_only = left_keys - right_keys
    right_only = right_keys - left_keys
    shared = left_keys & right_keys
    return CountDiffResult(
        left_count=len(left_keys),
        right_count=len(right_keys),
        added=len(right_only),
        removed=len(left_only),
        common=len(shared),
        left_only=left_only,
        right_only=right_only,
        shared=shared,
    )
