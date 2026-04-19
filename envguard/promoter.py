"""Promote .env values from one environment to another with conflict detection."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PromoteResult:
    source_env: str
    target_env: str
    promoted: Dict[str, str] = field(default_factory=dict)
    skipped: Dict[str, str] = field(default_factory=dict)
    overwritten: Dict[str, str] = field(default_factory=dict)
    merged: Dict[str, str] = field(default_factory=dict)

    def changed(self) -> bool:
        return bool(self.promoted or self.overwritten)

    def summary(self) -> str:
        lines = [f"Promote: {self.source_env} -> {self.target_env}"]
        lines.append(f"  Promoted : {len(self.promoted)}")
        lines.append(f"  Overwritten: {len(self.overwritten)}")
        lines.append(f"  Skipped  : {len(self.skipped)}")
        return "\n".join(lines)


def promote_env(
    source: Dict[str, str],
    target: Dict[str, str],
    source_env: str = "source",
    target_env: str = "target",
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Promote keys from source into target.

    Args:
        source: Source environment variables.
        target: Target environment variables.
        source_env: Label for source (used in result).
        target_env: Label for target (used in result).
        keys: Explicit list of keys to promote; if None promote all.
        overwrite: If True, overwrite existing keys in target.
    """
    result = PromoteResult(source_env=source_env, target_env=target_env)
    candidates = keys if keys is not None else list(source.keys())
    merged = dict(target)

    for key in candidates:
        if key not in source:
            continue
        value = source[key]
        if key in target:
            if overwrite:
                result.overwritten[key] = value
                merged[key] = value
            else:
                result.skipped[key] = value
        else:
            result.promoted[key] = value
            merged[key] = value

    result.merged = merged
    return result
