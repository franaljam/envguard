"""Redact sensitive values from env dicts before logging or display."""
from __future__ import annotations

import re
from typing import Dict, List

DEFAULT_PATTERNS: List[str] = [
    r"password",
    r"secret",
    r"token",
    r"api[_]?key",
    r"private[_]?key",
    r"auth",
    r"credential",
]

REDACT_PLACEHOLDER = "***REDACTED***"


class RedactorConfig:
    def __init__(self, patterns: List[str] | None = None, placeholder: str = REDACT_PLACEHOLDER):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in (patterns or DEFAULT_PATTERNS)]
        self.placeholder = placeholder


def _is_sensitive(key: str, config: RedactorConfig) -> bool:
    return any(p.search(key) for p in config.patterns)


def redact_env(env: Dict[str, str], config: RedactorConfig | None = None) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by the placeholder."""
    cfg = config or RedactorConfig()
    return {k: (cfg.placeholder if _is_sensitive(k, cfg) else v) for k, v in env.items()}


def redacted_keys(env: Dict[str, str], config: RedactorConfig | None = None) -> List[str]:
    """Return list of keys whose values would be redacted."""
    cfg = config or RedactorConfig()
    return [k for k in env if _is_sensitive(k, cfg)]
