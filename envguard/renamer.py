"""Rename keys in an env dict with optional dry-run support."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RenameResult:
    original: Dict[str, str]
    renamed: Dict[str, str]
    applied: List[tuple]  # (old_key, new_key)
    skipped: List[str]    # old keys not found

    def changed(self) -> bool:
        return bool(self.applied)

    def summary(self) -> str:
        lines = []
        for old, new in self.applied:
            lines.append(f"  {old} -> {new}")
        for key in self.skipped:
            lines.append(f"  (skipped, not found) {key}")
        if not lines:
            return "No renames applied."
        return "\n".join(lines)


def rename_env(
    env: Dict[str, str],
    renames: Dict[str, str],
) -> RenameResult:
    """Return a new env dict with keys renamed according to the mapping.

    Args:
        env: Original environment variables.
        renames: Mapping of old_key -> new_key.

    Returns:
        RenameResult with the updated dict and metadata.
    """
    result: Dict[str, str] = {}
    applied: List[tuple] = []
    skipped: List[str] = []
    rename_index = dict(renames)

    for key, value in env.items():
        if key in rename_index:
            new_key = rename_index.pop(key)
            result[new_key] = value
            applied.append((key, new_key))
        else:
            result[key] = value

    # Any remaining entries in rename_index were not found
    for old_key in rename_index:
        skipped.append(old_key)

    return RenameResult(
        original=dict(env),
        renamed=result,
        applied=applied,
        skipped=skipped,
    )
