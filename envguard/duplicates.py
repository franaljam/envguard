"""Detect duplicate keys in .env files (keys defined more than once)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateResult:
    duplicates: Dict[str, List[str]]  # key -> list of values found

    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates():
            return "No duplicate keys found."
        lines = ["Duplicate keys detected:"]
        for key, values in sorted(self.duplicates.items()):
            vals = ", ".join(f'"{v}"' for v in values)
            lines.append(f"  {key}: [{vals}]")
        return "\n".join(lines)


def find_duplicates(path: str) -> DuplicateResult:
    """Parse a file manually to catch duplicate keys (parser.py keeps last value)."""
    duplicates: Dict[str, List[str]] = {}
    seen: Dict[str, List[str]] = {}

    with open(path, "r") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            seen.setdefault(key, []).append(value)

    for key, values in seen.items():
        if len(values) > 1:
            duplicates[key] = values

    return DuplicateResult(duplicates=duplicates)
