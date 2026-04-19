"""Normalize .env variable values to consistent formats."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changed_keys: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return bool(self.changed_keys)

    def summary(self) -> str:
        if not self.changed_keys:
            return "No normalization changes."
        keys = ", ".join(self.changed_keys)
        return f"{len(self.changed_keys)} key(s) normalized: {keys}"


def _normalize_bool(value: str) -> str:
    """Normalize boolean-like values to 'true'/'false'."""
    if value.lower() in ("1", "yes", "on", "true"):
        return "true"
    if value.lower() in ("0", "no", "off", "false"):
        return "false"
    return value


def _strip_inline_comments(value: str) -> str:
    """Remove trailing inline comments (# ...) from values not quoted."""
    if value.startswith(("'", '"')):
        return value
    idx = value.find(" #")
    if idx != -1:
        return value[:idx].rstrip()
    return value


def normalize_env(
    env: Dict[str, str],
    *,
    normalize_bools: bool = True,
    strip_inline_comments: bool = True,
    lowercase_values: bool = False,
) -> NormalizeResult:
    """Apply normalization passes to an env dict."""
    result: Dict[str, str] = {}
    changed: List[str] = []

    for key, value in env.items():
        new_value = value

        if strip_inline_comments:
            new_value = _strip_inline_comments(new_value)

        if normalize_bools:
            new_value = _normalize_bool(new_value)

        if lowercase_values:
            new_value = new_value.lower()

        result[key] = new_value
        if new_value != value:
            changed.append(key)

    return NormalizeResult(original=dict(env), normalized=result, changed_keys=changed)
