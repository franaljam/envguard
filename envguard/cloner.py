"""Clone an env dict, optionally overriding or excluding specific keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class CloneResult:
    env: Dict[str, str]
    overridden: List[str] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return bool(self.overridden or self.excluded)

    def summary(self) -> str:
        parts: List[str] = []
        if self.overridden:
            parts.append(f"overridden: {', '.join(sorted(self.overridden))}")
        if self.excluded:
            parts.append(f"excluded: {', '.join(sorted(self.excluded))}")
        if not parts:
            return "clone identical to source"
        return "; ".join(parts)


def clone_env(
    source: Dict[str, str],
    overrides: Optional[Dict[str, str]] = None,
    exclude: Optional[List[str]] = None,
) -> CloneResult:
    """Return a deep copy of *source* with optional overrides and exclusions.

    Args:
        source:    The original env mapping.
        overrides: Key/value pairs that replace or add values in the clone.
        exclude:   Keys to omit from the clone entirely.

    Returns:
        A :class:`CloneResult` whose ``.env`` is the new mapping.
    """
    overrides = overrides or {}
    exclude_set: Set[str] = set(exclude or [])

    cloned: Dict[str, str] = {}
    excluded_keys: List[str] = []
    overridden_keys: List[str] = []

    for key, value in source.items():
        if key in exclude_set:
            excluded_keys.append(key)
            continue
        if key in overrides:
            cloned[key] = overrides[key]
            overridden_keys.append(key)
        else:
            cloned[key] = value

    # Overrides may also introduce brand-new keys not present in source.
    for key, value in overrides.items():
        if key not in source and key not in exclude_set:
            cloned[key] = value
            overridden_keys.append(key)

    return CloneResult(
        env=cloned,
        overridden=overridden_keys,
        excluded=excluded_keys,
    )
