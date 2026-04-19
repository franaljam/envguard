"""Tag .env keys with metadata labels (e.g. secret, config, feature-flag)."""
from dataclasses import dataclass, field
from typing import Dict, List, Set

DEFAULT_SECRET_PATTERNS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PRIVATE", "CREDENTIAL")
DEFAULT_FLAG_PATTERNS = ("ENABLE_", "DISABLE_", "FLAG_", "FEATURE_")


@dataclass
class TagResult:
    tags: Dict[str, Set[str]] = field(default_factory=dict)

    def keys_with_tag(self, tag: str) -> List[str]:
        return [k for k, t in self.tags.items() if tag in t]

    def summary(self) -> str:
        lines = []
        for key, t in sorted(self.tags.items()):
            lines.append(f"{key}: {', '.join(sorted(t))}")
        return "\n".join(lines) if lines else "No tags assigned."

    def all_tags(self) -> Set[str]:
        """Return the set of all unique tags assigned across all keys."""
        return {tag for t in self.tags.values() for tag in t}


def tag_env(
    env: Dict[str, str],
    secret_patterns: tuple = DEFAULT_SECRET_PATTERNS,
    flag_patterns: tuple = DEFAULT_FLAG_PATTERNS,
    extra_tags: Dict[str, Set[str]] = None,
) -> TagResult:
    """Assign tags to each key based on naming patterns."""
    result: Dict[str, Set[str]] = {}
    for key in env:
        t: Set[str] = set()
        upper = key.upper()
        if any(p in upper for p in secret_patterns):
            t.add("secret")
        if any(upper.startswith(p) for p in flag_patterns):
            t.add("feature-flag")
        if not t:
            t.add("config")
        if extra_tags and key in extra_tags:
            t.update(extra_tags[key])
        result[key] = t
    return TagResult(tags=result)
