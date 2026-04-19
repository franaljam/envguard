"""Key-level diff utilities: find added, removed, and renamed keys between two envs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import difflib


@dataclass
class KeyDiffResult:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    renamed: List[Tuple[str, str]] = field(default_factory=list)  # (old, new)
    common: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.renamed)

    def summary(self) -> str:
        parts = []
        if self.renamed:
            parts.append(f"{len(self.renamed)} renamed")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if not parts:
            return "No key changes detected."
        return "Key changes: " + ", ".join(parts) + "."


def _similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def diff_keys(
    base: Dict[str, str],
    target: Dict[str, str],
    detect_renames: bool = True,
    rename_threshold: float = 0.7,
) -> KeyDiffResult:
    base_keys = set(base)
    target_keys = set(target)

    common = sorted(base_keys & target_keys)
    only_base = sorted(base_keys - target_keys)
    only_target = sorted(target_keys - base_keys)

    renamed: List[Tuple[str, str]] = []

    if detect_renames and only_base and only_target:
        matched_base: set = set()
        matched_target: set = set()
        candidates: List[Tuple[float, str, str]] = []
        for ob in only_base:
            for ot in only_target:
                score = _similarity(ob, ot)
                if score >= rename_threshold:
                    candidates.append((score, ob, ot))
        candidates.sort(reverse=True)
        for score, ob, ot in candidates:
            if ob not in matched_base and ot not in matched_target:
                renamed.append((ob, ot))
                matched_base.add(ob)
                matched_target.add(ot)
        only_base = [k for k in only_base if k not in matched_base]
        only_target = [k for k in only_target if k not in matched_target]

    return KeyDiffResult(
        added=only_target,
        removed=only_base,
        renamed=renamed,
        common=common,
    )
