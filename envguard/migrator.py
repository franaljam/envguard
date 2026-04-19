"""Migrate .env files by applying a set of rename, remove, and add operations."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MigrationResult:
    original: Dict[str, str]
    migrated: Dict[str, str]
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    renamed: List[tuple] = field(default_factory=list)

    def changed(self) -> bool:
        return bool(self.added or self.removed or self.renamed)

    def summary(self) -> str:
        parts = []
        if self.renamed:
            parts.append(f"{len(self.renamed)} renamed")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        return ", ".join(parts) if parts else "no changes"


def migrate_env(
    env: Dict[str, str],
    renames: Optional[Dict[str, str]] = None,
    removals: Optional[List[str]] = None,
    additions: Optional[Dict[str, str]] = None,
) -> MigrationResult:
    """Apply migration operations to an env dict."""
    renames = renames or {}
    removals = removals or []
    additions = additions or {}

    result: Dict[str, str] = dict(env)
    renamed_pairs: List[tuple] = []
    removed_keys: List[str] = []
    added_keys: List[str] = []

    for old_key, new_key in renames.items():
        if old_key in result:
            result[new_key] = result.pop(old_key)
            renamed_pairs.append((old_key, new_key))

    for key in removals:
        if key in result:
            del result[key]
            removed_keys.append(key)

    for key, value in additions.items():
        if key not in result:
            result[key] = value
            added_keys.append(key)

    return MigrationResult(
        original=dict(env),
        migrated=result,
        added=added_keys,
        removed=removed_keys,
        renamed=renamed_pairs,
    )
