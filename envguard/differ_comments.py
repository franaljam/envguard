"""Diff inline comments between two .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


_COMMENT_RE = re.compile(r"(?:^|\s)#(.*)$")


def _extract_comment(raw_line: str) -> Optional[str]:
    """Return the inline comment text from a raw .env line, or None."""
    m = _COMMENT_RE.search(raw_line)
    if m:
        return m.group(1).strip()
    return None


def _parse_comments(lines: List[str]) -> Dict[str, Optional[str]]:
    """Map each key to its inline comment (or None) from raw file lines."""
    result: Dict[str, Optional[str]] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, rest = stripped.partition("=")
        key = key.strip()
        result[key] = _extract_comment(rest)
    return result


@dataclass
class CommentChange:
    key: str
    left: Optional[str]
    right: Optional[str]

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
class CommentDiffResult:
    changes: List[CommentChange] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    def added(self) -> List[CommentChange]:
        return [c for c in self.changes if c.added]

    def removed(self) -> List[CommentChange]:
        return [c for c in self.changes if c.removed]

    def modified(self) -> List[CommentChange]:
        return [c for c in self.changes if c.modified]

    def summary(self) -> str:
        if not self.has_changes:
            return "No comment differences."
        parts = []
        if self.added():
            parts.append(f"{len(self.added())} added")
        if self.removed():
            parts.append(f"{len(self.removed())} removed")
        if self.modified():
            parts.append(f"{len(self.modified())} modified")
        return "Comment changes: " + ", ".join(parts) + "."


def diff_comments(
    left_lines: List[str],
    right_lines: List[str],
) -> CommentDiffResult:
    """Compare inline comments between two sets of .env file lines."""
    left_map = _parse_comments(left_lines)
    right_map = _parse_comments(right_lines)
    all_keys = sorted(set(left_map) | set(right_map))
    changes: List[CommentChange] = []
    for key in all_keys:
        lc = left_map.get(key)
        rc = right_map.get(key)
        if lc != rc:
            changes.append(CommentChange(key=key, left=lc, right=rc))
    return CommentDiffResult(changes=changes)
