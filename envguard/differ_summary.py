"""Generate a structured change-log summary between two env snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.snapshot import Snapshot


@dataclass
class ChangeEntry:
    key: str
    change_type: str  # 'added' | 'removed' | 'modified'
    old_value: str | None = None
    new_value: str | None = None


@dataclass
class SnapshotDiff:
    base_label: str
    head_label: str
    changes: List[ChangeEntry] = field(default_factory=list)

    @property
    def added(self) -> List[ChangeEntry]:
        return [c for c in self.changes if c.change_type == "added"]

    @property
    def removed(self) -> List[ChangeEntry]:
        return [c for c in self.changes if c.change_type == "removed"]

    @property
    def modified(self) -> List[ChangeEntry]:
        return [c for c in self.changes if c.change_type == "modified"]

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)


def diff_snapshots(
    base: Snapshot,
    head: Snapshot,
    ignore_values: bool = False,
) -> SnapshotDiff:
    """Compare two snapshots and return a structured SnapshotDiff."""
    base_vars: Dict[str, str] = base.variables
    head_vars: Dict[str, str] = head.variables

    all_keys = set(base_vars) | set(head_vars)
    changes: List[ChangeEntry] = []

    for key in sorted(all_keys):
        if key not in base_vars:
            changes.append(ChangeEntry(key=key, change_type="added", new_value=head_vars[key]))
        elif key not in head_vars:
            changes.append(ChangeEntry(key=key, change_type="removed", old_value=base_vars[key]))
        elif not ignore_values and base_vars[key] != head_vars[key]:
            changes.append(
                ChangeEntry(
                    key=key,
                    change_type="modified",
                    old_value=base_vars[key],
                    new_value=head_vars[key],
                )
            )

    return SnapshotDiff(
        base_label=base.label,
        head_label=head.label,
        changes=changes,
    )
