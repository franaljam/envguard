"""Digest module: compute and compare env file checksums."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class DigestResult:
    digests: Dict[str, str]
    algorithm: str = "sha256"

    def __getitem__(self, key: str) -> str:
        return self.digests[key]

    def __contains__(self, key: str) -> bool:
        return key in self.digests


@dataclass
class DigestComparison:
    matched: Dict[str, str]
    changed: Dict[str, tuple]  # key -> (old, new)
    added: Dict[str, str]
    removed: Dict[str, str]

    @property
    def has_drift(self) -> bool:
        return bool(self.changed or self.added or self.removed)

    def summary(self) -> str:
        parts = []
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        return ", ".join(parts) if parts else "no drift detected"


def _hash(value: str, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    h.update(value.encode())
    return h.hexdigest()


def digest_env(env: Dict[str, str], algorithm: str = "sha256") -> DigestResult:
    digests = {k: _hash(v, algorithm) for k, v in env.items()}
    return DigestResult(digests=digests, algorithm=algorithm)


def compare_digests(old: DigestResult, new: DigestResult) -> DigestComparison:
    matched, changed, added, removed = {}, {}, {}, {}
    for key, digest in old.digests.items():
        if key not in new.digests:
            removed[key] = digest
        elif new.digests[key] == digest:
            matched[key] = digest
        else:
            changed[key] = (digest, new.digests[key])
    for key, digest in new.digests.items():
        if key not in old.digests:
            added[key] = digest
    return DigestComparison(matched=matched, changed=changed, added=added, removed=removed)


def save_digest(result: DigestResult, path: str) -> None:
    with open(path, "w") as f:
        json.dump({"algorithm": result.algorithm, "digests": result.digests}, f, indent=2)


def load_digest(path: str) -> DigestResult:
    with open(path) as f:
        data = json.load(f)
    return DigestResult(digests=data["digests"], algorithm=data.get("algorithm", "sha256"))
