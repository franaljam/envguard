"""Diff two env dicts by key presence only (ignoring values)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set


@dataclass(frozen=True)
class PresenceChange:
    key: str
    side: str  # 'left_only' | 'right_only'


@dataclass
class PresenceDiffResult:
    left_only: List[str] = field(default_factory=list)
    right_only: List[str] = field(default_factory=list)
    common: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.left_only or self.right_only)

    @property
    def changes(self) -> List[PresenceChange]:
        result: List[PresenceChange] = []
        for k in sorted(self.left_only):
            result.append(PresenceChange(key=k, side="left_only"))
        for k in sorted(self.right_only):
            result.append(PresenceChange(key=k, side="right_only"))
        return result

    def summary(self) -> str:
        parts: List[str] = []
        if self.left_only:
            parts.append(f"{len(self.left_only)} key(s) only in left")
        if self.right_only:
            parts.append(f"{len(self.right_only)} key(s) only in right")
        if not parts:
            return "No presence differences."
        return "; ".join(parts) + "."


def diff_presence(
    left: Dict[str, str],
    right: Dict[str, str],
) -> PresenceDiffResult:
    """Compare two env dicts and return which keys are present on each side."""
    left_keys: FrozenSet[str] = frozenset(left)
    right_keys: FrozenSet[str] = frozenset(right)

    return PresenceDiffResult(
        left_only=sorted(left_keys - right_keys),
        right_only=sorted(right_keys - left_keys),
        common=sorted(left_keys & right_keys),
    )
