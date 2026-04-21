"""Compressor: remove redundant or derivable keys from an env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class CompressResult:
    original: Dict[str, str]
    compressed: Dict[str, str]
    removed: List[str] = field(default_factory=list)
    reasons: Dict[str, str] = field(default_factory=dict)

    def changed(self) -> bool:
        return bool(self.removed)

    def summary(self) -> str:
        if not self.removed:
            return "No keys removed — env is already compact."
        lines = [f"Removed {len(self.removed)} key(s):"]
        for k in self.removed:
            lines.append(f"  - {k}: {self.reasons.get(k, '')}")
        return "\n".join(lines)


def _is_duplicate_value(
    key: str, env: Dict[str, str], seen_values: Dict[str, str]
) -> Optional[str]:
    """Return the first key that already holds this value, or None."""
    val = env[key]
    if val == "":
        return None
    for other_key, other_val in seen_values.items():
        if other_key != key and other_val == val:
            return other_key
    return None


def _is_interpolated_duplicate(
    key: str, env: Dict[str, str]
) -> Optional[str]:
    """Return referenced key if value is literally ${REF} or $REF."""
    val = env[key]
    m = re.fullmatch(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)", val)
    if m:
        ref = m.group(1) or m.group(2)
        if ref in env and ref != key:
            return ref
    return None


def compress_env(
    env: Dict[str, str],
    *,
    remove_duplicates: bool = True,
    remove_interpolated: bool = True,
    explicit_keys: Optional[List[str]] = None,
) -> CompressResult:
    """Return a CompressResult with redundant keys stripped."""
    result: Dict[str, str] = dict(env)
    removed: List[str] = []
    reasons: Dict[str, str] = {}

    if explicit_keys:
        for k in explicit_keys:
            if k in result:
                reasons[k] = "explicitly removed"
                removed.append(k)
                del result[k]

    if remove_interpolated:
        for k in list(result):
            ref = _is_interpolated_duplicate(k, result)
            if ref is not None:
                reasons[k] = f"pure reference to '{ref}'"
                removed.append(k)
                del result[k]

    if remove_duplicates:
        seen: Dict[str, str] = {}
        for k in list(result):
            ref = _is_duplicate_value(k, result, seen)
            if ref is not None:
                reasons[k] = f"duplicate value of '{ref}'"
                removed.append(k)
                del result[k]
            else:
                seen[k] = result[k]

    return CompressResult(
        original=dict(env),
        compressed=result,
        removed=removed,
        reasons=reasons,
    )
