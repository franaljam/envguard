"""Freeze an env dict into an immutable baseline and detect thaw (changes)."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FreezeEntry:
    key: str
    checksum: str


@dataclass
class FreezeResult:
    entries: Dict[str, str]  # key -> checksum
    thawed: List[str] = field(default_factory=list)  # keys that changed vs baseline
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    def is_frozen(self) -> bool:
        return not self.thawed and not self.added and not self.removed

    def summary(self) -> str:
        if self.is_frozen():
            return "Environment matches frozen baseline."
        parts = []
        if self.thawed:
            parts.append(f"{len(self.thawed)} changed")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        return "Drift detected: " + ", ".join(parts) + "."


def _checksum(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def freeze_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a mapping of key -> checksum for the given env."""
    return {k: _checksum(v) for k, v in env.items()}


def compare_freeze(
    env: Dict[str, str],
    baseline: Dict[str, str],
) -> FreezeResult:
    """Compare current env against a frozen baseline (key->checksum map)."""
    current = freeze_env(env)
    thawed = [k for k in current if k in baseline and current[k] != baseline[k]]
    added = [k for k in current if k not in baseline]
    removed = [k for k in baseline if k not in current]
    return FreezeResult(entries=current, thawed=thawed, added=added, removed=removed)


def save_freeze(baseline: Dict[str, str], path: str) -> None:
    with open(path, "w") as fh:
        json.dump(baseline, fh, indent=2, sort_keys=True)


def load_freeze(path: str) -> Dict[str, str]:
    with open(path) as fh:
        return json.load(fh)
