"""enforcer.py – enforce a set of rules against a parsed env dict.

Rules are expressed as a list of dicts (or loaded from JSON/YAML via
schema_loader).  Each rule has:
  key      : str           – the env key to check
  op       : str           – one of: required, forbidden, equals, not_equals,
                             matches, min_length, max_length
  value    : str | None    – operand for equals / not_equals / matches
  length   : int | None    – operand for min_length / max_length
  severity : str           – 'error' (default) or 'warning'
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnforceViolation:
    key: str
    op: str
    message: str
    severity: str = "error"  # 'error' | 'warning'


@dataclass
class EnforceResult:
    violations: List[EnforceViolation] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)

    @property
    def has_warnings(self) -> bool:
        return any(v.severity == "warning" for v in self.violations)

    def errors(self) -> List[EnforceViolation]:
        return [v for v in self.violations if v.severity == "error"]

    def warnings(self) -> List[EnforceViolation]:
        return [v for v in self.violations if v.severity == "warning"]

    def summary(self) -> str:
        if not self.violations:
            return "All rules passed."
        parts = []
        if self.errors():
            parts.append(f"{len(self.errors())} error(s)")
        if self.warnings():
            parts.append(f"{len(self.warnings())} warning(s)")
        return "Enforcement failed: " + ", ".join(parts) + "."


def enforce_env(
    env: Dict[str, str],
    rules: List[Dict],
) -> EnforceResult:
    """Apply *rules* to *env* and return an :class:`EnforceResult`."""
    result = EnforceResult()

    for rule in rules:
        key: str = rule["key"]
        op: str = rule["op"]
        severity: str = rule.get("severity", "error")
        present = key in env
        val = env.get(key, "")

        def _add(msg: str) -> None:
            result.violations.append(EnforceViolation(key=key, op=op, message=msg, severity=severity))

        if op == "required":
            if not present:
                _add(f"'{key}' is required but missing.")
        elif op == "forbidden":
            if present:
                _add(f"'{key}' is forbidden but present.")
        elif op == "equals":
            expected = rule.get("value", "")
            if present and val != expected:
                _add(f"'{key}' must equal '{expected}', got '{val}'.")
        elif op == "not_equals":
            forbidden_val = rule.get("value", "")
            if present and val == forbidden_val:
                _add(f"'{key}' must not equal '{forbidden_val}'.")
        elif op == "matches":
            pattern = rule.get("value", "")
            if present and not re.search(pattern, val):
                _add(f"'{key}' value '{val}' does not match pattern '{pattern}'.")
        elif op == "min_length":
            length = int(rule.get("length", 0))
            if present and len(val) < length:
                _add(f"'{key}' must be at least {length} chars (got {len(val)}).")
        elif op == "max_length":
            length = int(rule.get("length", 0))
            if present and len(val) > length:
                _add(f"'{key}' must be at most {length} chars (got {len(val)}).")

    return result
