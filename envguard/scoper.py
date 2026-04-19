"""Scope filtering: restrict env vars to a named scope via prefix mapping."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    scope: str
    env: Dict[str, str]
    matched_keys: List[str] = field(default_factory=list)
    unmatched_keys: List[str] = field(default_factory=list)

    def count(self) -> int:
        return len(self.matched_keys)

    def summary(self) -> str:
        return (
            f"Scope '{self.scope}': {len(self.matched_keys)} matched, "
            f"{len(self.unmatched_keys)} unmatched."
        )


def scope_env(
    env: Dict[str, str],
    scope: str,
    strip_prefix: bool = True,
    extra_keys: Optional[List[str]] = None,
) -> ScopeResult:
    """Return only keys belonging to *scope* (matched by prefix <SCOPE>_).

    Args:
        env: source environment dict.
        scope: scope name (case-insensitive prefix match).
        strip_prefix: if True, remove the prefix from result keys.
        extra_keys: additional exact keys to always include.
    """
    prefix = scope.upper() + "_"
    extra = set(extra_keys or [])
    matched: Dict[str, str] = {}
    matched_keys: List[str] = []
    unmatched_keys: List[str] = []

    for k, v in env.items():
        if k.startswith(prefix):
            out_key = k[len(prefix):] if strip_prefix else k
            matched[out_key] = v
            matched_keys.append(k)
        elif k in extra:
            matched[k] = v
            matched_keys.append(k)
        else:
            unmatched_keys.append(k)

    return ScopeResult(
        scope=scope,
        env=matched,
        matched_keys=matched_keys,
        unmatched_keys=unmatched_keys,
    )
