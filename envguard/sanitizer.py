"""Sanitize .env values by applying safe transformations."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SanitizeResult:
    original: Dict[str, str]
    sanitized: Dict[str, str]
    changes: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return bool(self.changes)

    def summary(self) -> str:
        if not self.changes:
            return "No sanitization changes."
        lines = [f"Sanitized {len(self.changes)} value(s):"]
        for c in self.changes:
            lines.append(f"  - {c}")
        return "\n".join(lines)


def sanitize_env(
    env: Dict[str, str],
    *,
    strip_quotes: bool = True,
    remove_control_chars: bool = True,
    normalize_booleans: bool = False,
) -> SanitizeResult:
    """Return a sanitized copy of env with optional transformations."""
    result: Dict[str, str] = {}
    changes: List[str] = []

    for key, value in env.items():
        new_value = value

        if strip_quotes:
            stripped = _strip_quotes(new_value)
            if stripped != new_value:
                changes.append(f"{key}: stripped surrounding quotes")
                new_value = stripped

        if remove_control_chars:
            cleaned = _remove_control_chars(new_value)
            if cleaned != new_value:
                changes.append(f"{key}: removed control characters")
                new_value = cleaned

        if normalize_booleans:
            normed = _normalize_boolean(new_value)
            if normed != new_value:
                changes.append(f"{key}: normalized boolean to '{normed}'")
                new_value = normed

        result[key] = new_value

    return SanitizeResult(original=dict(env), sanitized=result, changes=changes)


def _strip_quotes(value: str) -> str:
    for q in ('"', "'"):
        if value.startswith(q) and value.endswith(q) and len(value) >= 2:
            return value[1:-1]
    return value


def _remove_control_chars(value: str) -> str:
    return "".join(ch for ch in value if ch >= " " or ch == "\t")


def _normalize_boolean(value: str) -> str:
    if value.lower() in ("true", "yes", "1", "on"):
        return "true"
    if value.lower() in ("false", "no", "0", "off"):
        return "false"
    return value
