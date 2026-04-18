"""Format reports for diff, validation, audit, redaction, and lint results."""
import sys
from envguard.differ import DiffResult
from envguard.validator import ValidationResult
from envguard.auditor import AuditResult
from envguard.redactor import RedactorConfig
from envguard.linter import LintResult
from typing import Dict


def _colored(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def format_diff_report(result: DiffResult) -> str:
    lines = []
    for k in result.missing:
        lines.append(_colored(f"- MISSING : {k}", "31"))
    for k in result.extra:
        lines.append(_colored(f"+ EXTRA   : {k}", "32"))
    for k, (a, b) in result.changed.items():
        lines.append(_colored(f"~ CHANGED : {k} ({a!r} -> {b!r})", "33"))
    if not lines:
        lines.append(_colored("No differences found.", "32"))
    return "\n".join(lines)


def format_validation_report(result: ValidationResult) -> str:
    lines = []
    for k in result.missing:
        lines.append(_colored(f"MISSING  : {k}", "31"))
    for k in result.empty:
        lines.append(_colored(f"EMPTY    : {k}", "33"))
    if not lines:
        lines.append(_colored("Validation passed.", "32"))
    return "\n".join(lines)


def format_audit_report(result: AuditResult) -> str:
    lines = []
    for issue in result.issues:
        color = "31" if issue.severity == "error" else "33"
        lines.append(_colored(f"[{issue.severity.upper()}] {issue.key}: {issue.message}", color))
    if not lines:
        lines.append(_colored("Audit passed.", "32"))
    return "\n".join(lines)


def format_redaction_report(redacted: Dict[str, str], redacted_keys: list) -> str:
    lines = [f"Redacted {len(redacted_keys)} key(s):"]
    for k in redacted_keys:
        lines.append(_colored(f"  {k}: {redacted[k]}", "33"))
    if not redacted_keys:
        lines = [_colored("No sensitive keys found.", "32")]
    return "\n".join(lines)


def format_lint_report(result: LintResult) -> str:
    lines = []
    for issue in result.issues:
        color = "31" if issue.severity == "error" else "33"
        lines.append(_colored(f"[{issue.severity.upper()}] {issue.key}: {issue.message}", color))
    if not lines:
        lines.append(_colored("Lint passed.", "32"))
    lines.append(result.summary())
    return "\n".join(lines)
