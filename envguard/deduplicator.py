"""Deduplicator: remove duplicate values from an env dict, keeping the first or last occurrence."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeduplicateResult:
    env: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)
    value_map: Dict[str, List[str]] = field(default_factory=dict)  # value -> [keys]

    def changed(self) -> bool:
        return len(self.removed_keys) > 0

    def summary(self) -> str:
        if not self.changed():
            return "No duplicate values found."
        lines = [f"Removed {len(self.removed_keys)} duplicate key(s):"]
        for key in self.removed_keys:
            lines.append(f"  - {key}")
        return "\n".join(lines)


def deduplicate_env(
    env: Dict[str, str],
    keep: str = "first",
    ignore_empty: bool = True,
) -> DeduplicateResult:
    """Return a new env dict with duplicate values removed.

    Args:
        env: The source environment dictionary.
        keep: Which occurrence to keep — ``'first'`` or ``'last'``.
        ignore_empty: When *True*, empty-string values are not considered
            duplicates of each other.

    Returns:
        A :class:`DeduplicateResult` with the deduplicated env and metadata.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    # Build a mapping from value -> list of keys (in insertion order)
    value_map: Dict[str, List[str]] = {}
    for key, value in env.items():
        if ignore_empty and value == "":
            continue
        value_map.setdefault(value, []).append(key)

    # Determine which keys to remove
    removed: List[str] = []
    for value, keys in value_map.items():
        if len(keys) < 2:
            continue
        # keep first or last; drop the rest
        if keep == "first":
            to_drop = keys[1:]
        else:
            to_drop = keys[:-1]
        removed.extend(to_drop)

    removed_set = set(removed)
    deduped = {k: v for k, v in env.items() if k not in removed_set}

    return DeduplicateResult(
        env=deduped,
        removed_keys=removed,
        value_map={v: list(ks) for v, ks in value_map.items() if len(ks) > 1},
    )
