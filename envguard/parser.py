"""Parser for .env files."""

from pathlib import Path
from typing import Dict, Optional


class EnvParseError(Exception):
    """Raised when a .env file cannot be parsed."""
    pass


def _strip_quotes(value: str) -> str:
    """Strip matching surrounding quotes from a value string."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_env_file(filepath: str | Path) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dictionary of key-value pairs.

    Supports:
    - KEY=VALUE
    - KEY="VALUE" or KEY='VALUE'
    - Comments (#)
    - Empty lines
    - Keys without values (KEY=)

    Args:
        filepath: Path to the .env file.

    Returns:
        Dictionary mapping variable names to their values.

    Raises:
        EnvParseError: If the file cannot be read or contains invalid syntax.
    """
    path = Path(filepath)

    if not path.exists():
        raise EnvParseError(f"File not found: {filepath}")

    env_vars: Dict[str, Optional[str]] = {}

    try:
        with path.open("r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise EnvParseError(
                        f"Invalid syntax at line {lineno}: '{line}'"
                    )

                key, _, value = line.partition("=")
                key = key.strip()

                if not key:
                    raise EnvParseError(
                        f"Empty key at line {lineno}: '{line}'"
                    )

                if " " in key or "\t" in key:
                    raise EnvParseError(
                        f"Key contains whitespace at line {lineno}: '{key}'"
                    )

                value = _strip_quotes(value.strip())

                env_vars[key] = value if value else None

    except OSError as e:
        raise EnvParseError(f"Could not read file '{filepath}': {e}") from e

    return env_vars
