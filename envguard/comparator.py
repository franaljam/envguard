"""Compare two .env files and produce a structured comparison report."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyComparison:
    key: str
    left: Optional[str]
    right: Optional[str]
    status: str  # 'match' | 'changed' | 'left_only' | 'right_only'


@dataclass
class CompareResult:
    comparisons: List[KeyComparison] = field(default_factory=list)

    def matches(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.status == "match"]

    def changed(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.status == "changed"]

    def left_only(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.status == "left_only"]

    def right_only(self) -> List[KeyComparison]:
        return [c for c in self.comparisons if c.status == "right_only"]

    def is_equal(self) -> bool:
        return not self.changed() and not self.left_only() and not self.right_only()

    def summary(self) -> str:
        parts = []
        if self.is_equal():
            return "Environments are identical."
        if self.changed():
            parts.append(f"{len(self.changed())} changed")
        if self.left_only():
            parts.append(f"{len(self.left_only())} left-only")
        if self.right_only():
            parts.append(f"{len(self.right_only())} right-only")
        return ", ".join(parts) + "."


def compare_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    ignore_values: bool = False,
) -> CompareResult:
    all_keys = sorted(set(left) | set(right))
    comparisons: List[KeyComparison] = []
    for key in all_keys:
        in_left = key in left
        in_right = key in right
        if in_left and in_right:
            if ignore_values or left[key] == right[key]:
                status = "match"
            else:
                status = "changed"
            comparisons.append(KeyComparison(key, left[key], right[key], status))
        elif in_left:
            comparisons.append(KeyComparison(key, left[key], None, "left_only"))
        else:
            comparisons.append(KeyComparison(key, None, right[key], "right_only"))
    return CompareResult(comparisons=comparisons)
