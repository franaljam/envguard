"""Detect formatting differences between two .env files (quoting style, spacing, etc.)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


_QUOTED_DOUBLE = re.compile(r'^".*"$')
_QUOTED_SINGLE = re.compile(r"^'.*'$")
_HAS_INLINE_SPACE = re.compile(r'\s+=\s+|=\s+|\s+=')


def _detect_quote_style(raw_value: str) -> Optional[str]:
    if _QUOTED_DOUBLE.match(raw_value):
        return "double"
    if _QUOTED_SINGLE.match(raw_value):
        return "single"
    return None


def _detect_spacing(raw_line: str) -> str:
    """Return 'spaced', 'compact', or 'mixed' based on = surroundings."""
    if re.search(r'\s+=\s+', raw_line):
        return "spaced"
    if re.search(r'\s+=|=\s+', raw_line):
        return "mixed"
    return "compact"


@dataclass
class FormatChange:
    key: str
    left_quote: Optional[str]
    right_quote: Optional[str]
    left_spacing: str
    right_spacing: str

    @property
    def quote_changed(self) -> bool:
        return self.left_quote != self.right_quote

    @property
    def spacing_changed(self) -> bool:
        return self.left_spacing != self.right_spacing


@dataclass
class FormatDiffResult:
    changes: List[FormatChange] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def summary(self) -> str:
        if not self.has_changes:
            return "No formatting differences."
        lines = [f"{len(self.changes)} formatting difference(s):"]
        for c in self.changes:
            parts = []
            if c.quote_changed:
                parts.append(f"quote {c.left_quote!r} -> {c.right_quote!r}")
            if c.spacing_changed:
                parts.append(f"spacing {c.left_spacing!r} -> {c.right_spacing!r}")
            lines.append(f"  {c.key}: {', '.join(parts)}")
        return "\n".join(lines)


def _parse_raw_lines(path: str) -> Dict[str, tuple]:
    """Return {key: (raw_value, spacing)} for each assignment line."""
    result: Dict[str, tuple] = {}
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                continue
            if "=" not in line:
                continue
            key_part, _, val_part = line.partition("=")
            key = key_part.strip()
            spacing = _detect_spacing(line)
            result[key] = (val_part, spacing)
    return result


def diff_format(left_path: str, right_path: str) -> FormatDiffResult:
    left = _parse_raw_lines(left_path)
    right = _parse_raw_lines(right_path)
    changes: List[FormatChange] = []
    for key in sorted(set(left) & set(right)):
        lv, ls = left[key]
        rv, rs = right[key]
        lq = _detect_quote_style(lv)
        rq = _detect_quote_style(rv)
        if lq != rq or ls != rs:
            changes.append(FormatChange(key=key, left_quote=lq, right_quote=rq,
                                        left_spacing=ls, right_spacing=rs))
    return FormatDiffResult(changes=changes)
