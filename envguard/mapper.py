"""mapper.py — build a key-to-files mapping across multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

from envguard.parser import parse_env_file


@dataclass
class MapEntry:
    key: str
    files: List[str] = field(default_factory=list)
    values: Dict[str, str] = field(default_factory=dict)  # file -> value

    def is_consistent(self) -> bool:
        """Return True when every file that defines this key has the same value."""
        return len(set(self.values.values())) <= 1

    def appears_in(self, path: str) -> bool:
        return path in self.files


@dataclass
class MapResult:
    _entries: Dict[str, MapEntry] = field(default_factory=dict)

    # --- dict-like helpers --------------------------------------------------

    def __contains__(self, key: str) -> bool:
        return key in self._entries

    def __getitem__(self, key: str) -> MapEntry:
        return self._entries[key]

    def keys(self) -> List[str]:
        return sorted(self._entries.keys())

    # --- derived views -------------------------------------------------------

    def inconsistent_keys(self) -> List[str]:
        """Keys whose value differs across at least two files."""
        return sorted(k for k, e in self._entries.items() if not e.is_consistent())

    def unique_to(self, path: str) -> List[str]:
        """Keys that appear *only* in *path*."""
        return sorted(
            k for k, e in self._entries.items()
            if e.files == [path]
        )

    def summary(self) -> str:
        total = len(self._entries)
        inconsistent = len(self.inconsistent_keys())
        return (
            f"MapResult: {total} unique key(s) across "
            f"{len(self._file_set())} file(s); "
            f"{inconsistent} inconsistent"
        )

    def _file_set(self) -> set:
        files: set = set()
        for e in self._entries.values():
            files.update(e.files)
        return files


def map_envs(paths: Sequence[str | Path]) -> MapResult:
    """Parse each file and build a cross-file key map."""
    result = MapResult()
    for raw_path in paths:
        path = str(raw_path)
        env = parse_env_file(path)
        for key, value in env.items():
            if key not in result:
                result._entries[key] = MapEntry(key=key)
            entry = result._entries[key]
            if path not in entry.files:
                entry.files.append(path)
            entry.values[path] = value
    return result
