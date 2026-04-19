"""Generate a .env.template file from an existing .env, blanking out values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TemplateResult:
    template: Dict[str, str]
    source_keys: List[str]
    sensitive_keys: List[str]

    def summary(self) -> str:
        lines = [
            f"Template keys : {len(self.template)}",
            f"Sensitive keys: {len(self.sensitive_keys)}",
        ]
        return "\n".join(lines)


_SENSITIVE_FRAGMENTS = ("SECRET", "PASSWORD", "PASS", "TOKEN", "KEY", "PRIVATE", "AUTH")


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(frag in upper for frag in _SENSITIVE_FRAGMENTS)


def generate_template(
    env: Dict[str, str],
    placeholder: str = "",
    sensitive_placeholder: Optional[str] = None,
    keep_values: bool = False,
) -> TemplateResult:
    """Return a TemplateResult whose .template maps every key to a blanked value.

    Args:
        env: Source environment dict.
        placeholder: Value to use for non-sensitive keys (default empty string).
        sensitive_placeholder: Value for sensitive keys; defaults to placeholder.
        keep_values: If True, non-sensitive values are preserved as-is.
    """
    if sensitive_placeholder is None:
        sensitive_placeholder = placeholder

    template: Dict[str, str] = {}
    sensitive_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key):
            sensitive_keys.append(key)
            template[key] = sensitive_placeholder
        else:
            template[key] = value if keep_values else placeholder

    return TemplateResult(
        template=template,
        source_keys=list(env.keys()),
        sensitive_keys=sensitive_keys,
    )


def render_template(result: TemplateResult, comment_header: str = "") -> str:
    """Render a TemplateResult to a .env-style string."""
    lines: List[str] = []
    if comment_header:
        for line in comment_header.splitlines():
            lines.append(f"# {line}")
        lines.append("")
    for key, value in result.template.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"
