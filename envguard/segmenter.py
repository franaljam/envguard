"""Segment an env dict into named buckets based on key rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class SegmentResult:
    segments: Dict[str, Dict[str, str]] = field(default_factory=dict)
    unmatched: Dict[str, str] = field(default_factory=dict)

    def segment_names(self) -> List[str]:
        return sorted(self.segments.keys())

    def count(self, name: str) -> int:
        return len(self.segments.get(name, {}))

    def summary(self) -> str:
        lines = []
        for name in self.segment_names():
            lines.append(f"  [{name}] {self.count(name)} key(s)")
        if self.unmatched:
            lines.append(f"  [unmatched] {len(self.unmatched)} key(s)")
        return "\n".join(lines) if lines else "  no segments defined"


def segment_env(
    env: Dict[str, str],
    rules: Dict[str, str],
    *,
    strip_prefix: bool = False,
) -> SegmentResult:
    """Segment *env* into buckets defined by *rules*.

    *rules* maps segment name -> regex pattern applied to keys.
    Keys matched by multiple rules go into the first matching segment.
    """
    compiled = [(name, re.compile(pattern)) for name, pattern in rules.items()]
    segments: Dict[str, Dict[str, str]] = {name: {} for name in rules}
    unmatched: Dict[str, str] = {}

    for key, value in env.items():
        placed = False
        for name, rx in compiled:
            if rx.search(key):
                out_key = re.sub(rx, "", key, count=1) if strip_prefix else key
                segments[name][out_key] = value
                placed = True
                break
        if not placed:
            unmatched[key] = value

    return SegmentResult(segments=segments, unmatched=unmatched)
