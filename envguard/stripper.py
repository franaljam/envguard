"""Strip keys from an env dict based on patterns, prefixes, or explicit lists."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StripResult:
    original: Dict[str, str]
    stripped: Dict[str, str]
    removed: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return bool(self.removed)

    def summary(self) -> str:
        if not self.removed:
            return "No keys stripped."
        keys = ", ".join(self.removed)
        return f"Stripped {len(self.removed)} key(s): {keys}"


def strip_env(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    prefixes: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    invert: bool = False,
) -> StripResult:
    """Return a copy of *env* with matching keys removed.

    Args:
        env:      Source environment dict.
        keys:     Exact key names to remove.
        prefixes: Remove keys whose name starts with any of these prefixes.
        patterns: Remove keys matching any of these regex patterns.
        invert:   If True, *keep* only the matched keys (strip everything else).
    """
    compiled = [re.compile(p) for p in (patterns or [])]

    def _matches(k: str) -> bool:
        if keys and k in keys:
            return True
        if prefixes and any(k.startswith(px) for px in prefixes):
            return True
        if compiled and any(rx.search(k) for rx in compiled):
            return True
        return False

    removed: List[str] = []
    result: Dict[str, str] = {}

    for k, v in env.items():
        matched = _matches(k)
        should_remove = matched if not invert else not matched
        if should_remove:
            removed.append(k)
        else:
            result[k] = v

    return StripResult(original=dict(env), stripped=result, removed=sorted(removed))
