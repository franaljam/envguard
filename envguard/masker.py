"""masker.py — selectively mask env values for safe display or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_FRAGMENTS = ("SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "PRIVATE", "AUTH", "CREDENTIAL")


@dataclass
class MaskResult:
    masked: Dict[str, str]
    original_keys: List[str]
    masked_keys: List[str]

    def count(self) -> int:
        return len(self.masked_keys)

    def summary(self) -> str:
        if not self.masked_keys:
            return "No keys masked."
        keys = ", ".join(sorted(self.masked_keys))
        return f"{len(self.masked_keys)} key(s) masked: {keys}"


def _is_sensitive(key: str, extra_patterns: List[str]) -> bool:
    upper = key.upper()
    for fragment in _SENSITIVE_FRAGMENTS:
        if fragment in upper:
            return True
    for pattern in extra_patterns:
        if pattern.upper() in upper:
            return True
    return False


def mask_env(
    env: Dict[str, str],
    *,
    placeholder: str = "***",
    reveal_prefix: int = 0,
    extra_patterns: Optional[List[str]] = None,
    explicit_keys: Optional[List[str]] = None,
) -> MaskResult:
    """Return a copy of *env* with sensitive values replaced by *placeholder*.

    Args:
        env: Source environment mapping.
        placeholder: String to substitute for sensitive values.
        reveal_prefix: Number of leading characters to keep visible (0 = hide all).
        extra_patterns: Additional key fragments treated as sensitive.
        explicit_keys: If provided, *only* these keys are masked (overrides auto-detection).
    """
    extra_patterns = extra_patterns or []
    result: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        should_mask = (
            key in explicit_keys
            if explicit_keys is not None
            else _is_sensitive(key, extra_patterns)
        )
        if should_mask:
            if reveal_prefix > 0 and len(value) > reveal_prefix:
                result[key] = value[:reveal_prefix] + placeholder
            else:
                result[key] = placeholder
            masked_keys.append(key)
        else:
            result[key] = value

    return MaskResult(
        masked=result,
        original_keys=list(env.keys()),
        masked_keys=masked_keys,
    )
