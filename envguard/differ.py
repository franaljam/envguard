"""Diff two parsed .env variable sets and report missing/extra/changed keys."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DiffResult:
    missing: List[str] = field(default_factory=list)   # in base, not in target
    extra: List[str] = field(default_factory=list)      # in target, not in base
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (base_val, target_val)

    @property
    def has_differences(self) -> bool:
        return bool(self.missing or self.extra or self.changed)

    def summary(self) -> str:
        lines = []
        if self.missing:
            lines.append("Missing keys (in base, absent in target):")
            for k in sorted(self.missing):
                lines.append(f"  - {k}")
        if self.extra:
            lines.append("Extra keys (in target, absent in base):")
            for k in sorted(self.extra):
                lines.append(f"  + {k}")
        if self.changed:
            lines.append("Changed values:")
            for k in sorted(self.changed):
                base_val, target_val = self.changed[k]
                lines.append(f"  ~ {k}: {base_val!r} -> {target_val!r}")
        if not lines:
            return "No differences found."
        return "\n".join(lines)


def diff_envs(
    base: Dict[str, str],
    target: Dict[str, str],
    ignore_values: bool = False,
) -> DiffResult:
    """Compare *base* env dict against *target* env dict.

    Args:
        base: Reference environment (e.g. .env.example).
        target: Environment under test (e.g. .env.production).
        ignore_values: When True only check key presence, skip value comparison.

    Returns:
        DiffResult populated with missing, extra, and changed entries.
    """
    result = DiffResult()

    base_keys = set(base)
    target_keys = set(target)

    result.missing = list(base_keys - target_keys)
    result.extra = list(target_keys - base_keys)

    if not ignore_values:
        for key in base_keys & target_keys:
            if base[key] != target[key]:
                result.changed[key] = (base[key], target[key])

    return result
