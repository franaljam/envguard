"""Convert env dict to various string representations."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


class StringerError(Exception):
    pass


@dataclass
class StringResult:
    lines: List[str] = field(default_factory=list)
    format: str = "dotenv"

    def text(self) -> str:
        return "\n".join(self.lines)


def _escape_value(value: str) -> str:
    if any(c in value for c in (" ", "\t", "#", "'", '"')):
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def to_dotenv(env: Dict[str, str], sort: bool = False) -> StringResult:
    keys = sorted(env) if sort else list(env)
    lines = [f"{k}={_escape_value(v)}" for k, v in ((k, env[k]) for k in keys)]
    return StringResult(lines=lines, format="dotenv")


def to_ini(env: Dict[str, str], section: str = "env", sort: bool = False) -> StringResult:
    keys = sorted(env) if sort else list(env)
    lines = [f"[{section}]"]
    lines += [f"{k} = {env[k]}" for k in keys]
    return StringResult(lines=lines, format="ini")


def to_docker(env: Dict[str, str], sort: bool = False) -> StringResult:
    keys = sorted(env) if sort else list(env)
    lines = [f"-e {k}={_escape_value(env[k])}" for k in keys]
    return StringResult(lines=lines, format="docker")


_FORMATS = {"dotenv": to_dotenv, "ini": to_ini, "docker": to_docker}


def stringify_env(
    env: Dict[str, str],
    fmt: str = "dotenv",
    sort: bool = False,
    **kwargs,
) -> StringResult:
    if fmt not in _FORMATS:
        raise StringerError(f"Unknown format '{fmt}'. Choose from: {', '.join(_FORMATS)}")
    return _FORMATS[fmt](env, sort=sort, **kwargs)
