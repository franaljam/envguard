"""Diff metadata (file size, line count, comment count) between two .env files."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MetadataSnapshot:
    """Metadata captured from a single .env file."""

    file_size: int          # bytes
    line_count: int         # total lines including blanks
    blank_lines: int
    comment_lines: int
    key_count: int
    empty_value_count: int


@dataclass
class MetadataChange:
    """A single metadata field that changed between two snapshots."""

    field: str
    left_value: int
    right_value: int

    @property
    def delta(self) -> int:
        return self.right_value - self.left_value

    @property
    def direction(self) -> str:
        if self.delta > 0:
            return "increased"
        if self.delta < 0:
            return "decreased"
        return "unchanged"


@dataclass
class MetadataDiffResult:
    """Result of comparing metadata between two .env files."""

    left: MetadataSnapshot
    right: MetadataSnapshot
    changes: List[MetadataChange] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.changes)

    def changed_fields(self) -> List[str]:
        return [c.field for c in self.changes]

    def summary(self) -> str:
        if not self.has_changes():
            return "No metadata differences."
        lines = [f"{len(self.changes)} metadata field(s) changed:"]
        for c in self.changes:
            lines.append(
                f"  {c.field}: {c.left_value} -> {c.right_value} ({c.direction} by {abs(c.delta)})"
            )
        return "\n".join(lines)


def _collect_metadata(path: str, env: Dict[str, str]) -> MetadataSnapshot:
    """Read file-level metadata from *path* and cross-reference with *env*."""
    file_size = os.path.getsize(path)
    blank = 0
    comment = 0
    total = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            total += 1
            stripped = raw.strip()
            if not stripped:
                blank += 1
            elif stripped.startswith("#"):
                comment += 1
    empty_values = sum(1 for v in env.values() if v == "")
    return MetadataSnapshot(
        file_size=file_size,
        line_count=total,
        blank_lines=blank,
        comment_lines=comment,
        key_count=len(env),
        empty_value_count=empty_values,
    )


def diff_metadata(
    left_path: str,
    right_path: str,
    left_env: Dict[str, str],
    right_env: Dict[str, str],
) -> MetadataDiffResult:
    """Compare metadata of two .env files and return a :class:`MetadataDiffResult`.

    Parameters
    ----------
    left_path:
        Filesystem path to the *left* (baseline) .env file.
    right_path:
        Filesystem path to the *right* (comparison) .env file.
    left_env:
        Already-parsed key/value mapping for the left file.
    right_env:
        Already-parsed key/value mapping for the right file.
    """
    left_snap = _collect_metadata(left_path, left_env)
    right_snap = _collect_metadata(right_path, right_env)

    tracked_fields = [
        "file_size",
        "line_count",
        "blank_lines",
        "comment_lines",
        "key_count",
        "empty_value_count",
    ]

    changes: List[MetadataChange] = []
    for fname in tracked_fields:
        lv = getattr(left_snap, fname)
        rv = getattr(right_snap, fname)
        if lv != rv:
            changes.append(MetadataChange(field=fname, left_value=lv, right_value=rv))

    return MetadataDiffResult(left=left_snap, right=right_snap, changes=changes)
