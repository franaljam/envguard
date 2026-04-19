"""Filter .env variables by pattern, prefix, or tag."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterResult:
    matched: Dict[str, str]
    excluded: Dict[str, str]

    def count(self) -> int:
        return len(self.matched)

    def summary(self) -> str:
        return (
            f"{len(self.matched)} key(s) matched, "
            f"{len(self.excluded)} excluded"
        )


def filter_env(
    env: Dict[str, str],
    *,
    prefixes: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    keys: Optional[List[str]] = None,
    invert: bool = False,
) -> FilterResult:
    """Return variables matching any of the given criteria.

    Args:
        env: Parsed environment dict.
        prefixes: Include keys starting with any of these strings.
        patterns: Include keys matching any of these regex patterns.
        keys: Include exact key names.
        invert: If True, return keys that do NOT match.
    """
    compiled = [re.compile(p) for p in (patterns or [])]

    def _matches(key: str) -> bool:
        if keys and key in keys:
            return True
        if prefixes and any(key.startswith(p) for p in prefixes):
            return True
        if compiled and any(rx.search(key) for rx in compiled):
            return True
        return False

    no_criteria = not prefixes and not patterns and not keys

    matched: Dict[str, str] = {}
    excluded: Dict[str, str] = {}

    for k, v in env.items():
        hit = _matches(k) if not no_criteria else True
        if invert:
            hit = not hit
        if hit:
            matched[k] = v
        else:
            excluded[k] = v

    return FilterResult(matched=matched, excluded=excluded)
