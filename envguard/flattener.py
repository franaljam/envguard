"""Flatten nested prefix structures into a single-level env dict."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenResult:
    env: Dict[str, str]
    renamed: Dict[str, str]  # old_key -> new_key
    separator: str

    def changed(self) -> bool:
        return bool(self.renamed)

    def summary(self) -> str:
        if not self.renamed:
            return "No keys flattened."
        lines = [f"Flattened {len(self.renamed)} key(s):"]
        for old, new in sorted(self.renamed.items()):
            lines.append(f"  {old} -> {new}")
        return "\n".join(lines)


def flatten_env(
    env: Dict[str, str],
    separator: str = "__",
    prefix: Optional[str] = None,
    lowercase_keys: bool = False,
) -> FlattenResult:
    """Collapse keys that contain *separator* by removing a common prefix.

    If *prefix* is given, only keys starting with ``<prefix><separator>``
    are rewritten; the prefix segment is stripped.  All other keys are
    kept as-is.  When *prefix* is None every key containing the separator
    is left unchanged (nothing to flatten without a reference prefix).
    """
    result: Dict[str, str] = {}
    renamed: Dict[str, str] = {}

    for key, value in env.items():
        new_key = key
        if prefix is not None:
            full_prefix = prefix + separator
            if key.startswith(full_prefix):
                new_key = key[len(full_prefix):]
        if lowercase_keys:
            new_key = new_key.lower()
        if new_key != key:
            renamed[key] = new_key
        result[new_key] = value

    return FlattenResult(env=result, renamed=renamed, separator=separator)
