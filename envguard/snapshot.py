"""Snapshot support: save and load env variable snapshots for later diffing."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


class SnapshotError(Exception):
    pass


@dataclass
class Snapshot:
    label: str
    captured_at: str
    variables: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "captured_at": self.captured_at,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            label=data["label"],
            captured_at=data["captured_at"],
            variables=data.get("variables", {}),
        )


def create_snapshot(variables: Dict[str, str], label: str) -> Snapshot:
    """Create a snapshot from a parsed env dict."""
    now = datetime.now(timezone.utc).isoformat()
    return Snapshot(label=label, captured_at=now, variables=dict(variables))


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(snapshot.to_dict(), fh, indent=2)
    except OSError as exc:
        raise SnapshotError(f"Could not write snapshot to {path!r}: {exc}") from exc


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    if not os.path.exists(path):
        raise SnapshotError(f"Snapshot file not found: {path!r}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return Snapshot.from_dict(data)
    except (json.JSONDecodeError, KeyError) as exc:
        raise SnapshotError(f"Invalid snapshot file {path!r}: {exc}") from exc
