"""Sort .env variables by key or group."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_env: Dict[str, str]
    order: List[str]

    def changed(self) -> bool:
        return list(self.original.keys()) != self.order


def _group_key(key: str, groups: List[str]) -> tuple:
    """Return (group_index, key) for stable group-aware sorting."""
    key_upper = key.upper()
    for i, prefix in enumerate(groups):
        if key_upper.startswith(prefix.upper()):
            return (i, key)
    return (len(groups), key)


def sort_env(
    env: Dict[str, str],
    *,
    reverse: bool = False,
    groups: Optional[List[str]] = None,
) -> SortResult:
    """Sort env keys alphabetically, optionally grouping by prefix."""
    if groups:
        ordered = sorted(env.keys(), key=lambda k: _group_key(k, groups), reverse=reverse)
    else:
        ordered = sorted(env.keys(), reverse=reverse)
    sorted_env = {k: env[k] for k in ordered}
    return SortResult(original=dict(env), sorted_env=sorted_env, order=ordered)
