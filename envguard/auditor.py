"""Audit .env files for common security and quality issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

SECRET_PATTERNS = ("password", "secret", "token", "key", "api", "private")
WEAK_VALUES = {"changeme", "password", "secret", "1234", "test", "example", "placeholder"}


@dataclass
class AuditIssue:
    key: str
    message: str
    severity: str  # "warn" | "error"


@dataclass
class AuditResult:
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "warn"]

    def summary(self) -> str:
        if not self.has_issues:
            return "No audit issues found."
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        return "Audit: " + ", ".join(parts) + "."


def _looks_like_secret(key: str) -> bool:
    lower = key.lower()
    return any(p in lower for p in SECRET_PATTERNS)


def audit_env(variables: Dict[str, str], check_weak: bool = True) -> AuditResult:
    """Audit a parsed env dict for security and quality issues."""
    result = AuditResult()
    for key, value in variables.items():
        if value == "":
            result.issues.append(AuditIssue(key, "Variable is set but empty.", "warn"))
            continue
        if _looks_like_secret(key):
            if check_weak and value.lower() in WEAK_VALUES:
                result.issues.append(
                    AuditIssue(key, f"Weak or placeholder value detected: '{value}'.", "error")
                )
            if len(value) < 8:
                result.issues.append(
                    AuditIssue(key, "Secret-like variable has a very short value (< 8 chars).", "warn")
                )
    return result
