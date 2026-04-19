"""Score an env file for overall health/quality."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ScoreBreakdown:
    category: str
    score: int
    max_score: int
    notes: List[str] = field(default_factory=list)


@dataclass
class ScoreResult:
    breakdowns: List[ScoreBreakdown] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(b.score for b in self.breakdowns)

    @property
    def max_total(self) -> int:
        return sum(b.max_score for b in self.breakdowns)

    @property
    def grade(self) -> str:
        if self.max_total == 0:
            return "N/A"
        pct = self.total / self.max_total
        if pct >= 0.9:
            return "A"
        if pct >= 0.75:
            return "B"
        if pct >= 0.6:
            return "C"
        if pct >= 0.4:
            return "D"
        return "F"

    def summary(self) -> str:
        return f"Score: {self.total}/{self.max_total} (Grade: {self.grade})"


def score_env(env: Dict[str, str]) -> ScoreResult:
    result = ScoreResult()

    # Completeness: no empty values
    empty = [k for k, v in env.items() if v == ""]
    comp_score = max(0, 10 - len(empty) * 2)
    result.breakdowns.append(ScoreBreakdown(
        "completeness", comp_score, 10,
        [f"{k} has empty value" for k in empty],
    ))

    # Naming: all uppercase, no spaces
    bad_keys = [k for k in env if not k.isupper() or " " in k]
    name_score = max(0, 10 - len(bad_keys) * 2)
    result.breakdowns.append(ScoreBreakdown(
        "naming", name_score, 10,
        [f"{k} violates naming convention" for k in bad_keys],
    ))

    # Size: penalise very large envs (>50 keys)
    size_score = 10 if len(env) <= 50 else max(0, 10 - (len(env) - 50) // 5)
    notes = [] if len(env) <= 50 else [f"{len(env)} keys exceeds recommended 50"]
    result.breakdowns.append(ScoreBreakdown("size", size_score, 10, notes))

    return result
