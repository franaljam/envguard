"""Rewrite .env file content by applying key-value updates in-place."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class RewriteResult:
    original: Dict[str, str]
    rewritten: Dict[str, str]
    updated: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    def changed(self) -> bool:
        return bool(self.updated or self.added or self.removed)

    def summary(self) -> str:
        parts = []
        if self.updated:
            parts.append(f"{len(self.updated)} updated")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        return ", ".join(parts) if parts else "no changes"


def rewrite_env(
    env: Dict[str, str],
    *,
    set_keys: Optional[Dict[str, str]] = None,
    remove_keys: Optional[List[str]] = None,
    rename_keys: Optional[Dict[str, str]] = None,
) -> RewriteResult:
    """Return a new env dict with the requested mutations applied.

    Args:
        env: The source environment mapping.
        set_keys: Keys to add or overwrite with the given values.
        remove_keys: Keys to delete from the result.
        rename_keys: Mapping of old_key -> new_key to rename.
    """
    result: Dict[str, str] = dict(env)
    updated: List[str] = []
    added: List[str] = []
    removed: List[str] = []

    for old_key, new_key in (rename_keys or {}).items():
        if old_key in result:
            result[new_key] = result.pop(old_key)
            updated.append(new_key)

    for key, value in (set_keys or {}).items():
        if key in result:
            if result[key] != value:
                updated.append(key)
        else:
            added.append(key)
        result[key] = value

    for key in remove_keys or []:
        if key in result:
            del result[key]
            removed.append(key)

    return RewriteResult(
        original=dict(env),
        rewritten=result,
        updated=updated,
        added=added,
        removed=removed,
    )


def write_env_file(path: Path, env: Dict[str, str]) -> None:
    """Serialise *env* to *path* in KEY=VALUE format."""
    lines = [f"{k}={v}\n" for k, v in env.items()]
    path.write_text("".join(lines), encoding="utf-8")
