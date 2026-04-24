"""Key rotation helper: identify stale keys and produce a rotated env."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_PATTERNS = re.compile(
    r"(SECRET|PASSWORD|PASSWD|TOKEN|KEY|PRIVATE|CREDENTIAL|AUTH)",
    re.IGNORECASE,
)


@dataclass
class RotateResult:
    rotated: Dict[str, str]
    original: Dict[str, str]
    rotated_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return len(self.rotated_keys) > 0

    def summary(self) -> str:
        if not self.changed():
            return "No keys rotated."
        lines = [f"Rotated {len(self.rotated_keys)} key(s):"]
        for k in self.rotated_keys:
            lines.append(f"  {k}")
        if self.skipped_keys:
            lines.append(f"Skipped {len(self.skipped_keys)} key(s) (non-sensitive or excluded).")
        return "\n".join(lines)


def _is_sensitive(key: str) -> bool:
    return bool(_SENSITIVE_PATTERNS.search(key))


def rotate_env(
    env: Dict[str, str],
    replacements: Dict[str, str],
    *,
    sensitive_only: bool = True,
    exclude: Optional[List[str]] = None,
) -> RotateResult:
    """Return a new env dict with specified keys replaced by new values.

    Args:
        env: The source environment mapping.
        replacements: Mapping of key -> new_value to apply.
        sensitive_only: When True, only rotate keys that match sensitive patterns.
        exclude: Keys to skip even if present in replacements.
    """
    exclude_set = set(exclude or [])
    rotated: Dict[str, str] = dict(env)
    rotated_keys: List[str] = []
    skipped_keys: List[str] = []

    for key, new_value in replacements.items():
        if key in exclude_set:
            skipped_keys.append(key)
            continue
        if sensitive_only and not _is_sensitive(key):
            skipped_keys.append(key)
            continue
        if key not in env:
            skipped_keys.append(key)
            continue
        rotated[key] = new_value
        rotated_keys.append(key)

    return RotateResult(
        rotated=rotated,
        original=dict(env),
        rotated_keys=rotated_keys,
        skipped_keys=skipped_keys,
    )
