"""Merge multiple .env files with conflict detection."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envguard.parser import parse_env_file


@dataclass
class MergeConflict:
    key: str
    values: Dict[str, str]  # source -> value


@dataclass
class MergeResult:
    merged: Dict[str, str]
    conflicts: List[MergeConflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def conflict_keys(self) -> List[str]:
        return [c.key for c in self.conflicts]


def merge_envs(
    sources: Dict[str, Dict[str, str]],
    strategy: str = "last",
) -> MergeResult:
    """Merge multiple env dicts.

    Args:
        sources: Ordered dict of label -> env vars.
        strategy: 'last' keeps last value, 'first' keeps first value.
                  Conflicts are always recorded regardless of strategy.
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    seen: Dict[str, Dict[str, str]] = {}  # key -> {source: value}
    order: List[str] = []

    for source, env in sources.items():
        for key, value in env.items():
            if key not in seen:
                seen[key] = {}
                order.append(key)
            seen[key][source] = value

    merged: Dict[str, str] = {}
    conflicts: List[MergeConflict] = []

    for key in order:
        contributors = seen[key]
        unique_values = set(contributors.values())
        if len(unique_values) > 1:
            conflicts.append(MergeConflict(key=key, values=dict(contributors)))

        values_list = list(contributors.values())
        merged[key] = values_list[0] if strategy == "first" else values_list[-1]

    return MergeResult(merged=merged, conflicts=conflicts)


def merge_env_files(
    paths: Dict[str, str],
    strategy: str = "last",
) -> MergeResult:
    """Parse and merge .env files. paths is label -> filepath."""
    sources = {label: parse_env_file(path) for label, path in paths.items()}
    return merge_envs(sources, strategy=strategy)
