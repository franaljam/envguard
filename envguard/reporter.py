"""Format and output diff/validation results for CLI display."""
from typing import Optional
from envguard.differ import DiffResult
from envguard.validator import ValidationResult


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _colored(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_diff_report(result: DiffResult, use_color: bool = True) -> str:
    lines = []
    header = "=== Env Diff Report ==="
    lines.append(_colored(header, ANSI_BOLD, use_color))

    if not result["missing_keys"] and not result["extra_keys"] and not result["changed_values"]:
        lines.append(_colored("No differences found.", ANSI_GREEN, use_color))
        return "\n".join(lines)

    for key in sorted(result["missing_keys"]):
        lines.append(_colored(f"  - MISSING : {key}", ANSI_RED, use_color))

    for key in sorted(result["extra_keys"]):
        lines.append(_colored(f"  + EXTRA   : {key}", ANSI_GREEN, use_color))

    for key, (base_val, cmp_val) in sorted(result["changed_values"].items()):
        lines.append(_colored(f"  ~ CHANGED : {key}", ANSI_YELLOW, use_color))
        lines.append(f"      base : {base_val}")
        lines.append(f"      cmp  : {cmp_val}")

    return "\n".join(lines)


def format_validation_report(result: ValidationResult, use_color: bool = True) -> str:
    lines = []
    header = "=== Env Validation Report ==="
    lines.append(_colored(header, ANSI_BOLD, use_color))

    if result["valid"]:
        lines.append(_colored("All required keys are present and valid.", ANSI_GREEN, use_color))
        return "\n".join(lines)

    for key in sorted(result["missing_keys"]):
        lines.append(_colored(f"  - MISSING  : {key}", ANSI_RED, use_color))

    for key in sorted(result["empty_keys"]):
        lines.append(_colored(f"  ! EMPTY    : {key}", ANSI_YELLOW, use_color))

    return "\n".join(lines)
