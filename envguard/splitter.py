"""Split a flat env dict into multiple files by prefix or group."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class SplitResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def summary(self) -> str:
        lines = [f"Split into {len(self.groups)} group(s):"]
        for name in self.group_names():
            lines.append(f"  {name}: {len(self.groups[name])} key(s)")
        if self.ungrouped:
            lines.append(f"  (ungrouped): {len(self.ungrouped)} key(s)")
        return "\n".join(lines)


def split_env(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    strip_prefix: bool = False,
) -> SplitResult:
    """Split env dict by key prefixes.

    Args:
        env: Source environment variables.
        prefixes: List of prefixes to split on. If None, auto-detect.
        strip_prefix: Remove the prefix from keys in each group.

    Returns:
        SplitResult with groups and ungrouped keys.
    """
    if prefixes is None:
        prefixes = _auto_detect_prefixes(env)

    groups: Dict[str, Dict[str, str]] = {}
    ungrouped: Dict[str, str] = {}
    assigned: set = set()

    for prefix in prefixes:
        bucket: Dict[str, str] = {}
        pat = re.compile(r'^' + re.escape(prefix) + r'_', re.IGNORECASE)
        for key, value in env.items():
            if pat.match(key):
                out_key = key[len(prefix) + 1:] if strip_prefix else key
                bucket[out_key] = value
                assigned.add(key)
        if bucket:
            groups[prefix] = bucket

    for key, value in env.items():
        if key not in assigned:
            ungrouped[key] = value

    return SplitResult(groups=groups, ungrouped=ungrouped)


def _auto_detect_prefixes(env: Dict[str, str]) -> List[str]:
    counts: Dict[str, int] = {}
    for key in env:
        if '_' in key:
            prefix = key.split('_')[0]
            counts[prefix] = counts.get(prefix, 0) + 1
    return [p for p, c in counts.items() if c > 1]
