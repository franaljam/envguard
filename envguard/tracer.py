"""Trace where each env variable is used across source files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TraceEntry:
    key: str
    file: str
    line: int
    context: str


@dataclass
class TraceResult:
    entries: List[TraceEntry] = field(default_factory=list)
    _index: Dict[str, List[TraceEntry]] = field(default_factory=dict, repr=False)

    def for_key(self, key: str) -> List[TraceEntry]:
        return self._index.get(key, [])

    def found_keys(self) -> List[str]:
        return sorted(self._index.keys())

    def summary(self) -> str:
        if not self.entries:
            return "No usages found."
        lines = [f"{len(self.entries)} usage(s) across {len(self.found_keys())} key(s):"]
        for key in self.found_keys():
            refs = self._index[key]
            lines.append(f"  {key}: {len(refs)} reference(s)")
        return "\n".join(lines)


def _build_pattern(keys: List[str]) -> re.Pattern:
    escaped = [re.escape(k) for k in keys]
    return re.compile(r"(?:os\.environ(?:\.get)?\(?['\"]|\$\{?|getenv\(['\"])(%s)" % "|".join(escaped))


def trace_env(
    env: Dict[str, str],
    search_paths: List[str],
    extensions: Optional[List[str]] = None,
) -> TraceResult:
    if not env:
        return TraceResult()
    exts = set(extensions or [".py", ".sh", ".env", ".yml", ".yaml", ".toml"])
    keys = list(env.keys())
    pattern = _build_pattern(keys)
    entries: List[TraceEntry] = []
    index: Dict[str, List[TraceEntry]] = {}

    for sp in search_paths:
        root = Path(sp)
        paths = root.rglob("*") if root.is_dir() else [root]
        for path in paths:
            if path.is_file() and path.suffix in exts:
                try:
                    text = path.read_text(errors="replace")
                except OSError:
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    for m in pattern.finditer(line):
                        key = m.group(1)
                        entry = TraceEntry(key=key, file=str(path), line=lineno, context=line.strip())
                        entries.append(entry)
                        index.setdefault(key, []).append(entry)

    result = TraceResult(entries=entries)
    result._index = index
    return result
