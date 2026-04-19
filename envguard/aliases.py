"""Alias management: map shorthand keys to canonical names."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AliasResult:
    env: Dict[str, str]
    resolved: Dict[str, str]  # alias -> canonical
    unresolved: List[str] = field(default_factory=list)

    def has_unresolved(self) -> bool:
        return bool(self.unresolved)

    def summary(self) -> str:
        lines = []
        if self.resolved:
            lines.append(f"Resolved {len(self.resolved)} alias(es):")
            for alias, canonical in self.resolved.items():
                lines.append(f"  {alias} -> {canonical}")
        if self.unresolved:
            lines.append(f"Unresolved {len(self.unresolved)} alias(es): {', '.join(self.unresolved)}")
        if not lines:
            lines.append("No aliases processed.")
        return "\n".join(lines)


def resolve_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
    keep_alias: bool = False,
) -> AliasResult:
    """Resolve alias keys to canonical keys in env.

    Args:
        env: source environment dict.
        aliases: mapping of alias -> canonical key name.
        keep_alias: if True, retain the alias key alongside canonical.

    Returns:
        AliasResult with updated env.
    """
    result = dict(env)
    resolved: Dict[str, str] = {}
    unresolved: List[str] = []

    for alias, canonical in aliases.items():
        if alias in result:
            value = result[alias]
            result[canonical] = value
            if not keep_alias:
                del result[alias]
            resolved[alias] = canonical
        else:
            unresolved.append(alias)

    return AliasResult(env=result, resolved=resolved, unresolved=unresolved)
