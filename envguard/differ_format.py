"""Detect formatting differences between two .env files.

Compares quoting style, spacing around `=`, and trailing whitespace
for keys present in both environments.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FormatChange:
    key: str
    left_raw: str
    right_raw: str
    issues: List[str] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.issues)


@dataclass
class FormatDiffResult:
    changes: List[FormatChange] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.changes)

    def keys_with_issues(self) -> List[str]:
        return [c.key for c in self.changes if c.has_issues()]

    def summary(self) -> str:
        if not self.has_changes():
            return "No formatting differences found."
        lines = [f"Formatting differences: {len(self.changes)} key(s) affected"]
        for c in self.changes:
            for issue in c.issues:
                lines.append(f"  {c.key}: {issue}")
        return "\n".join(lines)


_QUOTE_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(["\']?)(.*)\2\s*$')


def _detect_quoting(raw: str) -> Optional[str]:
    """Return the quote character used, or None."""
    m = _QUOTE_RE.match(raw)
    if m:
        q = m.group(2)
        return q if q else None
    return None


def _has_spacing_around_eq(raw: str) -> bool:
    return bool(re.search(r'\s+=\s*|\s*=\s+', raw))


def _has_trailing_whitespace(raw: str) -> bool:
    return raw != raw.rstrip()


def diff_format(
    left_lines: Dict[str, str],
    right_lines: Dict[str, str],
) -> FormatDiffResult:
    """Compare raw line representations for formatting issues.

    Args:
        left_lines: mapping of key -> raw line string for the left file.
        right_lines: mapping of key -> raw line string for the right file.

    Returns:
        FormatDiffResult with per-key formatting changes.
    """
    result = FormatDiffResult()
    common_keys = set(left_lines) & set(right_lines)
    for key in sorted(common_keys):
        left_raw = left_lines[key]
        right_raw = right_lines[key]
        issues: List[str] = []

        lq = _detect_quoting(left_raw)
        rq = _detect_quoting(right_raw)
        if lq != rq:
            l_label = repr(lq) if lq else "unquoted"
            r_label = repr(rq) if rq else "unquoted"
            issues.append(f"quote style changed ({l_label} -> {r_label})")

        if _has_spacing_around_eq(left_raw) != _has_spacing_around_eq(right_raw):
            issues.append("spacing around '=' changed")

        if _has_trailing_whitespace(left_raw) != _has_trailing_whitespace(right_raw):
            issues.append("trailing whitespace changed")

        if issues:
            result.changes.append(
                FormatChange(key=key, left_raw=left_raw, right_raw=right_raw, issues=issues)
            )
    return result
