"""Patch an env dict by applying a set of key-value overrides or deletions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchAction:
    key: str
    operation: str          # 'set' | 'delete'
    old_value: Optional[str]
    new_value: Optional[str]


@dataclass
class PatchResult:
    env: Dict[str, str]
    actions: List[PatchAction] = field(default_factory=list)

    def changed(self) -> bool:
        return len(self.actions) > 0

    def summary(self) -> str:
        if not self.actions:
            return "No patches applied."
        lines = [f"{len(self.actions)} patch(es) applied:"]
        for a in self.actions:
            if a.operation == "set":
                if a.old_value is None:
                    lines.append(f"  + {a.key} = {a.new_value!r}  (added)")
                else:
                    lines.append(
                        f"  ~ {a.key}: {a.old_value!r} -> {a.new_value!r}  (updated)"
                    )
            else:
                lines.append(f"  - {a.key}  (deleted)")
        return "\n".join(lines)


def patch_env(
    env: Dict[str, str],
    *,
    set_keys: Optional[Dict[str, str]] = None,
    delete_keys: Optional[List[str]] = None,
) -> PatchResult:
    """Return a new env dict with *set_keys* applied and *delete_keys* removed.

    The original dict is never mutated.
    """
    result = dict(env)
    actions: List[PatchAction] = []

    for key, value in (set_keys or {}).items():
        old = result.get(key)
        result[key] = value
        actions.append(PatchAction(key=key, operation="set", old_value=old, new_value=value))

    for key in delete_keys or []:
        if key in result:
            old = result.pop(key)
            actions.append(PatchAction(key=key, operation="delete", old_value=old, new_value=None))

    return PatchResult(env=result, actions=actions)
