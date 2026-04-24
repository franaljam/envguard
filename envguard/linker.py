"""linker.py – cross-file key linking: discover which keys appear in multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class LinkEntry:
    key: str
    files: List[str]
    values: Dict[str, str]  # filename -> value

    @property
    def is_shared(self) -> bool:
        return len(self.files) > 1

    @property
    def is_consistent(self) -> bool:
        return len(set(self.values.values())) <= 1


@dataclass
class LinkResult:
    entries: Dict[str, LinkEntry] = field(default_factory=dict)

    def __contains__(self, key: str) -> bool:
        return key in self.entries

    def shared_keys(self) -> List[str]:
        return [k for k, e in self.entries.items() if e.is_shared]

    def inconsistent_keys(self) -> List[str]:
        return [k for k, e in self.entries.items() if e.is_shared and not e.is_consistent]

    def summary(self) -> str:
        total = len(self.entries)
        shared = len(self.shared_keys())
        inconsistent = len(self.inconsistent_keys())
        return (
            f"{total} unique key(s) across all files; "
            f"{shared} shared; {inconsistent} inconsistent."
        )


def link_envs(named_envs: Dict[str, Dict[str, str]]) -> LinkResult:
    """Build a LinkResult mapping each key to the files and values it appears in."""
    aggregated: Dict[str, LinkEntry] = {}

    for filename, env in named_envs.items():
        for key, value in env.items():
            if key not in aggregated:
                aggregated[key] = LinkEntry(key=key, files=[], values={})
            aggregated[key].files.append(filename)
            aggregated[key].values[filename] = value

    return LinkResult(entries=aggregated)
