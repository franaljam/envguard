"""Classify .env keys into semantic categories."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import re

_CATEGORIES: Dict[str, List[str]] = {
    "database": [r"DB_", r"DATABASE_", r"POSTGRES", r"MYSQL", r"MONGO", r"REDIS"],
    "auth": [r"SECRET", r"TOKEN", r"API_KEY", r"PASSWORD", r"PASSWD", r"AUTH_"],
    "network": [r"HOST", r"PORT", r"URL", r"ENDPOINT", r"ADDR"],
    "feature_flag": [r"FEATURE_", r"FLAG_", r"ENABLE_", r"DISABLE_"],
    "logging": [r"LOG_", r"LOGGING_", r"DEBUG", r"VERBOSE"],
    "cloud": [r"AWS_", r"GCP_", r"AZURE_", r"S3_", r"GCS_"],
}


@dataclass
class ClassifyResult:
    categories: Dict[str, List[str]] = field(default_factory=dict)
    uncategorized: List[str] = field(default_factory=list)

    def keys_in(self, category: str) -> List[str]:
        return self.categories.get(category, [])

    def category_names(self) -> List[str]:
        return sorted(self.categories.keys())

    def summary(self) -> str:
        lines = []
        for cat in self.category_names():
            keys = self.categories[cat]
            lines.append(f"{cat}: {len(keys)} key(s)")
        if self.uncategorized:
            lines.append(f"uncategorized: {len(self.uncategorized)} key(s)")
        return "\n".join(lines) if lines else "No keys classified."


def _detect_category(key: str) -> str | None:
    upper = key.upper()
    for category, patterns in _CATEGORIES.items():
        for pat in patterns:
            if re.search(pat, upper):
                return category
    return None


def classify_env(env: Dict[str, str]) -> ClassifyResult:
    categories: Dict[str, List[str]] = {}
    uncategorized: List[str] = []
    for key in env:
        cat = _detect_category(key)
        if cat:
            categories.setdefault(cat, []).append(key)
        else:
            uncategorized.append(key)
    return ClassifyResult(categories=categories, uncategorized=uncategorized)
