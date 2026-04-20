"""summarizer.py — Produce a human-readable summary report for an entire .env file.

Combines profiling, auditing, linting, scoring, and tagging into a single
consolidated view so operators can assess a file at a glance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envguard.profiler import profile_env, ProfileResult
from envguard.auditor import audit_env, AuditResult
from envguard.linter import lint_env, LintResult
from envguard.scorer import score_env, ScoreResult
from envguard.tagger import tag_env, TagResult


@dataclass(frozen=True)
class SummarySection:
    """A named section within the consolidated summary."""

    title: str
    lines: List[str] = field(default_factory=list)


@dataclass
class SummaryResult:
    """Aggregated summary of a parsed .env dictionary."""

    profile: ProfileResult
    audit: AuditResult
    lint: LintResult
    score: ScoreResult
    tags: TagResult

    # ------------------------------------------------------------------ #
    # Convenience helpers
    # ------------------------------------------------------------------ #

    @property
    def has_errors(self) -> bool:
        """True when any audit or lint errors are present."""
        return bool(self.audit.errors) or bool(self.lint.errors)

    @property
    def has_warnings(self) -> bool:
        """True when any audit or lint warnings are present."""
        return bool(self.audit.warnings) or bool(self.lint.warnings)

    @property
    def grade(self) -> str:
        """Letter grade derived from the scorer."""
        return self.score.grade

    def sections(self) -> List[SummarySection]:
        """Return ordered sections suitable for display."""
        secs: List[SummarySection] = []

        # --- Profile ---
        p = self.profile
        secs.append(SummarySection(
            title="Profile",
            lines=[
                f"Total keys   : {p.total}",
                f"Empty values : {p.empty_count}",
                f"Sensitive    : {p.sensitive_count}",
                f"Longest key  : {p.longest_key or '—'} ({p.longest_key_length} chars)",
            ],
        ))

        # --- Score ---
        s = self.score
        secs.append(SummarySection(
            title="Score",
            lines=[
                f"Grade        : {s.grade}",
                f"Total        : {s.total}/{s.max_total}",
                f"Completeness : {s.breakdown.completeness}",
                f"Naming       : {s.breakdown.naming}",
                f"Security     : {s.breakdown.security}",
                f"Size         : {s.breakdown.size}",
            ],
        ))

        # --- Audit ---
        audit_lines: List[str] = []
        for issue in self.audit.issues:
            prefix = "[ERROR]" if issue.severity == "error" else "[WARN] "
            audit_lines.append(f"{prefix} {issue.key}: {issue.message}")
        if not audit_lines:
            audit_lines = ["No audit issues found."]
        secs.append(SummarySection(title="Audit", lines=audit_lines))

        # --- Lint ---
        lint_lines: List[str] = []
        for issue in self.lint.issues:
            prefix = "[ERROR]" if issue.severity == "error" else "[WARN] "
            lint_lines.append(f"{prefix} {issue.key}: {issue.message}")
        if not lint_lines:
            lint_lines = ["No lint issues found."]
        secs.append(SummarySection(title="Lint", lines=lint_lines))

        # --- Tags ---
        tag_lines: List[str] = []
        for tag in sorted(self.tags.all_tags()):
            keys = self.tags.keys_with_tag(tag)
            tag_lines.append(f"{tag:12s}: {', '.join(sorted(keys))}")
        if not tag_lines:
            tag_lines = ["No tags assigned."]
        secs.append(SummarySection(title="Tags", lines=tag_lines))

        return secs

    def render(self, width: int = 60) -> str:
        """Render the full summary as a multi-line string."""
        bar = "=" * width
        thin = "-" * width
        parts: List[str] = [bar, "  envguard — Environment Summary", bar]
        for sec in self.sections():
            parts.append(f"\n[ {sec.title} ]")
            parts.append(thin)
            parts.extend(sec.lines)
        parts.append("\n" + bar)
        return "\n".join(parts)


def summarize_env(
    env: Dict[str, str],
    *,
    allow_lowercase: bool = False,
    check_weak_passwords: bool = True,
) -> SummaryResult:
    """Build a :class:`SummaryResult` from *env*.

    Parameters
    ----------
    env:
        Parsed key/value mapping.
    allow_lowercase:
        Passed through to the linter so lowercase keys are not flagged.
    check_weak_passwords:
        Passed through to the auditor.
    """
    return SummaryResult(
        profile=profile_env(env),
        audit=audit_env(env, check_weak_passwords=check_weak_passwords),
        lint=lint_env(env, allow_lowercase=allow_lowercase),
        score=score_env(env),
        tags=tag_env(env),
    )
