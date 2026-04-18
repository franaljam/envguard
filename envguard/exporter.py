"""Export parsed .env variables to different formats (JSON, YAML, shell)."""
from __future__ import annotations

import json
from typing import Dict

try:
    import yaml as _yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


class ExportError(Exception):
    pass


def to_json(variables: Dict[str, str], *, indent: int = 2) -> str:
    """Serialize variables to a JSON string."""
    return json.dumps(variables, indent=indent, sort_keys=True)


def to_yaml(variables: Dict[str, str]) -> str:
    """Serialize variables to a YAML string."""
    if not _YAML_AVAILABLE:
        raise ExportError(
            "PyYAML is not installed. Run: pip install pyyaml"
        )
    return _yaml.dump(dict(sorted(variables.items())), default_flow_style=False)


def to_shell(variables: Dict[str, str]) -> str:
    """Serialize variables as export statements for shell sourcing."""
    lines = []
    for key in sorted(variables):
        value = variables[key].replace("'", "'\\''")
        lines.append(f"export {key}='{value}'")
    return "\n".join(lines)


_FORMATS = {"json": to_json, "shell": to_shell}
if _YAML_AVAILABLE:
    _FORMATS["yaml"] = to_yaml


def export_env(variables: Dict[str, str], fmt: str) -> str:
    """Export variables in the requested format.

    Args:
        variables: Mapping of env var names to values.
        fmt: One of 'json', 'yaml', 'shell'.

    Returns:
        Formatted string representation.

    Raises:
        ExportError: If the format is unsupported or a dependency is missing.
    """
    fmt = fmt.lower()
    if fmt == "yaml":
        return to_yaml(variables)
    if fmt not in _FORMATS:
        raise ExportError(
            f"Unsupported format '{fmt}'. Choose from: json, yaml, shell"
        )
    return _FORMATS[fmt](variables)
