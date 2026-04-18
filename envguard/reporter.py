"""Format diff, validation, audit, and redaction reports for CLI output."""
from __future__ import annotations

import sys
from typing import Dict

from envguard.differ import DiffResult
from envguard.validator import ValidationResult
from envguard.auditor import AuditResult
from envguard.redactor import RedactorConfig, redact_env, redacted_keys


def _colored(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def format_diff_report(result: DiffResult) -> str:
    lines = []
    for k in sorted(result.missing_keys):
        lines.append(_colored(f"  - MISSING : {k}", "31"))
    for k in sorted(result.extra_keys):
        lines.append(_colored(f"  + EXTRA   : {k}", "33"))
    for k, (a, b) in sorted(result.changed_values.items()):
        lines.append(_colored(f"  ~ CHANGED : {k}  ({a!r} -> {b!r})", "36"))
    if not lines:
        return _colored("No differences found.", "32")
    return "\n".join(lines)


def format_validation_report(result: ValidationResult) -> str:
    if result.is_valid:
        return _colored("Validation passed.", "32")
    lines = [_colored("Validation failed:", "31")]
    for k in sorted(result.missing_keys):
        lines.append(f"  missing required key: {k}")
    for k in sorted(result.empty_keys):
        lines.append(f"  empty value for key : {k}")
    return "\n".join(lines)


def format_audit_report(result: AuditResult) -> str:
    if not result.has_issues:
        return _colored("Audit passed — no issues found.", "32")
    lines = []
    for issue in result.issues:
        colour = "31" if issue.severity == "error" else "33"
        lines.append(_colored(f"  [{issue.severity.upper()}] {issue.key}: {issue.message}", colour))
    return "\n".join(lines)


def format_redaction_report(env: Dict[str, str], config: RedactorConfig | None = None) -> str:
    """Return a human-readable summary of which keys will be redacted."""
    keys = redacted_keys(env, config)
    if not keys:
        return _colored("No sensitive keys detected.", "32")
    lines = [_colored(f"Redacting {len(keys)} sensitive key(s):", "33")]
    for k in sorted(keys):
        lines.append(f"  ~ {k}")
    return "\n".join(lines)
