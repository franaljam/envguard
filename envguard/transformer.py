"""Transform .env variable keys or values in bulk."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List


class TransformError(Exception):
    pass


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str]
    applied: List[str] = field(default_factory=list)

    def changed_keys(self) -> List[str]:
        return [
            k for k in self.transformed
            if self.transformed[k] != self.original.get(k)
        ]


def _apply(env: Dict[str, str], transforms: List[tuple]) -> TransformResult:
    result = dict(env)
    applied = []
    for name, fn in transforms:
        try:
            result = {k: fn(k, v) for k, v in result.items()}
            applied.append(name)
        except Exception as exc:
            raise TransformError(f"Transform '{name}' failed: {exc}") from exc
    return TransformResult(original=env, transformed=result, applied=applied)


def strip_whitespace(key: str, value: str) -> str:  # noqa: ARG001
    return value.strip()


def to_uppercase_value(key: str, value: str) -> str:  # noqa: ARG001
    return value.upper()


def mask_non_empty(key: str, value: str) -> str:  # noqa: ARG001
    return "***" if value else value


def prefix_keys(prefix: str) -> Callable[[str, str], str]:
    """Return a transform that prepends prefix to every key."""
    def _transform(key: str, value: str) -> str:  # noqa: ARG001
        return value  # values unchanged; key renaming handled separately
    _transform.__name__ = f"prefix_keys({prefix})"
    return _transform


def rename_keys(env: Dict[str, str], prefix: str) -> Dict[str, str]:
    """Return a new dict with all keys prefixed."""
    return {f"{prefix}{k}": v for k, v in env.items()}


def transform_env(
    env: Dict[str, str],
    *,
    strip: bool = False,
    uppercase_values: bool = False,
    mask: bool = False,
) -> TransformResult:
    transforms: List[tuple] = []
    if strip:
        transforms.append(("strip_whitespace", strip_whitespace))
    if uppercase_values:
        transforms.append(("to_uppercase_value", to_uppercase_value))
    if mask:
        transforms.append(("mask_non_empty", mask_non_empty))
    return _apply(env, transforms)
