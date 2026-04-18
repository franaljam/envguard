"""Profile .env files to produce statistics and summaries."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProfileResult:
    total: int
    empty: int
    commented: int
    sensitive_keys: List[str]
    longest_key: str
    longest_value_key: str
    duplicate_values: Dict[str, List[str]]

    def summary(self) -> str:
        lines = [
            f"Total variables : {self.total}",
            f"Empty values    : {self.empty}",
            f"Sensitive keys  : {len(self.sensitive_keys)}",
            f"Longest key     : {self.longest_key}",
            f"Longest value   : {self.longest_value_key}",
        ]
        if self.duplicate_values:
            lines.append("Duplicate values:")
            for val, keys in self.duplicate_values.items():
                lines.append(f"  {val!r} -> {', '.join(keys)}")
        return "\n".join(lines)


_SENSITIVE_PATTERNS = ("SECRET", "PASSWORD", "PASSWD", "TOKEN", "KEY", "AUTH", "PRIVATE")


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(p in upper for p in _SENSITIVE_PATTERNS)


def profile_env(env: Dict[str, str]) -> ProfileResult:
    if not env:
        return ProfileResult(
            total=0, empty=0, commented=0, sensitive_keys=[],
            longest_key="", longest_value_key="", duplicate_values={}
        )

    empty = sum(1 for v in env.values() if v == "")
    sensitive = [k for k in env if _is_sensitive(k)]
    longest_key = max(env.keys(), key=len)
    longest_value_key = max(env.keys(), key=lambda k: len(env[k]))

    value_map: Dict[str, List[str]] = {}
    for k, v in env.items():
        if v:
            value_map.setdefault(v, []).append(k)
    duplicate_values = {v: keys for v, keys in value_map.items() if len(keys) > 1}

    return ProfileResult(
        total=len(env),
        empty=empty,
        commented=0,
        sensitive_keys=sensitive,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
        duplicate_values=duplicate_values,
    )
