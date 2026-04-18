"""Variable interpolation for .env files."""
from __future__ import annotations

import re
from typing import Dict, Optional

_VAR_PATTERN = re.compile(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)')


class InterpolationError(Exception):
    """Raised when a variable reference cannot be resolved."""


def interpolate(value: str, context: Dict[str, str], *, strict: bool = True) -> str:
    """Replace $VAR and ${VAR} references in *value* using *context*.

    Args:
        value: The raw string that may contain variable references.
        context: Mapping of variable names to their resolved values.
        strict: If True, raise InterpolationError for missing variables.
                If False, leave unresolved references as-is.

    Returns:
        The interpolated string.
    """
    def _replace(match: re.Match) -> str:
        name = match.group(1) or match.group(2)
        if name in context:
            return context[name]
        if strict:
            raise InterpolationError(f"Undefined variable: '{name}'")
        return match.group(0)

    return _VAR_PATTERN.sub(_replace, value)


def interpolate_env(
    env: Dict[str, str],
    extra: Optional[Dict[str, str]] = None,
    *,
    strict: bool = True,
) -> Dict[str, str]:
    """Interpolate all values in *env*, resolving references within the same
    mapping and optionally against *extra* (e.g. OS environment variables).

    Variables are resolved in definition order; forward references are
    supported because the full *env* mapping is used as context.

    Args:
        env: Parsed environment mapping.
        extra: Additional variables available for resolution (not returned).
        strict: Passed through to :func:`interpolate`.

    Returns:
        New dict with all values interpolated.
    """
    context: Dict[str, str] = {}
    if extra:
        context.update(extra)
    context.update(env)

    return {key: interpolate(value, context, strict=strict) for key, value in env.items()}
