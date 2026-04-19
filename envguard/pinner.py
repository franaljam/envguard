"""Pin current env variable values to a lockfile for drift detection."""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class PinEntry:
    key: str
    checksum: str


@dataclass
class PinResult:
    entries: List[PinEntry] = field(default_factory=list)
    drifted: List[str] = field(default_factory=list)
    new_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    def has_drift(self) -> bool:
        return bool(self.drifted or self.new_keys or self.removed_keys)

    def summary(self) -> str:
        parts = []
        if self.drifted:
            parts.append(f"Drifted: {', '.join(self.drifted)}")
        if self.new_keys:
            parts.append(f"New: {', '.join(self.new_keys)}")
        if self.removed_keys:
            parts.append(f"Removed: {', '.join(self.removed_keys)}")
        return "; ".join(parts) if parts else "No drift detected."


def _checksum(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def pin_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a dict of key -> checksum for the given env."""
    return {k: _checksum(v) for k, v in env.items()}


def save_pinfile(env: Dict[str, str], path: str) -> None:
    pins = pin_env(env)
    Path(path).write_text(json.dumps(pins, indent=2, sort_keys=True))


def load_pinfile(path: str) -> Dict[str, str]:
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Invalid pinfile format: {path}")
    return data


def check_drift(env: Dict[str, str], pinfile_path: str) -> PinResult:
    """Compare current env against a saved pinfile."""
    pinned = load_pinfile(pinfile_path)
    current = pin_env(env)

    drifted = [k for k in pinned if k in current and current[k] != pinned[k]]
    new_keys = [k for k in current if k not in pinned]
    removed_keys = [k for k in pinned if k not in current]
    entries = [PinEntry(key=k, checksum=v) for k, v in current.items()]

    return PinResult(entries=entries, drifted=drifted, new_keys=new_keys, removed_keys=removed_keys)
