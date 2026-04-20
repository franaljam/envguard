"""Dependency graph builder for .env variable references."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set
import re

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass(frozen=True)
class GraphResult:
    nodes: FrozenSet[str]
    edges: Dict[str, List[str]]  # key -> keys it references
    cycles: List[List[str]]

    def has_cycles(self) -> bool:
        return bool(self.cycles)

    def dependencies_of(self, key: str) -> List[str]:
        return self.edges.get(key, [])

    def summary(self) -> str:
        parts = [f"nodes={len(self.nodes)}", f"edges={sum(len(v) for v in self.edges.values())}"]
        if self.cycles:
            parts.append(f"cycles={len(self.cycles)}")
        return ", ".join(parts)


def _extract_refs(value: str) -> List[str]:
    refs = []
    for m in _REF_RE.finditer(value):
        refs.append(m.group(1) or m.group(2))
    return refs


def _detect_cycles(edges: Dict[str, List[str]]) -> List[List[str]]:
    cycles: List[List[str]] = []
    visited: Set[str] = set()
    path: List[str] = []

    def dfs(node: str) -> None:
        if node in path:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        for neighbour in edges.get(node, []):
            dfs(neighbour)
        path.pop()

    for key in edges:
        dfs(key)
    return cycles


def build_graph(env: Dict[str, str]) -> GraphResult:
    """Build a reference dependency graph from an env dict."""
    edges: Dict[str, List[str]] = {}
    for key, value in env.items():
        refs = [r for r in _extract_refs(value) if r in env and r != key]
        if refs:
            edges[key] = refs
    cycles = _detect_cycles(edges)
    return GraphResult(
        nodes=frozenset(env.keys()),
        edges=edges,
        cycles=cycles,
    )
