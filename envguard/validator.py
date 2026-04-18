"""Validate .env files against a required keys schema."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    invalid_values: Dict[str, str] = field(default_factory=dict)  # key -> reason

    @property
    def is_valid(self) -> bool:
        return not self.missing_required and not self.invalid_values

    def summary(self) -> str:
        lines = []
        if self.missing_required:
            lines.append("Missing required keys:")
            for key in sorted(self.missing_required):
                lines.append(f"  - {key}")
        if self.invalid_values:
            lines.append("Invalid values:")
            for key, reason in sorted(self.invalid_values.items()):
                lines.append(f"  - {key}: {reason}")
        if not lines:
            return "All required keys present and valid."
        return "\n".join(lines)


def validate_env(
    env: Dict[str, str],
    required_keys: Optional[List[str]] = None,
    non_empty_keys: Optional[List[str]] = None,
) -> ValidationResult:
    """Validate an env dict against required keys and non-empty constraints.

    Args:
        env: Parsed environment variables.
        required_keys: Keys that must be present (can be empty string).
        non_empty_keys: Keys that must be present AND non-empty.

    Returns:
        ValidationResult with any issues found.
    """
    result = ValidationResult()
    required: Set[str] = set(required_keys or [])
    non_empty: Set[str] = set(non_empty_keys or [])

    # non_empty keys implicitly required
    required |= non_empty

    for key in sorted(required):
        if key not in env:
            result.missing_required.append(key)
        elif key in non_empty and env[key].strip() == "":
            result.invalid_values[key] = "must not be empty"

    return result
