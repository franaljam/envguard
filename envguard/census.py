"""census.py — count and categorise keys in a .env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_FRAGMENTS = ("secret", "password", "passwd", "token", "key", "api", "auth", "private")
_BOOL_VALUES = {"true", "false", "1", "0", "yes", "no", "on", "off"}


@dataclass
class CensusResult:
    total: int
    empty: List[str]
    sensitive: List[str]
    boolean: List[str]
    numeric: List[str]
    by_prefix: Dict[str, List[str]]

    def summary(self) -> str:
        lines = [
            f"Total keys   : {self.total}",
            f"Empty        : {len(self.empty)}",
            f"Sensitive    : {len(self.sensitive)}",
            f"Boolean      : {len(self.boolean)}",
            f"Numeric      : {len(self.numeric)}",
            f"Prefix groups: {len(self.by_prefix)}",
        ]
        return "\n".join(lines)


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(frag in lower for frag in _SENSITIVE_FRAGMENTS)


def _is_boolean(value: str) -> bool:
    return value.strip().lower() in _BOOL_VALUES


def _is_numeric(value: str) -> bool:
    try:
        float(value.strip())
        return True
    except ValueError:
        return False


def _prefix(key: str) -> str | None:
    if "_" in key:
        return key.split("_", 1)[0]
    return None


def census_env(env: Dict[str, str]) -> CensusResult:
    """Analyse *env* and return a :class:`CensusResult`."""
    empty: List[str] = []
    sensitive: List[str] = []
    boolean: List[str] = []
    numeric: List[str] = []
    by_prefix: Dict[str, List[str]] = {}

    for key, value in env.items():
        if value == "":
            empty.append(key)
        if _is_sensitive(key):
            sensitive.append(key)
        if value != "" and _is_boolean(value):
            boolean.append(key)
        if value != "" and _is_numeric(value):
            numeric.append(key)
        pfx = _prefix(key)
        if pfx:
            by_prefix.setdefault(pfx, []).append(key)

    return CensusResult(
        total=len(env),
        empty=empty,
        sensitive=sensitive,
        boolean=boolean,
        numeric=numeric,
        by_prefix=by_prefix,
    )
