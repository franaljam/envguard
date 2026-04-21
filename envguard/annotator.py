"""Annotate .env keys with inline comments describing their purpose or metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AnnotationResult:
    annotated: Dict[str, str]          # key -> "VALUE  # comment"
    source: Dict[str, str]             # original env dict
    comments: Dict[str, str]           # key -> raw comment text
    _skipped: List[str] = field(default_factory=list)

    def skipped(self) -> List[str]:
        return list(self._skipped)

    def summary(self) -> str:
        n = len(self.comments)
        s = len(self._skipped)
        return f"{n} key(s) annotated, {s} skipped (no annotation defined)"


def annotate_env(
    env: Dict[str, str],
    annotations: Dict[str, str],
    *,
    skip_unannotated: bool = False,
) -> AnnotationResult:
    """Attach inline comments to env values.

    Args:
        env: The source environment dict.
        annotations: Mapping of key -> comment string.
        skip_unannotated: When True, keys without an annotation are omitted
                          from the *annotated* output.

    Returns:
        AnnotationResult with annotated lines, comments, and skipped keys.
    """
    annotated: Dict[str, str] = {}
    comments: Dict[str, str] = {}
    skipped: List[str] = []

    for key, value in env.items():
        comment = annotations.get(key)
        if comment:
            annotated[key] = f"{value}  # {comment}"
            comments[key] = comment
        else:
            skipped.append(key)
            if not skip_unannotated:
                annotated[key] = value

    return AnnotationResult(
        annotated=annotated,
        source=dict(env),
        comments=comments,
        _skipped=skipped,
    )
