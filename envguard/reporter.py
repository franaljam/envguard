"""Format diff and validation results for terminal output."""
from __future__ import annotations
import sys
from envguard.differ import DiffResult
from envguard.validator import ValidationResult
from envguard.auditor import AuditResult


def _colored(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def format_diff_report(result: DiffResult) -> str:
    lines = []
    for key in sorted(result.missing_keys):
        lines.append(_colored(f"  - MISSING  {key}", "31"))
    for key in sorted(result.extra_keys):
        lines.append(_colored(f"  + EXTRA    {key}", "33"))
    for key, (base, other) in sorted(result.changed_values.items()):
        lines.append(_colored(f"  ~ CHANGED  {key}: '{base}' -> '{other}'", "36"))
    if not lines:
        return _colored("Environments match.", "32")
    return "\n".join(lines)


def format_validation_report(result: ValidationResult) -> str:
    lines = []
    for key in sorted(result.missing_keys):
        lines.append(_colored(f"  MISSING   {key}", "31"))
    for key in sorted(result.empty_keys):
        lines.append(_colored(f"  EMPTY     {key}", "33"))
    if not lines:
        return _colored("Validation passed.", "32")
    return "\n".join(lines)


def format_audit_report(result: AuditResult) -> str:
    if not result.has_issues:
        return _colored("Audit passed. No issues found.", "32")
    lines = [result.summary()]
    for issue in result.issues:
        color = "31" if issue.severity == "error" else "33"
        label = issue.severity.upper()
        lines.append(_colored(f"  [{label}] {issue.key}: {issue.message}", color))
    return "\n".join(lines)
