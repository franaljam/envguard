"""Group env variables by prefix into logical namespaces."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupResult:
    groups: Dict[str, Dict[str, str]]
    ungrouped: Dict[str, str]

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def summary(self) -> str:
        lines = [f"Groups: {len(self.groups)}, Ungrouped: {len(self.ungrouped)}"]
        for name in self.group_names():
            lines.append(f"  [{name}] {len(self.groups[name])} key(s)")
        if self.ungrouped:
            lines.append(f"  [ungrouped] {len(self.ungrouped)} key(s)")
        return "\n".join(lines)


def group_env(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    separator: str = "_",
) -> GroupResult:
    """Group keys by prefix. If prefixes is None, auto-detect from keys."""
    if prefixes is None:
        prefixes = _auto_detect_prefixes(env, separator)

    groups: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    ungrouped: Dict[str, str] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix + separator) or key == prefix:
                groups[prefix][key] = value
                matched = True
                break
        if not matched:
            ungrouped[key] = value

    return GroupResult(groups=groups, ungrouped=ungrouped)


def _auto_detect_prefixes(env: Dict[str, str], separator: str) -> List[str]:
    from collections import Counter
    counts: Counter = Counter()
    for key in env:
        if separator in key:
            counts[key.split(separator)[0]] += 1
    return [p for p, c in counts.items() if c >= 2]
