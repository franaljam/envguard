"""referencer.py – find all env files that reference a given key."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

_REF_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class ReferenceHit:
    file: str
    key: str
    line_number: int
    line: str


@dataclass
class ReferenceResult:
    target: str
    hits: List[ReferenceHit] = field(default_factory=list)

    def found(self) -> bool:
        return len(self.hits) > 0

    def files(self) -> List[str]:
        return sorted({h.file for h in self.hits})

    def summary(self) -> str:
        if not self.found():
            return f"No references to '{self.target}' found."
        lines = [f"Found {len(self.hits)} reference(s) to '{self.target}':"]
        for hit in self.hits:
            lines.append(f"  {hit.file}:{hit.line_number}  {hit.line.strip()}")
        return "\n".join(lines)


def _refs_in_value(value: str) -> List[str]:
    """Return all key names referenced inside *value*."""
    return [
        m.group(1) or m.group(2)
        for m in _REF_PATTERN.finditer(value)
    ]


def find_references(
    target: str,
    env_files: List[str | Path],
) -> ReferenceResult:
    """Search *env_files* for any value that references *target*.

    Args:
        target: The env key name to search for.
        env_files: Paths to .env files to scan.

    Returns:
        A :class:`ReferenceResult` with all matching hits.
    """
    result = ReferenceResult(target=target)
    for path in env_files:
        path = Path(path)
        if not path.exists():
            continue
        for lineno, raw in enumerate(path.read_text().splitlines(), start=1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            key = key.strip()
            if key == target:
                continue  # skip self-definition
            for ref in _refs_in_value(value):
                if ref == target:
                    result.hits.append(
                        ReferenceHit(
                            file=str(path),
                            key=key,
                            line_number=lineno,
                            line=raw,
                        )
                    )
    return result
