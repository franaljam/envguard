"""Pad missing keys in an env dict from a reference/template env."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PadResult:
    env: Dict[str, str]
    padded: Dict[str, str]  # keys added with their default values
    _original: Dict[str, str] = field(repr=False, compare=False)

    def changed(self) -> bool:
        return bool(self.padded)

    def summary(self) -> str:
        if not self.padded:
            return "No keys padded; env is already complete."
        keys = ", ".join(sorted(self.padded))
        return f"Padded {len(self.padded)} missing key(s): {keys}"


def pad_env(
    env: Dict[str, str],
    reference: Dict[str, str],
    default: Optional[str] = "",
    overwrite: bool = False,
) -> PadResult:
    """Add keys present in *reference* but missing from *env*.

    Args:
        env: The target env dict to pad.
        reference: The reference env dict whose keys act as the schema.
        default: Value to use when the reference value should not be copied.
                 Pass ``None`` to copy the actual reference value.
        overwrite: If True, overwrite existing keys with reference values.

    Returns:
        PadResult with the padded env and metadata.
    """
    result = dict(env)
    padded: Dict[str, str] = {}

    for key, ref_value in reference.items():
        if key not in result or overwrite:
            value = ref_value if default is None else default
            if result.get(key) != value or key not in result:
                padded[key] = value
            result[key] = value

    return PadResult(env=result, padded=padded, _original=dict(env))
