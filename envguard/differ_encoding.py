"""Detect encoding-related differences between two env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


_ESCAPE_SEQUENCES = {
    "\\n": "newline",
    "\\t": "tab",
    "\\r": "carriage return",
    "\\0": "null byte",
}


def _detect_escapes(value: str) -> List[str]:
    found = []
    for seq, label in _ESCAPE_SEQUENCES.items():
        if seq in value:
            found.append(label)
    return found


def _has_non_ascii(value: str) -> bool:
    return any(ord(c) > 127 for c in value)


@dataclass
class EncodingChange:
    key: str
    left_value: Optional[str]
    right_value: Optional[str]
    left_escapes: List[str] = field(default_factory=list)
    right_escapes: List[str] = field(default_factory=list)
    left_non_ascii: bool = False
    right_non_ascii: bool = False

    def description(self) -> str:
        parts = []
        if self.left_value is None:
            parts.append("added")
        elif self.right_value is None:
            parts.append("removed")
        else:
            if self.left_escapes != self.right_escapes:
                parts.append(f"escapes changed: {self.left_escapes} -> {self.right_escapes}")
            if self.left_non_ascii != self.right_non_ascii:
                parts.append("non-ASCII presence changed")
        return "; ".join(parts) if parts else "no encoding change"


@dataclass
class EncodingDiffResult:
    changes: List[EncodingChange] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.changes)

    def keys_with_changes(self) -> List[str]:
        return [c.key for c in self.changes]

    def summary(self) -> str:
        if not self.has_changes():
            return "No encoding differences detected."
        lines = [f"Encoding differences: {len(self.changes)} key(s) affected"]
        for c in self.changes:
            lines.append(f"  {c.key}: {c.description()}")
        return "\n".join(lines)


def diff_encoding(
    left: Dict[str, str],
    right: Dict[str, str],
) -> EncodingDiffResult:
    changes: List[EncodingChange] = []
    all_keys = sorted(set(left) | set(right))

    for key in all_keys:
        lv = left.get(key)
        rv = right.get(key)

        if lv is None or rv is None:
            lesc = _detect_escapes(lv) if lv is not None else []
            resc = _detect_escapes(rv) if rv is not None else []
            changes.append(EncodingChange(
                key=key,
                left_value=lv,
                right_value=rv,
                left_escapes=lesc,
                right_escapes=resc,
                left_non_ascii=_has_non_ascii(lv) if lv is not None else False,
                right_non_ascii=_has_non_ascii(rv) if rv is not None else False,
            ))
            continue

        lesc = _detect_escapes(lv)
        resc = _detect_escapes(rv)
        lna = _has_non_ascii(lv)
        rna = _has_non_ascii(rv)

        if lesc != resc or lna != rna:
            changes.append(EncodingChange(
                key=key,
                left_value=lv,
                right_value=rv,
                left_escapes=lesc,
                right_escapes=resc,
                left_non_ascii=lna,
                right_non_ascii=rna,
            ))

    return EncodingDiffResult(changes=changes)
