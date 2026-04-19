"""Watch a .env file for changes and report drift from a baseline."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


@dataclass
class WatchEvent:
    path: str
    previous_hash: str
    current_hash: str
    changed_keys: list[str]

    @property
    def has_changes(self) -> bool:
        return self.previous_hash != self.current_hash


@dataclass
class WatchResult:
    events: list[WatchEvent] = field(default_factory=list)

    def total_events(self) -> int:
        return len(self.events)

    def summary(self) -> str:
        if not self.events:
            return "No changes detected."
        return f"{len(self.events)} change event(s) recorded."


def _file_hash(path: str) -> str:
    content = Path(path).read_bytes()
    return hashlib.sha256(content).hexdigest()


def _parse_keys(path: str) -> dict[str, str]:
    from envguard.parser import parse_env_file
    try:
        return parse_env_file(path)
    except Exception:
        return {}


def _changed_keys(old: dict[str, str], new: dict[str, str]) -> list[str]:
    all_keys = set(old) | set(new)
    return sorted(k for k in all_keys if old.get(k) != new.get(k))


def watch_env(
    path: str,
    duration: float = 5.0,
    interval: float = 1.0,
    on_change: Optional[Callable[[WatchEvent], None]] = None,
) -> WatchResult:
    """Poll *path* for changes for up to *duration* seconds."""
    result = WatchResult()
    baseline_hash = _file_hash(path)
    baseline_keys = _parse_keys(path)
    deadline = time.monotonic() + duration

    while time.monotonic() < deadline:
        time.sleep(interval)
        current_hash = _file_hash(path)
        if current_hash != baseline_hash:
            current_keys = _parse_keys(path)
            event = WatchEvent(
                path=path,
                previous_hash=baseline_hash,
                current_hash=current_hash,
                changed_keys=_changed_keys(baseline_keys, current_keys),
            )
            result.events.append(event)
            if on_change:
                on_change(event)
            baseline_hash = current_hash
            baseline_keys = current_keys

    return result
