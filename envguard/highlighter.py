"""Highlight keys in an env dict based on match criteria."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class HighlightResult:
    env: Dict[str, str]
    highlighted: List[str] = field(default_factory=list)

    def count(self) -> int:
        return len(self.highlighted)

    def summary(self) -> str:
        if not self.highlighted:
            return "No keys highlighted."
        keys = ", ".join(self.highlighted)
        return f"{len(self.highlighted)} key(s) highlighted: {keys}"


def _matches(
    key: str,
    prefixes: Optional[List[str]],
    patterns: Optional[List[str]],
    exact: Optional[List[str]],
) -> bool:
    if exact and key in exact:
        return True
    if prefixes and any(key.startswith(p) for p in prefixes):
        return True
    if patterns and any(re.search(pat, key) for pat in patterns):
        return True
    return False


def highlight_env(
    env: Dict[str, str],
    *,
    prefixes: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    exact: Optional[List[str]] = None,
) -> HighlightResult:
    """Return a HighlightResult marking keys that match the given criteria."""
    if not prefixes and not patterns and not exact:
        return HighlightResult(env=dict(env), highlighted=[])

    highlighted: List[str] = [
        k for k in env if _matches(k, prefixes, patterns, exact)
    ]
    return HighlightResult(env=dict(env), highlighted=sorted(highlighted))
