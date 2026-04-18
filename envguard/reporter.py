"""Format reports for diff, validation, audit, redaction, and schema results."""
from __future__ import annotations
import sys
from typing import Dict

from envguard.differ import DiffResult
from envguard.validator import ValidationResult
from envguard.auditor import AuditResult
from envguard.redactor import RedactorConfig
from envguard.schema import SchemaResult


def _colored(text: str, code: str) -> str:
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text


def format_diff_report(result: DiffResult) -> str:
    lines = []
    for k in result.missing:
        lines.append(_colored(f"  - MISSING : {k}", "31"))
    for k in result.extra:
        lines.append(_colored(f"  + EXTRA   : {k}", "32"))
    for k, (a, b) in result.changed.items():
        lines.append(_colored(f"  ~ CHANGED : {k} ({a!r} -> {b!r})", "33"))
    if not lines:
        return _colored("No differences found.", "32")
    return "\n".join(lines)


def format_validation_report(result: ValidationResult) -> str:
    lines = []
    for k in result.missing:
        lines.append(_colored(f"  MISSING   : {k}", "31"))
    for k in result.empty:
        lines.append(_colored(f"  EMPTY     : {k}", "33"))
    if not lines:
        return _colored("Validation passed.", "32")
    return "\n".join(lines)


def format_audit_report(result: AuditResult) -> str:
    lines = []
    for issue in result.issues:
        color = "31" if issue.level == "error" else "33"
        lines.append(_colored(f"  [{issue.level.upper()}] {issue.key}: {issue.message}", color))
    if not lines:
        return _colored("Audit passed.", "32")
    return "\n".join(lines)


def format_redaction_report(config: RedactorConfig, env: Dict[str, str]) -> str:
    redacted = config.redacted_keys(env)
    if not redacted:
        return _colored("No keys redacted.", "32")
    lines = [_colored(f"  REDACTED  : {k}", "33") for k in sorted(redacted)]
    return "\n".join(lines)


def format_schema_report(result: SchemaResult) -> str:
    lines = []
    for v in result.violations:
        color = "31" if v.level == "error" else "33"
        lines.append(_colored(f"  [{v.level.upper()}] {v.key}: {v.message}", color))
    if not lines:
        return _colored("Schema validation passed.", "32")
    return "\n".join(lines)
