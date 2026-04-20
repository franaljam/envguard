"""Inspector: summarise key-level metadata for a .env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_SENSITIVE_RE = re.compile(
    r"(secret|password|passwd|token|api[_-]?key|private|auth|credential)",
    re.IGNORECASE,
)


@dataclass
class KeyInfo:
    key: str
    value: str
    length: int
    is_empty: bool
    is_sensitive: bool
    has_whitespace: bool
    is_numeric: bool
    is_boolean: bool


@dataclass
class InspectResult:
    entries: List[KeyInfo] = field(default_factory=list)

    def for_key(self, key: str) -> Optional[KeyInfo]:
        for e in self.entries:
            if e.key == key:
                return e
        return None

    @property
    def sensitive_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_sensitive]

    @property
    def empty_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_empty]

    def summary(self) -> str:
        total = len(self.entries)
        sensitive = len(self.sensitive_keys)
        empty = len(self.empty_keys)
        return (
            f"Inspected {total} key(s): "
            f"{sensitive} sensitive, {empty} empty."
        )


def _is_boolean(value: str) -> bool:
    return value.lower() in {"true", "false", "yes", "no", "1", "0"}


def inspect_env(env: Dict[str, str]) -> InspectResult:
    """Return per-key metadata for every entry in *env*."""
    entries: List[KeyInfo] = []
    for key, value in env.items():
        entries.append(
            KeyInfo(
                key=key,
                value=value,
                length=len(value),
                is_empty=value == "",
                is_sensitive=bool(_SENSITIVE_RE.search(key)),
                has_whitespace=value != value.strip(),
                is_numeric=value.lstrip("-").replace(".", "", 1).isdigit()
                if value
                else False,
                is_boolean=_is_boolean(value) if value else False,
            )
        )
    return InspectResult(entries=entries)
