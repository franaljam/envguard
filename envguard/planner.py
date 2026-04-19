"""Plan and preview changes before applying them to an env dict."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PlanAction:
    action: str  # 'set', 'delete', 'rename'
    key: str
    value: Optional[str] = None
    new_key: Optional[str] = None


@dataclass
class PlanResult:
    actions: List[PlanAction]
    preview: Dict[str, str]
    original: Dict[str, str]

    def changed(self) -> bool:
        return self.preview != self.original

    def summary(self) -> str:
        if not self.actions:
            return "No planned changes."
        lines = [f"Planned {len(self.actions)} change(s):"]
        for a in self.actions:
            if a.action == "set":
                lines.append(f"  SET {a.key}={a.value}")
            elif a.action == "delete":
                lines.append(f"  DELETE {a.key}")
            elif a.action == "rename":
                lines.append(f"  RENAME {a.key} -> {a.new_key}")
        return "\n".join(lines)


def plan_env(
    env: Dict[str, str],
    set_keys: Optional[Dict[str, str]] = None,
    delete_keys: Optional[List[str]] = None,
    rename_keys: Optional[Dict[str, str]] = None,
) -> PlanResult:
    """Build a preview of what the env would look like after applying actions."""
    actions: List[PlanAction] = []
    result = dict(env)

    for key, val in (set_keys or {}).items():
        actions.append(PlanAction(action="set", key=key, value=val))
        result[key] = val

    for key in (delete_keys or []):
        if key in result:
            actions.append(PlanAction(action="delete", key=key))
            del result[key]

    for old_key, new_key in (rename_keys or {}).items():
        if old_key in result:
            actions.append(PlanAction(action="rename", key=old_key, new_key=new_key))
            result[new_key] = result.pop(old_key)

    return PlanResult(actions=actions, preview=result, original=dict(env))
