"""Dependency checker: detect keys that reference other keys and find broken refs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set
import re

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)")


@dataclass
class DepCheckResult:
    env: Dict[str, str]
    dependencies: Dict[str, List[str]]  # key -> keys it references
    broken: Dict[str, List[str]]        # key -> missing keys it references

    def has_broken(self) -> bool:
        return any(self.broken.values())

    def summary(self) -> str:
        total = sum(len(v) for v in self.broken.values())
        if total == 0:
            return "All references resolved."
        lines = [f"{total} broken reference(s) detected:"]
        for key, missing in self.broken.items():
            for m in missing:
                lines.append(f"  {key} -> ${m} (missing)")
        return "\n".join(lines)


def _extract_refs(value: str) -> List[str]:
    refs = []
    for m in _REF_RE.finditer(value):
        refs.append(m.group(1) or m.group(2))
    return refs


def check_dependencies(env: Dict[str, str]) -> DepCheckResult:
    dependencies: Dict[str, List[str]] = {}
    broken: Dict[str, List[str]] = {}

    for key, value in env.items():
        refs = _extract_refs(value)
        dependencies[key] = refs
        missing = [r for r in refs if r not in env]
        if missing:
            broken[key] = missing

    return DepCheckResult(env=dict(env), dependencies=dependencies, broken=broken)
