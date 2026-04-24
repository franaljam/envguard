"""Value-level diff: compare two env dicts and report changed, added, removed entries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValueChange:
    key: str
    old: Optional[str]
    new: Optional[str]
    kind: str  # 'added' | 'removed' | 'changed'


@dataclass
class ValueDiffResult:
    changes: List[ValueChange] = field(default_factory=list)
    _left: Dict[str, str] = field(default_factory=dict, repr=False)
    _right: Dict[str, str] = field(default_factory=dict, repr=False)

    def has_changes(self) -> bool:
        return bool(self.changes)

    def added(self) -> List[ValueChange]:
        return [c for c in self.changes if c.kind == "added"]

    def removed(self) -> List[ValueChange]:
        return [c for c in self.changes if c.kind == "removed"]

    def modified(self) -> List[ValueChange]:
        return [c for c in self.changes if c.kind == "changed"]

    def summary(self) -> str:
        if not self.has_changes():
            return "No value differences found."
        parts = []
        if self.added():
            parts.append(f"{len(self.added())} added")
        if self.removed():
            parts.append(f"{len(self.removed())} removed")
        if self.modified():
            parts.append(f"{len(self.modified())} changed")
        return "Value diff: " + ", ".join(parts) + "."


def diff_values(
    left: Dict[str, str],
    right: Dict[str, str],
    ignore_keys: Optional[List[str]] = None,
    case_insensitive: bool = False,
) -> ValueDiffResult:
    """Return a ValueDiffResult describing differences between *left* and *right*."""
    skip = set(ignore_keys or [])
    changes: List[ValueChange] = []

    all_keys = set(left) | set(right)
    for key in sorted(all_keys):
        if key in skip:
            continue
        in_left = key in left
        in_right = key in right
        if in_left and not in_right:
            changes.append(ValueChange(key=key, old=left[key], new=None, kind="removed"))
        elif in_right and not in_left:
            changes.append(ValueChange(key=key, old=None, new=right[key], kind="added"))
        else:
            lv = left[key].lower() if case_insensitive else left[key]
            rv = right[key].lower() if case_insensitive else right[key]
            if lv != rv:
                changes.append(ValueChange(key=key, old=left[key], new=right[key], kind="changed"))

    return ValueDiffResult(changes=changes, _left=dict(left), _right=dict(right))
