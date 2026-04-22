"""Extract a subset of keys from an env dict into a new dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class ExtractResult:
    extracted: Dict[str, str]
    missing: List[str]
    source_keys: List[str]

    def found(self) -> List[str]:
        return list(self.extracted.keys())

    def has_missing(self) -> bool:
        return len(self.missing) > 0

    def summary(self) -> str:
        lines = [
            f"Extracted : {len(self.extracted)}",
            f"Missing   : {len(self.missing)}",
        ]
        if self.missing:
            lines.append("Missing keys: " + ", ".join(self.missing))
        return "\n".join(lines)


def extract_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    strip_prefix: bool = False,
) -> ExtractResult:
    """Extract keys from *env* matching any of the supplied criteria.

    Parameters
    ----------
    env:          Source environment dictionary.
    keys:         Exact key names to extract.
    prefix:       Extract keys that start with this prefix.
    pattern:      Extract keys matching this regex pattern.
    strip_prefix: When *prefix* is given, remove the prefix from extracted keys.
    """
    compiled = re.compile(pattern) if pattern else None
    source_keys = list(env.keys())
    extracted: Dict[str, str] = {}
    missing: List[str] = []

    # Collect by prefix / pattern first
    for k, v in env.items():
        matched = False
        if prefix and k.startswith(prefix):
            matched = True
        if compiled and compiled.search(k):
            matched = True
        if matched:
            out_key = k[len(prefix):] if (strip_prefix and prefix and k.startswith(prefix)) else k
            extracted[out_key] = v

    # Collect explicit keys (these are checked for missing)
    if keys:
        for k in keys:
            if k in env:
                if k not in extracted:
                    extracted[k] = env[k]
            else:
                missing.append(k)

    # If no criteria provided, return full copy
    if not keys and prefix is None and pattern is None:
        extracted = dict(env)

    return ExtractResult(
        extracted=extracted,
        missing=missing,
        source_keys=source_keys,
    )
