"""Pruner: remove keys from an env dict based on age, staleness, or explicit criteria."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional


@dataclass
class PruneResult:
    original: Dict[str, str]
    pruned: Dict[str, str]
    removed: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return bool(self.removed)

    def summary(self) -> str:
        if not self.removed:
            return "No keys pruned."
        keys = ", ".join(self.removed)
        return f"Pruned {len(self.removed)} key(s): {keys}"


def prune_env(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    prefixes: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    empty_only: bool = False,
) -> PruneResult:
    """Return a copy of *env* with matching keys removed.

    Parameters
    ----------
    keys:       exact key names to remove.
    prefixes:   remove any key whose name starts with one of these strings.
    patterns:   remove any key whose name matches one of these glob patterns.
    empty_only: when True, only remove a key if its value is the empty string.
    """
    removed: List[str] = []
    result: Dict[str, str] = {}

    for k, v in env.items():
        should_remove = False

        if keys and k in keys:
            should_remove = True
        elif prefixes and any(k.startswith(p) for p in prefixes):
            should_remove = True
        elif patterns and any(fnmatch(k, pat) for pat in patterns):
            should_remove = True

        if should_remove and empty_only and v != "":
            should_remove = False

        if should_remove:
            removed.append(k)
        else:
            result[k] = v

    return PruneResult(original=dict(env), pruned=result, removed=removed)
