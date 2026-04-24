"""envguard.indexer — build a searchable index of keys across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envguard.parser import parse_env_file


@dataclass
class IndexEntry:
    key: str
    files: List[str] = field(default_factory=list)
    values: Dict[str, str] = field(default_factory=dict)  # file -> value

    def appears_in(self, path: str) -> bool:
        return path in self.files

    def is_consistent(self) -> bool:
        """Return True if the key has the same value in every file it appears in."""
        return len(set(self.values.values())) <= 1


@dataclass
class IndexResult:
    entries: Dict[str, IndexEntry] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)

    def __contains__(self, key: str) -> bool:
        return key in self.entries

    def __getitem__(self, key: str) -> IndexEntry:
        return self.entries[key]

    def keys_in(self, path: str) -> List[str]:
        """Return all keys that appear in the given file path."""
        return [k for k, e in self.entries.items() if e.appears_in(path)]

    def inconsistent_keys(self) -> List[str]:
        """Return keys whose value differs across files."""
        return [k for k, e in self.entries.items() if not e.is_consistent()]

    def unique_to(self, path: str) -> List[str]:
        """Return keys that appear only in the given file."""
        return [k for k, e in self.entries.items() if e.files == [path]]

    def summary(self) -> str:
        total = len(self.entries)
        inconsistent = len(self.inconsistent_keys())
        return (
            f"{total} unique key(s) across {len(self.sources)} file(s); "
            f"{inconsistent} inconsistent"
        )


def index_env_files(paths: List[str], base_dir: Optional[str] = None) -> IndexResult:
    """Parse each file and build a combined key index."""
    result = IndexResult()

    for raw_path in paths:
        p = Path(raw_path)
        if base_dir:
            label = str(p.relative_to(base_dir))
        else:
            label = str(p)

        env = parse_env_file(str(p))
        result.sources.append(label)

        for key, value in env.items():
            if key not in result.entries:
                result.entries[key] = IndexEntry(key=key)
            entry = result.entries[key]
            entry.files.append(label)
            entry.values[label] = value

    return result
