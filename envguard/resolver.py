"""Resolve environment variable references from external sources (OS env, defaults)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os
import re

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class ResolveEntry:
    key: str
    original: str
    resolved: str
    sources: List[str] = field(default_factory=list)  # where each ref was found


@dataclass
class ResolveResult:
    entries: Dict[str, ResolveEntry] = field(default_factory=dict)
    unresolved: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return any(e.original != e.resolved for e in self.entries.values())

    def summary(self) -> str:
        resolved_count = sum(
            1 for e in self.entries.values() if e.original != e.resolved
        )
        unresolved_count = len(self.unresolved)
        return (
            f"Resolved {resolved_count} reference(s); "
            f"{unresolved_count} unresolved reference(s)."
        )


def resolve_env(
    env: Dict[str, str],
    *,
    fallback_to_os: bool = True,
    defaults: Optional[Dict[str, str]] = None,
    strict: bool = False,
) -> ResolveResult:
    """Resolve ${VAR} / $VAR references in values using env itself, OS env, and defaults."""
    defaults = defaults or {}
    result = ResolveResult()

    for key, value in env.items():
        resolved = value
        sources: List[str] = []
        broken: List[str] = []

        def _replace(m: re.Match) -> str:  # noqa: E306
            ref = m.group(1) or m.group(2)
            if ref in env:
                sources.append(f"{ref}=env")
                return env[ref]
            if fallback_to_os and ref in os.environ:
                sources.append(f"{ref}=os")
                return os.environ[ref]
            if ref in defaults:
                sources.append(f"{ref}=default")
                return defaults[ref]
            broken.append(ref)
            return m.group(0)

        resolved = _REF_RE.sub(_replace, value)

        for ref in broken:
            if ref not in result.unresolved:
                result.unresolved.append(ref)

        if strict and broken:
            from envguard.interpolator import InterpolationError
            raise InterpolationError(
                f"Unresolved reference(s) in '{key}': {broken}"
            )

        result.entries[key] = ResolveEntry(
            key=key, original=value, resolved=resolved, sources=sources
        )

    return result
