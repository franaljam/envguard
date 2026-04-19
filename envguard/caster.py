"""Type-casting utilities for .env values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class CastError(ValueError):
    pass


@dataclass
class CastResult:
    casted: Dict[str, Any]
    failed: Dict[str, str]  # key -> error message
    original: Dict[str, str]

    def has_failures(self) -> bool:
        return bool(self.failed)

    def summary(self) -> str:
        lines = [f"Casted {len(self.casted)} keys successfully."]
        if self.failed:
            lines.append(f"{len(self.failed)} key(s) failed to cast:")
            for k, msg in self.failed.items():
                lines.append(f"  {k}: {msg}")
        return "\n".join(lines)


_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def _cast_value(value: str, type_hint: str) -> Any:
    t = type_hint.lower()
    if t == "int":
        try:
            return int(value)
        except ValueError:
            raise CastError(f"cannot cast {value!r} to int")
    if t == "float":
        try:
            return float(value)
        except ValueError:
            raise CastError(f"cannot cast {value!r} to float")
    if t == "bool":
        if value.lower() in _BOOL_TRUE:
            return True
        if value.lower() in _BOOL_FALSE:
            return False
        raise CastError(f"cannot cast {value!r} to bool")
    if t == "list":
        return [item.strip() for item in value.split(",") if item.strip()]
    if t == "str":
        return value
    raise CastError(f"unknown type hint {type_hint!r}")


def cast_env(
    env: Dict[str, str],
    schema: Dict[str, str],
    strict: bool = False,
) -> CastResult:
    """Cast env values according to a type schema.

    Args:
        env: raw string env dict.
        schema: mapping of key -> type hint (int, float, bool, list, str).
        strict: if True, raise CastError on first failure instead of collecting.
    """
    casted: Dict[str, Any] = {}
    failed: Dict[str, str] = {}

    for key, value in env.items():
        if key in schema:
            try:
                casted[key] = _cast_value(value, schema[key])
            except CastError as exc:
                if strict:
                    raise
                failed[key] = str(exc)
        else:
            casted[key] = value

    return CastResult(casted=casted, failed=failed, original=dict(env))
