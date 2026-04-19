"""Trimmer: remove keys from an env dict by pattern or explicit list."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TrimResult:
    original: Dict[str, str]
    trimmed: Dict[str, str]
    removed: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return len(self.removed) > 0

    def summary(self) -> str:
        if not self.removed:
            return "No keys removed."
        keys = ", ".join(self.removed)
        return f"Removed {len(self.removed)} key(s): {keys}"


def trim_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    drop_empty: bool = False,
) -> TrimResult:
    """Return a new env dict with matching keys removed.

    Args:
        env: source environment dict.
        keys: explicit list of key names to remove.
        pattern: regex pattern; matching key names are removed.
        drop_empty: if True, also remove keys whose value is an empty string.
    """
    keys_set = set(keys or [])
    compiled = re.compile(pattern) if pattern else None

    removed: List[str] = []
    result: Dict[str, str] = {}

    for k, v in env.items():
        if k in keys_set:
            removed.append(k)
            continue
        if compiled and compiled.search(k):
            removed.append(k)
            continue
        if drop_empty and v == "":
            removed.append(k)
            continue
        result[k] = v

    removed.sort()
    return TrimResult(original=dict(env), trimmed=result, removed=removed)
